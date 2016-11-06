# Query engine 

from pymongo import MongoClient
import time

# Module files
from Tokenizer import *
from makeNGrams import *


class queryParser():

	# Private variables
	__mongoClient = None
	__database = None
	__databaseName = 'gsmArenaDataStore'	
	__collection = None
	__collectionName = 'dataStore'
	__titleDict = dict()
	__featuresDict = dict()
	__featuresMapDict = dict()
	__isKeywordComparePresent = False

	# Initilize the variables
	def __init__(self):
		#Get the connection to the mongodb
		try:
			# Get the mongo client connection
			self.__mongoClient = MongoClient('mongodb://localhost:27017/')
			# Get the specific database
			self.__database = self.__mongoClient[self. __databaseName]
			# Get the collection from that database(Collection can be simply understood as table)
			self.__collection = self.__database[self.__collectionName]
		except Exception as e:
			print ("[ERROR] Unable to initiate connection with mongodb client.")
			raise e

		# Load the features dict
		self.__featuresDict = {'cost':'Price', 'prize':'Price', 'value':'Price', 'price':'Price', 'color':'colors',
								'colors':'colors', 'colour':'colors', 'colour':'colors', 'camera':'camera', 
								'memory':'memory', 'communication':'comms', 'body':'body', 'platform':'platform', 
								'features':'features', 'feature':'feature', 'network':'network', 'battery':'battery', 
								'sound':'sound', 'display':'display', 'launch':'launch', "wlan":"wlan", "radio":"radio",
								"bluetooth":"bluetooth", "multitouch":"multitouch", "type":"type", "resolution":"resolution",
								"protection":"protection", "size":"size", "weight":"weight", "sim":"sim", "dimensions":"dimensions",
								"batterylife":"batterylife", "performance":"performance", "loudspeaker":"loudspeaker",
								"alerttypes":"alerttypes", "35mmjack":"35mmjack", "cardslot":"cardslot", "internal":"internal",
								"sareu":"sareu", "colors":"colors", "sarus":"sarus", "Price":"Price", "stand-by":"stand-by",
								"musicplay":"musicplay", "talktime":"talktime", "status":"status", "announced":"announced",
								"browser":"browser", "java":"java", "messaging":"messaging", "sensors":"sensors", "3g":"3gbands",
								"technology":"technology", "2g":"2gbands", "speed":"speed", "4g":"4gbands", "os":"os", "gpu":"gpu",
								"cpu":"cpu", "chipset":"chipset", "secondary":"secondary", "video":"video", "primary":"primary",
								"features":"features", "screen" : "display"}
		self.__featuresMapDict = {"usb":"comms","gps":"comms","wlan":"comms","radio":"comms","bluetooth":"comms","multitouch":"display",
								"type":"display","resolution":"display","protection":"display","size":"display","weight":"body",
								"sim":"body","dimensions":"body","batterylife":"tests","performance":"tests","loudspeaker":"sound",
								"yes":"sound","alerttypes":"sound","35mmjack":"sound","cardslot":"memory","internal":"memory",
								"sareu":"misc","colors":"misc","sarus":"misc","Price":"misc","":"battery","stand-by":"battery",
								"musicplay":"battery","talktime":"battery","status":"launch","announced":"launch","browser":"features",
								"java":"features","messaging":"features","sensors":"features","3gbands":"network","technology":"network",
								"2gbands":"network","speed":"network","4gbands":"network","os":"platform","gpu":"platform","cpu":"platform",
								"chipset":"platform","secondary":"camera","video":"camera","primary":"camera","features":"camera"}

		# Load the dictionaries
		self.loadDictFromPickle()

	def loadDictFromPickle(self):	
		#Load Transition Dict
		with open('PickleFiles/titleList.pickle', 'rb') as f:
			self.__titleDict = pickle.load(f)

	def removeStopWords(self, tokens):
		stopWordList = {'what', 'is', 'the', '?', '.', 'series', 'mobile', 'phones', 'list', 'between', 'among', 'in', 'terms', 'of', 'and', 'two', ''}
		compareDict = {'compare', 'difference', 'similarity', 'different', 'better', 'good', 'bad'}
		lefttokens = list()
		for token in tokens:
			if token in compareDict:
				self.__isKeywordComparePresent = True
			elif token not in stopWordList:
				lefttokens.append(token)

		# Assign the left tokens to the tokens
		return lefttokens
	
	def processQuery(self, query):

		# Reset the variable
		__isKeywordComparePresent = False

		# Convert the query to the lowercases
		query = query.lower()

		# Tokenize the query
		tokens = tokenize(query, ' ')

		# Remove the stop words
		tokens = self.removeStopWords(tokens)

		print ("Tokens are : ", tokens)

		# Extract feature words from the query
		featureToGetFromDB = list()
		lefttokens = list()
		for token in tokens:
			if token in self.__featuresDict:
				featureToGetFromDB.append(self.__featuresDict[token])				
			else:
				lefttokens.append(token)

		# Assign the left tokens to the tokens
		tokens = lefttokens

		print ("Extracted Features : ", featureToGetFromDB)
		print ("Tokens are : ", tokens)

		# Now get the phones list from the tokens 
		UIDList = set()
		gram = 6
		while gram > 0 and len(tokens) > 0:			
			# make the N - grams model and search	
			flag = 0
			for j in range(len(tokens) - gram + 1):
				currentString = ' '.join(tokens[j: j + gram])
				if self.__titleDict.get(currentString):
					UIDList = UIDList.union(self.__titleDict[currentString])
					flag = 1
					# delete the token from the tokens
					count = 0
					for k in range(j, j + gram, 1):
						if k - count >= len(tokens):
							break
						tokens.pop(k - count)
						count = count + 1
					break

			if flag == 0:
				gram = gram - 1

		if len(featureToGetFromDB) == 0:
			# Show all features
			for uid in UIDList:
				phoneRecord = self.__collection.find_one({"uid":uid})
				print (phoneRecord)
		else:
			print ("Here what I have found")
			for uid in UIDList:
				phoneRecord = self.__collection.find_one({"uid":uid})
				# print the title first
				print (phoneRecord['Title'])
				# If no feature is specified then what to do
				for feature in featureToGetFromDB:
					print (feature, end = ' ')
					try:
						print (phoneRecord[self.__featuresMapDict[feature]][feature], ' ')
					except Exception as e:
						try:
							print ("From here", phoneRecord[feature], ' ')
						except Exception as e:
							print ("No such feature exists...")

# Main Function
if __name__ == '__main__':
	
	q = queryParser()	
	while True:
		query = input("Enter the query : ")
		startTime = time.time()		
		q.processQuery(query)
		print("Results returned in [%s seconds]\n" % (time.time() - startTime))