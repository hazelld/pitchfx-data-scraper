#!/bin/python

import sys
import logging
import re
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import urllib2
import MySQLdb
import datetime

#   Where we get the files from & the names of the files
base_url  = "http://gd2.mlb.com/components/game/mlb/year_"
pitch_ext = "inning/inning_all.xml"
game_ext  = "boxscore.xml"

#   Database info 
db_name              = "mlb_stats"
batter_gameday_table = "gamestats_batter"
pitch_gameday_table  = "gamestats_pitcher"
pitches_table        = "pitches"


#
#
#
#
def data_scrape ( year, month, day ):
    logger   = logging.getLogger(__name__)
    full_url = base_url + str(year) + "/month_0" + str(month) + "/day_0" + str(day) + "/"
    
    #   Attempt to connect to DB
    db = MySQLdb.connect( host="localhost",
                          user="whaze",
                          passwd="",
                          db=db_name )
    cur = db.cursor()

    #
    date = datetime.datetime.strptime(str(year)+"-"+str(month)+"-"+str(day), "%Y-%m-%d")
    logger.info('Got date: ' + date.strftime('%Y-%m-%d'))
            
    #   Get the game links from the page. If there are any 
    #   errors then log it and return from the func
    logger.info("Getting " + full_url)
    links = get_links(full_url, logger)
    
    if links:
        logger.info("Successfully got links")
    else:
        logger.warning("Could not get links...Returning")
        return False
    
    for link in links:
        parse_pitches(full_url +  "gid_" + link + pitch_ext, logger, db, cur, date)
        parse_box(full_url + "gid_" + link + game_ext, logger, db, cur, date)
    

#
#
#
def parse_pitches ( url, logger, db, cur, date ):
    logger.info("Parsing pitches page: " + url)

    try: 
        f = urllib2.urlopen(url)
    except urllib2.URLError as e:
        logger.warning(e.reason)

#
#
#
def parse_box ( url, logger, db, cur, date ):
    logger.info("Parsing boxscore page: " + url)
    
    try: 
        f = urllib2.urlopen(url)
    except urllib2.URLError as e:
        logger.warning(e.reason)
        return False

    # Get all batter tags
    soup   = BeautifulSoup(f, "lxml")     
    batter = soup.find_all('batter')

    # Insert queries
    insert_batter = "insert into " + batter_gameday_table + """
                    (pid, game_date, pa, ab, hits, runs, hr, bb, so, rbi, 1b, 2b, 3b,
                    sb, cs, lob, bo, sac, sf, hbp) values (%s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    logger.info("Attempting to insert into " + batter_gameday_table)

    #
    #
    for b in batter:
        pa = int(b['ab']) +  int(b['sac']) + int(b['bb']) +  int(b['sf']) + int(b['hbp'])
        
        try:
            bo = int(b['bo']) / 100
        except:
            logger.warning("No BO attr...Skipping")
            bo = 0

        data = (int(b['id']), date.strftime('%Y-%m-%d'), int(pa), int(b['ab']),  int(b['h']), 
                int(b['r']), int(b['hr']), int(b['bb']), int(b['so']), int(b['rbi']),0,0,0,
                int(b['sb']), int(b['cs']), int(b['lob']), int(bo), int(b['sac']),
                int(b['sf']), int(b['hbp']) )
        
        print data 

        try:
            cur.execute(insert_batter, data)
            db.commit()
        except MySQLdb.Error as e:
            logger.warning("DB threw error: " + e)
            db.rollback

#
#
#
#
def get_links ( url, logger ):

    try: 
        f = urllib2.urlopen(url)
    except urllib2.URLError as e:
        logger.warning(e.reason)
        return False
    
    # Compile the regex to match links outside of the loop for 
    # performance
    links = []
    regex = re.compile("\"gid_(.*?)\"", re.IGNORECASE)
    
    # Find all links on page and if they are links to games then add to list
    for link in BeautifulSoup(f, "lxml",parse_only=SoupStrainer('a', href=True) ):
        match = regex.findall(str(link))
        if match:
           links.extend(match)
    
    return links

