# Parse from XML Nmap to json
import xml.etree.ElementTree as ET
from json import dumps as jsdump
from json import loads as jsload

class CantOpenXML(Exception):
	def __init__(self,filename):
		self.filename = filename
		print("Can't open XML: " + self.filename)

class NmapScanToJson(object):
	#Main tags
	x_host = './host'
	x_address = './address'
	x_ports = './ports'
	x_hostnames = './hostnames'
	x_os = './os'
	x_osmatch = './osmatch'
	x_osclass = './osclass'
	x_hostscript = './hostscript'
	x_status = './status'

	#Host attribs
	h_start = 'starttime'
	h_end = 'endtime'

	#Address attribs
	a_type = 'addrtype'
	a_addr = 'addr'

	#Os attribs
	o_name = 'name'
	o_accuracy = 'accuracy'
	o_class = 'type'
	o_vendor = 'vendor'
	o_family = 'osfamily'
	o_version = 'osgen'
	o_cpe = './cpe'

	#Port attibs
	p_num = 'portid'
	p_proto = 'protocol'
	p_state = 'state'

	#Address type
	ip_type = 'ipv4'

	#Status state
	s_state = 'state'
	s_must = 'up'

	def __init__(self,xml):
		self.xml = xml
		self.jsonDict = {"hosts":[]}
		try:
			self._xml_fd = open(xml,"r")
		except:
			raise CantOpenXML(self.xml)
		else:
			self._parse()

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
			state = port.find(self.p_state).attrib.get(self.p_state)
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
				cpe = possible_class.find(self.o_cpe).text

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


	def _parse(self):
		#xmlObject: contains the xml object of the scan
		xmlObject = ET.fromstringlist(self._xml_fd)
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

	def get_json(self):
		#TODO: this most probably needs a fix
		return(jsload(jsdump(self.jsonDict)))