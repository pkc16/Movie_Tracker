# Movies watched tracking application

from tkinter import *
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import MovieTrackerDBClass

class MovieTracker(object):
	def __init__(self, window):
		self.window = window
		self.window.wm_title("Watched Movies Tracker")
		self.classDB = MovieTrackerDBClass.MovieTracker_DB('Movie_Tracker')
		self.ActorsInMovieWidgetList = []
		self.ActorsInMovieWidgetListRoot = []
		self.MovieActorOIDList = []
		self.windowTypeRoot = "root"
		self.windowTypeActorAssoc = "actor_assoc"
		self.create_fields()


	def on_actor_window_close(self, window):
		# clear out the widget list
		if len(self.ActorsInMovieWidgetList) > 0:
			self.ActorsInMovieWidgetList.clear()
			self.MovieActorOIDList.clear()


	def get_formatted_name(self, fname, mname, lname):
		# return actor's name (include middle name if it exists)
		formattedname = ''
		if mname == '':
			formattedname = fname + ' ' + lname
		else:
			formattedname = fname + ' ' + mname + ' ' + lname

		return formattedname


	def execute_sql(self, window, sqlstatement):
		results, rowcount, columnList = self.classDB.execute_sql(sqlstatement.strip())
		
		# convert the column list to a string
		columnStr = ', '.join(columnList)

		formattedresults = ''
		for i, result in enumerate(results):
			if i > 0:
				# use slice to drop the first and last characters, which are "(" and ")" since original result is a tuple
				formattedresults = formattedresults + '\n' + ''.join(str(result)[1:-1])
			else:
				formattedresults = ''.join(str(result)[1:-1])

		self.result.delete(1.0, END)
		self.result.insert('insert', columnStr + '\n' + formattedresults)

		stmtType = sqlstatement[:6]
		if stmtType.upper() == 'SELECT':
			self.lblrowcount = Label(window, text="Number of records: " + str(rowcount))
			self.lblrowcount.grid(row=5, column=1, sticky=W)
		else:
			self.lblrowcount.grid_forget()

			# refresh the genre optionmenu in case the table got changed
			self.genre.grid_forget()
			self.genreOptions = self.classDB.get_genre_list()
			self.genreVar = StringVar(self.window)
			self.genre = OptionMenu(self.window, self.genreVar, *self.genreOptions.keys())
			self.genre.config(width=20, anchor='w', takefocus=1)	# takefocus=1 allows optionmenu to be tab order enabled
			self.genre.grid(row=1, column=2)


	def clear_sqlwindow(self):
		self.sqlentry.delete(1.0, END)
		self.result.delete(1.0, END)
		self.lblrowcount.grid_forget()


	def get_full_listing(self, window):
		# get sql to return all movies and actors associated with each movie
		self.clear_sqlwindow()
		sql = self.classDB.get_full_listing_sql()
		self.sqlentry.insert(END, sql)
		self.execute_sql(window, sql)


	def open_sql_window(self):
		sqlwindow = Tk()
		sqlwindow.title('SQL Window')
		sqlwindow.geometry("750x650")

		lbldummycol = Label(sqlwindow, width=5, text="")
		lbldummycol.grid(row=0, column=0)
		lblsql = Label(sqlwindow, text="Enter SQL:")
		lblsql.grid(row=0, column=1, sticky=W)
		self.sqlentry = Text(sqlwindow, height=10, width=70)
		self.sqlentry.grid(row=1, column=1)
		lbldummyrow = Label(sqlwindow, text="")
		lbldummyrow.grid(row=2, column=0)
		self.lblresult = Label(sqlwindow, text="Results:")
		self.lblresult.grid(row=3, column=1, sticky=W)
		self.result = ScrolledText(sqlwindow, width=70, height=20, wrap=WORD)
		self.result.grid(row=4, column=1, padx=10)
		self.lblrowcount = Label(sqlwindow, text="")
		self.lblrowcount.grid(row=5, column=1, sticky=W)

		btnExecute = Button(sqlwindow, width=10, text="Execute", command=lambda: self.execute_sql(sqlwindow, self.sqlentry.get("1.0", "end-1c")))
		btnExecute.grid(row=1, column=2)
		btnFullListing = Button(sqlwindow, width=10, text="Full Listing", command=lambda: self.get_full_listing(sqlwindow))
		btnFullListing.grid(row=2, column=2)
		btnClear = Button(sqlwindow, width=10, text="Clear", command=self.clear_sqlwindow)
		btnClear.grid(row=3, column=2)
		btnExit = Button(sqlwindow, width=10, text="Exit", command=sqlwindow.destroy)
		btnExit.grid(row=4, column=2)


	def open_actor_association_window(self):
		if not self.lblmovieID.cget("text"):
			messagebox.showerror("Movie not specified","Search for a movie first.")
			return

		entryWindow = Tk()
		entryWindow.title(f'Add/Delete Actors for {self.movie.get()}')
		entryWindow.geometry("600x300")
		entryWindow.protocol("WM_DELETE_WINDOW", self.on_actor_window_close(entryWindow))

		# Label data fields
		movie = Label(entryWindow, text=self.movie.get())
		movie.grid(row=0, column=1, columnspan=3, padx=20, pady=(10,0), sticky=W)
		year = Label(entryWindow, text=self.year.get())
		year.grid(row=1, column=1, padx=20, sticky=W)
		duration = Label(entryWindow, text=self.duration.get())
		duration.grid(row=2, column=1, padx=20, sticky=W)
		movieID = Label(entryWindow, text=self.lblmovieID.cget("text"))

		# Label fields
		lblmovie = Label(entryWindow, text="Movie Title:")
		lblmovie.grid(row=0, column=0, pady=(10,0), sticky=E)
		lblyear = Label(entryWindow, text="Year:")
		lblyear.grid(row=1, column=0, sticky=E)
		lblduration = Label(entryWindow, text="Duration:")
		lblduration.grid(row=2, column=0, sticky=E)
		lblblank = Label(entryWindow, text='')
		lblblank.grid(row=3, column=0)

		# create fields for actor data entry
		lblactor = Label(entryWindow, text="Add Actor:")
		lblactor.grid(row=5, column=0, sticky=W)
		lblactorfname = Label(entryWindow, text="First Name")
		lblactorfname.grid(row=5, column=1, sticky=W)
		lblactormname = Label(entryWindow, text="Middle Name")
		lblactormname.grid(row=5, column=2, sticky=W)
		lblactorlname = Label(entryWindow, text="Last Name")
		lblactorlname.grid(row=5, column=3, sticky=W)

		self.actorfname = Entry(entryWindow, width=15)
		self.actorfname.grid(row=6, column=1, sticky=W)
		self.actormname = Entry(entryWindow, width=15)
		self.actormname.grid(row=6, column=2, sticky=W)
		self.actorlname = Entry(entryWindow, width=15)
		self.actorlname.grid(row=6, column=3, sticky=W)

		btnAddActor = Button(entryWindow, text="Add Actor to Movie", width=20, command=lambda: self.insert_actor_record(entryWindow, self.actorfname.get(), self.actormname.get(), self.actorlname.get(), movieID.cget("text")))
		btnAddActor.grid(row=6, column=4, padx=15)

		lbladdedactors = Label(entryWindow, text="ID:")
		lbladdedactors.grid(row=7, column=0)

		self.deleteID = Entry(entryWindow, width=5)
		self.deleteID.grid(row=7, column=3, sticky=E)
		btnDeleteActor = Button(entryWindow, text="Remove Actor from Movie", width=20, command=lambda: self.remove_actor_from_movie(entryWindow, self.deleteID.get()))
		btnDeleteActor.grid(row=7, column=4) 
		btnExit = Button(entryWindow, text="Exit", width=20, command=entryWindow.destroy)
		btnExit.grid(row=8, column=4)

		# get actors associated with movie and display them
		actors = self.get_actors_for_movie(movieID.cget("text"))
		self.display_actors_for_movie(entryWindow, actors, self.windowTypeActorAssoc)

		# entryWindow.focus_force()
		# self.actorfname.focus()


	def get_actors_for_movie(self, movieID):
		# get the actors associated with a movie
		actors = self.classDB.get_actors_for_movie(movieID)

		# note: above function returns the oid and the actor's name
		return actors


	def display_actors_for_movie(self, window, actors, windowtype):
		# display the actors associated with a movie

		# clear out the widgets from the window and the list
		if windowtype == self.windowTypeRoot:
			for widget in self.ActorsInMovieWidgetListRoot:
				widget.grid_forget()
			self.ActorsInMovieWidgetListRoot.clear()
		else:
			for widget in self.ActorsInMovieWidgetList:
				widget.grid_forget()
			self.ActorsInMovieWidgetList.clear()

		self.MovieActorOIDList.clear()

		if actors == []:
			return
		
		numActors = len(actors)
		if windowtype == self.windowTypeRoot:
			startingGridRow = 5
		else:
			startingGridRow = 8

		for x in range(numActors):
			for y in range(2):
				if y == 0:
					if windowtype == self.windowTypeRoot:
						# don't need to do anything
						pass
					else:
						lblID = Label(window, text=actors[x][0])
						lblID.grid(row=x + startingGridRow, column=y)
						self.ActorsInMovieWidgetList.append(lblID)

					self.MovieActorOIDList.append(actors[x][0])
				else:
					lblFullName = Label(window, text=self.get_formatted_name(actors[x][1], actors[x][2], actors[x][3]))
					lblFullName.grid(row=x + startingGridRow, column=y, sticky=W)
					if windowtype == self.windowTypeRoot:
						self.ActorsInMovieWidgetListRoot.append(lblFullName)
					else:
						self.ActorsInMovieWidgetList.append(lblFullName)


	def search_movie(self, title):
		# search for movie
		
		result = self.classDB.search_movie(title.strip())

		if result:
			#self.year.grid_forget()
			self.year.delete(0, END)
			self.year.insert(0, result[0][2])
			self.duration.delete(0, END)
			self.duration.insert(0, result[0][3])
			self.genreVar.set(result[0][4])
			self.lblmovieID.grid_forget()
			self.lblmovieID = Label(self.window, text=result[0][0])

			# overwrite the movie title with that from the DB to get the titlecase correct
			self.movie.delete(0, END)
			self.movie.insert(0, result[0][1])

			# get any actors associated with movie
			actors = self.classDB.get_actors_for_movie(self.lblmovieID.cget("text"))

			actorSectionLabel = Label(self.window, text="Actors:")
			actorSectionLabel.grid(row=4, column=0, padx=10, sticky=E)

			if actors == []:
				self.lblactorsInMovie.grid_forget()
				self.lblactorsInMovie = Label(self.window, text='')
				self.lblactorsInMovie.grid(row=4, column=1, sticky=W)

				for widget in self.ActorsInMovieWidgetListRoot:
					widget.grid_forget()

			else:
				self.display_actors_for_movie(self.window, actors, self.windowTypeRoot)
		
		else:
			if self.movie.get():
				messagebox.showwarning("No matching results", f"{self.movie.get()} was not found.")
			else:
				messagebox.showerror("Movie not specified", "Enter a movie to search.")

			# clear out the widgets from the window and the list
			self.clear_fields()


	def update_movie_record(self):
		# update record in Movie table
		
		if not self.movie.get():
			messagebox.showerror("Movie not specified","Search for a movie first.")
			return
		elif not self.year.get().strip().isdigit():
			messagebox.showerror("Year invalid", "The Year must be numeric.")
			return
		elif not self.duration.get().strip().isdigit():
			messagebox.showerror("Duration invalid", "The Duration must be numeric.")
			return

		# get the value of the genre	
		genreKey = self.genreVar.get()
		genreVal = self.genreOptions.get(genreKey)

		dataDict = {
			"title": self.movie.get().strip(),
			"year": self.year.get().strip(),
			"duration": self.duration.get().strip(),
			"genreID": genreVal,
			"movieID": self.lblmovieID.cget("text")
		}
		
		resp = self.classDB.update_movie_record(dataDict)
		if resp == 1:
			messagebox.showinfo("Movie updated", "The movie was successfully updated.")


	def insert_movie_record(self):
		# insert record into Movie table 
		
		if not self.movie.get():
			messagebox.showerror("Movie not specified", "Enter the Movie Title.")
			return

		if self.year.get().strip() == '':
			pass
		elif not self.year.get().strip().isdigit():
			messagebox.showerror("Year invalid", "The Year must be numeric.")
			return

		if self.duration.get().strip() == '':
			pass
		elif not self.duration.get().strip().isdigit():
			messagebox.showerror("Duration invalid", "The Duration must be numeric.")
			return

		# get the value of the genre	
		genreKey = self.genreVar.get()
		genreVal = self.genreOptions.get(genreKey)

		dataDict = {
			"title": self.movie.get().strip(),
			"year": self.year.get().strip(),
			"duration": self.duration.get().strip(),
			"genreID": genreVal
		}

		movieID = self.classDB.insert_movie_record(dataDict)
		if movieID == 0:
			messagebox.showinfo("Movie Found", "The movie already exists in the database.")
			return
		else:
			messagebox.showinfo("Movie Inserted","Movie was successfully inserted.")
			self.lblactorsInMovie.grid_forget()
			self.lblmovieID = Label(self.window, text=str(movieID))
			for widget in self.ActorsInMovieWidgetListRoot:
				widget.grid_forget()

			self.ActorsInMovieWidgetListRoot.clear()
			self.MovieActorOIDList.clear()


	def remove_movie_record(self):
		# delete record from Movie table
		if len(str(self.lblmovieID.cget("text"))) > 0:
			resp = messagebox.askquestion("Delete Movie?", f"Do you want to delete the following movie?\n\n{self.movie.get()}")
			if resp == "no":
				return
			
			rtn = self.classDB.delete_movie(self.lblmovieID.cget("text"))
			if rtn == 1:
				messagebox.showinfo("Movie Deleted","Movie was successfully deleted.")
				self.clear_fields()
	
		else:
			messagebox.showerror("Delete Movie","Search for a movie first.")


	def insert_actor_record(self, editWindow, fname, mname, lname, movieID):
		# insert record into Actor table
		if fname == "" or lname == "":
			messagebox.showerror("Actor not specified", "Enter the actor's name.")
			editWindow.focus_force()
			return

		dataDict = {
				"fname": fname.strip(),
				"mname": mname.strip(),
				"lname": lname.strip()
			}

		newActorID = self.classDB.insert_actor_record(dataDict)

		if newActorID > 0:
			self.classDB.insert_movie_actor_record(movieID, newActorID)

			# redraw the actor section of the window
			actors = self.get_actors_for_movie(movieID)
			self.display_actors_for_movie(editWindow, actors, self.windowTypeActorAssoc)

			# clear out entry fields
			self.actorfname.delete(0, END)
			self.actormname.delete(0, END)
			self.actorlname.delete(0, END)

			self.actorfname.focus()
		else:
			messagebox.showinfo("Actor already added to movie", "Actor is already associated with the movie.")
			editWindow.focus_force()


	def update_actor_record(self, editWindow, fname, mname, lname, actorID):
		# update record in Actor table
		
		if not lname or not fname:
			messagebox.showerror("Actor not specified", "Enter the actor's name.")
			return
		else:
			dataDict = {
				"fname": fname.strip(),
				"mname": mname.strip(),
				"lname": lname.strip(),
				"actorID": actorID
			}

			self.classDB.update_actor_record(dataDict)


	def remove_actor_from_movie(self, window, movie_actor_OID):
		# delete record from Movie_Actor table, and from Actor table if necessary
		if movie_actor_OID == "":
			messagebox.showerror("ID Missing", "Enter the ID of the actor to remove from the movie.")
			window.focus_force()
			return

		if not movie_actor_OID.isnumeric():
			messagebox.showerror("ID Invalid", "ID entered is invalid.\nEnter the ID of the actor to remove from the movie.")
			self.deleteID.delete(0, END)
			window.focus_force()
			return

		if int(movie_actor_OID) not in self.MovieActorOIDList:
			messagebox.showerror("ID Invalid", "The ID is not associated with the movie.\nEnter a valid ID.")
			self.deleteID.delete(0, END)
			window.focus_force()
			return

		resp = messagebox.askquestion("Remove Actor from Movie?", "Do you want to delete the actor from the movie?")
		window.focus_force()
		if resp == "no":
			return

		# remember the movie ID
		movieID = self.classDB.get_movie_id_using_movie_actor_oid(movie_actor_OID)
		rtn = self.classDB.remove_actor_from_movie(movie_actor_OID)

		if rtn == 1:
			actors = self.get_actors_for_movie(movieID)
			self.display_actors_for_movie(window, actors, self.windowTypeActorAssoc)

			# clear out the entry field
			self.deleteID.delete(0, END)


	def clear_fields(self):
		self.movie.delete(0, END)
		self.year.delete(0, END)
		self.duration.delete(0, END)
		#self.genreVar.set(self.genreOptions[0])
		self.genreVar.set('')
		self.lblmovieID.grid_forget()

		for widget in self.ActorsInMovieWidgetListRoot:
			widget.grid_forget()

		self.ActorsInMovieWidgetListRoot.clear()
		self.MovieActorOIDList.clear()
		self.movie.focus()


	def export_db(self):
		rtn = self.classDB.export_db()
		if rtn > 0:
			messagebox.showinfo("Export", "Database successfully exported to file.")
		else:
			messagebox.showerror("Export", "Error occurred trying to export.")


	def copy_db(self):
		rtn = self.classDB.create_db_copy()
		if rtn > 0:
			messagebox.showinfo("Copy DB", "Database successfully copied.")
		else:
			messagebox.showerror("Copy DB", "Error occurred trying to copy database.")


	def create_fields(self):
		# Entry fields
		self.movie = Entry(self.window, width=50)
		self.movie.grid(row=0, column=1, columnspan=2, padx=20, pady=10, sticky=W)
		self.year = Entry(self.window, width=10)
		self.year.grid(row=1, column=1, padx=20, sticky=W)

		self.genreOptions = self.classDB.get_genre_list()
		self.genreVar = StringVar(self.window)
		self.genre = OptionMenu(self.window, self.genreVar, *self.genreOptions.keys())
		self.genre.config(width=20, anchor='w', takefocus=1)	# takefocus=1 allows optionmenu to be tab order enabled
		self.genre.grid(row=1, column=2)

		self.duration = Entry(self.window, width=10)
		self.duration.grid(row=2, column=1, padx=20, sticky=W)

		# Label fields
		self.lblmovie = Label(self.window, text="Movie Title:")
		self.lblmovie.grid(row=0, column=0, padx=10, pady=10, sticky=E)
		self.lblyear = Label(self.window, text="Year:")
		self.lblyear.grid(row=1, column=0, padx=10, sticky=E)
		self.lblduration = Label(self.window, text="Duration:")
		self.lblduration.grid(row=2, column=0, padx=10, sticky=E)
		self.lblmovieID = Label(self.window, text="")
		self.lblactorsInMovie = Label(self.window, text='')
		self.lblactorsInMovie.grid(row=4, column=1, sticky=W)

		# Buttons
		btnSearchMovie = Button(self.window, text="Search Movie", width=15, command=lambda: self.search_movie(self.movie.get()))
		btnSearchMovie.grid(row=0, column=3)
		btnUpdateMovie = Button(self.window, text="Update Movie", width=15, command=self.update_movie_record)
		btnUpdateMovie.grid(row=1, column=3)
		btnAddMovie = Button(self.window, text="Add Movie", width=15, command=self.insert_movie_record)
		btnAddMovie.grid(row=2, column=3)
		btnAddActor = Button(self.window, text="Add Actor to Movie", width=15, command=self.open_actor_association_window)
		btnAddActor.grid(row=3, column=3)
		btnDeleteMovie = Button(self.window, text="Delete Movie", width=15, command=self.remove_movie_record)
		btnDeleteMovie.grid(row=4, column=3)

		btnClear = Button(self.window, text="Clear", width=15, command=self.clear_fields)
		btnClear.grid(row=0, column=4, padx=10)
		btnSQL = Button(self.window, text="SQL Window", width=15, command=self.open_sql_window)
		btnSQL.grid(row=1, column=4, padx=10)
		btnExport = Button(self.window, text="Export", width=15, command=self.export_db)
		btnExport.grid(row=2, column=4, padx=10)
		btnCopyDB = Button(self.window, text="Copy Database", width=15, command=self.copy_db)
		btnCopyDB.grid(row=3, column=4, padx=10)
		btnExit = Button(self.window, text="Exit", width=15, command=self.window.destroy)
		btnExit.grid(row=4, column=4, padx=10)

		self.movie.focus()


root = Tk()
simple_app = MovieTracker(root)
root.geometry("700x600+300+300")  #(window width x window height + position right + position down)

root.mainloop()