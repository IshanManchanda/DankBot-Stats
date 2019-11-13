import os
import traceback
from datetime import datetime as dt
from time import sleep

from pymongo import MongoClient
from requests import get

from dbstats import globals
from .utils import Event, parse_command, parse_group, parse_user


def refresh():
	if globals.db is None:
		mongo = MongoClient(os.environ.get('MONGODB_URI'))
		globals.db = mongo.get_database()

	reached_end, min_id = False, None
	while not reached_end:
		events, reached_end, min_id = search(min_id)
		print("Starting to process %s events." % (len(events)))
		process(events)
	store_values()


def store_values():
	globals.db.general.find_one_and_update(
		{'name': 'events'},
		{'$set': {
			'total': globals.db.events.count_documents({})}
		}
	)
	globals.db.general.find_one_and_update(
		{'name': 'users'},
		{'$set': {
			'total': globals.db.users.count_documents({})}
		}
	)
	globals.db.general.find_one_and_update(
		{'name': 'groups'},
		{'$set': {
			'total': globals.db.groups.count_documents({})}
		}
	)
	globals.db.general.find_one_and_update(
		{'name': 'last_refreshed'},
		{'$set': {'time': dt.now()}}
	)


def search(min_id):
	url = 'https://papertrailapp.com/api/v1/events/search.json'
	headers = {'X-Papertrail-Token': os.environ.get('PAPERTRAIL_API_TOKEN')}

	params = {
		'q': 'app/web',
		'min_id': min_id if min_id
		else globals.db.general.find_one({'name': 'min_id'})['min_id'],
		'tail': 'false'
	}
	print("Getting batch. Min_id: " + str(params['min_id']))
	r = get(url, headers=headers, params=params)
	if r.status_code != 200:
		print("Status code: %s. Retrying..." % r.status_code)
		r = get(url, headers=headers, params=params)
		if r.status_code != 200:
			raise Exception(
				"Unable to reach papertrail API! Status: %d" % r.status_code
			)
	r = r.json()

	globals.db.general.find_one_and_update(
		{'name': 'min_id'},
		{'$set': {'min_id': r['max_id']}}
	)
	return r['events'], r['reached_end'], r['max_id']


def process(events):
	for event in events:
		try:
			# TODO: Log DEBUG and other log levels
			tokens = event['message'].split(' ')
			if tokens[0] != 'INFO':
				continue

			text = ' '.join(tokens[3:])
			c = g = u = None
			if text[0] == '{':
				c, g, u = parse_command(text)
				u.add_if_not_found()
				if not g:
					g.add_if_not_found()

			elif text[0] == '(':
				g, u = parse_group(text)
				g.add_if_not_found()
				u.add_if_not_found()

			else:
				u = parse_user(text)
				u.add_if_not_found()

			t = (' '.join(tokens[1:3]))[:-1]
			e = Event(u, t, g, c)
			e.add()
		except Exception as e:
			print('Exception!', e)
			sleep(2)
			traceback.print_tb(e.__traceback__)
