import logging
import pymysql.cursors
from scrapers import config

def init_db():
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


#   Insert into the database that is defined in config.py, rollback on 
#   error.
#
#   Arguments:
#       query => Text query to execute
#       data  => Data to insert
#
def insert_db (query, data):

    try:
        cur.execute(query, data)
        db.commit()
    except pymysql.Error as e:
        logger.warning('Got error {!r}, errno is {}'.format(e, e.args[0]))
        logger.warning('Previous error occured with data: ' + str(data[1]))
        db.rollback
        return False
    return True

#   Build the query string based on the database map defined
#   in config.py
#
#   If the date and gid need to be added then manually add.
def build_query (db_map, db_table, gid, date):

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
    return cur.lastrowid
