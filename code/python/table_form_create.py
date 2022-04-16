from tkinter import messagebox
from tkinter import *
from code.python.psql.Database_builder import *
import re
import random
from .widgets.ScrollableFrame import ScrollableFrame


class TableRow:
	def __init__(self, name, row_type, default, not_null, unique, primary_key):
		self.name = name
		self.type = row_type
		self.default = default
		self.not_null = not_null
		self.unique = unique
		self.primary_key = primary_key

	def create_sql_row(self):
		row = [self.name, self.type]

		if self.default != '':
			row.append("DEFAULT '" + self.default + "'")

		if self.primary_key == 1 and self.not_null == 1:
			row.append("NOT NULL")

		if self.primary_key == 1 and self.unique == 1:
			row.append("PRIMARY KEY")

		if self.unique == 1:
			row.append("UNIQUE")

		if self.not_null == 1:
			row.append("NOT NULL")

		if self.primary_key == 1:
			row.append("PRIMARY KEY")

		return " ".join(row)


class CreateTableForm:
	def __init__(self, root, data, cb=None):
		self.cb = cb
		self.database = data[0]
		self.rows = {}

		self.screen = ScrollableFrame(root)
		self.main = self.screen.scrollable_frame
		Label(self.main, text="Create table", height=2, pady=1, font=('Arial', 25, 'bold'), justify=CENTER).pack()

		Label(self.main, text="Table name", font=('Arial', 12, 'bold')).pack()
		self.table_name_entry = Entry(self.main)
		self.table_name_entry.pack()
		Label(self.main, text="Table name can only contain lower case letters").pack()

		self.fields = Frame(self.main)
		self.fields.pack()
		self.generated_sql_textbox = Text(self.main)

		self.start()

	def create_table(self):
		command, table_name = self.generate_create_table()

		try:
			Database_builder().create_table(self.database, command)
			self.cb(self.database, table_name)
			messagebox.showinfo('Success', 'Your table was successfully created')
			self.clean_form()
		except BaseException as ex:
			ex = str(ex)
			invalid_datatype = re.search("type \"(.+)\" does not exist", ex)

			if invalid_datatype:
				messagebox.showinfo('Wrong type', invalid_datatype.group() +
				                    ' see https://www.postgresql.org/docs/9.5/datatype.html for all possible data types.')
				return

			relation_exist = re.search("relation \"(.+)\" already exists", ex)
			if relation_exist:
				messagebox.showinfo('Already exists', table_name + ' already exists')
				return

			if 'syntax error' in ex:
				messagebox.showinfo('Syntax error', ex)
				return

			messagebox.showinfo('Error', 'We are sorry, but something went wrong, Error: ' + ex)

	def clean_form(self):
		self.table_name_entry.delete(0, 'end')

		row_i = 0
		for id in self.rows:
			row_i += 1
			row = self.rows[id]

			if row_i == 1:
				row['column_name'].delete(0, 'end')
				row['column_type'].delete(0, 'end')
				row['column_default'].delete(0, 'end')
				row['not_null'].set(0)
				row['unique'].set(0)
				row['primary_key'].set(0)
				continue
			row['destroy_field']()

		row_i = 0
		for id in self.rows:
			row_i += 1
			if row_i > 0:
				del self.rows[id]

		self.generated_sql_textbox.pack_forget()

	def generate_create_table(self):
		table_name = self.table_name_entry.get().lower()

		if table_name == '':
			messagebox.showinfo('Table name', 'Table name is missing')
			return

		name_checked = re.match("([_#@a-z0-9])+", table_name)

		if not name_checked or len(name_checked.group()) < len(table_name):
			messagebox.showinfo('Wrong letters', '''Your table name contains invalid characters. 
																					Only valid characters are #, @, _, a-z and 0-9''')
			return

		primary_key = None
		command = "CREATE TABLE " + table_name + " (\n"

		row_idx = 0
		for id in self.rows:
			row = self.rows[id]
			row_idx += 1

			vals = [
				row['column_name'].get(),
				row['column_type'].get(),
				row['column_default'].get(),
				row['not_null'].get(),
				row['unique'].get(),
				row['primary_key'].get()
			]

			if len(vals[0]) == 0 or len(vals[1]) == 0:
				messagebox.showinfo('Missing value',
				                    'In column ' + ('name' if len(vals[0]) == 0 else 'datatype'))
				return

			if vals[5] == 1:
				if primary_key is True:
					messagebox.showinfo('Primary key', 'Only one column can be primary key')
					return
				primary_key = True

			row_sql = TableRow(*vals)
			command += "    " + row_sql.create_sql_row() + (", \n" if row_idx != len(self.rows) else "\n")

		command += ");"
		return command, table_name

	def generate_sql(self):
		if not self.generated_sql_textbox.winfo_ismapped():
			self.generated_sql_textbox.pack()

		command, table_name = self.generate_create_table()
		self.generated_sql_textbox.delete('1.0', END)
		self.generated_sql_textbox.insert("1.0", command)

	def start(self):
		self.create_field()
		Button(self.main, text="Add column", command=self.create_field,
		       height=1, bg="#A877BA", font=('Arial', 16, 'bold'), pady=5).pack(side=TOP)
		Button(self.main, text="Create table", command=self.create_table,
		       height=1, bg="#A877BA", font=('Arial', 16, 'bold'), pady=5).pack(side=TOP)
		Button(self.main, text="Generate create table", command=self.generate_sql,
		       height=1, bg="#A877BA", font=('Arial', 16, 'bold'), pady=5).pack(side=TOP)

	def generate_random_id(self):
		repeat = True

		while repeat is True:
			n = random.randint(0, 22)
			if n not in self.rows:
				return n

	def create_field(self):
		row_id = self.generate_random_id()
		row = {}

		row_el = Frame(self.fields)
		row_el.pack()
		column1 = Frame(row_el, height=150)
		Label(column1, text="Name", font=('Arial', 12, 'bold')).pack()
		row['column_name'] = self.create_entry(column1)
		row['not_null'] = self.create_checkbutton(column1, "Not null")
		column1.pack(side=LEFT)

		column2 = Frame(row_el)
		Label(column2, text="Type", font=('Arial', 12, 'bold')).pack()
		row['column_type'] = self.create_entry(column2)
		row['unique'] = self.create_checkbutton(column2, "Unique")
		column2.pack(side=LEFT)

		column3 = Frame(row_el)
		Label(column3, text="Default (optional)", font=('Arial', 12, 'bold')).pack()
		row['column_default'] = self.create_entry(column3)
		row['primary_key'] = self.create_checkbutton(column3, "Primary key")

		column3.pack(side=LEFT)

		if len(self.rows) > 0:
			removeEl = Button(self.fields, text="Remove field")
			removeEl.pack()

			def remove(delete_field=False):
				if delete_field is True:
					del self.rows[row_id]
				row_el.destroy()
				removeEl.destroy()

			row['destroy_field'] = lambda: remove()
			removeEl['command'] = lambda: remove(True)

		self.rows[row_id] = row

	def create_entry(self, parent):
		e = Entry(parent)
		e.pack()
		return e

	def create_checkbutton(self, parent, text):
		var = IntVar()
		checkbox = Checkbutton(parent, text=text, variable=var)
		checkbox.pack()
		return var
