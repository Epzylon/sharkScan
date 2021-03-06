# Parse from XML Nmap to json
import xml.etree.ElementTree as ET
from json import dumps as jsdump
from json import loads as jsload
from sharkPlugins.sharkNmap.nmapxmlconfig import NmapConfig
from sharkPlugins.genericObjects import Parser

class CantOpenXML(Exception):
	def __init__(self,filename):
		self.filename = filename
		print("Can't open XML: " + self.filename)

class NmapScanToJson(Parser,NmapConfig):
	def __init__(self,xml=None):
		if xml != None:
			self.xml = xml
			self.set_input_file(self.xml)
			
		self.scan_name = ""
		self.jsonDict = {"hosts":[]}
		self.parsers_list = ['xml-json']
		self.selected_parser_type = self.parsers_list[0]
		super(NmapScanToJson,self).__init__("NmapParser", self.parsers_list)
		
		

	def __get_status(self,host):
		#get the host status
		status = host.find(self.x_status).attrib.get(self.s_state)
		return(status)

	def __get_addresses(self,host):

		result = {}
		addresses = []

		#Walking over each address of the host
		for address in host.findall(self.x_address):

			#Checking if addr is ipv4 (ip_type)
			addr_type = str(address.attrib.get(self.a_type))

			if addr_type == self.ip_type:
				#Get the ip address
				addr_num = address.attrib.get(self.a_addr)
				addresses.append(addr_num)
				
		#return the address
		if addresses != []:
			result.update({"address":addresses[0]})

		return(result)

	def __get_ports(self,host):

		#Result
		result = {}

		#Just open ports
		tcp_ports = []
		udp_ports = []

		#Walking over each port
		for port in host.find(self.x_ports):
			#Getting the port info
			number = port.attrib.get(self.p_num)
			protocol = port.attrib.get(self.p_proto)
			try:
				state = port.find(self.p_state).attrib.get(self.p_state)
			except:
				state = None
			#Saving open ports
			if state == "open":
				if protocol == "tcp":
					tcp_ports.append(number)
				if protocol == "udp":
					udp_ports.append(number)

		if tcp_ports != []:
			result.update({"tcp_ports": tcp_ports})

		if udp_ports != []:
			result.update({"udp_ports": udp_ports})

		return(result)

	def __get_os(self,host):

		result = {}
		os_matchs = []

		match = host.find(self.x_os)
		if match != None:
			for possible in match.findall(self.x_osmatch):

				#OSMATCH
				name = possible.attrib.get(self.o_name)
				accuracy = possible.attrib.get(self.o_accuracy)

				#OSCLASS
				possible_class = possible.find(self.x_osclass)
				osclass = possible_class.attrib.get(self.o_class)
				vendor = possible_class.attrib.get(self.o_vendor)
				family = possible_class.attrib.get(self.o_family)
				version = possible_class.attrib.get(self.o_version)
				cpe = possible_class.find(self.o_cpe)
				if cpe != None:
					cpe = cpe.text

				os_possible = {
				"name":name,
				"accuracy":accuracy,
				"class":osclass,
				"vendor":vendor,
				"family":family,
				"version":version,
				"cpe":cpe
				}
				os_matchs.append(os_possible)
			if os_matchs != []:
				result.update({"os_match":os_matchs})

		return(result)

	def __get_hostname(self,host):

		result = {}
		hostnames = []

		#Walking over hostnames
		for hostname in host.find(self.x_hostnames):
			name = hostname.attrib.get(self.h_name)
			hostnames.append(name)

		if hostnames != []:
			result.update({"hostnames":hostnames})

		return(result)

	def __get_stats(self,scan):
		#Getting the start time
		start_time = scan.attrib.get(self.scan_start)
		finished = scan.find(self.x_finished)
		end_time = finished.attrib.get(self.scan_time)
		elapsed = finished.attrib.get(self.scan_elapsed)
		summary = finished.attrib.get(self.scan_summary)
		exit_status = finished.attrib.get(self.scan_exit)

		stats = {
		"stats": 
			{
			"start_time":start_time,
			"finish_time":end_time,
			"elapsed":elapsed,
			"summary":summary,
			"exit":exit_status
			}
		}

		return(stats)

	@property
	def _result(self):
		return(self.get_json())
		
	def _parse(self):
		#xmlObject: contains the xml object of the scan
		xmlObject = ET.fromstringlist(self._string_list)
		
		#Setting the stats section
		self.jsonDict.update(self.__get_stats(xmlObject))

		#Setting the scan name
		if self.scan_name != "":
			self.jsonDict.update({"name": self.scan_name})

		#Walking over the xml host by host
		for host in xmlObject.findall(self.x_host):

			if self.__get_status(host) == self.s_must:
				#Dictionary of each host
				hostDict = {}

				hostDict.update(self.__get_addresses(host))
				hostDict.update(self.__get_ports(host))
				hostDict.update(self.__get_os(host))
				hostDict.update(self.__get_hostname(host))
				
				self.jsonDict["hosts"].append(hostDict)
			else:
				continue

	def set_name(self,name):
		self.jsonDict.update({"name":name})
		self._parse()

	def get_json(self):
		self._parse()
		#TODO: this most probably needs a fix
		return(jsload(jsdump(self.jsonDict)))