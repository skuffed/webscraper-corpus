# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 15:02:41 2019

@author: max kirin
"""

invind= dict()
maxFreq = []

#takes preprocessed file with tokens from the 
#document and builds an inverted index from them
# f - filename
def index(f):
    #invertedd index = dictionary
        #key = word
        #value = dictionary
          #key = doc number
          #value = number of appearances in doc
          #length of dict represents the document freq
    global invdind 
    #max frequencies - list
      #each index represents a doc, value is the 
      #number of times the most frequent word appears
    global maxFreq
    #setting for comparison
    maxFreq.append(1)

    global urlSeen
    #used in the dictionary as a key
    docnum = len(urlSeen)

    #read the contents of the preprocessed document
    d = open(f, "r")
    doc = d.read()
    #tokenize, now a list of words
    doc = doc.split()
    d.close()

    #open index file
    ii = open("docIndex.txt", "w")
    #analyze each word
    for word in doc:
      #make new key for word when it isn't found in the dict
      if word not in invind:
        #add key to the dictionary
        invind[word] = dict()
        invind[word][docnum] = 1
      else:
        #checking dictionary of given word to see if word has already been in 
        #this doc, incrementing term freq if so
        #otherwise, setting it to 1
        invind[word][docnum] = invind[word].get(docnum,0) + 1

        #checking to see if it is the new max freq in the doc
        if invind[word][docnum] > maxFreq[docnum -1]:
          maxFreq[docnum -1] = invind[word][docnum]

    #printing to the index file
    #may not need to do everytime
    #
    #
    #
    #
    #
    for key in invind:
      ii.write(key + " " + str(invind[key]) + "\n")
      
    ii.close()