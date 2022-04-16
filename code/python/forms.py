from code.python.widgets.form import *
from code.python.psql.Database_builder import *
import re


def check_invalid_letters(text, mode):
	name_checked = re.match("([_a-z0-9])+", text)

	if not name_checked or len(name_checked.group()) < len(text):
		messagebox.showinfo('Wrong letters', 'Your ' + mode + ''' name contains invalid characters. 
																Only valid characters are _, a-z and 0-9''')
		return False
	return True


class CreateDatabaseForm:
	def __init__(self, root, data, cb):
		self.cb = cb
		self.form = Form(
			root,
			"Create database",
			[
				Field(
					"Database name",
					warning="Database name can only contain lower case letters, numbers and underscores",
					required=True
				),
				Field("Owner name (optional)")
			],
			[
				FormButton(
					"Create",
					self.create_database
				)
			]
		)
		self.screen = self.form.main_frame

	def create_database(self):
		values = self.form.get_values()

		if values is None:
			return

		if check_invalid_letters(values[0], "database") is False:
			return

		try:
			Database_builder().create_db(values[0], values[1])
			self.form.clear()
			messagebox.showinfo('Database creation', 'Database was successfully created')
		except BaseException as ex:
			ex = str(ex)
			role_not_exist = re.search("role \"(.+)\" does not exist", ex)

			if role_not_exist:
				messagebox.showinfo('Role doesn\'t exist', 'Role ' + values[1] + ' does not exist')
				return

			database_already_exist = re.search("database \"(.+)\" already exist", ex)
			if database_already_exist:
				messagebox.showinfo('Database already exist', 'Database ' + values[0] + ' already exist')
				return

			messagebox.showinfo('Error', 'We are sorry, but something went wrong, Error: ' + ex)


class AddUserToDatabase:
	def __init__(self, root, data):
		self.database = data[0]
		self.form = Form(
			root,
			"Add user to database",
			[
				Field(
					"Username",
					required=True
				)
			],
			[
				FormButton(
					"Add",
					self.handle_create
				)
			]
		)
		self.screen = self.form.main_frame

	def handle_create(self):
		values = self.form.get_values()

		if values is None:
			return

		if check_invalid_letters(values[0], "username") is False:
			return

		try:
			Database_builder().add_user(self.database, values[0])
			self.form.clear()
			messagebox.showinfo('information', 'User was successfully created')
		except BaseException as ex:
			ex = str(ex)
			role_not_exist = re.search("role \"(.+)\" does not exist", ex)

			if role_not_exist:
				messagebox.showinfo('Role doesn\'t exist', 'Role ' + values[0] + ' does not exist')
				return

			messagebox.showinfo('Error', 'We are sorry, but something went wrong, Error: ' + ex)


class CreateUserForm:
	def __init__(self, root, data):
		self.database = data[0] if len(data) > 0 else None
		self.form = Form(
			root,
			"Create user",
			[
				Field(
					"Username",
					warning="Username can contain only lower case letters, _ and 0 - 9",
					required=True
				),
				Field("Password"),
				Field("Create db", type="check"),
				Field("Create role", type="check"),
				Field("Superuser", type="check")
			],
			[
				FormButton(
					"Create",
					self.create_user
				)
			]
		)
		self.screen = self.form.main_frame

	def create_user(self):
		values = self.form.get_values()

		if values is None:
			return

		if check_invalid_letters(values[0], "username") is False:
			return

		try:
			user_builder = UserBuilder(values[0], values[1], values[2], values[3], values[4])
			if self.database is not None:
				Database_builder().create_and_user_database(self.database, user_builder)
				messagebox.showinfo('information', 'User was successfully created and added')
			else:
				Database_builder().create_user(user_builder)
				messagebox.showinfo('information', 'User was successfully created')
			self.form.clear()
		except BaseException as ex:
			ex = str(ex)

			database_already_exist = re.search("role \"(.+)\" already exist", ex)
			if database_already_exist:
				messagebox.showinfo('Role already exist', 'Role ' + values[0] + ' already exist')
				return

			messagebox.showinfo('Error', 'We are sorry, but something went wrong, Error: ' + ex)


