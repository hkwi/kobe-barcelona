import pandas as pd
import sqlite3
import json
import re
import sklearn.decomposition
import numpy

filename = "tpob_2015-cp02.csv"

areas_db = sqlite3.connect("areas_b.db")
areas_db.row_factory = sqlite3.Row
cur = areas_db.cursor()
def query_geo(barris):
	cur.execute("SELECT * FROM barcelona WHERE barris=?", (barris,))
	area = cur.fetchone()
	if area is None:
		cur.execute("INSERT INTO barcelona(barris) VALUES(?)", (barris,))
		areas_db.commit()
	elif area["result"]:
		info = dict(
			lkey = area["key"],
			barris = barris,
		)
		res = json.loads(area["result"])
		if res["status"] != "ZERO_RESULTS":
			info["lname"] = res["results"][0].get("formatted_address")
			loc = res["results"][0]["geometry"]["location"]
			info["lat"] = loc["lat"]
			info["lng"] = loc["lng"]
		return info

def csv2json(filename):
	fail = None
	data = []
	for n,row in pd.read_csv(filename).iterrows():
		if not isinstance(row["Barris"], str):
			continue
		
		m = re.match(r"^\d+\.(.*)$", row["Barris"])
		if not m:
			continue
		
		barris = m.group(1).strip().replace("AEI ","")
		g = query_geo(barris)
		if g:
			data.append(pd.concat([row, pd.Series(g)]))
		else:
			fail = Exception("geo "+barris)
	
	if fail:
		raise fail
	
	data = pd.DataFrame(data, index=range(len(data)), columns=data[0].index).dropna()
	
	e = [c for c in data.columns if c.find("95 anys ") >= 0][0]
	
	model = sklearn.decomposition.NMF(3)
	w = model.fit_transform(data.loc[:,"0 anys":e].as_matrix())
	b = model.components_
	cidx = pd.Series.sort_values(pd.Series((range(len(b.T))*b).sum(axis=1)/b.sum(axis=1), index=[0,1,2]))
	rgb = [u[1] for u in sorted(zip(cidx.index, "GBR"))]
	
	pdw = pd.DataFrame(w, index=data.index, columns=["w"+x for x in rgb])
	w2 = numpy.sqrt((w*w).sum(axis=1))
	w2[w2==0] = 1.0
	n=w.T/w2
	pdn = pd.DataFrame(n.T, index=data.index, columns=rgb)
	data = pd.concat([data, pdw, pdn], axis=1)
	cdata = pd.DataFrame(b.T, columns=rgb)

	m = re.match(r"tpob_(?P<y>\d{4})-cp02.csv", filename)
	base = "barcelona_"+m.groupdict()["y"]

	out = []
	for idx, d in data.iterrows():
		out.append(dict(lat=d["lat"], lng=d["lng"],
			wR=d["wR"], wG=d["wG"], wB=d["wB"],
			R=d["R"], G=d["G"], B=d["B"],
			ages=[int(x) for x in d["0 anys":e]],
			lkey=d["lkey"], name=d["lname"],
			barris=d["barris"]))
	
	with open(base+"_ages.json", "w", encoding="UTF-8") as fp:
		json.dump(out, fp, ensure_ascii=False, allow_nan=False)
	
	out = dict()
	for idx, d in cdata.T.iterrows():
		out[idx] = list(d)
	
	with open(base+"_rgb.json", "w", encoding="UTF-8") as fp:
		json.dump(out, fp, allow_nan=False)

fs = [
	"tpob_2007-cp02.csv",
	"tpob_2008-cp02.csv",
	"tpob_2009-cp02.csv",
	"tpob_2010-cp02.csv",
	"tpob_2011-cp02.csv",
	"tpob_2012-cp02.csv",
	"tpob_2013-cp02.csv",
	"tpob_2014-cp02.csv",
	"tpob_2015-cp02.csv",
]
for f in fs:
	csv2json(f)
