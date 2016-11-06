import urllib.request as request
from bs4 import BeautifulSoup
from pymongo import MongoClient
import urllib.parse
import time
from PIL import Image
import requests
from io import StringIO

def getImage(URL):
	req = request.Request(URL)
	# Add the Google chrome useragent to the request so that it won't ban us
	req.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36')
	try:
		# Try fetching the page, if 404 continue to the next page
		# Open the connection that means get the page
		response = request.urlopen(req)
		# Read the response
		responseData = response.read()
		#Image.open(StringIO(responseData)).show()
		f = open('temp.jpg', 'wb')
		f.write(responseData)
		f.close()
		print ("This is the data : ", responseData)
	except Exception as e:
		pass



def parseNStore(data):
		# For insertion in mongodb create a dict as we will insert in the json format
		record = dict()
		# For the extraction of the data, we will use beautiful soap and parse it using lxml format
		soup = BeautifulSoup(data, "lxml")
		# Get the title of the mobile
		productTitle = soup.findAll('h1', {'class':'specs-phone-name-title'})[0].getText()
		productImageURL = soup.findAll('div', {'class':'specs-photo-main'})[0].find('img')['src']
		#getImage(productImageURL)
		record['Title'] = productTitle
		record['Price'] = 0
		# Read all the specs
		allTables = soup.find("div", {"id": "specs-list"}).findAll("table")
		# For each broad category get the smaller category
		for eachTable in allTables:
			# Get the broad category
			broadCategory = eachTable.find("th").getText()			
			# Now get the smaller category
			rows = eachTable.findAll("tr")
			lastfeature = ""
			tempdict = dict()	
			for row in rows:
				feature = values = ""				
				count = 0
				columns = row.findAll("td")
				for column in columns:					
					if count == 0:
						if len(column.getText()) <= 1:
							feature = lastfeature
						else:
							lastfeature = feature = column.getText()
					else :						
						values += column.getText();
					count += 1
				# Filter the data i.e. remove the '\n', '-', '(', ')' and replace them by space and replace multiple space by single space
				values = values.replace('\n', ' ').replace('-', ' ').replace('(', ' ').replace(')', ' ')
				values = ' '.join(values.split())

				if feature == "Price group":
					feature = "Price"
					try:
						values = int(values.split(' ')[2]) * 60
					except Exception as e:
						pass

				if tempdict.get(feature) :
					tempdict[feature] = tempdict[feature] + (" " + values)
				else:
					tempdict[feature] = values

				
			record[broadCategory] = tempdict

		print (record)


if __name__ == '__main__':
	f = open("test", "r").read()
	parseNStore(f)
