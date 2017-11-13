## SI 206 2017
## Project 3 - Imaan Munir Thurs 3-4pm
## Building on HW7, HW8 (and some previous material!)



##OBJECTIVE:
## In this assignment you will be creating database and loading data 
## into database.  You will also be performing SQL queries on the data.
## You will be creating a database file: 206_APIsAndDBs.sqlite

import unittest
import itertools
import collections
import tweepy
import twitter_info # same deal as always...
import json
import sqlite3

## Your name: Imaan Munir
## The names of anyone you worked with on this project:

#####

##### TWEEPY SETUP CODE:
# Authentication information should be in a twitter_info file...
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and 
# return it in a JSON format 
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

##### END TWEEPY SETUP CODE

## Task 1 - Gathering data

## Define a function called get_user_tweets that gets at least 20 Tweets 
## from a specific Twitter user's timeline, and uses caching. The function 
## should return a Python object representing the data that was retrieved 
## from Twitter. (This may sound familiar...) We have provided a 
## CACHE_FNAME variable for you for the cache file name, but you must 
## write the rest of the code in this file.

CACHE_FNAME = "206_APIsAndDBs_cache.json"
# Put the rest of your caching setup here:
try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}


# Define your function get_user_tweets here:
# here I am grabbing all tweets from @user, filling up a cache file, and then returning a dictionary 
def get_user_tweets(user):
	if user in CACHE_DICTION:
		print('using cached data')
		twitter_results = CACHE_DICTION[user]

	else:
		print('getting data from internet')
		twitter_results = api.user_timeline(user)
		CACHE_DICTION[user] = twitter_results
		f = open(CACHE_FNAME, 'w')
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return twitter_results



# Write an invocation to the function for the "umich" user timeline and 
# save the result in a variable called umich_tweets:

umich_tweets = get_user_tweets('umich')



## Task 2 - Creating database and loading data into database
conn = sqlite3.connect("206_APIsAndDBs.sqlite")
cur = conn.cursor() # 
cur.execute("DROP TABLE IF EXISTS Tweets") #deleting table Tweets if it already exists 
cur.execute("DROP TABLE IF EXISTS Users") #deleting table Users if it already exists 
query = "CREATE TABLE Tweets (tweet_id TEXT PRIMARY KEY, text TEXT, user_posted TEXT, time_posted DATETIME, retweets INTEGER, FOREIGN KEY (user_posted)REFERENCES Users(user_id))"
cur.execute(query)

query = "CREATE TABLE Users(user_id TEXT PRIMARY KEY,screen_name TEXT,num_favs INTEGER, description TEXT)"
cur.execute(query)


## You should load into the Users table:
# The umich user, and all of the data about users that are mentioned 
# in the umich timeline. 
# NOTE: For example, if the user with the "TedXUM" screen name is 
# mentioned in the umich timeline, that Twitter user's info should be 
# in the Users table, etc.

## You should load into the Tweets table: 
# Info about all the tweets (at least 20) that you gather from the 
# umich timeline.
# NOTE: Be careful that you have the correct user ID reference in 
# the user_id column! See below hints.

## HINT: There's a Tweepy method to get user info, so when you have a 
## user id or screenname you can find alllll the info you want about 
## the user.

## HINT: The users mentioned in each tweet are included in the tweet 
## dictionary -- you don't need to do any manipulation of the Tweet 
## text to find out which they are! Do some nested data investigation 
## on a dictionary that represents 1 tweet to see it!
 
#creating template to use for later
insert_user = "INSERT INTO Users (user_id, screen_name, num_favs, description) VALUES (?,?,?,?)" 
insert_tweet = "INSERT INTO Tweets (tweet_id, text, user_posted, time_posted, retweets) VALUES (?,?,?,?,?)" 
check_user = "SELECT COUNT(*) FROM Users WHERE screen_name = ?"
uu = umich_tweets[0]['user']
values = (uu['id_str'], uu['screen_name'], uu['favourites_count'], uu['description'])
cur.execute(insert_user, values)


for tweet in umich_tweets: 
	mentions = tweet['entities']['user_mentions']
	reply_acct = tweet['in_reply_to_user_id']
	
	if 'retweeted_status' in tweet: #checking if tweet is retweeted - and if so, add user to table User 
		rt_user = tweet['retweeted_status']['user'] 
		values = (rt_user['screen_name'],)
		cur.execute(check_user, values)
		count = cur.fetchone()[0]

		if(count == 0):
			values = (rt_user['id_str'], rt_user['screen_name'], rt_user['favourites_count'], rt_user['description'])
			cur.execute(insert_user, values)

		values = (tweet['id_str'], tweet['text'], rt_user['id_str'], tweet['created_at'], tweet['retweet_count'])
		cur.execute(insert_tweet, values) #insert tweet
	
	else: #don't insert user - insert tweet anyway
		values = (tweet['id_str'], tweet['text'], tweet['user']['id_str'], tweet['created_at'], tweet['retweet_count'])
		cur.execute(insert_tweet, values) 
	
	if len(mentions) > 0:
		for user in mentions:
			values = (user['screen_name'],)
			cur.execute(check_user, values)
			count = cur.fetchone()[0]

			if(count == 0):
				ui = api.get_user(user['screen_name'])
				values = (ui['id_str'], ui['screen_name'], ui['favourites_count'], ui['description'])
				cur.execute(insert_user, values)

conn.commit()
## Task 3 - Making queries, saving data, fetching data

# All of the following sub-tasks require writing SQL statements 
# and executing them using Python.

# Make a query to select all of the records in the Users database. 
# Save the list of tuples in a variable called users_info.

command = ("SELECT * FROM Users")
cur.execute(command)
users_info = cur.fetchall()

