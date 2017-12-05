#gmail API
#Imaan Munir
import requests, json, sqlite3
from quickstart import get_profile

def get_messages(service):
	response = service.users().messages().list(userId='me').execute()
	messages = response['messages']

	while 'nextPageToken' in response:
		page_token = response['nextPageToken']
		response = service.users().messages().list(userId='me' ,pageToken=page_token).execute()
		messages.extend(response['messages'])

		return messages

service = get_profile()
messages = get_messages(service)
message_ids = []

for message in messages:
	message_ids.append(message['id'])

i = 0
CACHE_FNAME = 'gmail_cache.json'
diction = {}

f = open(CACHE_FNAME, 'w')

for mid in message_ids:
	message = service.users().messages().get(userId='me', id=mid).execute()
	for header in message['payload']['headers']:
		if header['name'] == 'Date':
			diction[mid] = {
				'date' : header['value']
			}
			break
	i += 1
	if i == 101:
		break

f.write(json.dumps(diction))
f.close()

conn = sqlite3.connect("GMAIL_database.sqlite")
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Messages')
query = """
			CREATE TABLE Messages(
			mail_id TEXT PRIMARY KEY,
			datetime_sent TEXT)"""
cur.execute(query)

query = 'INSERT INTO Messages(mail_id, datetime_sent) VALUES (?,?)'

for pid,values in diction.items():
	datetime = values['date']
	values = (pid, datetime)
	cur.execute(query, values)

conn.commit()
conn.close()













