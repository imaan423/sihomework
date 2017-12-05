import requests, json, sqlite3

sf_longlat = '37.7578149,-122.5078121' # san francisco
la_longlat = '34.0207289,-118.6926135' # los angeles

KEY = "AIzaSyCsHJOuydJX8vWQCfaWJYPOm29jvXsOMw8"

def get_nearby(longlat):
	s = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={}&radius=5000&keyword=restaurant'.format(KEY, longlat)
	return s

def get_place(pid):
	s = 'https://maps.googleapis.com/maps/api/place/details/json?placeid={}&key={}'.format(pid, KEY)
	return s

diction = {
	'san_francisco':[],
	'los_angeles':[]
}

place_ids = {
	'san_francisco':[],
	'los_angeles':[]
}

# san francisco
r = requests.get(get_nearby(sf_longlat))
results = json.loads(r.text)['results']

for place in results:
	place_ids['san_francisco'].append(place['place_id'])

# los angeles
r = requests.get(get_nearby(la_longlat))
results = json.loads(r.text)['results']

for place in results:
	place_ids['los_angeles'].append(place['place_id'])

for pid in place_ids['san_francisco']:
	r = requests.get(get_place(pid))
	try:
		reviews = json.loads(r.text)['result']['reviews']
	except KeyError:
		reviews = []

	ratings = []
	for review in reviews:
		ratings.append(review['rating'])

	d = {
		'pid':pid,
		'ratings':ratings
	}
	diction['san_francisco'].append(d)

for pid in place_ids['los_angeles']:
	r = requests.get(get_place(pid))
	try:
		reviews = json.loads(r.text)['result']['reviews']
	except KeyError:
		reviews = []

	ratings = []
	for review in reviews:
		ratings.append(review['rating'])

	d = {
		'pid':pid,
		'ratings':ratings
	}
	diction['los_angeles'].append(d)

cache = open('places_cache.json', 'w')
cache.write(json.dumps(diction))
cache.close()

conn = sqlite3.connect("PLACES_database.sqlite")
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS LosAngeles')
cur.execute('DROP TABLE IF EXISTS SanFrancisco')

query = """
			CREATE TABLE LosAngeles(
			place_id TEXT,
			avg_rating FLOAT(2))"""

cur.execute(query)

query = """
		CREATE TABLE SanFrancisco(
		place_id TEXT,
		avg_rating FLOAT(2))"""

cur.execute(query)

query = 'INSERT INTO LosAngeles(place_id, avg_rating) VALUES (?,?)'
for info in diction['los_angeles']:
	if not len(info['ratings']) == 0:
		pid = info['pid']
		sum = 0
		for review in info['ratings']:
			sum += review
		avg = sum/len(info['ratings'])
		values = (pid, avg)
		cur.execute(query, values)

conn.commit()

query = 'INSERT INTO SanFrancisco(place_id, avg_rating) VALUES (?,?)'
for info in diction['san_francisco']:
	if not len(info['ratings']) == 0:
		pid = info['pid']
		sum = 0
		for review in info['ratings']:
			sum += review
		avg = sum/len(info['ratings'])
		values = (pid, avg)
		cur.execute(query, values)

conn.commit()
conn.close()





















