from tkinter import *
from PIL import Image, ImageTk


class Icon:
	def __init__(self, root, icon_name, command):
		image = Image.open("images/" + icon_name)
		img = ImageTk.PhotoImage(image)
		self.label = Label(root, image=img)
		self.label.image = img
		self.label.bind("<Button-1>", command)

