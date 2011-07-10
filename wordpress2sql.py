#!/usr/bin/env python
"""
 Wordpress XML export to postgres importer
 
 Importing only actual posts and assuming django created table schema.
 More about that in the README

 kaspars@fx.lv
"""


from optparse import OptionParser
from xml.dom.minidom import parse, parseString
import sys
import os.path

# category id for every imported post
category = 1

usage = "usage: %prog [options] --input <input.xml> --dbname <dbname> --dbuser <dbuser>"
parser = OptionParser(usage=usage)
parser.add_option("-d",action="store_true",dest="debug",default=False,help="Print debbugging messages")
parser.add_option("--input",dest="inputfile",default=None,help="Wordpress export xml file to use")
parser.add_option("--dbname",dest="dbname",default=None,help="Database name")
parser.add_option("--dbuser",dest="dbuser",default=None,help="Database user")
parser.add_option("--dbtable",dest="dbtable",default=None,help="Database table")

(options,args) = parser.parse_args()

if options.inputfile:
    inputfile = options.inputfile
    if not os.path.exists(inputfile):
        print "Input file does not exist"
        sys.exit(1)
else:
    parser.error("You hve to provide an input file")
if options.dbname:
    dbname = options.dbname
else:
    parser.error("You have to provide a database name")
if options.dbuser:
    dbuser = options.dbuser
else:
    parser.error("You have to provide a database user")
if options.dbtable:
    dbtable = options.dbtable
else:
    parser.error("You have to provide a database table")

try:
    import psycopg2
except ImportError:
    print "You need to have python psycopg2 module installed"
    sys.exit(1)

try:
    import dateutil.parser
except ImportError:
    print "You need to have python dateutil module installed"
    sys.exit(1)

def extractElement(elementName,item):
    try:
        pre = item.getElementsByTagName(elementName)[0].firstChild
    except IndexError:
        pre = False
    if pre:
        data = pre.data
    else:
        data = 'none'
    return data 


class dbconn:
    "db connection class"
    def __init__(self,dbname,dbuser):
        self.conn = psycopg2.connect("dbname="+dbname+" user="+dbuser)
        self.cur = self.conn.cursor()
    
    def add_item(self,idcounter,category,pubDate,title,content):
        self.cur.execute("INSERT INTO "+dbtable+" (id,category_id, title, pub_date, entry) VALUES (%s, %s, %s, %s, %s);",(idcounter,category,title,pubDate,content))

    def commit(self):
        self.conn.commit()
    
    def close(self):
        self.cur.close()
        self.conn.close()

def main():
    d  = parse(inputfile)
    # in wordpress export xml blog posts are enclosed in 'item' tags
    # so that is the part we are interested in 
    items = d.getElementsByTagName('item')
    db = dbconn(dbname,dbuser)
    idcounter=1
    for item in items:
        title=extractElement('title',item)
        pubDate=extractElement('pubDate',item)
        pubDate = dateutil.parser.parse(pubDate)
        content=extractElement('content:encoded',item)
        if options.debug:
            print pubDate
            print title
            print content
        db.add_item(idcounter,category,pubDate,title,content)
        idcounter +=1
    db.commit()
    db.close()
    print "May have imported "+str(len(items))+" posts"

if __name__ == "__main__":
    main()

