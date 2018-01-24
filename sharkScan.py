#!env python
#sharkScan Back End
#use APY.yml as API definition
from sharkDB.mdbdriver import mdb
from sharkDaemon.tiburacio import spilberg

if __name__ == '__main__':
    db = mdb()
    db.connect()
    director = spilberg(db)
    director.run()
