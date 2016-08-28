#!/bin/python

import logging
from scrapers import dscrape
import datetime

#   Set up the logger
logging.basicConfig(filename="mlb.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

date = datetime.date(2016, 7, 7)
dscrape.gdt_scrape(date, "web")
