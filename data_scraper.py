import psycopg2
import requests
import json

API_KEY = 'dce7f59e-26df-4ae3-bda5-e7a039a4a176'

def parse_keywords(country_code, cursor):
    keyword_query = 'SELECT id, name FROM keywords where level=1'
    cursor.execute(keyword_query)
    keyword_results = cursor.fetchall()
    
    try:

        if keyword_results:
            for id, name in keyword_results:
                str = 'id {}, name {}' % {"kid": id, "kname": name }
                print(str)
                print("response:")
                ingest_keyword_response(id, name, country_code, cursor)
            
                return
            
    except(Exception) as error:
        print(error)
        return

def add_related_item(primary_id, related_title, response_id, cursor):
    try:
        
        #check for related keyword
        sql = "SELECT id from keywords where name='" + related_title + "';" 
        cursor.execute(sql)
        results = cursor.fetchone()
        if results is not None:
            for r in results:
                related_id = int(r)
        else:
            related_id = insert_keyword(related_title, response_id, cursor)
                
        str = 'add relation: {} >> {} as {}'.format(keyword, related_title, related_id)
        print(str)
        
        sql = "INSERT into related_keywords (keyword_search_term_id, keyword_search_related_id, search_response_id) values({}, {}, {})"
        cursor.execute(sql.format(primary_id, related_id, response_id))
        #results = cursor.fetchone()
        
    except(Exception) as error:
        print(error)
        return
    
            
def insert_keyword(keyword, response_id, cursor):
    print("insert keyword " + keyword)
    sql = """INSERT INTO keywords(name, level)
             VALUES('{}', 2) RETURNING id;"""
    try:
        # execute the INSERT statement
        cursor.execute(sql.format(keyword))
        # get the generated id back
        keyword_id = cursor.fetchone()[0]
        return keyword_id
        
    except(Exception) as error:
        print(error)
        return
    
def build_new_response(country_id, keyword_id, page, json_string, cursor):
    sql = """INSERT INTO search_response(country_id, keyword_id, page, raw)
             VALUES({}, {}, {}, '{}') RETURNING id;"""
    cursor.execute(sql.format(country_id, keyword_id, page, json_string))
    response_id = cursor.fetchone()[0]
    return response_id

def ingest_keyword_response(id, name, country_code, cursor):
    str = 'ingest keyword id %(kid)s, name %(kname)s' % {"kid": id, "kname": name }
    print(str)
    #get json response from scrapingrobot
    resp = get_page(name, country_code.lower())
    json_string = json.loads(resp)
    #print(json_string)
    
    #find country id
    print('get country id')
    sql = "SELECT id from countries where code='" + country_code + "';" 
    print(sql)
    cursor.execute(sql)
    country_id = cursor.fetchone()[0]
    
    print('get primary keyword id')
    #check for primary keyword id
    sql = "SELECT id from keywords where name='" + name + "';" 
    print(sql)
    cursor.execute(sql)
    primary_id = cursor.fetchone()[0]
    
    #get response_id
    print('get response_id')
    response_id = build_new_response(country_id, primary_id, 1, json_string, cursor)
    print('response_id {}'.format(response_id))
    
    #process relatedQueries
    for related_query in json_string["result"]["relatedQueries"]:
        print("adding " + related_query["title"])
        add_related_item(primary_id, related_query["title"], response_id, cursor)
        
        
    #process paidResults
    for paid_result in json_string["result"]["paidResults"]:
        print("process paid_result " + paid_result["title"])
        add_ad_item(primary_id, paid_result["title"], paid_result["description"], paid_result["url"], response_id, cursor)
        
    #process organicResults
    for organic_result in json_string["result"]["organicResults"]:
        print("process organic_result " + organic_result["title"])
        add_ad_item(primary_id, organic_result["title"], organic_result["description"], paid_result["url"], response_id, cursor)
        
    
def get_page(query, country_code):
    
    try:

        url = 'https://api.scrapingrobot.com/?token=%(mytoken)s' % {"mytoken": API_KEY}

        payload = {
            "url":"https://www.google.com/",
            "params": {
                "query": query,
                "countryCode": country_code,
                "languageCode": "es",
                "num": 10
            },
            "module": "GoogleScraper",
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        return response.text
        
    except(Exception) as error:
        print(error)
        return

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to PostgreSQL...')
        conn = psycopg2.connect("dbname=persado user=knu")
        conn.autocommit = True
        
        # create a cursor
        cur = conn.cursor()
        
	    # print version
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(db_version)
        
        parse_keywords("US", cur)
       
	# close the PostgreSQL connection
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('The Postgres connection has closed.')


if __name__ == '__main__':
    connect()