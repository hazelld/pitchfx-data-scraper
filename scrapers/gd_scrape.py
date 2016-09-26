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



def gd_scrape(date, source):
    '''
        This function is the entry point to this module. It takes a date and 
        gets the mlb gameday data for that day and parses it into the database
        through scrapers/db. The source argument designates where the files are
        coming from:

        'web' => Download the gameday files from the web

        'disk'=> The files are already downloaded (from dl_gd.py) and are in 
                 a file in the root directory named gd2.
    '''
    global logger
    logger = logging.getLogger(__name__)
    
    # Init the logger and db connection 
    if init_db() == False:
        return False

    # Either get the web pages from the website and put in a list of bs4 
    # objects, or open the files on disk into a list of bs4 objects.
    if source == "web":
        xml = get_files_web(date)
    elif source == "disk":
        xml = get_files_disk(date)
    else:
        logger.warning("Invalid argument to gdt_scrape: " + source)
        return False

    # Don't need to log errors here as get_files_* will have already
    if xml == False: return False

    # Parse the xml files and add into the db 
    parse(xml, date)

    # Clear the db cache to ensure all data makes it to db
    flush_db()


'''
    get_files_web()
    get_files_disk()

    Both these functions are used to get the needed gd2 xml files that are defined
    in config.py (xml_files[]). They both take a date argument for the day to be 
    parsed.

    The return value is the same for both. It is list of dictionarys that holds the name 
    of the file as the key, and the value is the BeautifulSoup parsed object. This list 
    can then be used like:

    game_list = get_files_*()
    game_list[0]["ex_file"] -> BeautifulSoup object that corresponds to the first game
                                of the day's xml file with the name "ex_file"
'''
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
        
        # Loop through the files we need to get
        for f in xml_files:
            page = get_page(full_url + f)
            if page == False: return False

            games_parsed[f] = BeautifulSoup(page, "lxml")
        
        games.append(games_parsed)

    return games


