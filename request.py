#must refactor before deploying to cloud
import requests
from bs4 import BeautifulSoup

keyword = "skincare"
 
URL = "https://www.google.com/search?{0}".format(keyword)

r = requests.get(URL)
 
soup_resp = BeautifulSoup(r.content, 'html5lib')
print(soup_resp.prettify())

#print(URL)