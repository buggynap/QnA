# Read the data from the mongo db 
# Make the n grams model of it using the key and value pair

from pymongo import MongoClient
# Module files
from Tokenizer import *
from makeNGrams import *

import time

def makeLists(field):
	
	__mongoClient = None
	__database = None
	__databaseName = 'gsmArenaDataStore'
	__collection = None
	__collectionName = 'dataStore'
	try:
		# Get the mongo client connection
		__mongoClient = MongoClient('mongodb://localhost:27017/')
		# Get the specific database
		__database = __mongoClient[__databaseName]
		# Get the collection from that database(Collection can be simply understood as table)
		__collection = __database[__collectionName]
	except Exception as e:
		print ("[ERROR] Unable to initiate connection with mongodb client.")
		raise e

	titleList = dict()
	count = 1
	# Get all the documents from the mongo db
	myCursor = __collection.find()
	for item in myCursor:
		# For each item make a posting list of the field
		# Clear all the dictonaries for the ngrams or we can add this method in class so that while instanciating, it will automatically get clear
		clearAllDict()
		productTitle = item[field]
		productTitle = productTitle.replace(')', ' ').replace('(', ' ')
		productUID = item['uid']
		print ("[INFO] Parsing the uid : ", productUID, " ", productTitle, " Count = ", count)
		count = count + 1
		tokens = tokenize(productTitle, ' ')
		# Got the tokens make the posting list now
		gramDicts = getNGrams(6, tokens, 1)
		# For each key append the UID if present else add new key
		for gramDict in gramDicts:
			# If the n-gram is present then
			if gramDict:
				# Check if the title is present or not
				for key in gramDict.keys():
					# If the key is not present then add the key and initilise the dict with set for that key
					if not titleList.get(key):
						titleList[key] = set()
					titleList[key].add(productUID)

	# Save the data to the pickle
	saveToPickle("titleList", titleList)	

def saveToPickle(fileName, dictionary):
	# Load the dictionary 
	with open('PickleFiles/' + fileName + '.pickle', 'wb') as f:
		pickle.dump(dictionary, f, protocol=2)	

# Main Function
if __name__ == '__main__':
	s = makeLists('Title')