#!env python
#sharkScan Back End
#use APY.yml as API definition

from bottle import route, run, request, response
from mdbdriver import mdb

db = mdb()
db.connect()

response_type = 'application/json'



@route('/api/v1.0/Scan')
def get_scan():
	''' Retrieve all the scans saved showing name and stats'''
	name = request.query.name
	date = request.query.date
	if name != "" and date == "":
		response.content_type = response_type
		return(db.get_ScanByName(name))
	elif name != "" and date != "":
		pass
	else:
		response.content_type = response_type
		return(db.get_SavedScans())

# @route('/api/v1.0/Scan/<name>'):
# 	pass

# @route('/api/v1.0/Scan/<name>/<address>'):
#	pass


run(host='localhost',port=9898)