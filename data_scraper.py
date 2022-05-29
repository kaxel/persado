import psycopg2

def parse_keywords(country_code, cursor):
    keyword_query = 'SELECT id, name FROM keywords'
    cursor.execute(keyword_query)
    keyword_results = cursor.fetchall()

    if keyword_results:
        for id, name in keyword_results:
            str = 'id %(kid)s, name %(kname)s' % {"kid": id, "kname": name }
            print(str)

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect("dbname=persado user=knu")
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        
        parse_keywords("US", cur)
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()