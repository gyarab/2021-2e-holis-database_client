from tkinter import *


def create_button(screen, text, action):
	return Button(screen, text=text, command=action)


def create_label(screen, text):
	return Label(screen, text=text, font=("arial", 16, "bold", "italic"), bg='red', width=15)


def create_listbox(screen, items):
	list = Listbox(screen, bg='blue')
	for item in items:
		list.insert(END, item)
	return list
