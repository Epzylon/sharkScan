from time import time, sleep
from pkgutil import iter_modules as find_modules
from pydoc import locate
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
            result = self.db.get_PostedScanByName(name)
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
    #Dictionary for loaded plugins
    #format: sharker.plugins.update{"pluginName":Object}
    plugins = {}
    
    #Array with plugins asociated with their scans types
    scan_types = []
    
    plugin_types = []
    
    defautl_type = "os-scan"
    
    def __init__(self, db):
        #Min time to fetch (in minutes)
        self.min_fetch = 1
        self.db = db        
        self.verbose = True
        
        self._load_all_plugins()
    
    def _fetch_new(self):
        news = self.db.get_NewScans()
        if news != None:
            return(news)
        else:
            return(None)
    
    def _fetch_finished(self):
        finished = self.db.get_FinishedScans()
        if finished != None:
            if len(finished) > 0:
                return(finished)
            else:
                return([])
        
    def _find_plugins(self):
        if self.verbose:
            print("Searching plugins:")
        self.plugins_found = [module for _, module, _ in find_modules(['sharkPlugins'])]
        self.plugins_found.remove('genericObjects')
        if self.verbose:
            for plugin in self.plugins_found:
                print("\tPlugin found: " + plugin)
           
    def _load_plugin(self, pluginName):
        if self.verbose:
            print("\tLoading plugin: " + pluginName)
        try:
            #Loading the class for the plugin
            plugin_class = locate("sharkPlugins."+pluginName+".command.p_scan")
            
            #Creating the object from the class loaded
            plugin_object = plugin_class()
            
            #Updating the plugins available on the sharker class
            #loading the plugin object on the dictionary
            sharker.plugins.update({pluginName:plugin_object})
            
            #Then we search the supported types of scans for the plugin
            types = [p.name for p in plugin_object.supported_types]
            
            #and update the sharker class with the dictionary of plugin:types
            sharker.plugin_types.append({pluginName:types})
            sharker.scan_types.extend(types)
        except Exception:
            print("\tNot possible load " + pluginName)
    
    def _load_all_plugins(self):
        self._find_plugins()
        print("Loading all plugins:")
        for plugin in self.plugins_found:
            self._load_plugin(plugin)
    
    def find_plugin(self,scan_type):
        for plugin in self.plugins_found:
            for p in self.plugin_types:
                if scan_type in p[plugin]:
                    return(plugin)
            
    def exec_scan(self,scan):
        
        if self.verbose:
            print("\t\t\tAvailable scans " + str(self.scan_types))
            print("\t\t\tSelected scan type: " + scan['type'])
        
        if 'type' not in scan.keys():
            if self.verbose:
                print("No scan type selected. Using default")
            scan.update({'type':self.defautl_type})
        else:
            if self.verbose:
                print("Scan type selected " + scan['type'])
                
        #Select the plugin
        required_plugin = self.find_plugin(scan['type'])
        plugin = self.plugins[required_plugin]
    
        #Setting the target
        plugin.target = scan['target']
        
        #Setting the parser type
        scan.update({'parser_type':plugin.parser.selected_parser_type})
        
        try:
            self.db.set_ScanAsRunning(scan['name'])
            plugin.run()
        except:
            self.db.set_ScanAsFailed(scan['name'])
            print("Could not run the plugin")
        else:
            self.db.set_ScanAsFinished(scan['name'],
                                       plugin.output_path,
                                       plugin.parser_string,
                                       scan['parser_type'])
  
    def load_scan(self,scan):
        #First we need check if all the attributes are found 
        all_attr_found = True
        attributes = ['name','path','parser','parser_type']
        for attribute in attributes:
            if attribute not in scan:
                all_attr_found = False
        if all_attr_found:
            parser_class = locate(scan['parser'])
            parser = parser_class()
            parser.selected_parser = scan['parser_type']
            parser.set_input_file(scan['path'])
            parser.scan_name = scan['name']
            self.db.set_ScanAsUploading(scan)
            self.db.loadFromJSON(parser.parse())
            self.db.set_ScanAsUploaded(scan)
            
                
    def run(self):
        while True:
            current = time()
            s_current = int(str(current).split('.')[0])
            print("Time: " + str(s_current))
            if self.verbose:
                print("Scans posted:")
                
            #Searching for a new posted Scans
            newScans = self._fetch_new()
            if newScans != None:
                for scan in newScans:
                    if self.verbose:
                        print("\t"+scan['name'])
                    if "scheduled" in scan.keys():
                        if self.verbose:
                            print("\t\tscheduled for: "+str(scan['scheduled']))
                        if scan['scheduled'] != None:
                            #Warning: in case of scans with scheduled key 
                            # set to null, will never be executed
                            scheduled = int(scan['scheduled'])
                            if s_current >= scheduled:
                                print("\t\t" + "Scheduled and will run")
                                self.exec_scan(scan)
                    else:
                        if self.verbose:
                            print("\t\tNot scheduled scan, will run:")
                        self.exec_scan(scan)
                            
            else:
                print('\tNo new scans')    

            #Then search the finished scans
            if self.verbose:
                print("Finished Scans:")
            finished = self._fetch_finished()
            if finished != None:
                for scan in finished:
                    if self.verbose:
                        print("\t"+scan['name'])
                        print("\tLoading scan:")
                    #try:
                    self.load_scan(scan)
                    #except Exception as err:
                    #    print("\t\tCan't load the scan")
                    #    if self.verbose:
                    #        print("\t\t\t"+str(err))
            else:
                print("\tNo finished scans to be loaded")
            
            if self.verbose:
                print("Going to sleep by 1 minute")
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
        
        