def get_files_disk(date):
    path = "gd2/year_"+str(date.year)+"/month_"+'%02d'%date.month+"/day_"+'%02d' % date.day
    
    try:
        links= [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    except:
        logger.error("Path does not exist: " + path)
        return False

    games = []
    for link in links:
        games_parsed = {}
        npath = os.path.join(path, link)

        for f in xml_files:
            try:
                page = open(os.path.join(npath, f), "r")
            except:
                logger.warning("Could not open file: " + os.path.join(npath, f))
                return False
            
            games_parsed[f] = BeautifulSoup(page, "lxml")

        games.append(games_parsed)

    return games


def parse(game_xmls, date):
    '''
        This function parses all the xml files for each day. The game_xmls var
        is created with the get_files_* functions. 
    '''
    for game in game_xmls:
        gid = parse_game(game[box], date, game_table, False)
        
        if gid:
            print("Processed gid: " + gid)
            parse_gamestats(game[box], 'batter', batter_map, batter_gameday_table, gid, date)
            parse_gamestats(game[bis_box], 'pitcher', pitcher_map, pitch_gameday_table, gid, date)
            parse_pitches(game[ab_pitches], gid, date) 
    


def parse_game ( soup, date, db_table, gid ):
    '''
        Get the game information from the boxscore xml page, and add it to
        the database. Ensure the game is not already in the database. If
        it is then return false.

        If the game is added, return the gid value for future use
    '''
    query = build_query(box_map + line_map, db_table, gid, date)

    box  = soup.find('boxscore')
    line = soup.find('linescore')
    
    data = [date]
    data = data + build_data(box, box_map, False, False)
    data = data + build_data(line, line_map, False, False)
    
    if insert_db(query, data, True) == False:
        return False

    return data[1]


def parse_gamestats ( soup, tag, pmap, db_table, gid, date):
    '''
        Parse the game stats from the soup.

        Arguments:
            soup => BeautifulSoup Object to search
            tag  => Tag to search for in the soup
            pmap => Database map. See config.py for example
            db_table => Database table to insert into
            gid  => Game ID as returned from parse
            date => Date of the game being parsed

    '''
    query = build_query(pmap, db_table, gid, date)
    tags  = soup.find_all(tag)

    for i in tags:
        data = build_data(i, pmap, gid, date)
        insert_db (query, data, False)


def parse_pitches ( soup, gid, date ):
    '''
        Parse the pitchfx data from the innings/innings_all.xml. This function 
        finds the atbat information, and the corresponding pitch data for the at
        bat. It also gets other information such as the runners that are on base.

    '''
    atbats   = soup.find_all('atbat')
    ab_query = build_query(ab_map, ab_table, True, True)
    p_query  = build_query(pitch_map, pitches_table, True, True)

    for ab in atbats:
        data = build_data(ab, ab_map, gid, date)
        
        # If the atbat ID isn't here, then the inning finished without the atbat 
        # finishing, such as when a pickoff occurs. For now just ignore these
        if data[2] == 0:
            logger.warning("Missing abid...Skipping")
            print("Data that doesn't have abid: " + str(data))
            continue

        # Get runners on base
        data.extend(parse_runners(ab.find_all('runner')))
        insert_db(ab_query, data, False)

        # This info comes from ab tag, but is inserted into the pitch table
        abid = ab['play_guid']
        outs = ab['o']
        pid  = ab['pitcher']
        bid  = ab['batter']
        balls = strikes = 0
    
        pitches = ab.find_all('pitch')

        # Get all the pitches from the current atbat 
        for p in pitches:
            pdata = build_data(p, pitch_map, gid, date)
            pdata.extend([abid, balls, strikes, outs, pid, bid])
            insert_db(p_query, pdata, False)
            
            # Need to manually keep track of the count
            if p['type'] == 'B':
                balls = balls + 1
            elif p['type'] == 'S':
                if strikes < 2: strikes = strikes + 1
        

def parse_runners(tags):
    '''
        Parse all the <runner> tags from the <atbat> tags to get 
        the information about the current runners on base for the atbat.

        Return a list of the information so it may be appended to the running
        list
    '''
    r1 = r2 = r3 = rbi = 0
    
    for r in tags:
        if r['start'] == '1B':
            r1 = 1
        elif r['start'] == '2B':
            r2 = 1
        elif r['start'] == '3B':
            r3 = 1
        
        try: 
            if r['rbi'] == 'T': rbi = rbi + 1
        except: pass

    return [r1, r2, r3, rbi, r2+r3]


def build_data(tag, db_map, gid, date):
    '''
        This function takes a parsed xml tag (from a BeautifulSoup object) and
        builds a list of the data from the database map. This function is used 
        in conjunction with build_query (db.py) to be able to easily build the 
        query and corresponding data.

        Using these functions together also assures that the data and query is 
        matched up, so values are not being inserted into the wrong table.
    '''
    logger = logging.getLogger(__name__)
    data = []
    if date: data.append(date)
    if gid: data.append(gid)

    
    for item in db_map:
        try:

            # Extract the data from the tag for corresponding item from db map
            data.append(tag[item[1]])
        except:
            
            # If the item is in the map to get built into the query and
            # has no gd2 equivalent, (ie. value is calculated not scraped)
            # then don't add a default value. Value will be added manually.
            if item[1] != '':
                data.append(0)
    
    return data


def get_page ( url ):
    '''
        Safely attempt to get the page at the given URL. Log any error.
    '''
    logger = logging.getLogger(__name__)
    try:
        f = urlopen(url)
    except:
        logger.warning("Could not get page " + url)
        return False
    return f


def get_links ( url ):
    '''
        Get all the links off of the page:
        gd2.mlb.com/components/game/mlb/year/month/day/
        
        And finds the links for the games that have the following 
        format:
   
        gid_year_mm_dd_team1mlb_team2mlb   
    '''
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

