from time import time
from pkgutil import iter_modules as find_modules
from importlib import import_module

class sharker(object):
    ''' A daemon object to pull and run scans '''
    def __init__(self, db):
        #Min time to fetch (in minutes)
        self.min_fetch = 1
        self.db = db
        self._find_plugins()
    
    def _fetch(self):
        news = db.get_NewScans()
        if len(news) > 0:
            return(news)
        else:
            return(None)
        
    def _find_plugins(self):
        self.plugins = [module for _, module, _ in find_modules(['sharkPlugins'])]
        self.plugins.remove['genericObjects']
        
    
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
        while true:
            current = time()
            s_current = int(str(current).split('.')[0][:-3])
            for scan in self._fetch():
                if "scheduled" in scan.keys():
                    if scan['scheduled'] >= s_current:
                        self.exec_scan(scan)
                        

            
    