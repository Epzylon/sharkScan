from json import loads
from pymongo import MongoClient as connect
from nmap2json import NmapScanToJson as nmapParser


class CantOpenDB(Exception):
	def __init__(self,db):
		self.db = db
		print("Can't open db: " + self.db)


class uploadScan(object):
	def __init__(self,xml,db="mongodb://localhost"):
		self.xml = xml
		self.db = db
		self.json = ""

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
		self.json = parser.get_json()

	def upload(self):
		self.__connect()
		self.__parse()
		self.scans.insert(self.json)

	def test_db(self):
		try:
			self.__connect()
		except CantOpenDB:
			print("Not possible make the connection")
			return False
		else:
			return True




