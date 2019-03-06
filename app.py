import os
from datetime import datetime as dt

import requests
from dotenv import load_dotenv
from flask import Flask
from pymongo import MongoClient
from pytz import timezone

if 'MONGODB_URI' not in os.environ:
	load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

mongo = MongoClient(os.environ.get('MONGODB_URI'))
db = mongo.get_database()


@app.route('/')
def hello_world():
	for event in search():
		process(event)
	db.general.find_one_and_update(
		{'name': 'last_refreshed'},
		{'$set': {'time': dt.now(tz=timezone('Asia/Kolkata'))}}
	)
	return 'Hello World!'


def search(min_id=db.general.find_one({'name': 'min_id'})):
	url = 'https://papertrailapp.com/api/v1/events/search.json'
	headers = {'X-Papertrail-Token': os.environ.get('PAPERTAIL_API_TOKEN')}

	params = {'q': 'app/web', 'min_id': min_id, 'tail': 'false'}
	r = requests.get(url, headers=headers, params=params)
	r = r.json()

	# db.general.find_one_and_update(
	# 	{'name': 'min_id'},
	# 	{'$set': {'min_id': r['max_id']}}
	# )

	# TODO: Change such that the first batch is processed
	#  before second is accepted. Will prevent clogging memory.
	if not r['reached_end']:
		return r['events'] + search(r['max_id'])
	return r['events']

# TODO: Refactor into utils


def parse_user(text):
	n1 = text.find('[')
	n2 = text.find(']')
	uname = text[1:n1]
	uid = text[n1 + 1:n2]

	return {'name': uname, 'id': uid}


def parse_group(text):
	n1 = text.find('[')
	n2 = text.find(']')
	gname = text[1:n1]
	gid = text[n1 + 1:n2]

	return {'name': gname, 'id': gid}, parse_user(text[n2 + 2:])


def parse_command(text):
	n = text.find('}')
	cname = text[1:n]
	if text[n + 2] == '(':
		return cname, parse_group(text[n + 2:])
	return cname, parse_user(text[n + 2:])


def process(event):
	m: str = event.message
	tokens = m.split(' ')

	# TODO: Log DEBUG and others
	if tokens[0] == 'INFO':
		text = ' '.join(tokens[3:])
		# TODO: Cleanup
		if text[0] == '{':
			# TODO: Log commands
			c, g, u = parse_command(text)

			# TODO: Make utils
			if db.users.find_one({'user_id': u['id']}) is None:
				db.users.insert_one({'name': u['name'], 'user_id': u['id']})

			if db.groups.find_one({'group_id': g['id']}) is None:
				db.groups.insert_one({'name': g['name'], 'group_id': g['id']})

		if text[0] == '(':
			g, u = parse_group(text)

			if db.users.find_one({'user_id': u['id']}) is None:
				db.users.insert_one({'name': u['name'], 'user_id': u['id']})

			if db.groups.find_one({'group_id': g['id']}) is None:
				db.groups.insert_one({'name': g['name'], 'group_id': g['id']})
		else:
			u = parse_user(text)

			if db.users.find_one({'user_id': u['id']}) is None:
				db.users.insert_one({'name': u['name'], 'user_id': u['id']})


if __name__ == '__main__':
	app.run()