# Make a query to select all of the user screen names from the database. 
# Save a resulting list of strings (NOT tuples, the strings inside them!) 
# in the variable screen_names. HINT: a list comprehension will make 
# this easier to complete! 
command = ("SELECT screen_name FROM Users")
cur.execute(command)
all_tuples = cur.fetchall()
screen_names = []
for tup in all_tuples:
	screen_names.append(tup[0])


# Make a query to select all of the tweets (full rows of tweet information)
# that have been retweeted more than 10 times. Save the result 
# (a list of tuples, or an empty list) in a variable called retweets.
command = ("SELECT * FROM Tweets WHERE retweets > 10")
cur.execute(command)
retweets = cur.fetchall()


# Make a query to select all the descriptions (descriptions only) of 
# the users who have favorited more than 500 tweets. Access all those 
# strings, and save them in a variable called favorites, 
# which should ultimately be a list of strings.
command = ("SELECT description FROM Users WHERE num_favs > 500")
cur.execute(command)
tup_favorites = cur.fetchall()
favorites = []
for tup in tup_favorites:
	favorites.append(tup[0])


# Make a query using an INNER JOIN to get a list of tuples with 2 
# elements in each tuple: the user screenname and the text of the 
# tweet. Save the resulting list of tuples in a variable called joined_data.
command = ("SELECT Users.screen_name, Tweets.text FROM Users INNER JOIN Tweets ON Users.user_id = Tweets.user_posted")
cur.execute(command)
joined_data = cur.fetchall()

# Make a query using an INNER JOIN to get a list of tuples with 2 
# elements in each tuple: the user screenname and the text of the 
# tweet in descending order based on retweets. Save the resulting 
# list of tuples in a variable called joined_data2.
command = ("SELECT Users.screen_name, Tweets.text FROM Users INNER JOIN Tweets ON Users.user_id = Tweets.user_posted ORDER BY Tweets.retweets DESC")
cur.execute(command)
joined_data2 = cur.fetchall()
### IMPORTANT: MAKE SURE TO CLOSE YOUR DATABASE CONNECTION AT THE END 
### OF THE FILE HERE SO YOU DO NOT LOCK YOUR DATABASE (it's fixable, 
### but it's a pain). ###
conn.close()

###### TESTS APPEAR BELOW THIS LINE ######
###### Note that the tests are necessary to pass, but not sufficient -- 
###### must make sure you've followed the instructions accurately! 
######
print("\n\nBELOW THIS LINE IS OUTPUT FROM TESTS:\n")


class Task1(unittest.TestCase):
	def test_umich_caching(self):
		fstr = open("206_APIsAndDBs_cache.json","r")
		data = fstr.read()
		fstr.close()
		self.assertTrue("umich" in data)
	def test_get_user_tweets(self):
		res = get_user_tweets("umsi")
		self.assertEqual(type(res),type(["hi",3]))
	def test_umich_tweets(self):
		self.assertEqual(type(umich_tweets),type([]))
	def test_umich_tweets2(self):
		self.assertEqual(type(umich_tweets[18]),type({"hi":3}))
	def test_umich_tweets_function(self):
		self.assertTrue(len(umich_tweets)>=20)

class Task2(unittest.TestCase):
	def test_tweets_1(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result)>=20, "Testing there are at least 20 records in the Tweets database")
		conn.close()
	def test_tweets_2(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==5,"Testing that there are 5 columns in the Tweets table")
		conn.close()
	def test_tweets_3(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT tweet_id FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(result[0][0] != result[19][0], "Testing part of what's expected such that tweets are not being added over and over (tweet id is a primary key properly)...")
		if len(result) > 20:
			self.assertTrue(result[0][0] != result[20][0])
		conn.close()


	def test_users_1(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)>=2,"Testing that there are at least 2 distinct users in the Users table")
		conn.close()
	def test_users_2(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)<20,"Testing that there are fewer than 20 users in the users table -- effectively, that you haven't added duplicate users. If you got hundreds of tweets and are failing this, let's talk. Otherwise, careful that you are ensuring that your user id is a primary key!")
		conn.close()
	def test_users_3(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==4,"Testing that there are 4 columns in the Users database")
		conn.close()

class Task3(unittest.TestCase):
	def test_users_info(self):
		self.assertEqual(type(users_info),type([]),"testing that users_info contains a list")
	def test_users_info2(self):
		self.assertEqual(type(users_info[0]),type(("hi","bye")),"Testing that an element in the users_info list is a tuple")

	def test_track_names(self):
		self.assertEqual(type(screen_names),type([]),"Testing that screen_names is a list")
	def test_track_names2(self):
		self.assertEqual(type(screen_names[0]),type(""),"Testing that an element in screen_names list is a string")

	def test_more_rts(self):
		if len(retweets) >= 1:
			self.assertTrue(len(retweets[0])==5,"Testing that a tuple in retweets has 5 fields of info (one for each of the columns in the Tweet table)")
	def test_more_rts2(self):
		self.assertEqual(type(retweets),type([]),"Testing that retweets is a list")
	def test_more_rts3(self):
		if len(retweets) >= 1:
			self.assertTrue(retweets[1][-1]>10, "Testing that one of the retweet # values in the tweets is greater than 10")

	def test_descriptions_fxn(self):
		self.assertEqual(type(favorites),type([]),"Testing that favorites is a list")
	def test_descriptions_fxn2(self):
		self.assertEqual(type(favorites[0]),type(""),"Testing that at least one of the elements in the favorites list is a string, not a tuple or anything else")
	def test_joined_result(self):
		self.assertEqual(type(joined_data[0]),type(("hi","bye")),"Testing that an element in joined_result is a tuple")



if __name__ == "__main__":
	unittest.main(verbosity=2)








