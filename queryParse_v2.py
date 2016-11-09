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
	__stopWordList = dict()
	__compareDict = dict()
	__rangeDict = dict()
	__isKeywordComparePresent = False
	__isKeywordRangePresent = False

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
		# Nested feature mapping dictionary
		self.__featuresMapDict = {"usb":"comms","gps":"comms","wlan":"comms","radio":"comms","bluetooth":"comms","multitouch":"display",
								"type":"display","resolution":"display","protection":"display","size":"display","weight":"body",
								"sim":"body","dimensions":"body","batterylife":"tests","performance":"tests","loudspeaker":"sound",
								"yes":"sound","alerttypes":"sound","35mmjack":"sound","cardslot":"memory","internal":"memory",
								"sareu":"misc","colors":"misc","sarus":"misc","Price":"misc","":"battery","stand-by":"battery",
								"musicplay":"battery","talktime":"battery","status":"launch","announced":"launch","browser":"features",
								"java":"features","messaging":"features","sensors":"features","3gbands":"network","technology":"network",
								"2gbands":"network","speed":"network","4gbands":"network","os":"platform","gpu":"platform","cpu":"platform",
								"chipset":"platform","secondary":"camera","video":"camera","primary":"camera","features":"camera"}
		# Stop words dictionary
		self.__stopWordList = {'what', 'is', 'the', '?', '.', 'series', 'mobile', 'phones', 'list', 'between', 'among', 'in', 'terms', 
								'of', 'and', 'two', '', 'than', 'how'}
		# Compare dictionary
		self.__compareDict = {'compare', 'difference', 'similarity', 'different', 'better', 'good', 'bad', 'between'}
		# range dictionary
		self.__rangeDict = {'range', 'below', 'under', 'above', 'greater'}

		# Load the dictionaries
		self.loadDictFromPickle()

	def loadDictFromPickle(self):	
		#Load Transition Dict
		with open('PickleFiles/titleList.pickle', 'rb') as f:
			self.__titleDict = pickle.load(f)

	def removeStopWords(self, tokens):
		lefttokens = list()
		for token in tokens:
			if token not in self.__stopWordList:
				lefttokens.append(token)		
		return lefttokens
	
	def processQuery(self, query):

		# Reset the variable
		self.__isKeywordComparePresent = False
		self.__isKeywordRangePresent = False

		# Convert the query to the lowercases
		query = query.lower()

		# Store Original Query
		originalQuery = query

		# Tokenize the query
		tokens = tokenize(query, ' ')

		# Remove the stop words
		tokens = self.removeStopWords(tokens)

		# Extract feature words from the query
		featureToGetFromDB = list()
		lefttokens = list()
		for token in tokens:
			if token in self.__featuresDict:
				featureToGetFromDB.append(self.__featuresDict[token])
			else:
				lefttokens.append(token)

		# If the featues are null show the few specific features
		# I will show, Price, Released, Platform OS, Memory Internal, Camera- primary, secondary, battery
		if len(featureToGetFromDB) == 0:
			featureToGetFromDB.append('Price')
			featureToGetFromDB.append('status')
			featureToGetFromDB.append('os')
			featureToGetFromDB.append('internal')
			featureToGetFromDB.append('primary')
			featureToGetFromDB.append('secondary')
			featureToGetFromDB.append('battery')

		# Assign the left tokens to the tokens
		tokens = lefttokens

		print ("Extracted Features : ", featureToGetFromDB)

		print ("Now Left Tokens are : ", tokens)

		# Now get the phones list from the tokens 
		# while matching unigrams don't match the unigrams with the digits as it will yeild the bad result
		UIDList = set()
		gram = 6
		while gram > 0 and len(tokens) > 0:			
			# make the N - grams model and search			
			flag = 0
			for j in range(len(tokens) - gram + 1):
				'''
					If we are left with the unigram then check if it is digit or not, coz as said earlier 
					matching just digits against the titles won't yeild the better result
				'''
				if gram == 1 and tokens[j].isdigit():
					continue
				currentString = ' '.join(tokens[j: j + gram])
				print (gram, currentString)

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

		print ("Phones found are :",UIDList)		

	

		resultData = """<table style="solid #ddd; font-family: Trebuchet MS, Arial, Helvetica, sans-serif;
						padding: 5px;border: 1px solid #ddd; border-collapse: collapse; border-radius: 25px;
						border-collapse:separate; border:solid black 1px;border-radius:6px;-moz-border-radius:6px;
    					border-color:B0E0E6">"""

		# Now check with left keywords, whether the query is range query or compare query

		# How to check the compare query
		lefttokens = list()
		for token in tokens:
			if token in self.__compareDict:
				self.__isKeywordComparePresent = True
			elif token in self.__rangeDict	:
				self.__isKeywordRangePresent = True
				lefttokens.append(token)
			else:
				lefttokens.append(token)

		# Assign the remaning tokens to the tokens so that we can use it as required		
		tokens = lefttokens

		print ("self.__isKeywordRangePresent ", self.__isKeywordRangePresent, "self.__isKeywordComparePresent ", self.__isKeywordComparePresent)
		print ("Now Left Tokens are : ", tokens)

		# If the range query is present
		if self.__isKeywordRangePresent:

			# Get the price range out of the query
			numbers = list()
			greaterThan = False
			lessThan = False
			between = False
			for token in originalQuery.split():
				if token.isdigit():
					numbers.append(int(token))
				elif token == 'above' or token == 'greater':
					greaterThan = True
				elif token == 'below' or token == 'smaller' or token == "lesser" or token == "under":
					lessThan = True
				elif token == "between":
					between = True

			results = list()
			numbers.sort()

			if greaterThan:
				cursor = self.__collection.find({"misc.Price": { "$gt" : numbers[0]}}).sort( [("misc.Price", -1)] ).limit(10)
				for item in cursor:
					UIDList.add(item["uid"])

			elif lessThan:			
				cursor = self.__collection.find({"misc.Price": { "$lt" : numbers[0]}}).sort( [("misc.Price", -1)] ).limit(10)
				for item in cursor:
					UIDList.add(item["uid"])

			elif between:
				cursor = self.__collection.find({"misc.Price": { "$gt" : numbers[0], "$lt" : numbers[1]}}).sort( [("misc.Price", -1)] ).limit(10)
				for item in cursor:
					UIDList.add(item["uid"])

		print ("Here what I have found")
		for uid in UIDList:
			phoneRecord = self.__collection.find_one({"uid":uid})
			# print the title first
			print (phoneRecord['Title'])
			# If no feature is specified then what to do
			for feature in featureToGetFromDB:
				resultData += ("""<tr width = '15%'><td style="width:35%;padding-left:15px;background-color: #B0E0E6; padding: 8px;border: 1px solid #ddd;">""")
				print (feature, )
				resultData += (feature + "</td>")
				try:
					print phoneRecord[self.__featuresMapDict[feature]][feature]
					resultData += ("""<td style="padding-left:10px">""" + str(phoneRecord[self.__featuresMapDict[feature]][feature]))
					resultData += ("""</td>""")
				except Exception as e:
					try:
						resultData += ("""<td style="padding-left:10px">""" + str(phoneRecord[feature]))
						resultData += ("""</td>""")
						print ("From here", phoneRecord[feature], ' ')
					except Exception as e:
						print ("No such feature exists...")
				resultData += ("</tr>")
		resultData += ("""</table>""")

		print resultData

# Main Function
if __name__ == '__main__':
	
	q = queryParser()	
	while True:
		query = raw_input("Enter the query : ")
		startTime = time.time()		
		q.processQuery(query)
		print("Results returned in [%s seconds]\n" % (time.time() - startTime))