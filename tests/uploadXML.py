#!env python
#Sample script to parse and upload an nmap xml
import sys
from sharkDB.mdbdriver import uploadScan

upload = uploadScan(sys.argv[1])
upload.test_db()
upload.upload()