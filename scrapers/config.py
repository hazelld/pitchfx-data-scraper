import sys
import collections
import logging
import pymysql.cursors
import configparser
from datetime import datetime

#
config_file = "scrapers/scrapers.cfg"

#   Where we get the files from & the names of the files
base_url   = "http://gd2.mlb.com/components/game/mlb/year_"
ab_pitches = "inning/inning_all.xml"
bis_box    = "bis_boxscore.xml"
box        = "boxscore.xml"
xml_files  = (ab_pitches, bis_box, box)

#   pscrape website
pscrape_base = "http://crunchtimebaseball.com/"
pscrape_home = "baseball_map.html"
pscrape_data = "master.csv"

# Config file options
pscrape_opts = "PlayerScraper"
pscrape_last_update = "LastUpdate"

#   Database info 
db_opts = "Database"
batter_gameday_table = "gamestats_batter"
pitch_gameday_table  = "gamestats_pitcher"
pitches_table        = "pitches"
game_table           = "games"
ab_table             = "atbats"
player_table         = "players"



#   These dicts hold the database mappings for each xml file that 
#   is being parsed. This allows the scraper to be flexable and
#   the addition of new fields will be easy.
#   
#   They are in the format "sqlname":"mlb name"
#   
#   There must also be a variable that defines the tag that is being
#   searched for in the xml. If multiple tags are being searched for, 
#   then it must be dict holding the mappings:
#

#   The game table is parsing two seperate tags for info, so have to make 
#   two maps
box_map =(  ('gid','game_id'),
            ('vid','venue_id'),
            ('home_team','home_team_code'),
            ('away_team','away_team_code'),
            ('h_losses','home_loss'),
            ('h_wins','home_wins'),
            ('a_losses','away_loss'),
            ('a_wins','away_wins') )

line_map =( ('h_hits','home_team_hits'),
            ('h_runs','home_team_runs'),
            ('h_errors','home_team_errors'),
            ('a_hits','away_team_hits'),
            ('a_runs','away_team_runs'),
            ('a_errors','away_team_errors'))


# Batter Gameday stats
batter_map = (  ('pid','id'),
                ('ab', 'ab'),
                ('hits', 'h'),
                ('runs', 'r'),
                ('hr','hr'),
                ('bb', 'bb'),
                ('so', 'so'),
                ('rbi', 'rbi'),
                ('sb', 'sb'),
                ('cs', 'cs'),
                ('lob', 'lob'),
                ('bo', 'bo'),
                ('sac', 'sac'),
                ('sf', 'sf'),
                ('hbp', 'hbp') )

# Pitcher Gameday stats
pitcher_map = ( ('pid', 'id'),
                ('hits', 'h'),
                ('runs', 'r'),
                ('er', 'er'),
                ('hr','hr'),
                ('bb', 'bb'),
                ('so', 'so'),
                ('bf', 'bf'),
                ('outs', 'out'),
                ('strikes', 's'),
                ('pitches', 'np') )


# Pitchfx data map
pitch_map = (   ('play_guid', 'play_guid'),
                ('sv_id', 'sv_id'),
                ('des', 'des'),
                ('result', 'type'),
                ('start_speed', 'start_speed'),
                ('end_speed', 'end_speed'),
                ('sz_top', 'sz_top'),
                ('sz_bot', 'sz_bot'),
                ('pfx_x', 'pfx_x'),
                ('pfx_z', 'pfx_z'),
                ('px', 'px'),
                ('pz', 'pz'),
                ('x0', 'x0'),
                ('y0', 'y0'),
                ('z0', 'z0'),
                ('vx0', 'vx0'),
                ('vy0', 'vy0'),
                ('vz0', 'vz0'),
                ('ax','ax'),
                ('ay','ay'),
                ('az','az'),
                ('break_angle','break_angle'),
                ('break_length','break_length'),
                ('pitch_type','pitch_type'),
                ('type_confidence','type_confidence'),
                ('zone','zone'),
                ('nasty','nasty'),
                ('spin_dir','spin_dir'),
                ('spin_rate','spin_rate'),
                ('abid', ''),
                ('balls', ''),
                ('strikes', ''),
                ('outs', ''),
                ('pid', ''),
                ('bid', ''))

# At bat info 
ab_map = (  ('play_guid','play_guid'),
            ('bid','batter'),
            ('pid','pitcher'),
            ('abno','num'),
            ('des','des'),
            ('balls','b'),
            ('strikes','s'),
            ('outs','o'),
            ('event','event'),
            ('home_runs','home_team_runs'),
            ('away_runs','away_team_runs'),
            ('abid',''),
            ('runner_first',''),
            ('runner_second',''),
            ('runner_third',''),
            ('risp',''),
            ('rbi',''))

# Players database, its here so build_query may be called
player_map=(('pid', ''),
            ('name', ''),
            ('pos', ''), 
            ('team', ''),
            ('bats', ''),
            ('throws', ''))

def get_last_playerdb_update():
    Config = configparser.ConfigParser()
    Config.read(config_file)
    
    try:
        opts = Config.options(pscrape_opts)
    except:
        return datetime.MINYEAR
    
    date = Config.get(pscrape_opts, pscrape_last_update)
    return datetime.strptime(date, '%y%m%d')


def update_last_playerdb_update( date ):
    Config = configparser.ConfigParser()
    Config.read(config_file)

    date_string = date.strftime('%y%m%d')
    Config[pscrape_opts][pscrape_last_update] = date_string

    with open(config_file, 'w') as configfile:
        Config.write(configfile)


def get_db_config():
    '''
        This function returns a dict with the database configuration. The keys are the
        following:

        'host'  => Host of database
        'user'  => Database User
        'passwd'=> Database password. Blank if none provided
    '''
    Config = configparser.ConfigParser()
    Config.read(config_file)
    db = {}

    try:
        db['host'] = Config.get("Database", "Host")
        db['user'] = Config.get("Database", "User")
        db['db_name'] = Config.get("Database", "DB_Name")
    except:
        print("Error getting host & user information from " + config_file)
        sys.exit()

    try:
        db['passwd'] = Config.get("Database", "Password")
    except:
        db['passwd'] = ""

    return db
