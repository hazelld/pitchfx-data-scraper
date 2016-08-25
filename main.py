#!/bin/python

import logging
from scrapers import dscrape

#   Set up the logger
logging.basicConfig(filename="mlb.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

dscrape.data_scrape(2016, '07', 7)
