from tkinter import *


class FormButton:
	def __init__(self, name, command):
		self.name = name
		self.command = command


class Field:
	def __init__(self, text, type="entry", value="", warning="", optional=False):
		self.text = text
		self.value = value
		self.warning = warning
		self.optional = optional
		self.type = type


class Form:
	def __init__(self, root, title, fields, buttons):
		self.fields = fields
		self.main_frame = Frame(root)
		self.entries = []
		self.buttons = buttons

		Label(self.main_frame, text=title)
		self.show_fields()
		self.show_buttons()

	def get_values(self):
		vals = []
		for en in self.entries:
			vals.append(en.get())
		return vals

	def show_fields(self):
		for f in self.fields:
			frame = Frame(self.main_frame)
			field = None

			if f.type == "check":
				var = IntVar()
				Checkbutton(frame, text=f.text, variable=var).pack()
				field = var
			else:
				Label(frame, text=f.text).pack()
				field = Entry(frame)

				if len(f.value) > 0:
					field.insert(0, f.value)

				field.pack()

			if len(f.warning) > 0:
				Label(frame, text=f.warning).pack()

			self.entries.append(field)

			frame.pack()

	def show_buttons(self):
		for b in self.buttons:
			Button(self.main_frame, text=b.name, command=b.command).pack()
