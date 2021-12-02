from tkinter import messagebox
from code.python.widgets.form import *
from code.python.psql.Database_builder import *

class CreateDatabaseForm:
	def __init__(self, root, data, cb):
		self.cb = cb
		self.form = Form(
			root,
			"Create database",
			[
				Field("Database name", warning="Database will be converted to lower case"),
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
		#TODO exception handling
		values = self.form.get_values()
		Database_builder().create_db(values[0], values[1])
		messagebox.showinfo('Database creation', 'Database was successfully created')


class Create_user_form:
	def __init__(self, root, data):
		self.database = data[0]
		self.form = Form(
			root,
			"Create database",
			[
				Field("Username", warning="Username will be converted to lower case"),
				Field("Password"),
				Field("Create db", type="check"),
				Field("Create role", type="check"),
				Field("Superuser", type="check")
			],
			[
				FormButton(
					"Create",
					self.handle_create
				)
			]
		)
		self.screen = self.form.main_frame

	def handle_create(self):
		#TODO exception handling
		values = self.form.get_values()
		Database_builder().create_user(
			self.database,
			values[0],
			values[1],
			values[2],
			values[3],
			values[4]
		)
		messagebox.showinfo('information', 'User was successfully created')


class Connect_database_form:
	def __init__(self, root, data, cb):
		self.cb = cb
		self.form = Form(
			root,
			"Connect to database",
			[
				Field("Database name"),
				Field("User"),
				Field("Password")
			],
			[
				FormButton(
					"Test connection",
					self.test_connection
				),
				FormButton(
					"Connect",
					self.handle_connection
				)
			]
		)
		self.screen = self.form.main_frame

	def handle_connection(self):
		# TODO error handling
		values = self.form.get_values()
		database_connection = DatabaseConnection(database=values[0], user=values[1], password=values[2])
		Database_builder().save_database_connection(database_connection)
		self.cb(values[0])

	def test_connection(self):
		values = self.form.get_values()
		database_connection = DatabaseConnection(database=values[0], user=values[1], password=values[2])
		try:
			Database_builder().test_database_connection(database_connection)
			messagebox.showinfo("Database test connection",
			                    "Your connect configuration is correct " + values[0])
		except BaseException as e:
			print(e) #TODO error handling


class Rename_database_form:
	def __init__(self, root, data, cb):
		self.cb = cb
		self.database = data[0]
		self.form = Form(
			root,
			"Rename database",
			[
				Field(
					"Database name",
					value=self.database
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
		try:
			database_builder = Database_builder()
			connection = database_builder.get_database_connection(self.database)
			database_builder.rename_database(self.database, values[0])
			database_builder.remove_database_connection(self.database)

			database_connection = DatabaseConnection(database=values[0], user=connection['user'], password=connection['password'])
			database_builder.save_database_connection(database_connection)

			messagebox.showinfo("Database rename", "Your database was successfully renamed")
			self.cb(self.database, values[0])
		except BaseException as e:
			print(e) #TODO error handling

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
					value=self.table
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
		try:
			Database_builder().rename_table(self.database, self.table, values[0])
			#messagebox.showinfo("Table rename", "Your table was successfully renamed")
			self.cb(self.database, self.table, values[0])
		except BaseException as e:
			print(e)  # TODO error handling
