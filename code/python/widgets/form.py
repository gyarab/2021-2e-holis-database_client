from tkinter import *
from tkinter import messagebox

class FormButton:
	def __init__(self, name, command):
		self.name = name
		self.command = command


class Field:
	def __init__(self, text, type="entry", value="", warning="", required=False):
		self.text = text
		self.value = value
		self.warning = warning
		self.required = required
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
		idx = 0
		for en in self.entries:
			val = en.get()

			if self.fields[idx].required is True and (not val or len(val) == 0):
				messagebox.showerror('Field not filled', 'Field ' + self.fields[idx].text + ' must be filled')
				return

			vals.append(en.get())
			idx += 1
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
