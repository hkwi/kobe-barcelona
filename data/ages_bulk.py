import pandas as pd
import sqlite3
import json
import numpy
import sklearn.decomposition
import re
import os.path

areas_db = sqlite3.connect("areas.db")
areas_db.row_factory = sqlite3.Row
cur = areas_db.cursor()
def query_geo(ku, cho):
	cur.execute("SELECT * FROM gmap WHERE ku=? AND cho=?", (ku, cho))
	area = cur.fetchone()
	if area is None:
		cur.execute("INSERT INTO gmap(ku,cho) VALUES(?,?)", (ku, cho))
		areas_db.commit()
	elif area["result"]:
		info = dict(
			ku = ku,
			cho = cho,
			lkey=area["key"]
		)
		res = json.loads(area["result"])
		if res["status"] != "ZERO_RESULTS":
			info["lname"] = res["results"][0].get("formatted_address")
			loc = res["results"][0]["geometry"]["location"]
			info["lat"] = loc["lat"]
			info["lng"] = loc["lng"]
		return info

def xls2json(filename):
	zensi = False
	m = re.match(r"(?P<p>juuki|zensi)(?P<y>\d{2})(?P<m>\d{2}).xls", filename)
	if m:
		if m.groupdict()["p"]=="zensi":
			zensi = True
		
		y = int(m.groupdict()["y"])
		base = "kobe_%04d" % (y - 12 + 2000)
		if y < 21:
			base += "1231"
		else:
			base += {
				"03": "0331",
				"06": "0630",
				"09": "0930",
				"12": "1231",
			}[m.groupdict()["m"]]
	else:
		raise Exception("base name error")
	
	fail = None
	data = []
	e = pd.ExcelFile(filename)
	for sheet_name in e.sheet_names:
		if sheet_name.strip() in ("全市", "神戸市", "全世帯"):
			continue
		
		d = None
		m = re.match(r"^(\d{2})?(?P<ku>[^\d]+?)(\(再掲\))?$", sheet_name.strip())
		if m:
			ku = m.groupdict()["ku"]
			if ku == "須磨本区":
				ku = "須磨区"
			
			skiprows = 2
			if zensi:
				skiprows = 1
			
			d = e.parse(sheet_name, skiprows=skiprows)
			if zensi:
				d = d.iloc[1:,:]
			
			for n,row in d.iterrows():
				cho = row["町名"]
				if not cho or cho != cho:
					continue
				
				g = query_geo(ku, row["町名"].strip())
				if g:
					data.append(pd.concat([row, pd.Series(g)]))
				else:
					fail = Exception("geo "+m.group(2)+" "+row["町名"])
		else:
			fail = Exception("sheet_name")
	
	if fail:
		raise fail

	data = pd.DataFrame(data, index=range(len(data)), columns=data[0].index).dropna()
	
	def find(key):
		cs = list(data.columns)
		if key in cs:
			return cs.index(key)
		return -1
	
	s = e = -1
	if s < 0 or e < 0:
		s = find("0～4歳")
		e = find("80歳以上")
	
	if s < 0 or e < 0:
		s = find("0歳")
		e = find("100歳以上")
	
	if s < 0 or e < 0:
		raise Exception("column range error")
	
	model = sklearn.decomposition.NMF(3)
	w = model.fit_transform(data.iloc[:,s:e].as_matrix())
	b = model.components_
	cidx = pd.Series.sort_values(pd.Series((range(len(b.T))*b).sum(axis=1)/b.sum(axis=1), index=[0,1,2]))
	
	rgb = [u[1] for u in sorted(zip(cidx.index, "GBR"))]
#	if filename in ("juuki1412.xls", "juuki1512.xls", "juuki1712.xls", "juuki1812.xls", "juuki1912.xls"):
#		rgb = ["G","R","B"]
#	elif filename in ("juuki1312.xls",):
#		rgb = ["R","G","B"]

	pdw = pd.DataFrame(w, index=data.index, columns=["w"+x for x in rgb])
	w2 = numpy.sqrt((w*w).sum(axis=1))
	w2[w2==0] = 1.0
	n=w.T/w2
	pdn = pd.DataFrame(n.T, index=data.index, columns=rgb)
	data = pd.concat([data, pdw, pdn], axis=1)
	cdata = pd.DataFrame(b.T, columns=rgb)

	out = []
	for idx, d in data.iterrows():
		out.append(dict(lat=d["lat"], lng=d["lng"],
			wR=d["wR"], wG=d["wG"], wB=d["wB"],
			R=d["R"], G=d["G"], B=d["B"],
			ages=[int(x) for x in d.iloc[s:e]],
			lkey=d["lkey"], name=d["lname"],
			ku=d["ku"], cho=d["cho"]))

	with open(base+"_ages.json", "w", encoding="UTF-8") as fp:
		json.dump(out, fp, ensure_ascii=False, allow_nan=False)

	out = dict()
	for idx, d in cdata.T.iterrows():
		out[idx] = list(d)

	with open(base+"_rgb.json", "w", encoding="UTF-8") as fp:
		json.dump(out, fp, allow_nan=False)

# これ以前のデータは総人数しかなく、ベクトル化できない
fs = ["juuki1312.xls",
"juuki1412.xls",
"juuki1512.xls",
"juuki1612.xls",
"juuki1712.xls",
"juuki1812.xls",
"juuki1912.xls",
"juuki2012.xls",
"juuki2103.xls",
"juuki2106.xls",
"juuki2109.xls",
"juuki2112.xls",
"juuki2203.xls",
"juuki2206.xls",
"juuki2209.xls",
"juuki2212.xls",
"juuki2303.xls",
"juuki2306.xls",
"juuki2309.xls",
"juuki2312.xls",
"juuki2403.xls",
"juuki2406.xls",
"zensi2409.xls",
"zensi2412.xls",
"zensi2503.xls",
"zensi2506.xls",
"zensi2509.xls",
"zensi2512.xls",
"zensi2603.xls",
"zensi2606.xls",
"zensi2609.xls",
"zensi2612.xls",
"zensi2703.xls",
"zensi2706.xls",
"zensi2709.xls",
"zensi2712.xls",
]
for f in fs:
	xls2json(f)

