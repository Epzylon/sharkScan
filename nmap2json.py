# Parse from XML Nmap to json
import xml.etree.ElementTree as ET

class CantOpenXML(Exception):
	pass

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

	#Host attribs
	h_start = 'starttime'
	h_end = 'endtime'

	#Address attribs
	a_type = 'addrtype'
	a_addr = 'addr'

	#Address type
	ip_type = 'ipv4'

	def __init__(self,xml):
		self.xml = xml
		self.jsonDict = {}
		self.debug = True
		try:
			self._xml_fd = open(xml,"r")
		except:
			raise CantOpenXML

	def __get_addresses(self,host):
		#Walking over each address of the host
		for address in host.findall(self.x_address):

			#Checking if addr is ipv4 (ip_type)
			addr_type = str(address.attrib.get(self.a_type))

			if addr_type == self.ip_type:
				#Get the ip address
				addr_num = address.attrib.get(self.a_addr)
					
				#return the address
				return({"address": addr_num})
					


	def _parse(self):
		#xmlObject: contains the xml object of the scan
		xmlObject = ET.fromstringlist(self._xml_fd)

		#Walking over the xml host by host
		for host in xmlObject.findall(self.x_host):
			#Dictionary of each host
			hostDict = {}

			#Walking over each port
			for port in host.findall(self.ports):

