#must refactor before deploying to cloud
import requests
from bs4 import BeautifulSoup

keyword = "skincare"
 
URL = "https://www.google.com/search?{0}".format(keyword)

r = requests.get(URL)
 
soup_resp = BeautifulSoup(r.content, 'html5lib')
print(soup_resp.prettify())

#print(URL)


#dce7f59e-26df-4ae3-bda5-e7a039a4a176