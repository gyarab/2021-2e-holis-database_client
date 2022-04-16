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
		self.main_frame = Frame(root, width=400)
		self.form_frame = Frame(self.main_frame, bg="white", height=3, relief=RAISED, padx=10)
		self.entries = []
		self.buttons = buttons

		Label(self.form_frame, bg="white", text=title, height=2, pady=1, font=('Arial', 25, 'bold'), justify=CENTER).pack()
		self.show_fields()
		self.show_buttons()
		self.form_frame.pack(fill=X, expand=True)
		self.form_frame.place(relx=0.2, rely=0.2)

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

	def clear(self):
		for en in self.entries:
			en.delete(0, 'end')

	def show_fields(self):
		i = 0
		for f in self.fields:
			i = i + 1
			frame = Frame(self.form_frame, bg="white")
			field = None

			if f.type == "check":
				var = IntVar()
				Checkbutton(frame, text=f.text, variable=var).pack()
				field = var
			else:
				Label(frame, text=f.text, background="white", font=('Arial', 12, 'bold')).pack()
				field = Entry(frame, justify=CENTER, width=20, border=0)

				if i == 1:
					field.focus()

				if len(f.value) > 0:
					field.insert(0, f.value)

				field.pack(pady=5)

			if len(f.warning) > 0:
				Label(frame, text=f.warning, background="white", wraplength=360).pack()

			self.entries.append(field)

			frame.pack()

	def show_buttons(self):
		for b in self.buttons:
			Button(self.form_frame, text=b.name, command=b.command,
			       height=1, bg="#A877BA", font=('Arial', 16, 'bold'), pady=5).pack(padx=2, pady=10)