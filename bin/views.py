import threading

from bin import globals
from bin.refresh import refresh


@globals.app.route('/')
def main():
	return '''
	Hi! There have been %d events in the last 2 days. <br>
	Further, DankBot has %d active users who are a part of %d groups.
	<br><br>
	This data was last refreshed on %s. <br>
	To refresh, please visit https://dankbot-stats.herokuapp.com/refresh/ 
	''' % (
		globals.db.events.count_documents({}),
		globals.db.users.count_documents({}),
		globals.db.groups.count_documents({}),
		globals.db.general.find_one({'name': 'last_refreshed'})['time']
	)


@globals.app.route('/refresh/')
def page_refresh():
	threading.Thread(target=refresh).start()
	return 'Refreshing! Please check the main page in a while.'
