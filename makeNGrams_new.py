#!/usr/bin/python

# Empty list of all the dictonaries
''' 
	The below dictionary is in the form of w2 -> [w1, count], not like [w1, w2]
	this is used to detect the next word, still we will make a dictonary like w1 w2
'''

#Create dictonary of grams
def createDictOfNGrams(tokenList, gramCount):

	gramListOfDictCombine = dict()
	for i in range(len(tokenList) - gramCount + 1):
		currentString = ' '.join(tokenList[i: i + gramCount])
		gramListOfDictCombine[currentString] = gramListOfDictCombine.get(currentString, 0) + 1
	return gramListOfDictCombine

def getNGrams(gramCount, tokenList):

	# create a dictionary for all required grams
	return createDictOfNGrams(tokenList, gramCount)