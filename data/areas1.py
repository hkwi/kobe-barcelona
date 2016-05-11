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
cur.execute("SELECT * FROM gmap")
for row in cur.fetchall():
	if row["result"] and json.loads(row["result"])["status"] not in ["OK", "ZERO_RESULTS"]:
		cur2.execute("UPDATE gmap SET result=? WHERE key=?", (None, row["key"]))
		db.commit()

cur.execute("SELECT * FROM gmap WHERE result IS NULL")
for row in cur.fetchall():
	addr = "神戸市 %s %s" % (row["ku"], row["cho"])
	print((datetime.datetime.now(), addr))
	r = requests.get("https://maps.googleapis.com/maps/api/geocode/json",
		params=dict(address=addr, key=os.environ["GMAPKEY"], sensor="true"))
	if not r.ok:
		print(("query failed", r.reason))
		break
	elif r.json()["status"] not in ["OK", "ZERO_RESULTS"]:
		print(("query failed", r.json()))
	else:
		cur2.execute("UPDATE gmap SET result=? WHERE key=?", (json.dumps(r.json()), row["key"]))
		db.commit()
	
	time.sleep(3)
