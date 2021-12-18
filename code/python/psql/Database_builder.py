from psycopg2 import *
import json
from psycopg2 import extras


class DatabaseConnection:
	def __init__(self, database='postgres', user='postgres', password='postgres', host='127.0.0.1', port='5432'):
		self.database = database
		self.user = user
		self.password = password
		self.host = host
		self.port = port

	def convertToJson(self):
		return {
			'database': self.database,
			'user': self.user,
			'password': self.password,
			'host': self.host,
			'port': self.port,
		}


class SelectParams:
	def __init__(self, offset=0, limit=100, order_by=None):
		self.order_by = order_by
		self.limit = limit
		self.offset = offset
		self.conditions = {}

	def build_question(self):
		command = []

		if len(self.conditions) > 0:
			i = 0
			for con in self.conditions:
				command.append(("WHERE " if i == 0 else "") +
				               self.conditions[con] + (" AND" if i + 1 < len(self.conditions) else ""))
				i += 1

		if self.order_by is not None:
			command.append('ORDER BY ' + self.order_by)

		if self.offset is not None:
			command.append("OFFSET " + str(self.offset))

		if self.limit is not None:
			command.append("LIMIT " + str(self.limit))

		return " ".join(command)

	def order_by_change(self, order_by, direction="ASC"):
		self.order_by = '"' + order_by + '" ' + direction

	def change_range(self, offset, limit):
		self.offset = offset
		self.limit = limit

	def add_condition(self, con_id, column, value):
		if value != "IS NULL":
			value = "= '" + value + "'"

		self.remove_condition(con_id)

		self.conditions[str(con_id)] = '"' + column + '" ' + value

	def remove_condition(self, con_id):
		if str(con_id) in self.conditions:
			del self.conditions[str(con_id)]


class UserBuilder:
	def __init__(self, user, password, create_db, create_role, superuser):
		self.user = user
		self.password = password
		self.create_db = create_db
		self.create_role = create_role
		self.superuser = superuser

	def build_command(self):
		command = "CREATE USER " + self.user
		options = []

		if self.create_role == 1:
			options.append("CREATEROLE")

		if self.create_db == 1:
			options.append("CREATEDB")

		if self.superuser == 1:
			options.append("SUPERUSER")

		if len(options) > 0 or len(self.password) > 0:
			command += " WITH "

		if len(self.password) > 0:
			command += "PASSWORD %s"

		if len(options) > 0:
			command += (" " if len(self.password) > 0 is not None else "") + " ".join(options)

		return command + ";"


