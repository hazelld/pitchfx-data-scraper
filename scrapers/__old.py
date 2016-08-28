

#
#
#
#
def data_scrape ( year, month, day ):
    
    if init_globs(year, month, day) == False: return False
    logger.debug('Got date: ' + date.strftime('%Y-%m-%d'))

    full_url = base_url + str(year) + "/month_0" + str(month) + "/day_0" + str(day) + "/"
    links = get_links(full_url)
    
    if links:
        logger.debug("Successfully got links")
    else:
        logger.warning("Could not get links...Returning")
        return False
    
    for link in links:
        full_link = full_url + "gid_" + link 
        gid = parse_game (full_link + game_ext, game_table, False)       
        
        print(gid)
        if gid:
            parse_game_stats(full_link+game_ext_b, 'batter', batter_map, batter_gameday_table, gid)
            parse_game_stats(full_link+game_ext, 'pitcher', pitcher_map, pitch_gameday_table, gid)
            parse_pitches(full_link + pitch_ext, gid)




#
#   The pitching data needs it's own function as it has alot of very specific
#   logic. It needs to link the pitch to it's corresponding entry in the atbat
#   table. There are also some specific calculations that need to be done in 
#   the atbat data for the runners
#
def parse_pitches ( url, gid ):
    logger.info("Parsing pitches page: " + url)
    f = get_page(url)
    if f == False: return False

    soup    = BeautifulSoup(f, "lxml")
    atbat   = soup.find_all('atbat')
    ab_query= build_query(ab_map, ab_table, gid, False)

    print(ab_query)
    # Loop through each atbat tag
    for ab in atbat:
        data = [ gid ]

        # Get data from the tag
        for item in ab_map:
            try:
                data.append(ab[item[1]])
            except:
                
                if item[1] != '':
                    data.append('0')
                    logger.warning("No data associated with: " + item[1])
        
        # Have to get the runners for the other stats
        runners = ab.find_all('runner')
        r1 = r2 = r3 = rbi = risp = 0
        
        for r in runners:
            
            if r['start'] == '1B':
                r1 = 1
            elif r['start'] == '2B':
                r2 = 1
            elif r['start'] == '3B':
                r3 = 1

            try:
                if r['rbi'] == 'T':
                    rbi = rbi + 1
            except:
                pass
        
        risp = r2 + r3

        # Append this to data
        data.append(r1)
        data.append(r2)
        data.append(r3)
        data.append(risp)
        data.append(rbi)
           
        insert_db(ab_query, data)
        

#
#
#
def parse_game_stats ( url, tag, pmap, db_table, gid):
    logger.debug("Parsing game stats")
    
    f = get_page(url)
    if f == False: return False

    soup  = BeautifulSoup(f, "lxml")
    query = build_query(pmap, db_table, gid, True)

    tags  = soup.find_all(tag)

    for i in tags:
        data = [ date, gid ]
        for item in pmap:
            try:
                data.append(i[item[1]])
            except:
                data.append('0')
                logger.warning("No Data associated with: " + item[1])
        insert_db (query, data)


