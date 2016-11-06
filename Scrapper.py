# Request Response paradigm
import urllib.request as request
from bs4 import BeautifulSoup
from pymongo import MongoClient
import urllib.parse
import time

class Scrapper():
	
	# Private variables
	__urlStartRange = 10
	__urlEndRange = 8420
	__userAgentString = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
	__delay = 0
	__baseURL = ''
	__mongoClient = None
	__database = None
	__databaseName = 'gsmArenaDataStore'	
	__collection = None
	__collectionName = 'dataStore'
	__uid = 0

	# Initilize the variables
	def __init__(self, delayTime, baseURL):
		self.__delay = delayTime
		self.__baseURL = baseURL
		self.__delay = int(delayTime)
		try:
			# Get the mongo client connection
			self.__mongoClient = MongoClient('mongodb://localhost:27017/')
			# Get the specific database
			self.__database = self.__mongoClient[self.__databaseName]
			# Get the collection from that database(Collection can be simply understood as table)
			self.__collection = self.__database[self.__collectionName]
		except Exception as e:
			print ("[ERROR] Unable to initiate connection with mongodb client.")
			raise e		

	def getImage(self, URL):
		imageData = ""
		req = request.Request(URL)
		# Add the Google chrome useragent to the request so that it won't ban us
		req.add_header('User-Agent',self.__userAgentString)
		try:
			# Try fetching the page, if 404 continue to the next page
			# Open the connection that means get the page
			response = request.urlopen(req)
			# Read the response
			imageData = response.read()
			#f = open('temp.jpg', 'wb')
			#f.write(responseData)
			#f.close()
		except Exception as e:
			print (e)
		return imageData

	# Parse the data and store it in the mongodb
	def parseNStore(self, data, URL):
		# For insertion in mongodb create a dict as we will insert in the json format
		record = dict()
		# For the extraction of the data, we will use beautiful soap and parse it using lxml format
		soup = BeautifulSoup(data, "lxml")
		# Get the title of the mobile
		self.__uid = self.__uid + 1
		record['uid'] = self.__uid		
		record['URL'] = URL
		record['Title'] = soup.findAll('h1', {'class':'specs-phone-name-title'})[0].getText().lower()
		productImageURL = soup.findAll('div', {'class':'specs-photo-main'})[0].find('img')['src']
		record['image'] = self.getImage(productImageURL)
		record['productImageURL'] = productImageURL
		record['Price'] = 0
		# Read all the specs
		allTables = soup.find("div", {"id": "specs-list"}).findAll("table")
		# For each broad category get the smaller category
		for eachTable in allTables:
			# Get the broad category
			broadCategory = eachTable.find("th").getText().lower()
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
							lastfeature = feature = column.getText().lower()
					else :						
						values += column.getText().lower();
					count += 1
				# Filter the data i.e. remove the '\n', '-', '(', ')' and replace them by space and replace multiple space by single space
				values = values.replace('\n', ' ').replace('-', ' ').replace('(', ' ').replace(')', ' ').replace(',', ' ')
				values = ' '.join(values.split())

				# Remove . from the feature list
				feature = feature.replace(".", " ")

				# Convert the price to INR 
				if feature.lower() == "price group":
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
		print ("[INFO] Inserting in mongodb : ", record['Title'], " UID : ", self.__uid)
		# Insert into the mongodb
		try:
			result = self.__collection.insert_one(record)
		except Exception as e:			
			print ('[ERROR] In document insertion in mongodb ', e)			
		
	# Start the crawling
	def start(self):
		# Iterate through the startrange till the end range
		for i in range(self.__urlStartRange, self.__urlEndRange, 1):
			# Construct the additional part of the url which we will concatenate with the base URL
			extension = 'a' + '-' + str(i) + '.php'
			completeURL = self.__baseURL + extension
			# Create a request
			req = request.Request(completeURL)
			# Add the Google chrome useragent to the request so that it won't ban us
			req.add_header('User-Agent',self.__userAgentString)
			try:
				# Try fetching the page, if 404 continue to the next page
				# Open the connection that means get the page
				response = request.urlopen(req)
				# Read the response
				responseData = response.read()
				# Get the redirected url i.e. original URL of the page
				realURL = response.geturl()
				# add delay if specified any
				time.sleep(self.__delay)
				# print (responseData)
				# Parse the data and store the data in the mongo db				
				self.parseNStore(responseData, realURL)
			except Exception as e:
				pass
			
# Main Function
if __name__ == '__main__':
	print ('[Starting Crawling]')
	s = Scrapper(0, 'http://www.gsmarena.com/')
	s.start()
	print ('[Crawling Completed]')