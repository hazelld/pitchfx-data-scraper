import logging
import pymysql.cursors
from scrapers import config

CACHE_LIMIT = 1000

def init_db():
    '''
        Initialize the globals for this module.

        Returns False on error, True otherwise
    '''
    global logger
    global db 
    global cur
    global insert_list
    global cached_count

    insert_list = []
    cached_count = 0
    logger = logging.getLogger(__name__)
    
    try:
        db  = pymysql.connect(host=config.db_host, user=config.db_user, \
                              passwd=config.db_passwd, db=config.db_name)
        cur = db.cursor()
    except:
        logger.error("Could not connect to database.")
        return False
    
    return True


def insert_db (query, data, need_result):
    '''
        Insert data into the database using the connection established in 
        init_db(). If an error is encountered, rollback the database. If need_result 
        is true, then the data is inserted immediately. If it is false the data will
        be grouped before the insert for efficiency.

        Return False on Error, otherwise return True.
    '''
    global cached_count
    global insert_list
    
    ins = (query, data)
    cached_count += 1
    insert_list.append((query, data))

    if need_result == True or cached_count > CACHE_LIMIT:
        result = _insert(insert_list)
        del insert_list[:]
        insert_list = []
        cached_count = 0
        return result

def _insert (insert_list):
    '''
        Actually insert data into the database, not to be called externally.
    '''
    
    for i in insert_list:
        try:
            cur.execute(i[0], i[1])
        except pymysql.Error as e:
            logger.warning('Got error {!r}, errno is {}'.format(e, e.args[0]))
            db.rollback
            return False
    
    # Commit changes to db
    try:
        db.commit()
    except pymysql.Error as e:
        logger.warning('Got error {!r}, errno is {}'.format(e, e.args[0]))
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
