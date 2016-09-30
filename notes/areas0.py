import pandas as pd
import sqlite3
import json
import glob

def proc(filename, data):
	e = pd.ExcelFile(filename)
	for sheet_name in e.sheet_names:
		if sheet_name.endswith("市"):
			continue
		
		d = e.parse(sheet_name, skiprows=1).loc[1:,:]
		if data is None:
			data = d
		else:
			d.index = [len(data) + d for d in d.index]
			data = pd.concat([data, d])
	return data

data = None
for f in glob.glob("zensi*.xls"):
	data = proc(f, data)

areas_db = sqlite3.connect("areas.db")
areas_db.row_factory = sqlite3.Row
cur = areas_db.cursor()
for idx, s in data.iterrows():
	args = (s["区・支所"], s["町名"])
	skip = False
	for a in args:
		if not isinstance(a, str) or not a:
			skip = True
	if skip:
		continue
	
	cur.execute("SELECT * FROM gmap WHERE ku=? AND cho=?", args)
	if cur.fetchone() is None:
		cur.execute("INSERT INTO gmap (ku,cho) VALUES (?,?)", args)
		areas_db.commit()
