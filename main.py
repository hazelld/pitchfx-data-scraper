#!/bin/python

import logging
from scrapers import pscrape, gd_scrape
from datetime import timedelta
import datetime

def daterange (start, end):
    for n in range(int ((end-start).days)):
        yield start + timedelta(n)

#   Set up the logger
logging.basicConfig(filename="mlb.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

date = datetime.date(2016, 7, 8)
pscrape.pscrape(date)

start = datetime.date(2016, 5, 1)
end = datetime.date(2016, 6, 1)

for dt in daterange(start, end):
    gd_scrape.gd_scrape(dt, "disk")
