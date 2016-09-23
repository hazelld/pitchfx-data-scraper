#!/usr/bin/python

from urllib.request import urlopen
import re
import csv
import sys
import logging
import pymysql.cursors
import logging
from datetime import datetime
from scrapers.gd_scrape import *
from scrapers.db import *



def pscrape (current_date):
    '''
        Determine if there is a newer version to the player database. If there
        is, then download and update the database. The last date updated is stored 
        in the scrapers.cfg file.
    '''
    logger = logging.getLogger(__name__)
    if init_db() == False: return False

    home = get_page(pscrape_base + pscrape_home)
    if home == False: return False
    
    newest_update = get_last_update(home.read(), logger)
    last_update   = get_last_playerdb_update()
    
    if newest_update > last_update:
        did_update = update_player_db()
        
        if did_update:
            update_last_playerdb_update(newest_update)
            print("Successfully updated playerdb")
    else:
        print("No playerdb update available")


def update_player_db():
    '''
        Update the player database by getting the csv page and parsing it.
    '''
    csv_file = get_page(pscrape_base + pscrape_data)
    if csv_file == False: return False
    
    page = str(csv_file.read()).split('\\r\\n')
    reader = list(csv.reader(page, delimiter=','))
    
    # Some reason there is always a blank last element in the list
    reader = reader[1:-1]
    
    for row in reader:
        data = row[0:4] + row[5:7]
        query = build_query(player_map, player_table, False, False)
        insert_db(query, data, False)
    
    return True


def get_last_update (page, logger):
    '''
        Return the datestring of the last update of the crunchtime player
        csv file.
    '''
    regex = re.compile("\(last update:.*?([0-9]+)", re.IGNORECASE)
    match = regex.findall(str(page))
    
    if match == False:
        logger.warning("Could not find the last date crunchtime player map was updated")
        return False

    return datetime.strptime(match[0], '%y%m%d')
