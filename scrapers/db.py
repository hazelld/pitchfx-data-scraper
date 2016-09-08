import logging
import pymysql.cursors
from scrapers import config


def init_db():
    '''
        Initialize the globals for this module.

        Returns False on error, True otherwise
    '''
    global logger
    global db 
    global cur

    logger = logging.getLogger(__name__)
    
    try:
        db  = pymysql.connect(host=config.db_host, user=config.db_user, \
                              passwd=config.db_passwd, db=config.db_name)
        cur = db.cursor()
    except:
        logger.error("Could not connect to database.")
        return False
    
    return True


def insert_db (query, data):
    '''
        Insert data into the database using the connection established in 
        init_db(). If an error is encountered, rollback the database.

        Return False on Error, otherwise return True.
    '''
    try:
        cur.execute(query, data)
        db.commit()
    except pymysql.Error as e:
        logger.warning('Got error {!r}, errno is {}'.format(e, e.args[0]))
        logger.warning('Previous error occured with data: ' + str(data[1]))
        db.rollback
        return False
    return True


def build_query (db_map, db_table, gid, date):
    '''
        Build the query based on the database map given. Since gid and
        date are excluded from the maps, they must be manually added at 
        the start.

        Returns the query that will look like:

        insert into db_table (x, y, z) values (%s, %s, %s)
    '''
    query = "insert into " + db_table + "("
    val_query = " values ("

    if date:
        query     += "game_date, "
        val_query += "%s," 

    if gid:
        query += "gid, " 
        val_query += "%s,"

    # Build the query
    i = len(db_map)
    for key in db_map:
        query     += key[0]
        val_query += "%s"
        i -= 1
        if i > 0:
             query +=  ","
             val_query += ","
    
    query += ")" + val_query + ")"
    return query


def get_last_id():
    '''
        Return the ID from the last item inserted. 
    '''
    return cur.lastrowid
