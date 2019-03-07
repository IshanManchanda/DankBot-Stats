from datetime import datetime

from bin import globals


class User:
	def __init__(self, name, user_id):
		self.name = name
		self.user_id = user_id

	def __eq__(self, other):
		return type(self) == type(other) and self.user_id == other.user_id

	def __str__(self):
		return '%s[%s]' % (self.name, self.user_id)

	def add_if_not_found(self):
		if globals.db.users.find_one({'user_id': self.user_id}) is None:
			globals.db.users.insert_one({
				'name': self.name, 'user_id': self.user_id
			})


class Group:
	def __init__(self, name, group_id):
		self.name = name
		self.group_id = group_id

	def __eq__(self, other):
		return type(self) == type(other) and self.group_id == other.group_id

	def __str__(self):
		return '%s[%s]' % (self.name, self.group_id)

	def add_if_not_found(self):
		if globals.db.groups.find_one({'group_id': self.group_id}) is None:
			globals.db.groups.insert_one({
				'name': self.name, 'group_id': self.group_id
			})


class Command:
	def __init__(self, name):
		self.name = name

	def __eq__(self, other):
		return type(self) == type(other) and self.name == other.name

	def __str__(self):
		return self.name


class Event:
	def __init__(self, user, timestamp, group=None, command=None):
		self.user_name = user.name
		self.user_id = user.user_id
		self.timestamp = datetime.strptime(
			timestamp[:-3] + timestamp[-2:],
			'%Y-%m-%d %H:%M:%S.%f%z'
		)

		self.group_name = group.name if group else None
		self.group_id = group.group_id if group else None
		self.command = command.name if command else None

	def add(self):
		globals.db.events.insert_one({
			'user_name': self.user_name,
			'user_id': self.user_id,
			'timestamp': self.timestamp,
			'group_name': self.group_name,
			'group_id': self.group_id,
			'command': self.command,
		})


def parse_user(text):
	n1 = text.find('[')
	n2 = text.find(']')
	uname = text[0:n1]
	uid = text[n1 + 1:n2]

	return User(uname, uid)


def parse_group(text):
	n1 = text.find('[')
	n2 = text.find(']')
	gname = text[1:n1]
	gid = text[n1 + 1:n2]

	return Group(gname, gid), parse_user(text[n2 + 3:])


def parse_command(text):
	n = text.find('}')
	c = Command(text[1:n])
	if text[n + 2] == '(':
		g, u = parse_group(text[n + 2:])
	else:
		g, u = None, parse_user(text[n + 2:])
	return c, g, u
