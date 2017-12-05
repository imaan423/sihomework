import facebook
import requests
import json
import datetime
import sqlite3

MONDAY = 0

tkn = 'EAACEdEose0cBAJdfSgF9blJFjF9HtHHmbaTRB6icrzu262YmD7b7NtQ557wf9pj4BPWgpGmZCnTZCoJbH8Xz2ZCjNOTWiQyI6NlkBZAiZAb6axUMj0hs3krxvYOtzEDzZBcZAoSqze2nXJ70emwmQASdDUZBSGgSUHajgki0iA9J1jMUWryDMfLFs1Eu5UbZC3nhKFXalRTMROgZDZD'
graph = facebook.GraphAPI(access_token=tkn, version="2.11")
profile = graph.get_object('me')
photos = graph.get_connections(id='me', connection_name='photos')

photo_ids = []

while True:
    try:
        for photo in photos['data']:
            photo_ids.append(photo['id'])
        photos=requests.get(photos['paging']['next']).json()
    except KeyError:
        break

diction = {}

for pid in photo_ids:
	photo = graph.get_object(pid)
	datetime = photo['created_time'].split('T')
	diction[pid] = {
		'date' : datetime[0],
		'time' : datetime[1].split('+')[0]
	}

filename = 'fb_cache.json'

cache = open(filename, 'w')
cache.write(json.dumps(diction))
cache.close()


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

for pid,values in diction.items():
	date = values['date']
	time = values['time']
	values = (pid, date, time)
	cur.execute(query, values)

conn.commit()
conn.close()
























