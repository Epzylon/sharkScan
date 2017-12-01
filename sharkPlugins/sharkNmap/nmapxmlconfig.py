#############
# XML Parser config object
#############

class NmapConfig(object):
	''' XML Config variables object '''
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
	x_runstats = './runstats'
	x_finished = x_runstats + '/finished'

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

	#Scan attrib
	scan_start = 'start'
	scan_time = 'time'
	scan_elapsed = 'elapsed'
	scan_summary = 'summary'
	scan_exit = 'exit'