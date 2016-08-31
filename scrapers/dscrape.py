#!/bin/python

import logging
import re
import os
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from urllib.request import urlopen
import datetime
from scrapers.config import *
from scrapers.db import *

#
#
#
def gdt_scrape(date, source):
    global logger

    # Init the logger and db connection 
    if init_db() == False:
        return False
    logger = logging.getLogger(__name__)

    # Either get the web pages from the website and put in a list of bs4 
    # objects, or open the files on disk into a list of bs4 objects.
    if source == "web":
        xml = get_files_web(date)
    elif source == "disk":
        xml = get_files_disk(date)
    else:
        logger.warning("Invalid argument to gdt_scrape: " + source)
        return False

    if xml == False: return False

    # Parse the xml files and add into the db 
    parse(xml, date)



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
            parse_gamestats(game[box], 'batter', batter_map, batter_gameday_table, gid, date)
            parse_gamestats(game[bis_box], 'pitcher', pitcher_map, pitch_gameday_table, gid, date)
            parse_pitches(game[ab_pitches], gid, date) 
    


#
#   Get the game information from the boxscore xml page, and add it to
#   the database. Ensure the game is not already in the database. If
#   it is then return false.
#
#   If the game is added, return the gid value for future use
#
def parse_game ( soup, date, db_table, gid ):

    query = build_query(box_map + line_map, db_table, gid, date)

    box  = soup.find('boxscore')
    line = soup.find('linescore')
    
    data = [date]
    data = data + build_data(box, box_map, False, False)
    data = data + build_data(line, line_map, False, False)
    
    if insert_db(query, data) == False:
        return False

    return data[1]

#
#
#
def parse_gamestats ( soup, tag, pmap, db_table, gid, date):
    
    query = build_query(pmap, db_table, True, True)
    tags  = soup.find_all(tag)

    for i in tags:
        data = build_data(i, pmap, gid, date)
        insert_db (query, data)

#
#
#
def parse_pitches ( soup, gid, date ):
    
    atbats   = soup.find_all('atbat')
    ab_query = build_query(ab_map, ab_table, True, True)
    p_query  = build_query(pitch_map, pitches_table, True, True)

    for ab in atbats:
        data = build_data(ab, ab_map, gid, date)
        
        # Get runners on base
        r1 = r2 = r3 = rbi = 0
        runners = ab.find_all('runner')
        
        for r in runners:
            if r['start'] == '1B':
                r1 = 1
            elif r['start'] == '2B':
                r2 = 1
            elif r['start'] == '3B':
                r3 = 1

            # Safely check for rbi
            try: 
                if r['rbi'] == 'T': rbi = rbi + 1
            except: pass

        data.append(r1)
        data.append(r2)
        data.append(r3)
        data.append(rbi)
        data.append(r2 + r3)

        # Insert data, get the abid key back
        insert_db(ab_query, data)
        abid = get_last_id()

        pitches = ab.find_all('pitch')
        outs = ab['o']
        pid  = ab['pitcher']
        bid  = ab['batter']
        balls = strikes = 0

        for p in pitches:
            pdata = build_data(p, pitch_map, gid, date)
            pdata.append(abid)
            pdata.append(balls)
            pdata.append(strikes)
            pdata.append(outs)
            pdata.append(pid)
            pdata.append(bid)
            insert_db(p_query, pdata)
            
            if p['type'] == 'B':
                balls = balls + 1
            elif p['type'] == 'S':
                if strikes < 2: strikes = strikes + 1
        
        

#   Given a parsed xml tag, this builds a list of data from the db map.
def build_data(tag, db_map, gid, date):
    data = []
    if date: data.append(date)
    if gid: data.append(gid)

    for item in db_map:
        try:
            data.append(tag[item[1]])
        except:
            
            # If the item is in the map to get built into the query and
            # has no gd2 equivalent, (ie. value is calculated not scraped)
            # then don't add a default value. Value will be added manually.
            if item[1] != '':
                data.append(0)
                logger.warning("No data associated with: " + item[1])
    
    return data


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

