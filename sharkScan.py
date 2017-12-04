#!env python
#sharkScan Back End
#use APY.yml as API definition
from json import load
from bottle import route, run, response, request
from sharkDB.mdbdriver import mdb

db = mdb()
db.connect()

response_type = 'application/json'

@route('/api/v1.0/Scans')
def get_scans():
	from_date = request.query.from_date
	to_date = request.query.to_date
	response.content_type = response_type	
	
	if from_date != "" and to_date == "":
		#from_date given
		result = db.get_SavedScans(from_date=from_date)

	elif from_date == "" and to_date != "":
		#to_date given
		result = db.get_SavedScans(to_date=to_date)

	elif from_date != "" and to_date != "":
		#from_date and to_date given
		result = db.get_SavedScans(from_date=from_date,to_date=to_date)

	else:
		#from_date and to_date not given
		result = db.get_SavedScans()

	#Just checking if the result is empty
	if result == None:
		response.status = 404
		return()
	else:
		return(result)

@route('/api/v1.0/Scans', method='POST')
def post_scan():
	#TODO: Check json code inject
	post = load(request.body)
	keys = post.keys()
	if 'name' in keys and 'target' in keys:
		name = post['name']
		target = post['target']
	else:
		response.status = 400
		return({"error":"name and target field are mandatory"})
	
	if 'args' in keys:
		args = post['args']
	else:
		args = None
		
	if 'scheduled_date' in keys:
		scheduled_date = post['scheduled_date']
	else:
		scheduled_date = None
		
	if 'type' in keys:
		scan_type = post['type']
	else:
		scan_type = None

	result = db.SendNewScan(name,target,scan_type,args,scheduled_date)

	if result != False:
		response.status = 202
		return(result)
	else:
		response.status = 418
		return(None)

@route('/api/v1.0/Scans/<name>')
def get_scanByName(name=None):
	#Get the scan selected by Name
	response.content_type = response_type
	result = db.get_ScanByName(name)
	if result != None:
		return(result)
	else:
		response.status = 404
		return(None)
	

@route('/api/v1.0/Scans/<name>/<address>')
def get_hostScanAddress(name,address):
	#Get the host in a particular scan
	response.content_type = response_type
	result = db.get_hostInScan(address, name)
	if result != None:
		return(result)
	else:
		response.status = 404
		return

run(host='localhost',port=9898)
