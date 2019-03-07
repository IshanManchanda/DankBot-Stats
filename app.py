import os
import threading

from dotenv import load_dotenv
from flask import Flask
from pymongo import MongoClient

from bin.utils import User, Group, Event
from bin.main import refresh

if 'MONGODB_URI' not in os.environ:
	load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

mongo = MongoClient(os.environ.get('MONGODB_URI'))
db = User.db = Group.db = Event.db = mongo.get_database()


@app.route('/')
def main():
	return '''
	Hi! There have been %d events in the last 2 days. <br>
	Further, DankBot has %d active users who are a part of %d groups.
	<br><br>
	This data was last refreshed on %s. <br>
	To refresh, please visit https://dankbot-stats.herokuapp.com/refresh/ 
	''' % (
		db.events.count_documents({}),
		db.users.count_documents({}),
		db.groups.count_documents({}),
		db.general.find_one({'name': 'last_refreshed'})['time']
	)


@app.route('/refresh/')
def page_refresh():
	threading.Thread(target=refresh).start()
	return 'Refreshing! Please check the main page in a while.'


if __name__ == '__main__':
	refresh()
	app.run(host='0.0.0.0')
