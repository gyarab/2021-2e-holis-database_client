from tkinter import *
from tkinter.ttk import *
from code.python.psql.Database_builder import *


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
		self.table_dict = None

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
		con_id = len(self.conditions.winfo_children()) + 1
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
			row_data = self.table_dict[row]
			database_builder.remove_table_row(self.database, self.table_name, self.headers, row_data)
			item_to_delete = self.table.selection()[0]
			self.table.delete(item_to_delete)

	def header(self):
		header = Frame(self.screen)

		refresh = Label(header, text="Refresh")
		refresh.bind("<Button-1>", self.refresh_table)
		refresh.pack(side=LEFT)

		refresh = Label(header, text="Reset params")
		refresh.bind("<Button-1>", self.reset_search_params)
		refresh.pack(side=LEFT)

		minus = Label(header, text="Minus")
		minus.bind("<Button-1>", self.remove_rows)
		minus.pack(side=LEFT)

		previous_page = Label(header, text="Previous page")
		previous_page.bind("<Button-1>", lambda e: self.change_display_range('down'))
		previous_page.pack(side=LEFT)

		actual_columns_number = Label(header, textvariable=self.displayed_set)
		actual_columns_number.pack(side=LEFT)

		next_page = Label(header, text="Next page")
		next_page.bind("<Button-1>", lambda e: self.change_display_range('up'))
		next_page.pack(side=LEFT)

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

		self.table_dict = {}
		row_id = 0
		for row in data:
			self.table_dict[str(row_id)] = row
			self.table.insert(parent='', index=END, iid=row_id, text='', values=row)
			row_id += 1