import os

import redis
from dotenv import load_dotenv
from rq import Connection, Queue, Worker

if 'MONGODB_URI' not in os.environ:
	load_dotenv()
listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
	with Connection(conn):
		worker = Worker(map(Queue, listen))
		worker.work()
