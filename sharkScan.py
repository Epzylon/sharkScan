#!env python
#sharkScan Back End
#use APY.yml as API definition

from bottle import route, run, request, response
from mdbdriver import mdb

db = mdb()
db.connect()

response_type = 'application/json'



@route('/api/v1.0/Scans')
@route('/api/v1.0/Scans/<name>'):
@route('/api/v1.0/Scans/<name>/<address>'):
def get_scan(name=None,address=None,date=None):
	''' Retrieve all the scans saved showing name and stats'''
	
	#When use just /Scans there are uri parameters available:
	# name of the scan
	# date of the scans
	name = request.query.name
	date = request.query.date

	#If only name is specified as uri parameter or query parameter
	if name != None and date == None:
		response.content_type = response_type
		return(db.get_ScanByName(name))

	elif name != None and date == None:
		response.content_type = response_type
		pass

	else:
		#If no parameter was provided
		response.content_type = response_type
		return(db.get_SavedScans())






run(host='localhost',port=9898)