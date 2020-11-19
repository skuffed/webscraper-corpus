#function to calculate the weights of the words in a document
#and create a vector to represent the document
def calcWeight():
  #loop through each document
  totalDoc = len(urlSeen)

  global docVector

  #calculating the idf for each word in our index
  # idf = log base 10(docs/docFreq)
  for word in invind:
    tempinv = totalDoc/invind[word]
    tempinv = math.log(tempinv,10) + .00000001
    invind[word] = tempinv

  #calculate the weights for each term in the doc
  #weight = tf * idf
  #tf = freq in doc/maxFreq in doc
  for doc in range(totalDoc):
    #add new vector to list
    docVector.append(dict())
    #calc weight
    for word in docIndex[doc]:
      tf = docIndex[doc][word]/maxFreq[doc]
      idf = invind[word]
      weight = tf * idf
      docVector[doc][word] = weight

  global ii

  print(docVector)
  print(maxFreq)