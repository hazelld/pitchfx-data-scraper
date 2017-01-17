# pitchfx-data-scaper  
Scrape pitchfx data from the MLBs publically available files at gd2.mlb.com/components/game/mlb. This program will setup 
the SQL database, scrape the data for a given date range, and put it in the database. It also creates a player database 
from the [Crunch Time Baseball](http://www.crunchtimebaseball.com/) website. This program is designed to be run daily, as it 
will pull the newest data that isn't in the database.   

# Install
```
git clone git@github.com:whazell/pitchfx-data-scraper.git  
cd pitchfx-data-scraper  
pip3 install -r requirements.txt
```  

# Usage  

This program requires a database already created. To do this just run:  
```
mysql -e "create database db_name"
``` 
With whatever name tickles your fancy. The other db info such as user, host etc will 
be prompted for when running.  

To run the program just use:  

```
python3 main.py
```  

and follow the prompts.
