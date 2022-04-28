from python.databases_list_screen import *
from python.forms import *
from python.database_table import *
from python.table_form_create import *
from python.home_screen import *

main = Tk()
main.geometry("1000x800")
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
		self.active_db = None
		self.active_table = None

		self.screens = [
			Screen("home", HomeScreen, self.change_screen),
			Screen("database_table", DatabaseTable),
			Screen("database_create", CreateDatabaseForm, self.add_database),
			Screen("add_user_database", AddUserToDatabase),
			Screen("database_connect", ConnectDatabaseForm, self.add_database),
			Screen("database_rename", RenameDatabaseForm, self.rename_database),
			Screen("table_rename", RenameTable, self.rename_table),
			Screen("database_table", DatabaseTable),
			Screen("create_user", CreateUserForm),
			Screen("create_and_add_user_database", CreateUserForm),
			Screen("table_create", CreateTableForm, self.add_table),
			Screen("change_application_main_user", ApplicationMainUserChange)
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
		if screen == self.active and screen == "database_table":
			if data[0] == self.active_db and data[1] == self.active_table and len(data) == 3 and data[2] == "refresh":
				screen = self.get_screen_by_name()
				screen.screen.reset_search_params(None)
				return
			elif data[0] == self.active_db and data[1] == self.active_table:
				return

			self.active_db = data[0]
			self.active_table = data[1]

		if screen == "database_table" and len(data) == 3 and data[2] == "refresh":
			return

		if screen == "database_table":
			self.active_db = data[0]
			self.active_table = data[1]

		self.screen_switch('hide')
		self.active = screen
		self.screen_switch('show', data)

	def screen_switch(self, mode, data=None):
		screen = self.get_screen_by_name()


		if screen.active is False:
			screen.activate(data)
		elif mode == 'show':
			screen.already_activated(data)

		screen_el = screen.screen.screen
		screen_el.pack(side=LEFT, fill=BOTH, expand=True) if mode == 'show' else screen_el.pack_forget()

	def get_screen_by_name(self):
		for sc in self.screens:
			if sc.name == self.active:
				return sc

	def start(self):
		self.database_list.show().pack(side=LEFT, fill="y")
		self.active = "home"
		self.screen_switch("show")


ScreenManager().start()

main.mainloop()
