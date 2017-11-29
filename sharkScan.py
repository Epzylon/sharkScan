#!env python
#sharkScan Back End
#use APY.yml as API definition

from bottle import route, run, response
from sharkDB.mdbdriver import mdb

db = mdb()
db.connect()

response_type = 'application/json'



@route('/api/v1.0/Scans')
def get_scans(from_date=None,to_date=None):
	response.content_type = response_type

	if from_date != None and to_date == None:
		#from_date given
		return(db.get_SavedScans(from_date=from_date))

	elif from_date == None and to_date != None:
		#to_date given
		return(db.get_SavedScans(to_date=to_date))

	elif from_date != None and to_date != None:
		#from_date and to_date given
		return(db.get_SavedScans(from_date=from_date,to_date=to_date))

	else:
		#from_date and to_date not given
		return(db.get_SavedScans())

@route('/api/v1.0/Scans/<name>')
def get_scanByName(name=None):
	#Get the scan selected by Name
	response.content_type = response_type
	return(db.get_ScanByName(name))

@route('/api/v1.0/Scans/<name>/<address>')
def get_hostScanAddress(name,address):
	#Get the host in a particular scan
	response.content_type = response_type
	return(db.get_hostInScan(address,name))

run(host='localhost',port=9898)
