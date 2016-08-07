#!/bin/python

#
#
#
#
def data_scrape ( year, month, day ):
    logger   = logging.getLogger(__name__)
    full_url = base_url + str(year) + "/month_0" + str(month) + "/day_0" + str(day) + "/"
    
    #   Attempt to connect to DB
    db = MySQLdb.connect( host="localhost",
                          user="whaze",
                          passwd="",
                          db=db_name )
    cur = db.cursor()

    #
    date = datetime.datetime.strptime(str(year)+"-"+str(month)+"-"+str(day), "%Y-%m-%d")
    logger.info('Got date: ' + date.strftime('%Y-%m-%d'))
            
    #   Get the game links from the page. If there are any 
    #   errors then log it and return from the func
    logger.info("Getting " + full_url)
    links = get_links(full_url, logger)
    
    if links:
        logger.info("Successfully got links")
    else:
        logger.warning("Could not get links...Returning")
        return False
    
    for link in links:
        full_link = full_url + "gid_" + link 
        gid = parse_game (full_link + game_p_ext, logger, db, cur, date)
        
        if gid:
            parse_batter_box(full_link + game_b_ext, logger, db, cur, date, gid)
            parse_pitcher_box(full_link + game_p_ext, logger, db, cur, date, gid)
            parse_pitches(full_link + pitch_ext, logger, db, cur, date, gid)


#
#   Get the game information from the boxscore xml page, and add it to
#   the database. Ensure the game is not already in the database. If
#   it is then return false.
#
def parse_game ( url, logger, db, cur, date ):
    logger.info("Getting game information")
    f = get_page(url, logger)

    soup = BeautifulSoup(f, "lxml")
    box  = soup.find('boxscore')
    line = soup.find('linescore')

    query = "insert into " + game_table + """ (gid, game_date, vid,
            home_team, away_team, h_losses, h_wins, h_hits, h_runs, h_errors, 
            a_losses, a_wins, a_hits, a_runs, a_errors) values ( %s, %s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s )"""
    
    logger.info('Attempting to add data too ' + game_table)

    data = (box['game_id'], date, box['venue_id'], box['home_team_code'], box['away_team_code'],
            box['home_loss'], box['home_wins'], line['home_team_hits'], line['home_team_runs'],
            line['home_team_errors'], box['away_loss'], box['away_wins'], line['away_team_hits'],
            line['away_team_runs'], line['away_team_errors'])

    if insert_db(query, data, logger, db, cur) == False:
        return False
    else:
        return box['game_id']

#
#
#
def parse_pitches ( url, logger, db, cur, date, gid ):
    logger.info("Parsing pitches page: " + url)
    f = get_page(url, logger)

    soup    = BeautifulSoup(f, "lxml")
    atbat   = soup.find_all('atbat')
    
    query = "insert into " + pitches_table + """ pitch_date, sv_id, pid, bid, gid, pitcher_throws, 
             batter_hits, description, pitch_result, balls, strikes, outs, start_speed, end_speed,
             sz_top, sz_bot, pfx_x, pfx_z, px, pz, x0, y0, z0, vx0, vy0, vz0, ax, ay, az, break_y, 
             break_angle, break_length, pitch_type, type_confidence, zone, nasty, spin_dir, 
             spin_rate values (  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s, 
              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
              %s, %s)"""

    for ab in atbat:
        pitches = ab.find_all('pitch')
        balls, strikes = 0,0

        for p in pitches:
            
            data = ( date, p['sv_id'], ab['pitcher'], ab['batter'], gid, ab['p_throws'],
                     ab['stand'], p['des'], p['type'], balls, strikes, ab['o'], ['start_speed'], 
                     p['end_speed'], p[''],)

    
#
#
#
def parse_pitcher_box ( url, logger, db, cur, date, gid ):
    logger.info("Starting to parse pitcher's box score")
    f = get_page(url, logger)

    soup  = BeautifulSoup(f, "lxml")
    pitch = soup.find_all('pitcher')
    
    insert_pitcher = "insert into " + pitch_gameday_table + """ 
                     (gid, pid, game_date, win, loss, save, hits, runs,
                     er, hr, bb, so, bf, outs, strikes, pitches) values (
                     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                     %s, %s, %s )"""
    logger.info("Attempting to insert into " + pitch_gameday_table)
    
    for p in pitch:
        win, loss, save = 0, 0, 0
        
        if p.has_attr('win'): 
            win = 1
        if p.has_attr('loss'):
            loss = 1
        if p.has_attr('save'):
            save = 1

        data = ( gid, p['id'], date, win, loss, save, p['h'], p['r'], p['er'],
                 p['hr'], p['bb'], p['so'], p['bf'], p['out'], p['s'], p['np'] )

        insert_db(insert_pitcher, data, logger, db, cur)

#
#
#
def parse_batter_box ( url, logger, db, cur, date, gid ):

    logger.info("Starting to parse batter's box score")
    f = get_page(url, logger)

    # Get all batter tags
    soup   = BeautifulSoup(f, "lxml")     
    batter = soup.find_all('batter')

    # Insert queries
    insert_batter = "insert into " + batter_gameday_table + """
                    (gid, pid, game_date, pa, ab, hits, runs, hr, bb, so, rbi, 1b, 2b, 3b,
                    sb, cs, lob, bo, sac, sf, hbp) values (%s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    logger.info("Attempting to insert into " + batter_gameday_table)


    # Loop through each batter tag and extract the info
    for b in batter:
        pa = int(b['ab']) +  int(b['sac']) + int(b['bb']) +  int(b['sf']) + int(b['hbp'])
        
        try:
            bo = int(b['bo']) / 100
        except:
            logger.warning("No BO attr...Skipping")
            bo = 0

        data = (gid, b['id'], date.strftime('%Y-%m-%d', pa, b['ab'],  
                b['h'], b['r'], b['hr'], b['bb'], b['so'], 
                b['rbi'], 0, 0, 0, b['sb'], b['cs'], b['lob'], 
                bo, b['sac'], b['sf'], b['hbp'])
        
        insert_db(insert_batter, data, logger, db, cur)

#
#
#
def get_page ( url, logger ):
    logger.info("Getting Page: " + url)

    try:
        f = urllib2.urlopen(url)
    except urllib2.URLError as e:
        logger.warning(e.reason)
        return False

    return f



#   Get all the links off of the page:
#       gd2.mlb.com/components/game/mlb/year/month/day/
#   
#   And finds the links for the games that have the following 
#   format:
#   
#   gid_year_mm_dd_team1mlb_team2mlb   
#
def get_links ( url, logger ):

    try: 
        f = urllib2.urlopen(url)
    except urllib2.URLError as e:
        logger.warning(e.reason)
        return False
    
    # Compile the regex to match links outside of the loop for 
    # performance
    links = []
    regex = re.compile("\"gid_(.*?)\"", re.IGNORECASE)
    
    # Find all links on page and if they are links to games then add to list
    for link in BeautifulSoup(f, "lxml",parse_only=SoupStrainer('a', href=True) ):
        match = regex.findall(str(link))
        if match:
           links.extend(match)
    
    return links


#   
#
#
def insert_db (query, data, logger, db, cur):

    # Attempt to insert, rollback on error
    try:
        cur.execute(query, data)
        db.commit()
    except MySQLdb.Error as e:
        logger.warning("DB threw error: " + str(e))
        db.rollback
        return False
    
    return True
