mysql mlb_stats < db/db_scripts/clear_db.sql
rm scrapers/scrapers.cfg
printf "[PlayerScraper]\nlastupdate = 160828" > scrapers/scrapers.cfg
python3 -m cProfile main.py
