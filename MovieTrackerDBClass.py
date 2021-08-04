from TrackerDBClass import TrackerDB
import sqlite3
import pandas as pd
import os

# this class inherits from TrackerDB class

class MovieTracker_DB(TrackerDB):
	def __init__(self, database):
		TrackerDB.__init__(self, database)
		self.className = type(self).__name__	# store the name of the class (used for error messages)
		self.databaseName = database + '.db'
		self.exportFileName = database + '_export.csv'
		self.create_database()


	def create_database(self):
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()

			# create tables
			cur.execute("""CREATE TABLE IF NOT EXISTS Movie (
					Title text,
					Year text,
					Duration integer,
					GenreID integer
					)""")

			cur.execute("""CREATE TABLE IF NOT EXISTS Actor (
					Last_Name text,
					First_Name text,
					Middle_Name text
					)""")

			cur.execute("""CREATE TABLE IF NOT EXISTS Movie_Actor (
					MovieID integer,
					ActorID integer
					)""")

			cur.execute("""CREATE TABLE IF NOT EXISTS Genre (
					Genre_Name text
					)""")

			# insert values into Genre table if this is very first time database is being created
			cur.execute("SELECT COUNT(*) FROM Genre")
			results = cur.fetchone()
			if results[0] == 0:
				cur.execute("INSERT INTO Genre VALUES('')")
				cur.execute("INSERT INTO Genre VALUES('Action')")
				cur.execute("INSERT INTO Genre VALUES('Animation')")
				cur.execute("INSERT INTO Genre VALUES('Comedy')")
				cur.execute("INSERT INTO Genre VALUES('Documentary')")
				cur.execute("INSERT INTO Genre VALUES('Drama')")
				cur.execute("INSERT INTO Genre VALUES('Fantasy')")
				cur.execute("INSERT INTO Genre VALUES('Horror')")
				cur.execute("INSERT INTO Genre VALUES('Musical')")
				cur.execute("INSERT INTO Genre VALUES('Sci-Fi')")
				cur.execute("INSERT INTO Genre VALUES('Thriller')")
				cur.execute("INSERT INTO Genre VALUES('Western')")

			conn.commit()
			conn.close()

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.create_database: {error}")
			if conn:
				conn.close()


	def export_db(self):
		# Override the parent class function because need to include associated actors with the movie export
		try:
			conn = sqlite3.connect(self.databaseName)
			df = pd.read_sql_query("SELECT m.oid, Title, Year, Duration, Genre_Name FROM Movie m INNER JOIN Genre g ON g.oid = m.genreID", conn)
	
			# get actors for each movie
			actors = []
			for ind in df.index:
				movie_id = df['rowid'][ind]

				sql = f"""SELECT First_Name ||' '|| IFNULL(Middle_Name, '') || Last_Name AS Name
							 				FROM Movie m
							 				INNER JOIN Movie_Actor ma ON ma.movieID = m.oid
							 				INNER JOIN Actor a ON a.oid = ma.actorID
							 				WHERE m.oid = {movie_id}"""

				df2 = pd.read_sql_query(sql, conn)
				actorStr = ''
				for ind2 in df2.index:
					actorStr = actorStr + ', ' + df2['Name'][ind2]

				if actorStr != '':
					actors.append(actorStr[1:].strip())
				else:
					actors.append('')

			# Now create a column in the dataframe and populate with the actors
			df['Actors'] = actors

			# drop the id column
			df = df.drop('rowid', 1)

			filepath = os.getcwd() + '\\' + self.exportFileName
			df.to_csv(filepath, index=False)

			return 1

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.export_db: {error}")
			if conn:
				conn.close()
			return -1


	# SELECT functions......................................................
	def search_movie(self, title):
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()

			# do a LIKE search and return top result
			cur.execute(f"""SELECT m.oid, Title, Year, Duration, Genre_Name 
							FROM Movie m 
							INNER JOIN Genre g ON g.oid = m.genreID 
							WHERE LOWER(Title) LIKE '{title}%' LIMIT 1"""
						)

			result = cur.fetchall()
			conn.close()
			return result

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.search_movie: {error}")
			if conn:
				conn.close()
			return []


	def get_actors_for_movie(self, movieID):
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()

			cur.execute("""SELECT ma.oid, First_Name, Middle_Name, Last_Name
								FROM Actor act
								INNER JOIN Movie_Actor ma ON ma.ActorID = act.oid
								WHERE ma.MovieID = :movieID""",
						{
							'movieID': movieID
						}
						)

			actors = cur.fetchall()
			conn.close()
			return actors

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.get_actors_for_movie: {error}")
			if conn:
				conn.close()
			return []


	def get_movie_id_using_movie_actor_oid(self, movie_actor_oid):
		# select the movie ID
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()

			cur.execute("""SELECT MovieID FROM Movie_Actor WHERE oid = :ID""",
						{
							'ID': movie_actor_oid
						}
						)
			result = cur.fetchone()
			conn.close()

			if result:
				return result[0]

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.get_movie_id_using_movie_actor_oid: {error}")
			if conn:
				conn.close()
			return 0


	def get_full_listing_sql(self):
		# sql which returns movies with associated actors
		sql = ("SELECT Title, Year, Duration, Genre_Name,\n"
		"First_Name, Last_Name\n"
		"FROM Movie m\n"
		"LEFT JOIN Movie_Actor ma ON ma.movieID = m.oid\n"
		"LEFT JOIN Actor a ON a.oid = ma.actorID\n"
		"LEFT JOIN Genre g ON g.oid = m.genreID\n"
		"ORDER BY Title")

		return sql


	def get_genre_list(self):
		# get the genre types and return as a dictionary
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()

			cur.execute("SELECT oid, Genre_Name FROM Genre ORDER BY Genre_Name")
			records = cur.fetchall()

			genreList = [x[1] for x in records]

			dictGenre = {}
			for i, y in enumerate(records):
				key = y[1]
				value = y[0]
				dictGenre.update({y[1] : y[0]})

			return dictGenre

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.get_genre_list: {error}")
			if conn:
				conn.close()
			return {}


