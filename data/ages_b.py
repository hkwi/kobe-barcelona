import pandas as pd
import sqlite3
import json
import re

filename = "tpob_2015-cp02.csv"

areas_db = sqlite3.connect("areas_b.db")
areas_db.row_factory = sqlite3.Row
cur = areas_db.cursor()

out = dict()
for n,r in pd.read_csv(filename).iterrows():
	if not isinstance(r["Barris"], str):
		continue
	
	m = re.match(r"^\d+\.(.*)$", r["Barris"])
	if not m:
		continue
	
	barris = m.group(1).strip()
	
	cur.execute("SELECT * FROM barcelona WHERE barris=?", (barris,))
	area = cur.fetchone()
	res = json.loads(area["result"])
	if res["status"] == "ZERO_RESULTS":
		d = pd.Series([None, None, None, None], ["lkey", "lname", "lat", "lng"])
	else:
		loc = res["results"][0]["geometry"]["location"]
		fa = res["results"][0].get("formatted_address")
		d = pd.Series([area["key"], fa, loc["lat"], loc["lng"]], ["lkey", "lname", "lat", "lng"])
	
	out[n] = pd.concat([r,d])

data = pd.DataFrame(out).T.dropna()
e = [c for c in data.columns if c.find("95 anys ") >= 0][0]

model = sklearn.decomposition.NMF(3)
w = model.fit_transform(data.loc[:,"0 anys":e].as_matrix())
b = model.components_
cidx = pd.Series.sort_values(pd.Series((range(len(b.T))*b).sum(axis=1), index=[0,1,2]))
pdw = pd.DataFrame(w, index=data.index, columns=["w"+"GBR"[x] for x in cidx.index])
n=w.T/numpy.sqrt((w*w).sum(axis=1))
pdn = pd.DataFrame(n.T, index=data.index, columns=["GBR"[x] for x in cidx.index])
data = pd.concat([data, pdw, pdn], axis=1)
cdata = pd.DataFrame(b.T, columns=["GBR"[list(cidx.index).index(x)] for x in range(3)])

out = []
for idx, d in data.iterrows():
	out.append(dict(lat=d["lat"], lng=d["lng"],
		wR=d["wR"], wG=d["wG"], wB=d["wB"],
		R=d["R"], G=d["G"], B=d["B"],
		ages=[int(x) for x in d["0 anys":e]],
		lkey=d["lkey"], name=d["lname"],
		barris=d["Barris"]))

with open("ages_b.json", "w", encoding="UTF-8") as fp:
	json.dump(out, fp, ensure_ascii=False, allow_nan=False)

out = dict()
for idx, d in cdata.T.iterrows():
	out[idx] = list(d)

with open("rgb_b.json", "w", encoding="UTF-8") as fp:
	json.dump(out, fp, allow_nan=False)

