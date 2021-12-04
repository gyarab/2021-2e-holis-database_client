from tkinter import messagebox
from tkinter import *
from code.python.psql.Database_builder import *
import re
import random


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

		self.screen = Frame(root)
		self.screen.pack()
		Label(self.screen, text="Create table").pack()

		Label(self.screen, text="Table name")
		self.table_name_entry = Entry(self.screen)
		self.table_name_entry.pack()
		Label(self.screen, text="Table name can only contain lower case letters").pack()

		self.fields = Frame(self.screen)
		self.fields.pack()

		self.start()

	def create_table(self):
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
		command = "CREATE TABLE " + table_name + " ("

		row_idx = 0
		for row in self.rows:
			row_idx += 1
			vals = []

			i = 0
			for f in self.rows[row]:
				i += 1

				val = f.get()
				if (i == 1 or i == 2) and len(val) == 0:
					messagebox.showinfo('Missing value',
										'In column ' + str(row_idx) + ' is missing ' + ('name' if i == 1 else 'datatype'))
					return

				if i == 6 and val == 1:
					if primary_key is True:
						messagebox.showinfo('Primary key', 'Only one column can be primary key')
						return

					primary_key = True

				vals.append(val)

			row_sql = TableRow(*vals)
			command += row_sql.create_sql_row() + (", " if row_idx != len(self.rows) else "")

		command += ");"
		try:
			Database_builder().create_table(self.database, command)
			self.cb(self.database, table_name)
			messagebox.showinfo('Success', 'Your table was successfully created')
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

	def start(self):
		self.create_field()
		Button(self.screen, text="Add column", command=self.create_field).pack(side=LEFT)
		Button(self.screen, text="Create table", command=self.create_table).pack(side=LEFT)

	def remove_row(self, row1, row2, row3, row_id):
		row1.pack_forget()
		row1.destroy()
		row2.pack_forget()
		row2.destroy()
		row3.pack_forget()
		row3.destroy()
		del self.rows[row_id]

	def generate_random_id(self):
		repeat = True

		while repeat is True:
			n = random.randint(0, 22)
			if n not in self.rows:
				return n

	def create_field(self):
		row_id = self.generate_random_id()
		row = []

		row1 = Frame(self.fields)
		Label(row1, text="Name").pack(side=LEFT)
		Label(row1, text="Type").pack(side=LEFT)
		Label(row1, text="Default (optional)").pack(side=LEFT)
		row1.pack()

		row2 = Frame(self.fields)
		self.create_entry(row2, row)
		self.create_entry(row2, row)
		self.create_entry(row2, row)
		row2.pack()

		row3 = Frame(self.fields)
		self.create_checkbutton(row3, row, "Not null")
		self.create_checkbutton(row3, row, "Unique")
		self.create_checkbutton(row3, row, "Primary key")

		if len(self.rows) > 0:
			Button(row3, text="Remove field", command=lambda: self.remove_row(row1, row2, row3, row_id)).pack(side=LEFT)

		row3.pack()

		self.rows[row_id] = row

	def create_entry(self, parent, row):
		e = Entry(parent)
		row.append(e)
		e.pack(side=LEFT)

	def create_checkbutton(self, parent, row, text):
		var = IntVar()
		Checkbutton(parent, text=text, variable=var).pack(side=LEFT)
		row.append(var)
