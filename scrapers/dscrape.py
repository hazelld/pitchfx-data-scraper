#!/bin/python

from scrapers.config import *
import logging
import re
import os
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from urllib.request import urlopen
import pymysql.cursors
import datetime


#
#
#
def gdt_scrape(arg, source):

    # Init the logger and db connection
    if init_globs(arg) == False: 
        return False

    # Either get the web pages from the website and put in a list of bs4 
    # objects, or open the files on disk into a list of bs4 objects.
    if source == "web":
        xml = get_files_web(arg)
    elif source == "disk":
        xml = get_files_disk(arg)
    else:
        logger.warning("Invalid argument to gdt_scrape: " + source)
        return False

    if xml == False: return False

    # Parse the xml files and add into the db 
    parse(xml, arg)



#
#
#
#
#
def get_files_web(date):
    url = base_url+str(date.year)+"/month_"+'%02d'%date.month+"/day_"+'%02d' % date.day
      
    links = get_links(url)
    if links == False:
        logger.warning("Could not get links on page: " + url)
        return False
    
    games = []
    for link in links:
        full_url    = url + "/gid_" + link 
        games_parsed = {}
        
        for f in xml_files:
            page = get_page(full_url + f)
            if page == False: return False

            games_parsed[f] = BeautifulSoup(page, "lxml")
        
        games.append(games_parsed)

    return games

# 
def get_files_disk(date):
    path = "gd2/year_"+str(date.year)+"/month_"+'%02d'%date.month+"/day_"+'%02d' % date.day
    links= [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    games = []
    for link in links:
        games_parsed = {}
        npath = os.path.join(path, link)

        for f in xml_files:
            try:
                page = open(os.path.join(npath, f), "r")
            except:
                logger.warning("Could not open file: " + os.path.join(npath, f))
                continue
            
            games_parsed[f] = BeautifulSoup(page, "lxml")

        games.append(games_parsed)

    return games


#   This function is used to parse the xml files for each day. It takes a 
#   list that holds each game. Each list item is a dictionary that has the 
#   name of the file, and the corresponding BeautifulSoup object. 
#
#   The files that will be parsed are defined in the config.py file
def parse(game_xmls, date):
      
    for game in game_xmls:
        gid = parse_game(game[box], date, game_table, False)
        
        if gid:
            print("Processed gid: " + gid)
          #  parse_gamestats(game[box], 'batter', batter_map, batter_gameday_table, gid)
           # parse_gamestats(game[bis_box], 'pitcher', pitcher_map, pitch_gameday_table, gid)
            #parse_pitches(game[ab_pitches]) 
    


#
#   Get the game information from the boxscore xml page, and add it to
#   the database. Ensure the game is not already in the database. If
#   it is then return false.
#
#   If the game is added, return the gid value for future use
#
def parse_game ( soup, date, db_table, gid ):

    query = build_query(box_map + line_map, db_table, gid, True)

    box  = soup.find('boxscore')
    line = soup.find('linescore')
    
    data = [date]
    data = data + build_data(box, box_map, False, False)
    data = data + build_data(line, line_map, False, False)
    
    if insert_db(query, data) == False:
        return False

    return data[1]


#   Given a parsed xml tag, this builds a list of data from the db map.
def build_data(tag, db_map, gid, date):
    data = []
    if gid: data.append(gid)
    if date: data.append(date)

    for item in db_map:
        try:
            data.append(tag[item[1]])
        except:
            
            # If the item is in the map to get built into the query and
            # has no gd2 equivalent, (ie. value is calculated not scraped)
            # then don't add a default value. Value will be added manually.
            if item[1] == '':
                data.append(0)
                logger.warning("No data associated with: " + item[1])
    
    return data

#   Build the query string based on the database map defined
#   in config.py
#
#   If the date and gid need to be added then manually add.
def build_query (db_map, db_table, gid, date):

    query = "insert into " + db_table + "("
    val_query = " values ("

    if date:
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


#   Safely open the url that is passed to the function
def get_page ( url ):
    try:
        f = urlopen(url)
    except:
        logger.warning("Could not get page " + url)
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
def get_links ( url ):
    
    f = get_page (url)
    if f==False: return False

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


#   Insert into the database that is defined in config.py, rollback on 
#   error.
#
#   Arguments:
#       query => Text query to execute
#       data  => Data to insert
#
def insert_db (query, data):
    
    try:
        cur.execute(query, data)
        db.commit()
    except pymysql.Error as e:
        logger.warning('Got error {!r}, errno is {}'.format(e, e.args[0]))
        db.rollback
        return False
    return True


#
def init_globs (arg_date):
    global logger
    global db
    global date
    global cur
    
    date = arg_date
    try:
        logger = logging.getLogger(__name__)
        db     = pymysql.connect( host=db_host, user=db_user, passwd=db_passwd, db=db_name )
        cur    = db.cursor()
    except:
        return False

    return True

