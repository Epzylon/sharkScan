from json import loads, dumps
from pymongo import MongoClient as connect
from nmap2json import NmapScanToJson as nmapParser


class CantOpenDB(Exception):
	def __init__(self,db):
		self.db = db
		print("Can't open db: " + self.db)

class mdb(object):
	def __init__(self,dbstring="mongodb://localhost"):
		self.dbstring = dbstring
		self.db = "sharkScan"
		self.collection = "scans"
		self.projection = { "_id": 0 }


	def connect(self):
		try:
			#Mongo connection
			self.connection = connect(self.dbstring)
			self._db = self.connection[self.db]
			self._collection = self._db[self.collection]
		except:
			raise CantOpenDB()
		else:
			return True

	def disconnect(self):
		self.connection.close()

	def get_SavedScans(self,from_date=None,to_date=None):
		''' Return saved scans optionally filter by date '''


		#other wise if a date range was specified:
		if from_date != None and to_date != None:
			query = {"$and":[{"stats.start_time":{"$gte":from_date}},{"stats.start_time":{"$lte":to_date}}]}

		elif from_date != None and to_date == None:
			query = {"stats.start_time":{"$gte":from_date}}

		elif from_date == None and to_date != None:
			query = {"stats.start_time":{"$lte":to_date}}

		elif from_date == None and to_date == None:
			#If there is no date filter get all the scans
			query = {}


		projection = { "_id": 0, "name": 1,"stats":1}
		cursor = self._collection.find(query,projection)
		total = {"scans":[]}
		for c in cursor:
		 	total['scans'].append(c)

		return(dumps(total))


	def get_RunningScans(self):
		pass

	def get_hostInScan(self,address):
		pass

	def get_ScanByName(self,name):
		query = { "name": name }
		return(dumps(self._collection.find_one(query,self.projection)))


class uploadScan(object):
	def __init__(self,xml,db="mongodb://localhost"):
		self.xml = xml
		self.db = db
		self.json = ""
		filename = self.xml.split('/')[-1]
		point = filename.rfind('.')
		self.name = filename[:point]
		print(self.name)

	def __connect(self):
		#By default connect to localhost
		try:
			#Mongo connection
			self.mongo = connect(self.db)
			#DB
			self.shark = self.mongo.sharkScan
			#Collection
			self.scans = self.shark.scans
		except:
			raise CantOpenDB()

	def __parse(self):
		parser = nmapParser(self.xml)
		parser.set_name(self.name)
		self.json = parser.get_json()


	def upload(self):
		self.__connect()
		self.__parse()
		return(self.scans.insert(self.json))

	def test_db(self):
		try:
			self.__connect()
		except CantOpenDB:
			print("Not possible make the connection")
			return False
		else:
			return True