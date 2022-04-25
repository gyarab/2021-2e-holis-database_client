from tkinter.ttk import *
from tkinter import filedialog
from .widgets.svg_pic import *
import webbrowser
from .widgets.ScrollableFrame import ScrollableFrame


class HomeScreen:
	def __init__(self, root, data, change_screen):
		self.screen = ScrollableFrame(root)
		self.main = self.screen.scrollable_frame
		self.change_screen = change_screen

		Label(self.main, text="Welcome to Postgresql database client", font=('Arial', 30, 'bold')).pack()

		asset = Image.open("images/postgresql.png")
		image_resized = asset.resize((160, 120), Image.ANTIALIAS)
		img = ImageTk.PhotoImage(image_resized)
		logo = Label(self.main, image=img, width=160, height=120)
		logo.image = img
		logo.pack()

		self.render_description()
		self.render_app_navigation()
		self.render_external_sources()

		footer = Frame(self.main, bg="#065fd4")
		Label(footer, text="Created by Oren Holiš · 2022", bg="#065fd4", font=('Arial', 14, 'bold')).pack(fill=BOTH)
		Label(footer, text="As a school project", bg="#065fd4", font=('Arial', 10, 'bold')).pack(fill=BOTH)

		footer.pack(padx=10, pady=5, fill=BOTH)

	def render_description(self):
		Label(self.main,
	      text="""
		      In this application you can manage your databases, tables and their data. All at one place.
		      Here from home screen you can go explore appplication itself or read some informations first
		      and tips where to look when you need something. Only requirements you will need are PostgreSQL
		      database with one super which is at the start of application prefilled as a postgres. This user 
		      can be changed on the Application user form screen. On which you can get by clicking on a link at
		      the bottom of the database list.
	      """,
	      anchor=W
	    ).pack(fill=X)

	def render_app_navigation(self):
		navigation = Frame(self.main)

		Label(navigation, text="Select screen where do you want to go.").pack()

		self.create_link_field(
			navigation,
			"Create user",
			"On this screen you can create user which will not belong to any database",
			"create_user")
		self.create_link_field(
			navigation,
			"Connect to db",
			"On this screen you can connect database client to any database you have rights to connect",
			"database_connect")
		self.create_link_field(
			navigation,
			"Create db",
			"On this screen you can create database",
			"database_create")

		navigation.pack()

	def render_external_sources(self):
		sources = Frame(self.main)

		Label(sources, text="Application resources", font=("arial", 22, "bold")).pack(fill=X)
		Label(sources,
		      text="""
	        In this section are external sources where you should look when you need some help or need sources from
	        which was this application created.
            """
		      ).pack(fill=X)

		def create_link(title, link_text, desc):
			frame = Frame(sources)
			Label(frame, text=title, font=("arial", 15, "bold"), anchor=W).pack(fill=X)
			link = Label(frame, text=link_text, font=("arial", 13, "bold"), fg="blue", anchor=W)
			link.bind("<Button-1>", lambda e: webbrowser.open_new_tab(link_text))
			link.pack(padx=20, fill=X)
			Label(frame, text=desc, anchor=W).pack(padx=20, fill=X)
			frame.pack(fill=X)

		Label(sources, text="Sources where to look for some clue", font=("arial", 18, "bold")).pack()
		create_link("PostgreSQL",
		            "https://www.postgresql.org/",
		            """Official distribution of PostgreSQL database""")
		create_link("PostgreSQL documentation",
		            "https://www.postgresql.org/files/documentation/pdf/14/postgresql-14-A4.pdf",
		            """Official PostgreSQL documentation""")
		create_link("PostgreSQL youtube tutorial",
		            "https://www.youtube.com/watch?v=qw--VYLpxG4",
		            """One of the best youtube tutorials""")
		create_link("PostgreSQL tutorial",
		            "https://www.postgresqltutorial.com/",
		            """Here you can study queries and database management""")
		create_link("Stackoverflow",
		            "https://stackoverflow.com/",
		            """Best place where to find clues for anything""")
		create_link("PostgreSQL syntax",
		            "https://www.postgresql.org/docs/7.0/syntax525.htm",
		            """PostgreSQL syntax""")

		Label(sources, text="Sources with which was this app created", font=("arial", 18, "bold")).pack()

		create_link("Python 3.9",
		            "https://devdocs.io/python~3.9/",
		            """Official python 3.9 documentations""")
		create_link("Tkinter",
		            "http://tkdocs.com/",
		            """Official tkinter documentation""")
		create_link("PostgreSQL in python",
		            "https://www.postgresqltutorial.com/postgresql-python/",
		            """Implementation of postgresql in python""")

		sources.pack(fill=BOTH, padx=15)

	def create_link_field(self, parent, text, description, screen_name, position="left"):
		field = Frame(parent, width=300)
		field.configure(borderwidth=3, bg="#8ec3e6")
		link = Label(field, text=text, bg="#8ec3e6", font=("arial", 16, "bold"))
		link.bind("<Button-1>", lambda e, name=screen_name: self.change_screen(name))
		link.pack()
		Label(field, text=description, bg="#8ec3e6", font=("arial", 13), wraplength=160, justify="center").pack()
		field.pack(side=position, padx=20, pady=30)