class ConnectDatabaseForm:
	def __init__(self, root, data, cb):
		self.cb = cb
		self.form = Form(
			root,
			"Connect to database",
			[
				Field(
					"Database name",
					warning="Database can contain only lower case letters, _ and 0 - 9",
					required=True
				),
				Field(
					"Username",
					warning="Username can contain only lower case letters, _ and 0 - 9",
					required=True
				),
				Field("Password")
			],
			[
				FormButton(
					"Test connection",
					lambda: self.handle_connection("test")
				),
				FormButton(
					"Connect",
					lambda: self.handle_connection("apply")
				)
			]
		)
		self.screen = self.form.main_frame

	def handle_connection(self, mode):
		values = self.form.get_values()

		if values is None:
			return

		if check_invalid_letters(values[0], "database") is False:
			return

		if check_invalid_letters(values[1], "database") is False:
			return

		database_connection_exist = Database_builder().get_database_connection(values[0])

		if database_connection_exist is not None:
			messagebox.showinfo('Database connection', 'You are already connected to database ' + values[0])
			return

		database_connection = DatabaseConnection(database=values[0], user=values[1], password=values[2])

		try:
			Database_builder().test_database_connection(database_connection)

			if mode is not "test":
				Database_builder().save_database_connection(database_connection)
				self.cb(values[0])
				self.form.clear()
			messagebox.showinfo('Correct credentials', 'Credentials for connection are correct')
		except BaseException as ex:
			ex = str(ex)

			role_not_exist = re.search("role \"(.+)\" does not exist", ex)
			if role_not_exist:
				messagebox.showinfo('Role already exist', 'Role ' + values[1] + ' does not exist')
				return

			database_not_exist = re.search("database \"(.+)\" does not exist", ex)
			if database_not_exist:
				messagebox.showinfo('Role already exist', 'Database ' + values[0] + ' does not exist')
				return

			if 'password authentication' in ex:
				messagebox.showinfo('Wrong password', 'Wrong password for role ' + values[0])
				return

			messagebox.showinfo('Error', 'We are sorry, but something went wrong, Error: ' + ex)


class RenameDatabaseForm:
	def __init__(self, root, data, cb):
		self.cb = cb
		self.database = data[0]
		self.form = Form(
			root,
			"Rename database",
			[
				Field(
					"Database name",
					value=self.database,
					warning="Database name can only contain lower case letters, numbers and underscores",
					required=True
				)
			],
			[
				FormButton(
					"Rename",
					self.rename
				)
			]
		)
		self.screen = self.form.main_frame

	def rename(self):
		values = self.form.get_values()

		if values is None:
			return

		if check_invalid_letters(values[0], "database") is False:
			return

		try:
			database_builder = Database_builder()
			connection = database_builder.get_database_connection(self.database)
			database_builder.rename_database(self.database, values[0])
			database_builder.remove_database_connection(self.database)

			database_connection = DatabaseConnection(database=values[0], user=connection['user'], password=connection['password'])
			database_builder.save_database_connection(database_connection)

			messagebox.showinfo("Database rename", "Your database was successfully renamed")
			self.cb(self.database, values[0])
			self.database = values[0]
			self.form.clear()
		except BaseException as ex:
			ex = str(ex)

			database_already_exist = re.search("database \"(.+)\" already exist", ex)
			if database_already_exist:
				messagebox.showinfo('Database already exist', 'Database ' + values[0] + ' already exist')
				return

			messagebox.showinfo('Error', 'We are sorry, but something went wrong, Error: ' + ex)


class RenameTable:
	def __init__(self, root, data, cb):
		self.cb = cb
		self.database = data[0]
		self.table = data[1]
		self.form = Form(
			root,
			"Rename table",
			[
				Field(
					"Table name",
					value=self.table,
					required=True
				)
			],
			[
				FormButton(
					"Rename",
					self.rename
				)
			]
		)
		self.screen = self.form.main_frame

	def rename(self):
		values = self.form.get_values()

		if values is None:
			return

		if values[0] == self.table:
			messagebox.showinfo('Wrong rename', 'Table cannot be renamed to same name')
			return

		name_checked = re.match("([_#@a-z0-9])+", values[0])

		if not name_checked or len(name_checked.group()) < len(values[0]):
			messagebox.showinfo('Wrong letters', '''Your table name contains invalid characters. 
																		Only valid characters are #, @, _, a-z and 0-9''')
			return

		try:
			Database_builder().rename_table(self.database, self.table, values[0])
			messagebox.showinfo("Table rename", "Table" + self.table + " was successfully renamed")
			self.cb(self.database, self.table, values[0])
			self.table = values[0]
			self.form.clear()
		except BaseException as ex:
			messagebox.showinfo('Error', 'We are sorry, but something went wrong, Error: ' + str(ex))
