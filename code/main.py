from code.python.databases_list_screen import *
from code.python.forms import *
from code.python.query_console import *
from code.python.database_table import *
from code.python.table_form_create import *

main = Tk()
main.geometry("800x800")
main.title('PSQL database client')


class Screen:
	def __init__(self, name, screen, cb=None):
		self.name = name
		self.active = False
		self.screen_name = screen
		self.screen = None
		self.cb = cb

	def activate(self, data):
		self.screen = self.screen_name(main, data, self.cb) if self.cb is not None else self.screen_name(main, data)
		self.active = True

	def already_activated(self, data):
		self.screen.screen.pack_forget()
		self.screen.screen.destroy()
		self.activate(data)


class ScreenManager:
	def __init__(self):
		self.active = None
		self.database_list = Database_list_screen(main, self.change_screen)
		self.screens = [
			Screen("query_console", Query_console),
			Screen("database_table", DatabaseTable),
			Screen("database_create", CreateDatabaseForm, self.add_database),
			Screen("add_user_database", AddUserToDatabase),
			Screen("database_connect", ConnectDatabaseForm, self.add_database),
			Screen("database_rename", RenameDatabaseForm, self.rename_database),
			Screen("table_rename", RenameTable, self.rename_table),
			Screen("database_table", DatabaseTable),
			Screen("create_user", CreateUserForm),
			Screen("create_and_add_user_database", CreateUserForm),
			Screen("table_create", CreateTableForm, self.add_table)
		]

	def add_database(self, database):
		self.database_list.add_database(database)

	def rename_table(self, database, table_name_old, table_name_new):
		self.database_list.rename_table(database, table_name_old, table_name_new)

	def rename_database(self, database_name_old, database_name_new):
		self.database_list.rename_database(database_name_old, database_name_new)

	def add_table(self, database, table):
		self.database_list.add_table(database, table)

	def change_screen(self, screen, *data):
		self.screen_switch('hide')
		self.active = screen
		self.screen_switch('show', data)

	def screen_switch(self, mode, data=None):
		for sc in self.screens:
			if sc.name == self.active:
				if sc.active is False:
					sc.activate(data)
				elif mode == 'show':
					sc.already_activated(data)

				screen = sc.screen.screen

				screen.pack(side=RIGHT, fill=BOTH) if mode == 'show' else screen.pack_forget()
				break

	def start(self):
		self.database_list.show().pack(side=LEFT, fill="y")
		self.active = "database_create"
		self.screen_switch("show")


ScreenManager().start()

main.mainloop()
