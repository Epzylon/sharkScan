#===============================================================================
# default class to be used by the plugin engine
#===============================================================================
from shutil import which
#from subprocess import call
from time import time
from pathlib import Path as path
from sharkPlugins.genericObjects import Plugin, ScanType

class scan(Plugin):
    ''' Nmap plugin '''
    def __init__(self):
        ''' plugin constructor '''
        name = "NmapPlugin"
        description = "Nmap base plugin for sharkScan"
        nmap_binary = which('nmap')
        Plugin.__init__(self,name,nmap_binary,description)
        self.version = 0.1
        
        #Output configuration
        self.output_parameter = '-oX'
        folder = '/tmp/sharkScan/nmap/'
        self.output_path = folder + str(int(time())) + '.xml'
        
        #Creating the folder 
        path(folder).mkdir(parents=True,exist_ok=True)
        
        self.__set_supported_types()
    
    def __set_supported_types(self):
        
        #Scan with OS recognition
        osscan = ScanType("os-scan")
        osscan.description = "OS detection" 
        osscan.parmeters = "-O -T4"
        osscan.require_privileges = True
        
        self.supported_types.append(osscan)
    
    def scan_os(self):
        self.set_target("127.0.0.1")
        self.selected_type = 1
        self.run()
        

        
           
        
        
        
        
    