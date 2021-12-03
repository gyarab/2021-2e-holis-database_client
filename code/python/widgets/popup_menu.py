from tkinter import *

class Option:
	def __init__(self, name, command, separator=False):
		self.name = name
		self.command = command
		self.separator = separator


class OptionSelectMenu:
	def __init__(self, root, options):
		self.popup = Menu(root, tearoff=0)

		for op in options:
			if op.separator is True:
				self.popup.add_separator()
			self.popup.add_command(label=op.name, command=op.command)

		root.bind("<Button-2>", self.menu_popup)

	def menu_popup(self, event):
		# display the popup menu
		try:
			self.popup.tk_popup(event.x_root, event.y_root, 0)
		finally:
			# Release the grab
			self.popup.grab_release()
