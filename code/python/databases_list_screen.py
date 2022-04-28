from .widgets.popup_menu import *
from .forms import *


class Table:
    def __init__(self, root, database, name, change_screen, remove_table):
        self.frame = Frame(root)
        self.database = database
        self.table_title = StringVar()
        self.table_title.set("".join(name))
        self.change_screen = change_screen
        self.hidden = False
        self.remove_table = remove_table
        self.options = None

        self.create_table_title()

    def drop_table(self):
        MsgBox = messagebox.askquestion('Drop table',
                                        'Are you sure you want drop table ' + self.table_title.get() + ' ?',
                                        icon='warning')
        if MsgBox == 'yes':
            try:
                Database_builder().drop_table(self.database, self.table_title.get())
                self.delete_table()
            except BaseException as ex:
                too_low_role(ex)

    def delete_table(self):
        self.remove_table(self.table_title.get())
        self.options.popup.destroy()
        self.frame.pack_forget()
        self.frame.destroy()

    def rename_table_screen(self):
        self.change_screen("table_rename", self.database, self.table_title.get())

    def refresh_table(self):
        table_name = self.table_title.get()
        table = Database_builder().check_table_existence(self.database, table_name)

        if table is None:
            self.delete_table()
            messagebox.showinfo('Table doesn\'t exist', 'Table ' + table_name + ' no longer exist')
            return

        self.change_screen("database_table", self.database, table_name, "refresh")

    def create_table_title(self):
        label = Label(self.frame, textvariable=self.table_title, font=("arial", 16, "bold", "italic"))
        label.bind('<Double-Button-1>', lambda e, name="database_table": self.change_screen(name, self.database, self.table_title.get()))

        options = [
            Option("Rename table", self.rename_table_screen),
            Option("Drop", self.drop_table),
            Option("Refresh", self.refresh_table)
        ]

        self.options = OptionSelectMenu(label, options)
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
    def __init__(self, root, name, change_screen, resize):
        self.frame = Frame(root, bd=1, relief="solid")
        self.frame.bind("<Configure>", resize)

        try:
            self.tables = Database_builder().get_all_tables(name)
        except BaseException as ex:
            messagebox.showinfo('Database doesn\'t exist', 'Database ' + name + ' doesn\'t exist')

        self.database_title = StringVar()
        self.database_title.set(name)
        self.table_els = []
        self.change_screen = change_screen
        self.frame.pack(expand=True, fill=BOTH)
        self.create_database_title()

    def add_user(self):
        self.change_screen("add_user_database", self.database_title.get())

    def create_and_add_user(self):
        self.change_screen("create_and_add_user_database", self.database_title.get())

    def drop_database(self):
        MsgBox = messagebox.askquestion('Drop database',
                                        'Are you sure you want drop database ' + self.database_title.get() + ' ?',
                                        icon='warning')
        if MsgBox == 'yes':
            try:
                Database_builder().drop_database(self.database_title.get())
                self.frame.pack_forget()
                self.frame.destroy()
                Database_builder().remove_database_connection(self.database_title.get())
            except BaseException as ex:
                too_low_role(str(ex))

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
        title = Label(self.frame, textvariable=self.database_title,
                      font=("arial", 16, "bold", "italic"),
                      anchor="w", bg="blue")
        title.bind("<Button-1>", lambda e: self.handle_table_selection())
        title.pack(expand=True, fill=BOTH)

        options = [
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
        table = Table(self.frame, self.database_title.get(), table, self.change_screen, self.remove_table)
        table.change_visibility()
        self.table_els.append(table)

    def remove_table(self, table):
        for t in self.table_els:
            if t.table_title.get() == table:
                self.table_els.remove(t)


class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, width):
        wscale = float(width)/self.width
        hscale = 1
        self.width = width
        self.config(width=self.width, height=self.height)
        self.scale("all", 0, 0, wscale, hscale)


class Database_list_screen:
    def __init__(self, screen, change_screen):
        self.screen = Frame(screen)
        self.canvas = ResizingCanvas(self.screen, bg="blue")
        scrollbar = Scrollbar(self.screen, orient="vertical", command=self.canvas.yview)

        self.databases = []
        self.list = list = LabelFrame(self.canvas, text="Databases", width=300, font=('verdana', 10, 'bold'),
                                 borderwidth=3, relief=RIDGE, highlightthickness=4, bg="white", highlightcolor="white",
                                 highlightbackground="white", fg="#248aa2")

        list.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=list, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="left", fill="y")
        self.canvas.pack(fill=BOTH, expand=True)
        self.canvas.addtag_all("all")

        self.change_screen = change_screen
        self.database_list = Frame(list)
        self.database_list.pack()

        self.database_actions = Frame(list)
        self.database_actions.pack(fill=X)

        self.databases_els = {}

    def load_databases(self):
        connections = Database_builder().get_database_connections()

        for con in connections:
            self.databases.append(con)

    def add_database(self, database):
        self.databases_els[database] = Database(self.database_list, database, self.change_screen, lambda e: self.canvas.on_resize(self.list.winfo_width()))

    def show(self):
        self.load_databases()

        for d in self.databases:
            self.databases_els[d] = Database(self.database_list, d, self.change_screen, lambda e: self.canvas.on_resize(self.list.winfo_width()))

        def create_link(text, name):
            link = Label(self.database_actions, text=text, anchor="w", bg="green")
            link.bind("<Button-1>", lambda e: self.change_screen(name))
            link.pack(fill=BOTH, expand=True)

        create_link("Connect to db", "database_connect")
        create_link("Create db", "database_create")
        create_link("Connect user", "create_user")
        create_link("Home", "home")
        create_link("Application user", "change_application_main_user")

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
