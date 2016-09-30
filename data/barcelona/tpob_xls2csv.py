# -*- coding: utf-8 -*-
# Converts Barcelona city opendata from xls or xlsx into csv format.
# "Age of the population (year by year). Reading register of inhabitants."
# 
# cp02: total
# cp03: male
# cp04: female
# 
import glob
import pandas as pd
import csv
import re

dte2name = dict()
for r in csv.DictReader(open("dte.csv", encoding="UTF-8")):
	dte2name[r["num"]] = r["name"]

def proc(filename, skiprows):
	e = pd.ExcelFile(filename)
	d = e.parse(e.sheet_names[0], skiprows=skiprows)
	outfile = filename.replace(".xlsx", ".csv").replace(".xls", ".csv")

	# Dte. = districte 区番号。1 は Ciutat Vella とか。
	# Barris = 直訳は地域。街のほうが近いニュアンス？
	with open(outfile, "w", newline="", encoding="UTF-8") as fp:
		w = csv.writer(fp)
		
		columns = "path name".split()
		columns += [c for c in d.columns if not c.startswith("Unnamed:")]
		w.writerow(columns)
		
		dte_cur = dict(name=None)
		for n,row in d.iterrows():
			dte = row["Dte."]
			barris = row["Barris"]
			
			if dte != dte_cur["name"]:
				if dte_cur["name"] is not None:
					dte_cur["Dte."] = dte_cur["name"]
					dte_cur["name"] = dte2name[str(int(dte_cur["name"]))]
					w.writerow([dte_cur[k] for k in columns])
				
				if dte == dte and isinstance(dte, (int, float)):
					dte_cur = dict(row)
					dte_cur["Barris"] = None
					dte_cur.update(path="b/%d" % int(dte), name=dte)
				else:
					dte_cur = dict(name=None)
			else:
				for k,v in dict(row).items():
					if isinstance(v, (int,float)):
						dte_cur[k] += v
			
			if isinstance(dte, str) and dte.strip().lower() == "barcelona":
				row_data = dict(row)
				row_data.update(path="b", name="Barcelona")
				w.writerow([row_data[k] for k in columns])
			elif barris != barris:
				pass
			elif dte != dte:
				row_data = dict(row)
				row_data.update(path="b/a", name=row["Barris"])
				w.writerow([row_data[k] for k in columns])
			elif isinstance(barris, str):
				m = re.match(r"^(\d+)\.(.*)$", barris)
				row_data = dict(row)
				row_data.update(path="b/%d/%s" % (dte,m.group(1)), name=m.group(2).strip())
				w.writerow([row_data[k] for k in columns])

for f in glob.glob("tpob_*.xls"):
	proc(f, skiprows=2)

for f in glob.glob("tpob_*.xlsx"):
	proc(f, skiprows=0)
