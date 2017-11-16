#!env python
import sys
from nmap2json import NmapScanToJson as parseNmap

filename = sys.argv[1]

try:
	output = parseNmap(filename)
	print(output.get_json())
except:
	print("Can't parse the fie " + filename)

