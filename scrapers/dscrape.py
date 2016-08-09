#!/bin/python

from dscrape import *
from config import *
import sys
import logging
import re
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import urllib2
import MySQLdb
import datetime


#
def init_globs ( year, month, day ):
    global logger
    global db
    global cur
    global date

    logger = logging.getLogger(__name__)
    db     = MySQLdb.connect( host=db_host, user=db_user, passwd=db_passwd, db=db_name )
    cur    = db.cursor()

    try:
        date   = datetime.datetime.strptime(str(year)+"-"+str(month)+"-"+str(day), "%Y-%m-%d")
    except:
        logger.warning('Invalid date range')
        return False
    return True

#
#
#
#
def data_scrape ( year, month, day ):
    
    if init_globs(year, month, day) == False: return False
    logger.debug('Got date: ' + date.strftime('%Y-%m-%d'))

    full_url = base_url + str(year) + "/month_0" + str(month) + "/day_0" + str(day) + "/"
    links = get_links(full_url, logger)
    
    if links:
        logger.debug("Successfully got links")
    else:
        logger.warning("Could not get links...Returning")
        return False
    
    for link in links:
        full_link = full_url + "gid_" + link 
        gid = parse_game (full_link + game_ext, game_table, False)       
        
        print gid
        if gid:
            parse_game_stats(full_link+game_ext_b, 'batter', batter_map, batter_gameday_table, gid)
            parse_pitcher_box(full_link+game_ext, 'pitcher', pitcher_map, pitch_gameday_table, gid)
            #parse_pitches(full_link + pitch_ext, gid)


#
#   Get the game information from the boxscore xml page, and add it to
#   the database. Ensure the game is not already in the database. If
#   it is then return false.
#
def parse_game ( url, db_table, gid):
    logger.debug("Getting information from " + url)
    
    f = get_page(url, logger)
    if f == False: return False

    soup  = BeautifulSoup(f, "lxml")
    query = build_query(box_map + line_map, db_table, gid)

    box  = soup.find('boxscore')
    line = soup.find('linescore')

    data = [date]
    for item in box_map:
        data.append(box[item[1]])

    for item in line_map:
        data.append(line[item[1]])

    if insert_db(query, data) == False:
        return False

    return data[1]

#
#
#
def build_query (db_map, db_table, gid):

    query = "insert into " + db_table + "("
    val_query = " values ("

    query     += "game_date, "
    val_query += "%s," 

    if gid:
        query += "gid, " 
        val_query += "%s,"

    # Build the query
    i = len(db_map)
    for key in db_map:
        query     += key[0]
        val_query += "%s"
        i -= 1
        if i > 0:
             query +=  ","
             val_query += ","
    
    query += ")" + val_query + ")"
    return query




def parse_pitches ( url, gid ):
    logger.info("Parsing pitches page: " + url)
    f = get_page(url, logger)

    soup    = BeautifulSoup(f, "lxml")
    atbat   = soup.find_all('atbat')
    
    query = "insert into " + pitches_table + """ pitch_date, sv_id, pid, bid, gid, pitcher_throws, 
             batter_hits, description, pitch_result, balls, strikes, outs, start_speed, end_speed,
             sz_top, sz_bot, pfx_x, pfx_z, px, pz, x0, y0, z0, vx0, vy0, vz0, ax, ay, az, break_y, 
             break_angle, break_length, pitch_type, type_confidence, zone, nasty, spin_dir, 
             spin_rate values (  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s, 
              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
              %s, %s)"""

    for ab in atbat:
        pitches = ab.find_all('pitch')
        balls, strikes = 0,0

        for p in pitches:
            
            data = ( date, p['sv_id'], ab['pitcher'], ab['batter'], gid, ab['p_throws'],
                     ab['stand'], p['des'], p['type'], balls, strikes, ab['o'], ['start_speed'], 
                     p['end_speed'], p[''],)

    
#
#
#
def parse_game_stats ( url, tag, pmap, db_table, gid):
    logger.debug("Parsing game stats")
    
    f = get_page(url, logger)
    if f == False: return False

    soup  = BeautifulSoup(f, "lxml")
    query = build_query(pmap, db_table, gid)

    tags  = soup.find_all(tag)

    for i in tags:
        data = [ date, gid ]
        for item in pmap:
            try:
                data.append(i[item[1]])
            except:
                data.append('0')
                logger.warning("No Data associated with: " + item[1])
        insert_db (query, data)


#
#
#
def get_page ( url, logger ):
    logger.info("Getting Page: " + url)

    try:
        f = urllib2.urlopen(url)
    except urllib2.URLError as e:
        logger.warning(e.reason)
        return False

    return f



#   Get all the links off of the page:
#       gd2.mlb.com/components/game/mlb/year/month/day/
#   
#   And finds the links for the games that have the following 
#   format:
#   
#   gid_year_mm_dd_team1mlb_team2mlb   
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


#   
#
#
def insert_db (query, data):

    # Attempt to insert, rollback on error
    try:
        cur.execute(query, data)
        db.commit()
    except MySQLdb.Error as e:
        logger.warning("DB threw error: " + str(e))
        db.rollback
        return False
    
    return True
