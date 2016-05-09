# coding: UTF-8
import sqlite3
import requests
import json
import time
import datetime
import os

db = sqlite3.connect("areas.db")
db.row_factory = sqlite3.Row
cur = db.cursor()
cur2 = db.cursor()
cur.execute("SELECT * FROM gmap WHERE result IS NULL")
for row in cur.fetchall():
	if row["ku"].endswith("支所"):
		addr = "神戸市 %s %s" % (row["ku"][:-2], row["cho"])
	else:
		addr = "神戸市 %s %s" % (row["ku"], row["cho"])
	
	print((datetime.datetime.now(), addr))
	r = requests.get("https://maps.googleapis.com/maps/api/geocode/json",
		params=dict(address=addr, key=os.environ["GMAPKEY"]))
	if r.ok:
		cur2.execute("UPDATE gmap SET result=? WHERE key=?", (json.dumps(r.json()), row["key"]))
		db.commit()
	else:
		print(("query failed", r.reason))
		break
	time.sleep(3)
