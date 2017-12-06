import facebook
import requests
import json
import datetime
import sqlite3
import plotly
from plotly.graph_objs import Bar, Layout, Scatter, Line


tkn = 'EAACEdEose0cBANbTZCp82YTuKHfLg2ShxSxEumtdoo7ZCZBLQFQZCuIiCZCAW1LbBQfvE1O4BdmNk2R0KRSvim5p7ZC1yJo2PO1w3nrozISv8p830c2dPlDZCDNleMfuHPZBcM57EPJDjHJs9sZAU1JVJQGpIhgtTUWjfCicMdRhFcmZBZBiQf7FcFQieF2BX8tRL4YsBnobVD6FQZDZD'
myreq = "me?fields=photos.limit(100){created_time}"

FB_json = "fb_cache.json"
try:
	fbfile = open(FB_json, 'r')
	fbcontents = fbfile.read()
	fbfile.close()
	FB_Diction = json.loads(fbcontents)
except:
	FB_Diction = {}

def get_fbdata():
	
	if (len(FB_Diction['Facebook']['photos']['data'])) == 100:
		return (FB_Diction)
	else:
		print ('Getting Data')
		getdata = requests.get('https://graph.facebook.com/v2.11/' + myreq, {'access_token' : tkn})
		getdata = getdata.json()
		try:
			FB_Diction['Facebook'] = getdata
			dump = json.dumps(FB_Diction)
			fw = open(FB_json, 'w')
			fw.write(dump)
			return (FB_Diction)
			fw.close()
		except:
			return ('Invalid')


facebookdata = get_fbdata()

day_count = {}
weekdays = []

for timestamp in facebookdata['Facebook']['photos']['data']:
	time = (timestamp['created_time'])
	date = time.split('T')[0]
	YMD = date.split('-')
	Y = int(YMD[0])
	M = YMD[1]
	if M[0] == '0':
		M = int(M[1])
	else:
		M = int(M)
	D = YMD[2]
	if D[0] == '0':
		D = int(D[1])
	else:
		D = int(D)

	now = datetime.datetime(Y, M, D)
	now = (now.weekday())

	if now == 0:
		weekdays.append('Monday')
	if now == 1:
		weekdays.append('Tuesday')
	if now == 2:
		weekdays.append('Wednesday')
	if now == 3:
		weekdays.append('Thursday')
	if now == 4:
		weekdays.append('Friday')
	if now == 5:
		weekdays.append('Saturday')
	if now == 6:
		weekdays.append('Sunday')

for day in weekdays:
	if day not in day_count:
		day_count[day] = 1
	else:
		day_count[day] += 1


conn = sqlite3.connect("FB_database.sqlite")
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Photos')
query = """
			CREATE TABLE Photos(
			photo_id INTEGER PRIMARY KEY,
			date_posted TEXT,
			time_posted TEXT)"""

cur.execute(query)

query = 'INSERT INTO Photos(photo_id, date_posted, time_posted) VALUES (?,?,?)'

for timestamp in facebookdata['Facebook']['photos']['data']:
	ID = (timestamp['id'])
	timestamp = (timestamp['created_time'])
	date = timestamp.split('T')[0]
	time = timestamp.split('T')[1]
	values = (ID,date,time)
	cur.execute(query, values)

conn.commit()
conn.close()

plotly.offline.plot({
	"data": [Scatter(x = list(day_count.keys()), y= list(day_count.values()))],
	"layout": Layout(title = 'Most Active times for Facebook Photo Uploads')
	})





















