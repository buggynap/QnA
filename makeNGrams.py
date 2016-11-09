#!/usr/bin/python

import re
import pickle
import sys
import HTMLParser
import codecs
import time
import operator

# Empty list of all the dictonaries
''' 
	The below dictionary is in the form of w2 -> [w1, count], not like [w1, w2]
	this is used to detect the next word, still we will make a dictonary like w1 w2
'''
gramListOfDictForward = []


# For count of all the grams in each dict
countOfAllGrams = []

# Dictionary like w1 w2
gramListOfDictCombine = []



#Create dictonary of grams
def createDictOfNGrams(gramListOfDictForward, gramListOfDictCombine, tokenList):

	if len(tokenList) == 0:
		return 

	last = []
	
	for token in tokenList:
		#If last is greater than 6 then reset it to 6
		if len(last) > 5:
			last = last[1:]
		#Now to fill all the grams dict
		for i in xrange(len(last) + 1):

			#For Forward
			if i == 0:
				gramListOfDictForward[0][token] = gramListOfDictForward[0].get(token, 0) + 1
				gramListOfDictCombine[0][token] = gramListOfDictCombine[0].get(token, 0) + 1
			else:
				currentString = ' '.join(last[len(last) - i:])
				if currentString in gramListOfDictForward[i]:
						gramListOfDictForward[i][currentString][token] = gramListOfDictForward[i][currentString].get(token, 0) + 1
				else:
					gramListOfDictForward[i][currentString] = {token:1}

				#For combine
				gramListOfDictCombine[i][currentString + ' ' + token] = gramListOfDictCombine[i].get(currentString + ' ' + token, 0) + 1

			countOfAllGrams[i] = countOfAllGrams[i] + 1
		#Append the current token to the list
		last.append(token)




def getNGrams(gramCount, tokenList, flag):

	# Add the required number of dictionaries required
	for i in range(gramCount):
		gramListOfDictForward.append({})
		gramListOfDictCombine.append({})
		countOfAllGrams.append(0)

	# create a dictionary for all required grams
	createDictOfNGrams(gramListOfDictForward, gramListOfDictCombine, tokenList)
	
	# If flag is 0 w1 : w2
	if(flag == 0):
		return gramListOfDictForward
	# If flag is 1 then "w1 w2"
	else:
		return gramListOfDictCombine

def clearAllDict():
	global gramListOfDictForward
	del gramListOfDictForward[:]
	global gramListOfDictCombine
	del gramListOfDictCombine[:]
	global countOfAllGrams
	del countOfAllGrams[:]



#Gives the count of the grams
def getCountOfNGrams(gram):

	return countOfAllGrams[gram]