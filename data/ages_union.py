import sqlite3
import pandas as pd
import json

def csv2json(kname, bname, prefix):
	data = []
	for n,row in pd.read_csv(bname).iterrows():
		if not isinstance(row["Barris"], str):
			continue
		
		m = re.match(r"^\d+\.(.*)$", row["Barris"])
		if not m:
			continue
		
		barris = m.group(1).strip().replace("AEI ","")
		data.append(pd.concat([row, pd.Series([barris], index=["barris"])]))
	
	b = pd.DataFrame(data, index=range(len(data)), columns=data[0].index).dropna()
	be = [c for c in b.columns if c.find("95 anys ") >= 0][0]
	
	data = []
	e = pd.ExcelFile(kname)
	zensi = kname.startswith("zensi")
	
	for sheet_name in e.sheet_names:
		if sheet_name.strip() in ("全市", "神戸市", "全世帯"):
			continue
		
		d = None
		m = re.match(r"^(\d{2})?(?P<ku>[^\d]+?)(\(再掲\))?$", sheet_name.strip())
		if not m:
			print("unexpected sheet name:"+sheet_name)
			continue
		
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
			
			data.append(pd.concat([row, pd.Series([ku], index=["区"])]))
	k = pd.DataFrame(data, index=range(len(data)), columns=data[0].index).dropna()
	
	def find(key):
		cs = list(k.columns)
		if key in cs:
			return cs.index(key)
		return -1
	
	s = find("0歳")
	m = find("95歳")
	e = find("100歳以上")
	
	k2 = pd.concat([k.iloc[:,range(s,m)], k.iloc[:,range(m,e+1)].sum(axis=1).T], axis=1)
	k2.columns=range(0,96)
	b2 = b.loc[:,"0 anys":be]
	b2.columns=range(0,96)
	b2.index = range(len(k2), len(k2)+len(b2))
	
	model = sklearn.decomposition.NMF(3)
	w = model.fit_transform(pd.concat([k2, b2]))
	w2 = sklearn.preprocessing.normalize(w)
	k3 = pd.concat([k,
		pd.DataFrame(w[:len(k),:], index=k.index, columns=["wR","wG","wB"]),
		pd.DataFrame(w2[:len(k),:], index=k.index, columns=list("RGB"))], axis=1)
	b3 = pd.concat([b,
		pd.DataFrame(w[len(k):,:], index=b.index, columns=["wR","wG","wB"]),
		pd.DataFrame(w2[len(k):,:], index=b.index, columns=list("RGB"))], axis=1)

	# kobe geo
	k_areas_db = sqlite3.connect("areas.db")
	k_areas_db.row_factory = sqlite3.Row
	cur = k_areas_db.cursor()
	def query_geo(ku, cho):
		cur.execute("SELECT * FROM gmap WHERE ku=? AND cho=?", (ku, cho))
		area = cur.fetchone()
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
	
	kout = []
	for idx,d in k3.iterrows():
		g = query_geo(d["区"], d["町名"].strip())
		if not g:
			continue
		
		kout.append(dict(lat=g["lat"], lng=g["lng"],
			wR=d["wR"], wG=d["wG"], wB=d["wB"],
			R=d["R"], G=d["G"], B=d["B"],
			ages=[int(x) for x in d.iloc[s:e+1]],
			lkey=g["lkey"], name=g["lname"],
			ku=g["ku"], cho=g["cho"]))
	
	with open("kobe_union_"+prefix+"_ages.json", "w", encoding="UTF-8") as fp:
		json.dump(kout, fp, ensure_ascii=False, allow_nan=False)
	
	# barcelona geo
	areas_db = sqlite3.connect("areas_b.db")
	areas_db.row_factory = sqlite3.Row
	cur = areas_db.cursor()
	def query_geo(barris):
		cur.execute("SELECT * FROM barcelona WHERE barris=?", (barris,))
		area = cur.fetchone()
		if not area:
			print(barris)
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
	
	bout = []
	for idx,d in b3.iterrows():
		g = query_geo(d["barris"])
		bout.append(dict(lat=g["lat"], lng=g["lng"],
			wR=d["wR"], wG=d["wG"], wB=d["wB"],
			R=d["R"], G=d["G"], B=d["B"],
			ages=[int(x) for x in d["0 anys":be]],
			lkey=g["lkey"], name=g["lname"],
			barris=g["barris"]))
		
	with open("barcelona_union_"+prefix+"_ages.json", "w", encoding="UTF-8") as fp:
		json.dump(bout, fp, ensure_ascii=False, allow_nan=False)

csv2json("zensi2706.xls", "tpob_2015-cp02.csv", "2015")
