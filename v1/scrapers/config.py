import collections

#   Where we get the files from & the names of the files
base_url   = "http://gd2.mlb.com/components/game/mlb/year_"
pitch_ext  = "inning/inning_all.xml"
game_ext   = "bis_boxscore.xml"
game_ext_b = "boxscore.xml"

#   Database info 
db_name              = "mlb_stats"
batter_gameday_table = "gamestats_batter"
pitch_gameday_table  = "gamestats_pitcher"
pitches_table        = "pitches"
game_table           = "games"

db_host   = "localhost"
db_user   = "whaze"
db_passwd = ""




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
