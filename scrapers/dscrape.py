#!/bin/python

from scrapers.config import *
import logging
import re
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from urllib.request import urlopen
import MySQLdb
import datetime


#
#
#
def gdt_scrape(arg):

    # Init the logger and db connection
    if init_globs() == False: 
        return False

    # Either get the web pages from the website and put in a list of bs4 
    # objects, or open the files on disk into a list of bs4 objects.
    if isinstance(arg, datetime.datetime):
        xml = get_files_web(arg)
    else:
        xml = get_files_disk(arg)

    if xml == False: return False

    # Parse the xml files and add into the db 
    parse(xml)


#
#
#
#
#
#
def get_files_web(date):
    url = base_url+date.year+"/month_"+'%02d'%date.month+"/day_"+'%02d' % date.day
    
    links = get_links(url)
    if links == False:
        logger.warning("Could not get links on page: " + url)
        return False
    
    games = []
    for link in links:
        full_url    = url + "/gid_" + link + "/"
        game_parsed = {}
        
        for f in xml_files:
            page = get_page(full_url + f)
            if page == False: return False

            games_parsed[f] = BeautifulSoup(f, "lxml")
        
        games.append(games_parsed)

    return games

#
def get_files_disk(base_dir):
    pass


#   This function is used to parse the xml files for each day. It takes a 
#   list that holds each game. Each list item is a dictionary that has the 
#   name of the file, and the corresponding BeautifulSoup object. 
#
#   The files that will be parsed are defined in the config.py file
def parse(game_xmls):
    
    for game in game_xmls:
        gid = parse_game(game[box])
        
        if gid:
            parse_gamestats(game[box], 'batter', batter_map, batter_gameday_table, gid)
            parse_gamestats(game[bis_box], 'pitcher', pitcher_map, pitch_gameday_table, gid)
            parse_pitches(game[ab_pitches]) 
    
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
    except MySQLdb.Error as e:
        logger.warning("DB threw error: " + str(e))
        db.rollback
        return False
    return True
