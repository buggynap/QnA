#!/usr/bin/python

import re
import pickle
import sys
import codecs
import time
import operator

#Regex for handling the text
emoticons = r'''
    (?:
        [:=;] 				# Eyes
        [oO\-]? 			# Nose
        [D\)\]\(\]/\\OpP] 	# Mouth
    )'''

regexString = [
	emoticons,
    r'(?:@[\w_]+):?',	# @-mentions both @text and @text:
    r'(?:\#+[\w_]+[\w\'_\-]*[\w_]+)', 	# hash-tags
    r'http[s]?:?\/?\/?(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f])*|[(\.)*])*', # URLs
    r'[a-zA-Z0-9_\.\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-\.]*[a-zA-Z0-9]', # e-mail address
    r'[\d]{1,}\.[\d]{1,}\.[\d]{1,}\.[\d]{1,}', # for IP address
    r'[\d]{1,}\/[\d]{1,}\/[\d]{1,}', # For dates
    r'[\d]{1,}\/[\d]{1,}', #For numbers like 3/4
    r'[\d]{1,}:[\d]{1,}', #For numbers like 3:4
    r'[\d]{1,}\-[\d]{1,}', #For numbers like 3-4
 	r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers*
 	r'[a-zA-Z\.]{1,3}\.', # For abbreviations like Dr. or e.g.
    u'(?:[a-z][a-z\'(\u2019)\-_]+[a-z])', # words with - and '   
    r'(?:[\w_]+)', # other words
    #r'(?:\S)' # anything else
]

tokensRegex = re.compile(r'('+'|'.join(regexString)+')', re.VERBOSE | re.IGNORECASE | re.UNICODE)


def tokenizeOnSpace(data):
    return data.split(' ')


# Returns the list of tokens
def tokenize(data, delimiter):

    if delimiter == ' ':
        tokensList = tokenizeOnSpace(data)
    else:
        tokensList = tokensRegex.findall(data)
    return tokensList