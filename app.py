import os

from dotenv import load_dotenv
from flask import Flask
from pymongo import MongoClient

from bin import globals
from bin.refresh import refresh

if 'MONGODB_URI' not in os.environ:
	load_dotenv()

globals.app = Flask(__name__)
globals.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app = globals.app

mongo = MongoClient(os.environ.get('MONGODB_URI'))
globals.db = mongo.get_database()


if __name__ == '__main__':
	refresh()
	app.run(host='0.0.0.0')
