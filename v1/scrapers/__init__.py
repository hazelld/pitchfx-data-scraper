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
base_url   = "http://gd2.mlb.com/components/game/mlb/year_"
pitch_ext  = "inning/inning_all.xml"
game_b_ext = "boxscore.xml"
game_p_ext = "bis_boxscore.xml"

#   Database info 
db_name              = "mlb_stats"
batter_gameday_table = "gamestats_batter"
pitch_gameday_table  = "gamestats_pitcher"
pitches_table        = "pitches"
game_table           = "games"
