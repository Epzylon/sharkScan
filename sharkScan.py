#!env python
#sharkScan Back End
#use APY.yml as API definition
from sharkDB.mdbdriver import mdb
from sharkDaemon.tiburacio import spilberg
from argparse import ArgumentParser

if __name__ == '__main__':
    args = ArgumentParser(description='SharkScan')
    args.add_argument('-m',help="By default mongodb://localhost",dest='host',default='mongodb://localhost')
    args.add_argument('-d',help="Database name, by default sharkScan",dest='db',default='sharkScan')
    args.add_argument('-r',help="Running collection, by default running",dest='runningCollection',default='running')
    args.add_argument('-s',help="Scans collection, by default scans",dest='scanCollection',default='scans')
    args.add_argument('-p',help="Web service port number, by default 8080",dest='port',default='8080')
    args.add_argument('-l',help="Web Listen address, by default localhost",dest='address',default='localhost')
    args.add_argument('-n',help="Not start the web service",dest='webservice',action='store_false')
    args.add_argument('-a',help="Angel Mode, no daemon is started",dest='angel',action='store_false')
    config = args.parse_args()
    
    #lets config the db
    db = mdb(config.host)
    db.db = config.db      
    db.collection = config.scanCollection
    db.run_collection = config.runningCollection
    db.connect()
    #Now lets config the program director
    director = spilberg(db)
    director.port = config.port
    director.host = config.address
    
    #It means, if was requested to not run the webservice
    if not config.webservice:
        director.run_webservice = False
    #It means, if was requested to not run the angel mode
    if not config.angel:
        director.run_daemon = False
    if not config.webservice and not config.angel:
        print("What do you want from me? no webservice, no Angel mode..")
        exit(1)
    else:
        director.run()
