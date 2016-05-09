import pandas as pd
import sqlite3
import glob
import re

areas_db = sqlite3.connect("areas_b.db")
areas_db.row_factory = sqlite3.Row
cur = areas_db.cursor()

def proc(filename, skiprows, skip2):
	e = pd.ExcelFile(filename)
	for sheet_name in e.sheet_names:
		d = e.parse(sheet_name, skiprows=skiprows).iloc[skip2:,:]
		for n,r in d.iterrows():
			if not isinstance(r["Barris"], str):
				continue
			
			m = re.match(r"^(\d+)\.(.*)$", r["Barris"])
			if not m:
				continue
			
			num = int(m.group(1))
			barris = m.group(2).strip()
			cur.execute("SELECT * FROM barcelona WHERE barris=?", (barris,))
			if cur.fetchone() is None:
				cur.execute("INSERT INTO barcelona(num,barris) VALUES(?,?)", (num,barris,))
				areas_db.commit()

for f in glob.glob("tpob_*.xls"):
	proc(f, 2, 2)

for f in glob.glob("tpob_*.xlsx"):
	proc(f, 0, 0)