class Database_builder:

	def execute(self, database_connection, command, values=None, mode='none', resAsDict=False):
		if values is None:
			values = []

		try:
			conn = connect(
				database=database_connection['database'],
				user=database_connection['user'],
				password=database_connection['password'],
				host=database_connection['host'],
				port=database_connection['port']
			)
			cursor = conn.cursor(cursor_factory=extras.RealDictCursor if resAsDict is True else None)
			res = None
			cursor.execute(command, values) if len(values) > 0 else cursor.execute(command)
			conn.commit()

			if mode == 'all':
				res = cursor.fetchall()
			elif mode == 'one':
				res = cursor.fetchone()

			conn.close()

			if mode != 'none':
				return res
		except BaseException as ex:
			raise ex

	def all(self, database_connection, command, values=None, asDict=False):
		return self.execute(database_connection, command, values, 'all', asDict)

	def autocommit_execute(self, command, values=None):
		conn = connect(database="postgres", user='postgres', password='postgres', host='127.0.0.1', port='5432')
		conn.autocommit = True
		cursor = conn.cursor()
		cursor.execute(command, values)
		conn.close()

	def create_db(self, name, owner=None):
		command = "CREATE database " + name + (" with owner %s;" if owner is not None else ";")
		values = [owner] if owner is not None else []
		self.autocommit_execute(command, values)

	def test_database_connection(self, database_connection):
		command = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
		self.execute(database_connection.convertToJson(), command)

	def create_user(self, user_builder):
		command = user_builder.build_command()
		if user_builder.password is not None:
			values = [user_builder.password]
			self.autocommit_execute(command, values)
			return

		self.autocommit_execute(command)

	def add_user(self, database, user):
		command = "GRANT ALL PRIVILEGES ON DATABASE " + database + " TO " + user + ";"
		self.autocommit_execute(command)

	def create_and_user_database(self, database, user_builder):
		self.create_user(user_builder)
		self.add_user(database, user_builder.user)

	def save_database_connection(self, database_connection):
		json_object = json.load(open("data/database_connections.json", "r"))
		a_file = open("data/database_connections.json", "w")
		json_object[database_connection.database] = database_connection.convertToJson()
		json.dump(json_object, a_file)
		a_file.close()

	def get_database_connection(self, database_name):
		a_file = open("data/database_connections.json", "r")
		json_object = json.load(a_file)
		a_file.close()

		connection = None
		if database_name in json_object:
			connection = json_object[database_name]

		return connection

	def remove_database_connection(self, database_name):
		json_object = json.load(open("data/database_connections.json", "r"))
		a_file = open("data/database_connections.json", "w")
		del json_object[database_name]
		json.dump(json_object, a_file)
		a_file.close()

	def get_database_connections(self):
		a_file = open("data/database_connections.json", "r")
		json_object = json.load(a_file)
		a_file.close()

		return json_object

	def get_all_tables(self, database_name):
		command = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
		database_connection = self.get_database_connection(database_name)
		return self.all(database_connection, command, [])

	def get_all_table_data(self, database, table, select_params=None):
		database_connection = self.get_database_connection(database)
		command = 'SELECT * FROM "' + table + '"'

		if select_params is not None:
			command += " " + select_params.build_question()

		return self.all(database_connection, command + ';', asDict=True)

	def get_all_table_columns(self, database, table):
		command = 'SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %s ORDER BY column_name;'
		database_connection = self.get_database_connection(database)
		return self.all(database_connection, command, [table])

	def drop_database(self, database_name):
		command = "DROP DATABASE IF EXISTS " + database_name + ";"
		self.autocommit_execute(command)

	def drop_table(self, database_name, table_name):
		database_connection = self.get_database_connection(database_name)
		command = "DROP TABLE " + table_name + ";"
		self.execute(database_connection, command)

	def rename_database(self, database_name_old, database_name_new):
		command1 = "SELECT pg_terminate_backend (pid) FROM pg_stat_activity WHERE datname = %s;"
		self.autocommit_execute(command1, [database_name_old])
		command2 = "ALTER DATABASE " + database_name_old + " RENAME TO " + database_name_new + ";"
		self.autocommit_execute(command2)

	def rename_table(self, database, table_name_old, table_name_new):
		database_connection = self.get_database_connection(database)
		command = 'ALTER TABLE "' + table_name_old + '" RENAME TO "' + table_name_new + '";'
		self.execute(database_connection, command)

	def create_table(self, database, source):
		database_connection = self.get_database_connection(database)
		self.execute(database_connection, source)

	def build_specific_row_conditions(self, header, row):
		conditions = []
		values = []

		idx = 0
		for h in header:
			condition = '"' + "".join(h) + '"'

			if row[idx] is None:
				condition += " IS NULL "
			else:
				values.append(str(row[idx]) if not isinstance(row[idx], tuple) else "".join(row[idx]))
				condition += " = %s"

			if idx + 1 < len(header):
				condition += " AND "

			conditions.append(condition)
			idx += 1

		return " WHERE " + ''''''.join(conditions), values

	def remove_table_row(self, database, table, row):
		command = 'DELETE FROM "' + table + '"'

		headers = []
		vals = []

		for k in row:
			headers.append(k)
			vals.append(row[k])

		conditions, values = self.build_specific_row_conditions(headers, vals)
		database_connection = self.get_database_connection(database)

		command_whole = command + conditions + ";"
		self.execute(database_connection, command_whole, values)

	def add_table_row(self, database, table, header, row):
		database_connection = self.get_database_connection(database)
		command = 'INSERT INTO ' + table + '('
		values = 'VALUES('

		idx = 0
		for h in header:
			command += '"' + "".join(h) + '"' + (", " if idx + 1 < len(header) else ") ")
			values += "%s" + (", " if idx + 1 < len(header) else ")")
			idx += 1

		command += values
		self.execute(database_connection, command, row)

	def edit_table_row(self, database, table, new_values, original_values):
		vals = []
		headers = []

		for key in original_values:
			headers.append(key)
			vals.append(original_values[key])

		database_connection = self.get_database_connection(database)
		command = 'UPDATE "' + table + '"'
		conditions, values = self.build_specific_row_conditions(headers, vals)
		set = ' SET '

		idx = 0
		for h in headers:
			set += '"' + "".join(h) + '" = '
			set += "%s" + (", " if idx + 1 < len(headers) else " ")
			idx += 1

		values_connected = [y for x in [new_values, values] for y in x]
		command_whole = command + set + conditions
		self.execute(database_connection, command_whole, values_connected)

	def check_table_existence(self, database, table):
		database_connection = self.get_database_connection(database)
		command = "SELECT table_name FROM information_schema.tables WHERE table_name = '" + table + "';"
		return self.execute(database_connection, command, mode='one')

# https://www.psycopg.org/docs/usage.html
# https://www.postgresql.org/docs/9.1/sql-createdatabase.html
# https://pynative.com/python-postgresql-tutorial/
# https://karloespiritu.github.io/cheatsheets/postgresql/
# https://www.postgresqltutorial.com/postgresql-python/update/
# https://www.tutorialspoint.com/python_data_access/python_postgresql_create_database.htm
