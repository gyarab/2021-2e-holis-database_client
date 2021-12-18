from tkinter import messagebox
from tkinter.ttk import *
from code.python.psql.Database_builder import *
import random
from code.python.widgets.svg_pic import *
import re


class DatabaseTable:
	def __init__(self, root, data):
		self.screen = Frame(root)
		self.database = data[0]
		self.table_name = data[1]
		self.table = None
		self.displayed_set = StringVar()
		self.select_params = SelectParams()
		self.headers = None
		self.conditions = None
		self.condition_ids = {}
		self.add_row_frame = Frame(self.screen)
		self.update_row_frame = Frame(self.screen)

		self.start()

	def change_display_range_text(self):
		offset = self.select_params.offset
		limit = self.select_params.limit
		self.displayed_set.set(str(offset) + '-' + str(limit))

	def change_display_range(self, mode):
		if self.select_params.offset == 0 and mode == 'down':
			return

		self.reset_table()

		offset = self.select_params.offset
		limit = self.select_params.limit

		self.select_params.change_range(
			offset + 100 if mode == 'up' else offset - 100,
			limit + 100 if mode == 'up' else limit - 100
		)

		self.change_display_range_text()
		self.load_table()

	def order_by(self, order_by, direction, dir_change=None):
		if dir_change is True:
			direction.set("ASC" if direction.get() == "DESC" else "DESC")

		self.select_params.order_by_change(order_by.get(), direction.get())
		self.reset_table()
		self.load_table()

	def reset_table(self):
		for item in self.table.get_children():
			self.table.delete(item)

	def order_by_button(self):
		filters = Frame(self.screen)
		filters.pack()

		Label(filters, text="Order by").pack(side=LEFT)
		order_by = StringVar()
		direction = StringVar()

		headers = self.transform_header_to_list()

		OptionMenu(
			filters,
			order_by,
			headers[0],
			*headers,
			command=lambda e: self.order_by(order_by, direction)).pack(side=LEFT)

		direction.set("ASC")
		direction_label = Label(filters, textvariable=direction)
		direction_label.bind("<Button-1>", lambda e: self.order_by(order_by, direction, True))
		direction_label.pack(side=LEFT)

	def generate_random_id(self):
		repeat = True

		while repeat is True:
			n = random.randint(0, 22)
			if n not in self.condition_ids:
				self.condition_ids[n] = n
				return n

	def handle_condition(self, column, value, con_id):
		column_str = column.get()

		if value == 'None':
			value = "IS NULL"

		self.select_params.add_condition(con_id, column_str, value)
		self.reset_table()
		self.load_table()

	def handle_condition_remove(self, frame, con_id):
		self.select_params.remove_condition(con_id)
		frame.pack_forget()
		frame.destroy()
		self.reset_table()
		self.load_table()

	def transform_header_to_list(self):
		headers = []

		for c in self.headers:
			st = ''.join(map(str, c))
			headers.append(st)

		return headers

	def render_condition_input(self):
		con_id = self.generate_random_id()
		condition = Frame(self.conditions)
		condition.pack()

		Label(condition, text="Condition").pack(side=LEFT)
		Label(condition, text="Column").pack()
		column_name = StringVar()

		headers = self.transform_header_to_list()

		OptionMenu(
			condition,
			column_name,
			headers[0],
			*headers).pack(side=LEFT)

		Label(condition, text="Value").pack(side=LEFT)
		entry = Entry(condition)
		entry.pack(side=LEFT)

		Button(condition, text="Apply",
		       command=lambda: self.handle_condition(column_name, entry.get(), con_id)).pack(side=LEFT)
		Button(condition, text="Remove",
		       command=lambda: self.handle_condition_remove(condition, con_id)).pack(side=LEFT)

	def refresh_table(self, args):
		self.reset_table()
		self.load_table()

	def reset_search_params(self, args):
		for ch in self.screen.winfo_children():
			ch.destroy()

		self.table = None
		self.select_params = SelectParams()
		self.start()

	def start(self):
		self.load_header_header()
		self.change_display_range_text()

		self.header()
		self.order_by_button()

		self.conditions = Frame(self.screen)
		self.conditions.pack()
		Button(self.screen, text="Add condition", command=self.render_condition_input).pack()

		self.screen.pack()
		self.load_table()

	def remove_rows(self, args):
		rows = self.table.selection()

		database_builder = Database_builder()
		for row in rows:
			val = self.get_row_value(row)
			database_builder.remove_table_row(self.database, self.table_name, val)
			item_to_delete = self.table.selection()[0]
			self.table.delete(item_to_delete)

	def edit_row(self):
		rows = self.table.selection()

		if len(rows) > 1:
			messagebox.showinfo('Only one line can be edited at a time')
			return

		edited = self.get_row_value(rows[0])
		self.add_row_form(edited)

	def add_row(self, entries, original_values):
		vals = []

		for e in entries:
			v = e.get()
			vals.append(v if len(v) > 0 else None)

		if original_values is not None:
			Database_builder().edit_table_row(self.database, self.table_name, vals, original_values)
			selected = self.table.focus()
			self.table.item(selected, values=vals)
		else:
			Database_builder().add_table_row(self.database, self.table_name, self.headers, vals)
			self.table.insert(parent='', index=END, iid=len(self.table.get_children()), text='', values=vals)

		self.reset_add_row_form()
		self.add_row_frame.pack_forget()

	def reset_add_row_form(self):
		for ch in self.add_row_frame.winfo_children():
			ch.destroy()

	def add_row_form(self, values=None):
		self.reset_add_row_form()
		self.add_row_frame.pack()

		Label(self.add_row_frame, text="Add row to table").pack()
		columns = values if values is not None else self.transform_header_to_list()
		entries = []

		print(values)
		print(columns)
		for col in columns:
			row = Frame(self.add_row_frame)
			row.pack()
			Label(row, text=col).pack(side=LEFT)

			e = Entry(row)
			if values is not None:
				e.insert(0, columns[col])

			entries.append(e)
			e.pack(side=LEFT)

		button_text = "Edit row" if values is not None else "Add row"
		Button(self.add_row_frame, text=button_text, command=lambda: self.add_row(entries, values)).pack()

	def header(self):
		header = Frame(self.screen)

		Icon(header, "refresh.png", self.refresh_table).label.pack(side=LEFT)
		Icon(header, "reset.png", self.reset_search_params).label.pack(side=LEFT)
		Icon(header, "delete.png", self.remove_rows).label.pack(side=LEFT)
		Icon(header, "add.png", lambda e: self.add_row_form()).label.pack(side=LEFT)
		Icon(header, "edit.png", lambda e: self.edit_row()).label.pack(side=LEFT)
		Icon(header, "left.png", lambda e: self.change_display_range('down')).label.pack(side=LEFT)
		actual_columns_number = Label(header, textvariable=self.displayed_set)
		actual_columns_number.pack(side=LEFT)
		Icon(header, "right.png", lambda e: self.change_display_range('up')).label.pack(side=LEFT)
		header.pack()

	def load_table_data(self):
		return Database_builder().get_all_table_data(self.database, self.table_name, self.select_params)

	def load_header_header(self):
		self.headers = Database_builder().get_all_table_columns(self.database, self.table_name)

	def load_table(self):
		data = self.load_table_data()

		if self.table is None:
			self.table = Treeview(self.screen, columns=self.headers, show='headings')
			self.table.pack(fill=BOTH)

		for col in self.headers:
			self.table.heading(col, text=col, anchor=CENTER)

		string_headers = self.transform_header_to_list()

		row_id = 0
		for row in data:
			r = self.build_row(row, string_headers)
			self.table.insert(parent='', index=END, iid=row_id, text='', values=r)
			row_id += 1

	def build_row(self, row, headers):
		row_val = []

		for h in headers:
			row_val.append(row[h])

		return row_val

	def get_row_value(self, idx):
		curRow = self.table.set(idx)
		edited = {}

		for col in curRow:
			name = re.sub("['(.*?)+, ]", "", col)
			edited[name] = curRow[col]

		return edited
