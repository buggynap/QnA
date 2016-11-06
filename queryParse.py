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
								'sound':'sound', 'display':'display', 'launch':'launch'}
		# Load the dictionaries
		self.loadDictFromPickle()

	def loadDictFromPickle(self):	
		#Load Transition Dict
		with open('PickleFiles/titleList.pickle', 'rb') as f:
			self.__titleDict = pickle.load(f)

	def removeStopWords(self, tokens):
		stopWordList = {'what', 'is', 'the', '?', '.', 'series', 'mobile', 'phones', 'list', 'between', 'among', 'in', 'terms', 'of', 'and'}
		compareDict = {'compare', 'difference', 'similarity', 'different', 'better'}
		for token in tokens:
			if token in stopWordList:
				tokens.remove(token)
			elif token in compareDict:
				self.__isKeywordComparePresent = True
		return tokens
	
	def processQuery(self, query):

		# Reset the variable
		__isKeywordComparePresent = False

		# Convert the query to the lowercases
		query = query.lower()

		# Tokenize the query
		tokens = tokenize(query, ' ')

		# Remove the stop words
		tokens = self.removeStopWords(tokens)

		# Clear all the dictionaries first for the n grams
		clearAllDict()

		# Extract feature words from the query
		# Needed features
		featureToGetFromDB = list()
		for token in tokens:
			if self.__featuresDict.get(token):
				featureToGetFromDB.append(self.__featuresDict[token])
				tokens.remove(token)

		print (tokens)

		# make the N - grams model and search
		gramDicts = getNGrams(6, tokens, 1)

		print ("Compare keyword is present")

		UIDList = set()

		for gramDict in gramDicts:
				# If the n-gram is present then
				if gramDict:
					# Check if the title is present or not
					for key in gramDict.keys():
						if self.__titleDict.get(key):							
							if len(UIDList) == 0:
								UIDList = self.__titleDict[key]
							else:
								UIDList = UIDList.intersection(self.__titleDict[key])

		print  (UIDList)
		if self.__isKeywordComparePresent :
			pass
		else:
			

			print ("Here what I have found")
			for uid in UIDList:
				phoneRecord = self.__collection.find_one({"uid":uid})
				# print the title first
				print (phoneRecord['Title'])
				# If no feature is specified then what to do
				for feature in featureToGetFromDB:
					print (feature, end = ' ')

					if feature == 'Price' or feature == 'colors':
						try:
							print (phoneRecord['misc'][feature], ' ')
						except Exception as e:
							print ("No Price in record")					
					else:
						print (phoneRecord[feature], ' ')





# Main Function
if __name__ == '__main__':
	
	q = queryParser()	
	while True:
		query = input("Enter the query : ")
		startTime = time.time()		
		q.processQuery(query)
		print("Results returned in [%s seconds]\n" % (time.time() - startTime))