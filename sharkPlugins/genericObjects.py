from os import system
from pydoc import locate


class NoParserAvailable(Exception):
    '''
    Raised when no parser type is available
    '''
    def __init__(self,selected_parser):
        print("The selected parser is not available: " + str(selected_parser))

class CantOpenFile(Exception):
    '''
    Raised when not possible open the file
    '''
    def __init__(self,file):
        print("Can't open the file: " + file )
    
class ScanType(object):
    def __init__(self,name):
        self.name = name
        self.description = None
        
        #Parameters related to the scan type
        self.parameters = None
        self.require_privileges = False
        self.privileges_prefix = "sudo"

        
    def __str__(self):
        return(self.name + ": " + self.parameters)
    
class Plugin(object):
    '''
    Generic Plugin Object
    '''
    
    #This variable, is set to load the list of
    #plugins and their available scans
    #each plugin should load its name and their 
    #scans types
    found_plugins = {}
    
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
        self.parser_string = None
        
        #Supported types of scans
        self.supported_types = []
        
        #TODO: is an object really needed? should we use just an dictionary?
        #By default we add basic type (just use the basic_args)
        basic_name = self.name.replace(" ","")
        basic = ScanType(basic_name)
        basic.description = "Basic Scan type for " + self.name
        self.supported_types.append(basic)
        
        #Index for the supported_types array
        self.selected_type = 0
        
        #Selected parser
        self.selected_parser_type = None
     
    def set_parser(self,value):
        try:
            parser = locate(value)
            self.parser = parser()
            self.parser_string = value
        except:
            print("Not possible load the parser")
            
    @property
    def selected_type(self):
        return(self._selected_type)
    
    @selected_type.setter
    def selected_type(self,value):
        self._selected_type = value
        self._configure_selected_scan()
                
    @property
    def target(self):
        return(self._target)
    
    @target.setter
    def target(self, value):     
        self._target = value 
        
        #Blanking the args
        #WARNING: this is muggy
        self.args = ""                 
        #Check if there are target parameter to be set
        if self.target_parameter != None:
            self.args = self.args + self.target_parameter
        
        self.args = self.args + self.SEPARATOR + self._target
    
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

    def run(self):
        self._configure_basics()
        system(self.command + self.SEPARATOR + self.args)

class Parser(object):
    ''' 
    Generic parser Objecnt
    '''
    def __init__(self,name,supported_parsers):
        self.name = name
        self.supported_parsers = supported_parsers   
         
    def set_input_file(self,file):
        try:
            self._fd = open(file,"r")
        except:
            raise CantOpenFile(file)
        else:
            self._string_list = self._fd.readlines()
    
    def set_input_string_list(self,string_list):
        self._string_list = string_list
    
    @property
    def selected_parser(self):
        return(self._selected_parser)
    
    @selected_parser.setter
    def selected_parser(self,value):
        if value in self.supported_parsers:
            self._selected_parser = value
        else:
            raise NoParserAvailable(value)    
                                    
    def parse(self):
        return(self._result)

    