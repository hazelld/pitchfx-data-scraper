#!/usr/bin/python

from datetime import timedelta, date
from scrapers.gd_scrape import *
from scrapers.config import *
import os

start_date = date(2016, 4, 1)
end_date   = date(2016, 10, 1)
base_dir   = "gd2/"

#
def daterange (start, end):
    for n in range(int ((end-start).days)):
        yield start + timedelta(n)


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

