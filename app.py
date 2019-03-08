import os

from dotenv import load_dotenv
from flask import Flask, render_template
from pymongo import MongoClient
from rq import Queue

from dbstats import globals
from dbstats.refresh import refresh
from worker import conn

if 'MONGODB_URI' not in os.environ:
	load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

mongo = MongoClient(os.environ.get('MONGODB_URI'))
globals.db = mongo.get_database()
q = Queue(connection=conn, default_timeout=600)
q.enqueue(refresh)


@app.route('/')
def main():
	return render_template(
		'index.html',
		events=globals.db.events.count_documents({}),
		users=globals.db.users.count_documents({}),
		groups=globals.db.groups.count_documents({}),
		last_updated=globals.db.general.find_one({'name': 'last_refreshed'})[
			'time']
	)


@app.route('/refresh/')
def page_refresh():
	if len(q) == 0:
		q.enqueue(refresh)
	return render_template('refresh.html')


if __name__ == '__main__':
	app.run()
