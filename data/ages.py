import pandas as pd
import sqlite3
import json
import numpy
import sklearn.decomposition

filename = "zensi2409.xls"

data = None
e = pd.ExcelFile(filename)
for sheet_name in e.sheet_names:
	if sheet_name == "神戸市":
		continue
	
	d = e.parse(sheet_name, skiprows=1).loc[1:,:]
	if data is None:
		data = d
	else:
		d.index = [len(data) + d for d in d.index]
		data = pd.concat([data, d])

location = dict()
areas_db = sqlite3.connect("areas.db")
areas_db.row_factory = sqlite3.Row
cur = areas_db.cursor()
for idx in data.index:
	args = (data.loc[idx,"区・支所"], data.loc[idx,"町名"])
	cur.execute("SELECT * FROM gmap WHERE ku=? AND cho=?",
		(data.loc[idx,"区・支所"], data.loc[idx,"町名"]))
	area = cur.fetchone()
	res = json.loads(area["result"])
	if res["status"] == "ZERO_RESULTS":
		d = pd.Series([None, None, None, None], ["lkey", "name", "lat", "lng"])
	else:
		fa = res["results"][0].get("formatted_address")
		geo = res["results"][0]["geometry"]
#		sz = None
#		if "bounds" in geo:
#			lat = geo["bounds"]["northeast"]["lat"]+geo["bounds"]["southwest"]["lat"];
#			delta_lat = geo["bounds"]["northeast"]["lat"]-geo["bounds"]["southwest"]["lat"];
#			delta_lng = geo["bounds"]["northeast"]["lng"]-geo["bounds"]["southwest"]["lng"];
#			sz = 6000*1000.0*(math.pi*(delta_lat+delta_lng)/360.0) * math.cos(math.pi*lat/360.0)
#			if sz > 500:
#				sz = 500
		
		loc = geo["location"]
		d = pd.Series([area["key"], fa, loc["lat"], loc["lng"]], ["lkey", "name", "lat", "lng"])
	
	location[idx] = d

data = pd.concat([data, pd.DataFrame(location).T], axis=1).dropna()
model = sklearn.decomposition.NMF(3)
w = model.fit_transform(data.loc[:,"0歳":"100歳以上"].as_matrix())
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
		ages=[int(x) for x in d["0歳":"100歳以上"]],
		lkey=d["lkey"], name=d["name"],
		ku=d["区・支所"], cho=d["町名"]))

with open("ages.json", "w", encoding="UTF-8") as fp:
	json.dump(out, fp, ensure_ascii=False, allow_nan=False)

out = dict()
for idx, d in cdata.T.iterrows():
	out[idx] = list(d)

with open("rgb.json", "w", encoding="UTF-8") as fp:
	json.dump(out, fp, allow_nan=False)

