rm mlb.log
mysql mlb_stats < db/db_scripts/clear_db.sql
rm scrapers/scrapers.cfg
python3 main.py
