from time import time, sleep
from pkgutil import iter_modules as find_modules
from importlib import import_module
from json import load
from bottle import Bottle, response, request
from threading import Thread

class whiteShark(Bottle):
    def __init__(self,name,db):
        super(whiteShark,self).__init__()
        self.name = name
        self.response_type = 'application/json'
        self.db = db
        self._route_all()
    
    def _route_all(self):
        self.route('/api/v1.0/Scans',callback=self.get_scans)
        self.route('/api/v1.0/Scans',method='POST',callback=self.post_scan)
        self.route('/api/v1.0/Scans/<name>',callback=self.get_scanByName)
        self.route('/api/v1.0/Scans/<name>/<address>',callback=self.get_hostScanAddress)
        
        
    #@route('/api/v1.0/Scans')
    def get_scans(self):
        from_date = request.query.from_date
        to_date = request.query.to_date
        response.content_type = self.response_type    
    
        if from_date != "" and to_date == "":
            #from_date given
            result = self.db.get_SavedScans(from_date=from_date)
        
        elif from_date == "" and to_date != "":
            #to_date given
            result = self.db.get_SavedScans(to_date=to_date)
        
        elif from_date != "" and to_date != "":
            #from_date and to_date given
            result = self.db.get_SavedScans(from_date=from_date,to_date=to_date)
        
        else:
            #from_date and to_date not given
            result = self.db.get_SavedScans()
        
        #Just checking if the result is empty
        if result == None:
            response.status = 404
            return()
        else:
            return(result)

    #@route('/api/v1.0/Scans', method='POST')
    def post_scan(self):
        #TODO: Check json code inject
        post = load(request.body)
        keys = post.keys()
        if 'name' in keys and 'target' in keys:
            name = post['name']
            if self.db.get_ScanByName(name) != None:
                response.status = 409
                return({"error":"Duplicated name"})
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
    
        result = self.db.SendNewScan(name,target,scan_type,args,scheduled_date)
    
        if result != False:
            response.status = 202
            return(result)
        else:
            response.status = 418
            return(None)
    
    #@route('/api/v1.0/Scans/<name>')
    def get_scanByName(self,name=None):
        #Get the scan selected by Name
        response.content_type = self.response_type
        result = self.db.get_ScanByName(name)
        if result != None:
            return(result)
        else:
            response.status = 404
            return(None)
        
    
    #@route('/api/v1.0/Scans/<name>/<address>')
    def get_hostScanAddress(self,name,address):
        #Get the host in a particular scan
        response.content_type = self.response_type
        result = self.db.get_hostInScan(address, name)
        if result != None:
            return(result)
        else:
            response.status = 404
            return  
 
class sharker(object):
    ''' A daemon object to pull and run scans '''
    def __init__(self, db):
        #Min time to fetch (in minutes)
        self.min_fetch = 1
        self.db = db
        self._find_plugins()
    
    def _fetch(self):
        news = self.db.get_NewScans()
        if len(news) > 0:
            return(news)
        else:
            return(None)
        
    def _find_plugins(self):
        self.plugins = [module for _, module, _ in find_modules(['sharkPlugins'])]
        self.plugins.remove('genericObjects')
        
    
    def exec_scan(self,scan):
        if 'type' in scan.keys():
            if scan['type'] in self.plugins:
                try:
                    plugin, scan_type = scan['type'].split('-')
                    module = "sharkPlugins." + plugin + ".command"
                    plugin_module = import_module(module)
                except:
                    print("Can't import the requested plugin")
                    return(1)
                else:
                    if scan_type in plugin_module.supported_types:
                        plugin_module.selected_type(scan_type)
                    
                    plugin_module.target = scan['target']    
                    self.db.set_ScanAsRunning(scan['name'])
                    plugin_module.run()
                                        
            
            
    
    def run(self):
        while True:
            current = time()
            s_current = int(str(current).split('.')[0])
            print("Time: " + str(s_current))
            for scan in self._fetch():
                if "scheduled" in scan.keys():
                    if scan['scheduled'] != None:
                        scheduled = int(scan['scheduled'])
                        if scheduled >= s_current:
                            print("\t" + "Scheduled and will run: " + str(scan['scheduled']))
                            self.exec_scan(scan)
            sleep(60)

class spilberg(object):
    ''' This class is meant to be the director of the shark '''
    
    def __init__(self,db):
        #We need the daemon sharker and the web service
        self._db = db
        self._db.connect()
        self._sharker = sharker(self._db)
        self._whiteshark = whiteShark("sharkScan",self._db)
    
    def run(self):
        #Lets run to threads
        webservice = Thread(target=self._whiteshark.run)
        daemon = Thread(target=self._sharker.run)
        webservice.start()
        daemon.start()
        
        