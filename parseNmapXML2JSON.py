#!env python
import sys
from nmap2json import NmapScanToJson as parseNmap

filename = str(sys.argv[1])

try:
	output = parseNmap(filename)
except:
	print("Can't parse the fie " + filename)

print(output.get_json())