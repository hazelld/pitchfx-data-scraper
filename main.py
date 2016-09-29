#!/bin/python

import logging
from scrapers import pscrape, gd_scrape, config, db
from datetime import timedelta
import datetime
import time
import os.path
import os
import sys

#   Set up the logger
logging.basicConfig(filename="mlb.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

todays_date = time.strftime("%d%m%Y")

# Check if the config file exists, if not get the db info manually
if os.path.isfile(config.config_file) == False:
    print("Config file not found. Need to make one before continuing.")
    config.make_config_file()

# Check if we can connect to the database
if db.init_db() == False:
    print("Could not connect to database. Please ensure database exists and try again")
    sys.exit()

# Check if the proper database tables are available
if db.check_tables() == False:
    print("Proper tables are not available in database...")
    schema = db.get_newest_schema()
    print("Newest schema is: " + schema + "\nInstalling Schema...")
    os.system("mysql " + db.get_name() + " < " + schema)
    print("Schema is installed")


# Update player database
print("Attempting to update the player database")
pscrape.pscrape(todays_date)


# Get the lastest date of game
# Ask if they would like to update the databases until today
# Ask if web or disk download


def daterange (start, end):
    ''' 
        This function allows for iteration over a date range
        defined by start and end arguments
    '''
    for n in range(int ((end-start).days)):
        yield start + timedelta(n)
