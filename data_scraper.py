import psycopg2
import pycurl
import requests as HTTPRequest
from urllib.parse import urlencode

API_KEY = 'dce7f59e-26df-4ae3-bda5-e7a039a4a176'

def parse_keywords(country_code, cursor):
    keyword_query = 'SELECT id, name FROM keywords'
    cursor.execute(keyword_query)
    keyword_results = cursor.fetchall()

    if keyword_results:
        for id, name in keyword_results:
            str = 'id %(kid)s, name %(kname)s' % {"kid": id, "kname": name }
            print(str)
            print("response:")
            ingest_keyword_response(id, name, country_code)
            return

def ingest_keyword_response(id, name, country_code):
    str = 'ingest keyword id %(kid)s, name %(kname)s' % {"kid": id, "kname": name }
    print(str)
    #get json response from scrapingrobot
    resp = load_json_response(name, country_code)
    
def get_page(url, data=None):
    
    try:
        response = HTTPRequest.post(url, json=data)
        print(response.status_code)
    except(Exception) as error:
        print("get_page exception")
        print(error)
        return 

def send_REST_request(api_key, query, country_code):
    try:
        url = "https://api.scrapingrobot.com/?token=%s" % (api_key)
        headers = ["Content-Type:application/json"]
        
        #post data - params
        post_data = {
         "params": {
              "query": query,
              "countryCode": country_code,
              "languageCode": "es",
              "num": 1
         },
         "module": "GoogleScraper"
        }

        return get_page(url, post_data)
    except:
        print("exception")
        return 
    
def load_json_response(query, country_code):
    return send_REST_request(API_KEY, query, country_code)

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to PostgreSQL...')
        conn = psycopg2.connect("dbname=persado user=knu")
		
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