# UPDATE functions........................................................
	def update_movie_record(self, dataDict):
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()

			cur.execute("""UPDATE Movie 
							SET Title = :title, 
								Year = :year, 
								Duration = :duration,
								GenreID = :genreID
							WHERE oid = :movieID""",
						{
							'title': dataDict["title"],
							'year': dataDict["year"],
							'duration': dataDict["duration"],
							'genreID': dataDict["genreID"],
							'movieID': dataDict["movieID"]
						}
						)

			conn.commit()
			conn.close()
			return 1

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.update_movie_record: {error}")
			if conn:
				conn.close()
			return 0


	def update_actor_record(self, dataDict):
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()

			cur.execute("""UPDATE Actor
							SET Last_Name = :lname,
								First_Name = :fname,
								Middle_Name = :mname
							WHERE oid = :id""",
					{
						'lname': dataDict["lname"],
						'fname': dataDict["fname"],
						'mname': dataDict["mname"],
						'id': dataDict["actorID"]
					}
					)

			conn.commit()
			conn.close()
			return 1

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.update_actor_record: {error}")
			if conn:
				conn.close()
			return 0


# INSERT functions........................................................
	def insert_movie_record(self, dataDict):
		movieID = 0
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()

			# check if Movie record already exists
			cur.execute("SELECT COUNT(*) FROM Movie WHERE Title = :title AND Year = :year AND Duration = :duration AND GenreID = :genreID",
						{
							'title': dataDict["title"],
							'year': dataDict["year"],
							'duration': dataDict["duration"],
							'genreID': dataDict["genreID"]
						}
						)

			result = cur.fetchone()

			if result[0] == 0:
				cur.execute("INSERT INTO Movie (Title, Year, Duration, GenreID) VALUES (:title, :year, :duration, :genreID)",
							{
								'title': dataDict["title"],
								'year': dataDict["year"],
								'duration': dataDict["duration"],
								'genreID': dataDict["genreID"]
							}
							)

				conn.commit()
				movieID = cur.lastrowid

			conn.close()
			return movieID

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.insert_movie_record: {error}")
			if conn:
				conn.close()
			return 0


	def insert_actor_record(self, dataDict):
		# insert record into Actor table and if successful, insert record into Movie_Actor table
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()

			# check if Actor record already exists
			cur.execute("SELECT COUNT(*) FROM Actor WHERE Last_Name = :lname AND First_Name = :fname AND Middle_Name = :mname",
						{
							'lname': dataDict["lname"],
							'fname': dataDict["fname"],
							'mname': dataDict["mname"]
						}
						)

			actorCount = cur.fetchone()
			actorID = 0

			if actorCount[0] == 0:
				if dataDict["lname"] or dataDict["fname"]:
					# insert record into Actor table
					cur.execute("INSERT INTO Actor (Last_Name, First_Name, Middle_Name) VALUES (:lname, :fname, :mname)",
							{
								'lname': dataDict["lname"],
								'fname': dataDict["fname"],
								'mname': dataDict["mname"]
							}
							)

					actorID = cur.lastrowid
					conn.commit()
			else:
				# Actor record already exists, so return the id
				cur.execute("SELECT oid FROM Actor WHERE Last_Name = :lname AND First_Name = :fname AND Middle_Name = :mname",
						{
							'lname': dataDict["lname"],
							'fname': dataDict["fname"],
							'mname': dataDict["mname"]
						}
						)
				result = cur.fetchone()
				actorID = result[0]

			conn.close()
			return actorID

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.insert_actor_record: {error}")
			if conn:
				conn.close()
			return 0


	def insert_movie_actor_record(self, movieID, actorID):
		# insert record into Movie_Actor table
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()
			cur.execute("INSERT INTO Movie_Actor (MovieID, ActorID) VALUES (:movieID, :actorID)",
							{
								'movieID': movieID,
								'actorID': actorID
							}
							)
			
			newRecordID = cur.lastrowid

			conn.commit()
			conn.close()
			return newRecordID

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.insert_movie_actor_record: {error}")
			if conn:
				conn.close()
			return 0


