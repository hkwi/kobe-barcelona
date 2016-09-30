import sqlite3
import re
import datetime
import requests
import os
import json

areas_db = sqlite3.connect("areas_b.db")
areas_db.row_factory = sqlite3.Row
cur = areas_db.cursor()
cur.execute("SELECT * FROM barcelona WHERE result IS NULL");
for row in cur.fetchall():
	addr = "Spain Barcelona %s" % row["barris"]
	print((datetime.datetime.now(), addr))
	r = requests.get("https://maps.googleapis.com/maps/api/geocode/json",
		params=dict(address=addr, key=os.environ["GMAPKEY"]))
	if r.ok:
		cur.execute("UPDATE barcelona SET result=? WHERE key=?", (json.dumps(r.json()), row["key"]))
		areas_db.commit()

