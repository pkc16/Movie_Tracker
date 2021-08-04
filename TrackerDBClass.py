# This is the base class

import sqlite3
from datetime import datetime
from shutil import copyfile
import os
import pandas as pd

class TrackerDB():
	def __init__(self, database):
		self.className = type(self).__name__	# store the name of the class (used for error messages)
		self.databaseName = database + '.db'
		self.databaseNamePrefix = database
		self.create_database()


	def create_database(self):
		# create the database
		return 1


	def create_db_copy(self):
		try:
			now = datetime.now()
			copyfile(self.databaseName, self.databaseNamePrefix + '_copy_' + str(now.strftime("%m%d%Y_%H%M")) + '.db')
			return 1

		except:
			print(f"Error occurred in {self.className}.create_db_copy: {error}")
			return -1


	# def create_connection(self):
	# 	try:
	# 		self.conn = sqlite3.connect(self.databaseName)
	# 		return 1

	# 	except sqlite3.Error as error:
	# 		print(f"Error occurred in {self.className}.create_connection: {error}")
	# 		return -1


	# def close_connection(self):
	# 	try:
	# 		self.conn.close()
	# 		return 1

	# 	except sqlite3.Error as error:
	# 		print(f"Error occurred in {self.className}.close_connection: {error}")
	# 		return -1


	def execute_sql(self, sql):
		try:
			conn = sqlite3.connect(self.databaseName)
			cur = conn.cursor()
			cur.execute(sql)
			result = cur.fetchall()
			rc = len(result)

			columnList = []

			# check what kind of statement this is by checking first 6 characters of the statement
			stmtType = sql[:6]
			if stmtType.upper() in ('INSERT','UPDATE','DELETE'):
				conn.commit()
				cur.close()

			elif stmtType.upper() == 'SELECT':
				# get the column names involved in the query if a SELECT was executed
				columnList = [tuple[0] for tuple in cur.description]

			conn.close()
			return result, rc, columnList

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.execute_sql: {error}")
			if conn:
				conn.close()
	
			return [], 0, columnList


	def export_db(self, sql):
		try:
			conn = sqlite3.connect(self.databaseName, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)

			filepath = os.getcwd() + r"\export.csv"

			df = pd.read_sql_query(sql, conn)
			df.to_csv(filepath, index=False)

			conn.close()
			return 1

		except sqlite3.Error as error:
			print(f"Error occurred in {self.className}.export_db: {error}")
			if conn:
				conn.close()

			return -1