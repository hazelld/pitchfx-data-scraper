#!/usr/bin/python

from datetime import timedelta, date
from scrapers.gd_scrape import *
from scrapers.config import *
import os

base_dir   = "gd2/"


def daterange (start, end):
    for n in range(int ((end-start).days)):
        yield start + timedelta(n)


def download (start_date, end_date):
    '''
        Download the needed files as defined in config.py (xml_files) and save
        them to disk. This is the safest route for running gd_scrape on any
        sizeable amount of data. 

        The files will be saved in the root project directory under the gd2/ 
        folder.
    '''
    for sd in daterange(start_date, end_date):
        
        ext     = str(sd.year)+"/month_"+'%02d'%sd.month+"/day_"+'%02d' % sd.day + "/"
        url     = base_url + ext
        new_dir = base_dir + "year_" + ext 
        games   = get_links(url)

        for game in games:
            path     = new_dir + game
            game_url = url + "gid_" + game

            if not os.path.exists(path):
                os.makedirs(path + "inning")

            for f in xml_files:
                
                try:
                    xml = get_page(game_url + f)
                except:
                    print("Could not get page: " + game_url + f)
                    continue 

                print("Writing File: " + os.path.join(path, f))
                try:
                    with open(os.path.join(path, f), 'w') as temp_file:
                        temp_file.write(str(xml.read()))
                except:
                    print("Error trying to write to file")