# DELETE functions.........................................................
	def remove_actor_from_movie(self, movie_actor_oid):
		# delete record from Movie_Actor table, and from Actor table if necessary
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()

			# get the actor ID first so the record can be deleted if there are no more movies for actor
			cur = conn.cursor()
			cur.execute("""SELECT ActorID FROM Movie_Actor WHERE oid = :movie_actor_id""",
						{
							'movie_actor_id': movie_actor_oid
						}
						)
			actorID = cur.fetchone()

			# Now delete from Movie_Actor table
			cur.execute("""DELETE FROM Movie_Actor WHERE oid = :id""",
						{
							'id': movie_actor_oid
						}
						)

			# Now delete the actor record if there are no more associations to any movies
			cur.execute("""SELECT COUNT(*) FROM Movie_Actor WHERE ActorID = :actorID""",
						{
							'actorID': actorID[0]
						}
						)
			cnt = cur.fetchone()

			if cnt[0] == 0:
				cur.execute("""DELETE FROM Actor WHERE oid = :id""",
						{
							'id': actorID[0]
						}
						)
			
			conn.commit()
			conn.close()
			return 1

		except sqlite3.Error as error:
			print(f"Error occurred in{self.className}.remove_actor_from_movie: {error}")
			if conn:
				conn.close()
			return 0


	def delete_movie(self, movieID):
		# delete record from Movie table, but first delete records from Movie_Actor table
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()

			actors = self.get_actors_for_movie(movieID)
			print(actors)

			for actor in actors:
				print("oid = " + str(actor[0]))
				self.remove_actor_from_movie(actor[0])

			# now delete the movie
			cur.execute("DELETE FROM Movie WHERE oid = :id",
						{
							'id': movieID
						}
						)
			
			conn.commit()
			conn.close()
			return 1

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.delete_movie: {error}")
			if conn:
				conn.close()
			return 0