from os import system

class ScanType(object):
    def __init__(self,name):
        self.name = name
        self.description = None
        
        #Parameters related to the scan type
        self.parameters = None
        self.require_privileges = False
        self.privileges_prefix = "sudo"
        
    def __str__(self):
        return(str(self.parameters))
    
    

class Plugin(object):
    '''
    Generic Plugin Object
    '''
    def __init__(self,name,binary,description=None):
        
        #Name of the plugin
        self.name = name
        self.description = description
        self.version = 0
        self.SEPARATOR = " "

        
        #Execution parameters
        self.binary = binary
        self.command = self.binary
        self.args = ""
        self.basic_args = None
        self.target_parameter = None
        self.output_parameter = None
        self.output_path = None
        
        #Supported types of scans
        self.supported_types = []

        
        #TODO: is an object really needed? should we use just an dictionary?
        #By default we add basic type (just use the basic_args)
        basic_name = self.name.replace(" ","")
        basic = ScanType(basic_name)
        basic.description = "Basic Scan type for " + self.name
        self.supported_types.append(basic)
        
        #Index for the supported_types array
        self._selected_type = 0


        
    @property
    def selected_type(self):
        return(self._selected_type)
    
    @selected_type.setter
    def selected_type(self,value):
        self._selected_type = value
        self._configure_selected_scan()
    
    def _configure_selected_scan(self):
        #Check if sudo is required
        if self.supported_types[self.selected_type].require_privileges:
            self.command = self.supported_types[self.selected_type].privileges_prefix + self.SEPARATOR + self.command
        
        #Check if there is additionals parameters on the selected_type
        p = self.supported_types[self.selected_type].parameters
        if  p != None:
            self.args = self.args + self.SEPARATOR + p 

            
    def _configure_basics(self):
        #Check if there are basic args
        if self.basic_args != None:
            self.args = self.basic_args
        
        #Check if there are output parameter to be set
        if self.output_path != None:
            self.args = self.args + self.SEPARATOR + self.output_parameter
        
        self.args = self.args + self.SEPARATOR + self.output_path
        

    def set_target(self, target):                    
        #Check if there are target parameter to be set
        if self.target_parameter != None:
            self.args = self.args + self.target_parameter
        
        self.args = self.args + self.SEPARATOR + target
    
    def run(self):
        self._configure_basics()
        system(self.command + self.SEPARATOR + self.args)
            
        
        

