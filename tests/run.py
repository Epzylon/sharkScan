#!/bin/python
'''
Created on 14 dic. 2017

@author: epzylon
'''
#from sharkDaemon.tiburacio import sharker
from sharkDaemon.tiburacio import spilberg
from sharkDB.mdbdriver import mdb

if __name__ == '__main__':
    db = mdb()
    db.connect()
    director = spilberg(db)
    director.run()
