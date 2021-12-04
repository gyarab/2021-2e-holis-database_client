from tkinter import messagebox
from code.python.psql.Database_builder import *
from code.python.widgets.popup_menu import *


class Table:
    def __init__(self, root, database, name, change_screen):
        self.frame = Frame(root)
        self.database = database
        self.table_title = StringVar()
        self.table_title.set("".join(name))
        self.change_screen = change_screen
        self.hidden = False

        self.create_table_title()

    def drop_table(self):
        MsgBox = messagebox.askquestion('Drop table',
                                        'Are you sure you want drop table ' + self.table_title.get() + ' ?',
                                        icon='warning')
        if MsgBox == 'yes':
            Database_builder().drop_table(self.database, self.table_title.get())

    def rename_table_screen(self):
        self.change_screen("table_rename", self.database, self.table_title.get())

    def modify_table(self):
        print("Drop table")
        #Database_builder().drop_database()

    def open_query_console(self):
        print("Drop table")
        #Database_builder().drop_database()

    def refresh_table(self):
        #TODO check existence
        #TODO reload table data
        print("refresh")

    def create_table_title(self):
        label = Label(self.frame, textvariable=self.table_title, font=("arial", 16, "bold", "italic"))
        label.bind('<Double-Button-1>', lambda e, name="database_table": self.change_screen(name, self.database, self.table_title.get()))

        options = [
            Option("Query console", self.open_query_console),
            Option("Rename table", self.rename_table_screen),
            Option("Drop", self.drop_table),
            Option("Modify", self.modify_table),
            Option("Refresh", self.refresh_table)
        ]

        OptionSelectMenu(label, options)
        label.pack()

    def change_visibility(self):
        if self.hidden is False:
            self.frame.pack()
        else:
            self.frame.pack_forget()
        self.hidden = not self.hidden

    def rename(self, table_name):
        self.table_title.set(table_name)


class Database:
    def __init__(self, root, name, change_screen):
        self.frame = Frame(root)
        try:
            self.tables = Database_builder().get_all_tables(name)
        except BaseException as ex:
            messagebox.showinfo('Database doesn\'t exist', 'Database ' + name + ' doesn\'t exist')

        self.database_title = StringVar()
        self.database_title.set(name)
        self.table_els = []
        self.change_screen = change_screen
        self.frame.pack()
        self.create_database_title()

    def open_query_console(self):
        self.change_screen("query_console", self.database_title.get())

    def add_user(self):
        self.change_screen("add_user_database", self.database_title.get())

    def create_and_add_user(self):
        self.change_screen("create_and_add_user_database", self.database_title.get())

    def drop_database(self):
        MsgBox = messagebox.askquestion('Drop database',
                                        'Are you sure you want drop database ' + self.database_title.get() + ' ?',
                                        icon='warning')
        if MsgBox == 'yes':
            Database_builder().drop_database(self.database_title.get())
            self.frame.pack_forget()
            self.frame.destroy()
            Database_builder().remove_database_connection(self.database_title.get())

    def disconnect_database(self):
        MsgBox = messagebox.askquestion('Disconnect database',
                                        'Are you sure you want disconnect from database ' + self.database_title.get() + ' ?',
                                        icon='warning')
        if MsgBox == 'yes':
            self.frame.pack_forget()
            self.frame.destroy()
            Database_builder().remove_database_connection(self.database_title.get())

    def refresh_database(self):
        for t in self.table_els:
            t.frame.pack_forget()
            t.frame.destroy()

        #TODO pokud jsou otevřené nechat otevřené/pokud zavřené nechat zavřené
        self.tables = Database_builder().get_all_tables(self.database_title.get())
        self.table_els = []
        self.handle_table_selection()

    def open_rename_database_screen(self):
        self.change_screen("database_rename", self.database_title.get())

    def create_table(self):
        self.change_screen("table_create", self.database_title.get())

    def create_database_title(self):
        title = Label(self.frame, textvariable=self.database_title, font=("arial", 16, "bold", "italic"))
        title.bind("<Button-1>", lambda e: self.handle_table_selection())
        title.pack()

        options = [
            Option("Query console", self.open_query_console),
            Option("Rename", self.open_rename_database_screen),
            Option("Drop", self.drop_database),
            Option("Disconnect", self.disconnect_database),
            Option("Refresh", self.refresh_database),
            Option("Create table", self.create_table),
            Option("Add user", self.add_user),
            Option("Create and add user", self.create_and_add_user)
        ]
        OptionSelectMenu(title, options)

    def handle_table_selection(self):
        if len(self.table_els) == 0:
            for t in self.tables:
                self.add_table(t)

        for t in self.table_els:
            t.change_visibility()

    def rename_database(self, database_name_new):
        self.database_title.set(database_name_new)

    def rename_table(self, table_name_old, table_name_new):
        for t in self.table_els:
            if t.table_title.get() == table_name_old:
                t.rename(table_name_new)

    def add_table(self, table):
        table = Table(self.frame, self.database_title.get(), table, self.change_screen)
        table.change_visibility()
        self.table_els.append(table)


class Database_list_screen:
    def __init__(self, screen, change_screen):
        self.screen = screen
        self.databases = []
        self.screen = LabelFrame(self.screen, text="Databases", width=300, font=('verdana', 10, 'bold'),
                                 borderwidth=3, relief=RIDGE, highlightthickness=4, bg="white", highlightcolor="white",
                                 highlightbackground="white", fg="#248aa2")
        self.change_screen = change_screen
        self.database_list = Frame(self.screen)
        self.database_list.pack()
        self.databases_els = {}

    def load_databases(self):
        connections = Database_builder().get_database_connections()

        for con in connections:
            self.databases.append(con)

    def add_database(self, database):
        self.databases_els[database] = Database(self.database_list, database, self.change_screen)

    def show(self):
        self.load_databases()

        for d in self.databases:
            self.databases_els[d] = Database(self.database_list, d, self.change_screen)

        connect_db = Label(self.screen, text="Connect to db")
        create_db = Label(self.screen, text="Create db")
        create_user = Label(self.screen, text="Create user")

        connect_db.bind("<Button-1>", lambda e, name="database_connect": self.change_screen(name))
        create_db.bind("<Button-1>", lambda e, name="database_create": self.change_screen(name))
        create_user.bind("<Button-1>", lambda e, name="create_user": self.change_screen(name))

        create_user.pack()
        connect_db.pack()
        create_db.pack()

        return self.screen

    def rename_database(self, database_name_old, database_name_new):
        self.databases_els[database_name_old].rename_database(database_name_new)
        val = self.databases_els[database_name_old]
        del self.databases_els[database_name_old]
        self.databases_els[database_name_new] = val

    def rename_table(self, database, table_name_old, table_name_new):
        self.databases_els[database].rename_table(table_name_old, table_name_new)

    def add_table(self, database, table):
        self.databases_els[database].add_table(table)
