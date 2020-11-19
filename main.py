# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 15:06:00 2019

@author: Max Kirin and Alex McCarthy
"""

#creating a function to crawl a website
#and grab more links to crawl
#to create a document corpus
#demonstrating this method in the main function
import ast
import math
import requests
from requests.exceptions import SSLError
import re
from nltk.stem.porter import *

numberDocs = 0
urlSeen = []
cossim = []
stemmer = PorterStemmer()
invind = dict()
maxFreq = []
docIndex = []
docVector = []
relDict = {}
idf = dict()
tp = 0
fn = 0
fp = 0
#controls for stemming and stopword functionality
doStem = True
doStopWords = False
#open the stopwords file to be ready when needed
stop = open("stopwords.txt", "r", encoding='utf-8')
stopwords = stop.read()
stopwords = stopwords.split()
cranDocs = []
cranQry = {}
#function to access a website and extract links from it
#will continue to crawl until certain number of 
#webpages have been analyzed
# websites - list of websites we want to analyze
def crawl(websites):
    print("Crawling in process...")
    global urlSeen
    #counters for total url statistics
    totalabs = 0
    totalrel = 0
    #list of all redirection errors we come across, so we can abort them in the future
    urlError = []
    robotlist = []
    robotword = []
    #checking the robots.txt page for the muhlenberg.edu domain
    #in case we need to check if we are allowed
    print("crawling robots.txt")
    robtxt = open("robots.txt", "wb", encoding='utf-8')
    robots = requests.get("https://www.muhlenberg.edu/robots.txt", allow_redirects = False, timeout = 10)
    robotlist = robots.content.split()
    #adding each part of the file to a list
    for word in robotlist:
      word = str(word)
      words = re.search(r"^(b')(.*)(')$", word)
      if words:
        robotword.append(words.group(2))

    while len(urlSeen) < 10:
        #counters for number of links found for given site
        abscount = 0
        relcount = 0
        #list to keep track of all links found, to add to websites later
        urlFound = []
        pagenotfound = False
        #get the next website we want to crawl
        site = websites.pop()
        #choose the next site that hasn't given us an error
        while site in urlError:
            site = websites.pop()
        #clean to ensure make it easier to compare agaisnt visited sites
        site = re.sub(r"^https?://", r"", site)
        site = re.sub(r"#.+$", r"", site)
        #site = re.sub(r"/$", r"", site)
        #ensuring it is valid html page, aka not an image or document
        notValidHtml = re.search(r"\.pdf|\.gif|\.jpe?g|\.ps|\.ppt|\.ppsx|\.doc|\.docx|\.PDF|\.GIF|\.JPE?G|\.PS|\.PPT|\.PPSX|\.DOC|\.DOCX", site)
        #checking to see if the link found has already been seen
        #if not, we can visit it and crawl it
        if site not in urlSeen and not notValidHtml:
            #add https:// to beginning of site again to be able to visit it
            site = "https://" + site
            print(site)
            try:
                r = requests.get(site, allow_redirects = False, timeout = 10)
            except SSLError as e:
                #unable to query using https url, so switch to http
                print("sslerror, fixing...")
                site = re.sub(r"https", "http", site)
                r = requests.get(site)
            
            #getting errors 303 and 301
            if r.status_code == 301 or r.status_code == 303:
                urlError.append(site)
            #if site is valid, we can continue
            elif r.status_code == 200:
                #tokenize to find links easier
                contents = r.text.split(">")
                for token in contents:
                    #print(token)
                    #check if redirected to Page Not Found
                    notFound = re.match(r"^ *Page Not Found.*?</title$", token)
                    if notFound:
                        #print("page not found")
                        #set boolean to fix outside of for loop
                        pagenotfound = True
                        break
                    #test if token is a link tags
                    linktag = re.search(r"<a .*?href=[\"\']([\S]+)", token)
                    if linktag:
                        #retrieving the href link from the html code
                        url = linktag.group(1)
                        #print("before", url)
                        #remove ending quotation mark
                        if url[-1] == '"' or url[-1] == "'":
                            url = url[0:len(url)-1]
                        #print("after", url)
                        #determining if the link is relative or absolute
                        #len(url) > 1 to ensure we aren't referencing home page
                        #since we are starting with that
                        if len(url) > 1 and url[0] == '/' and url[1] == '/':
                            #double slashes to start are a form of absolute
                            #replace them with our protocol, https://
                            url = re.sub(r"^//", r"https://www.", url)
                            #check to make sure it is a muhlenberg site
                            validSite = re.match(r"https?://www\.muhlenberg\.edu", url)
                            if validSite:
                                #i am thinking this would be an absolute link, so
                                #that is what i am tallying here
                                abscount = abscount + 1
                                #add url to list
                                urlFound.append(url)
                                #print(url)
                                #print("rel/abs")
                        elif len(url) > 1 and url[0] == '/':
                            #relative, referring back to home page
                            #start relative path from muhlenberg.edu
                            home = re.match(r"(https?://[\S]+\.muhlenberg\.edu)", site)
                            #get home path to add relative path onto
                            url = home.group(1) + url
                            relcount = relcount + 1
                            #add to list
                            urlFound.append(url)
                            #print(url)
                            #print("rel")
                        else:
                            #check to see if it is absolute link to muhlenberg.edu site
                            validSite = re.match(r"https?://[\S]+\.muhlenberg\.edu", url)
                            if validSite:
                                abscount = abscount + 1
                                #add to list
                                urlFound.append(url)
                                #print(url)
                                #print("abs")
                    
                #if the page doesn't redirect to the page not found page
                if not pagenotfound:
                    #file has been crawled
                    #clean site before adding it to the seen list
                    site = re.sub(r"https?://", r"", site)
                    #visited it, so add to seen list
                    urlSeen.append(site)
                    #total up counters
                    totalabs = totalabs + abscount
                    totalrel = totalrel + relcount
                    #add links to the stack
                    websites = websites + urlFound
                    #create file for website we crawled and display information
                    filename = "doc" + str(len(urlSeen)) + ".txt"
                    #print(site)
                    print(filename)
                    f = open(filename, "w", encoding='utf-8')
                    urlinfo = "URL: " + site + "\nRelative links: " + str(relcount) + "\nAbsolute links: " + str(abscount) + "\n"
                    f.write(urlinfo)
                    f.write(r.text)
                    f.close()
                    #pass the page to be preprocessed and added
                    #to our index
                    preprocess(filename)
                
    print("Crawling complete")
    print("Number of pages retrieved: ", len(urlSeen))
    print("Relative URLs found: ", totalrel)
    print("Absolute URLs found: ", totalabs)
    print("Total URLs found: ", totalrel+totalabs)
    print("url errors: ", urlError)

#takes html code and extracts text that appears on the
#webpage that a user would be searching for
#cleans the text to shrink the number of unique tokens
# f = filename
def preprocess(f):
  #open our webpage we crawled
  d = open(f, "r", encoding='utf-8')
  #tokenize by tags
  doc = d.read()
  contents = doc.split("<")
  #close the file and reopen in write mode
  #to add text we find to 
  d.close()
  
  #cleanedText
  #for now, opening file under another name
  #cf = re.sub(r"\.txt", r"clean.txt", f)
  #cleandoc = open(cf, "w")
  #loop through each token
  for token in contents:
    #tags we want to get rid of
    #may contain text in tags that will be caught by our regex
    badtoken = re.match(r"^script|style|!--", token)
    #every token that may have some text that is displayed on the page
    if not badtoken:
      #check if text is included
      # [^/] - prevents picking up false ending of the tag, such as in link
      containsText = re.search(r"[^/]>(.+)$", token)
      if containsText:
        #if so save it and clean it of any html language
        text = containsText.group(1)
        #clean the text string
        text = clean(text)
        index(text)
        #write it to the doc
        #cleandoc.write(text)
        #cleandoc.write("\n")

  #close the new doc
  #cleandoc.close()
  #call the index function to add to our inverted index

def clean(text):
  global doStem
  global doStopWords
  #fixing some html language
  text = re.sub(r"&amp;|&\s", r"and", text)
  text = re.sub(r"&rsquo;", r"'", text)
  text = re.sub(r"&lsquo;", r"'", text)
  #copyright logo - remove
  text = re.sub(r"&copy;", r"", text)
  #getting rid of possessives
  text = re.sub(r"'s", r"", text)
  #remove puncuation
  text = re.sub(r"[\(\)\[\]\{\}';:\"?!\|\<\>]", r"", text)
  #remove commas in numbers
  text = re.sub(r"([0-9]+),([0-9]+)", r"/g<1>/g<2>", text)
  #replace all remaining commas with a space
  text = re.sub(r",", r" ", text)
  #remove period when end of sentence, saves emails and others
  text = re.sub(r"\.\s", r" ", text)
  text = re.sub(r"\.$", r"", text)
  #hypens to spaces
  text = re.sub(r"-", r" ", text)
  #lowercase
  text = text.lower() 
        
  if doStopWords:
    global stopwords
    #split the string up into a list of words
    text = text.split()
    for word in text:
      #check if each word is a stopword
      if word in stopwords:
        #remove it if so
        text.remove(word)
    #join back into a string
    text = " ".join(text)
      
  if doStem:
    stemText = []
    #tokenize the text
    text = text.split()
    for word in text:
      #stem the word
      word = stemmer.stem(word)
      stemText.append(word)
    #update text string with the stemmed words
    text = " ".join(stemText)

  return text

#takes preprocessed file with tokens from the 
#document and builds an inverted index from them
# text = string of all words in doc
def index(text):
    #inverted index = dictionary
        #key = word
        #value = document freq
    global invdind 
    #max frequencies - list
      #each index represents a doc, value is the 
      #number of times the most frequent word appears
    global maxFreq
    #setting for comparison
    maxFreq.append(1)

    #list of pages we have visitied so far
    global urlSeen
    #used in the dictionary as a key
    #docnum = len(urlSeen)
    docnum = numberDocs +1

    #list that contains dictionary for each document
      #key = word
      #value - term freq
    global docIndex
    docIndex.append(dict())

    #read the contents of the preprocessed document
    #d = open(f, "r")
    #doc = d.read()
    #tokenize, now a list of words
    #doc = doc.split()
    #d.close()

    text = text.split()
    #open index file
    #ii = open("docIndex.txt", "w")
    global ii
    #analyze each word
    for word in text:
      #if the word is found in the index, add to the doc list
      #otherwise, create a new key and make a new list
      #Only increment when word appears for first time in doc
      if word not in docIndex[docnum -1]:
        doclist = invind.get(word,0)
        if isinstance(doclist, list):
          doclist.append(docnum-1)
          invind[word] = doclist
        else:
          invind[word] = [docnum-1]
      #do the same for the docIndex
      docIndex[docnum -1][word] = docIndex[docnum -1].get(word,0) + 1

      #checking to see if it is the new max freq in the doc
      if docIndex[docnum -1][word] > maxFreq[docnum -1]:
        maxFreq[docnum -1] = docIndex[docnum-1][word]


    #ii.write("\n\n\nDoc " + str(docnum) + " Index\n")

    #for key, count in docIndex[docnum -1].items():
      #ii.write(key + " " + str(count) + "\n")

#function to calculate the weights of the words in a document
#and create a vector to represent the document
def buildVectors():
  #loop through each document
  #totalDoc = len(urlSeen)
  totalDoc = numberDocs +1

  global docVector
  #stores the idfs for later use
  global idf

  #calculating the idf for each word in our index
  # idf = log base 10(docs/docFreq)
  for word in invind:
    #doc freq is length of list in invind[word]
    docFreq = invind.get(word, 0)
    if isinstance(docFreq, list):
      docFreq = len(invind[word])
    tempinv = totalDoc/docFreq
    tempinv = math.log(tempinv,10) + .00000001
    idf[word] = tempinv

  #calculate the weights for each term in the doc
  #weight = tf * idf
  #tf = freq in doc/maxFreq in doc
  for doc in range(totalDoc):
    #add new vector to list
    docVector.append(dict())
    #calc weight
    for word in docIndex[doc]:
      tf = docIndex[doc][word]/maxFreq[doc]
      idfval = idf[word]
      weight = tf * idfval
      docVector[doc][word] = weight


#function to ask user for search query and 
#create a vector from it
def getQuery(query):
  #keep track of term freq
  qindex = dict()
  #final vector for the query
  qvector = dict()
  q = clean(query)
  #create an index for the query to find tfs
  #save the max freq from the query
  mf = indexQuery(q, qindex)
  #print(mf)
  #once index is built, we can calculate the weights
  #and create a vector
  qvector = vectorQuery(qindex, mf)
  #print(qvector)
  return qvector

#builds index from input string
def indexQuery(q, qindex):
  mf = 0
  tokens = q.split()
  for word in tokens:
    #tally term freq in qindex
    qindex[word] = qindex.get(word, 0) + 1
    if qindex[word] > mf:
      mf = qindex[word]
  #return max freq to use in tf*idf calc
  return mf

#calculates tf*idf for each word and adds it the a dictionary
def vectorQuery(qindex, mf):
  global urlSeen
  global idf
  vector = dict()
  for word in qindex:
    #tf = term freq/max freq
    tf = qindex[word]/mf
    #normal idf is log base 10(totaldocs/docFreq)
    #in the case of a single query,
    #totaldocs/docFreq = 1/1 = 1
    #so will use small number instead of 0
    idfval = idf.get(word,0)
    #print(idfval)
    vector[word] = tf*idfval

  #return query in vector form
  return vector

#given a query as a vector, loop through all documents
#that have at least one of the words found in the query
#calculate the cosine similiarity, and add this value
#to a list to be sorted later
def calcCosSim(query):
  global docVector
  global invind
  global cossim
  relevantDocs = []
  qbottom = 0
  #loop through each key of the dictionary
  for key in query:
    #grab each document that is relevant to our query
    if invind.get(key,0) != 0:
      relevantDocs = relevantDocs + invind[key]
      #qbottom calculates the magnitude of our query
      #to be used in our cosine similarity
      qbottom = qbottom + math.pow(query[key], 2)
    

  #getting rid of duplicate documents in the list
  relevantDocs = list(set(relevantDocs))

  #calc cosine similarity for each document
  #against our query
  for doc in relevantDocs:
    #trackers for our calculations
    top = 0
    bottom = 0
    dbottom = 0
    #grab the vector for the doc
    v = docVector[doc]
    #find the magnitude of our document vector
    for word in v:
      #dbottom calculates the magnitude of our docVector
      dbottom = dbottom + math.pow(v.get(word,0), 2)
    #for each word in our string
    for word in query:
      #top totals up the dot product of the vectors
      #on the top of our equations
      top = top + (query[word])*(v.get(word,0))
    #print(qbottom)
    #print(dbottom)
    #print(doc)
    bottom = math.sqrt(qbottom) * math.sqrt(dbottom)
    cossimval = top/bottom
    cossim.append(tuple([cossimval, doc]))
    
  cossim.sort(reverse=True)
  cossim = cossim[0:10]
  #for i in range(len(cossim)):
    #print(cossim[i])
  
  #global urlSeen
  #for _,urlnum in cossim:
      #print(urlSeen[urlnum])
  
def splitCranQs():

  file = open("cran.qry", "r", encoding='utf-8')

  global cranQry

  qrys = file.read().replace('\n', ' ')
  #split each document into it's own index
  qrys = qrys.split(".I")

  #remove blank string at the beginning
  del qrys[0]

  #clean unnecessary words out of document
  for i in range(len(qrys)):
    #find the query number to be used in the dictionary
    qnum = re.match(r"^ ([0-9]+)", qrys[i])
    qnum = int(qnum.group(1))
    #remove the number from the string
    qrys[i] = re.sub(r"^ ([0-9]+)", r"", qrys[i])
    #remove any other tags
    qrys[i] = re.sub(r"\.[TAWB]", " ", qrys[i])
    #change any new line characters to spaces
    qrys[i] = re.sub(r"\n", r" ", qrys[i])
    #pass string to be cleaned, and save in dictionary
    cranQry[qnum] = clean(qrys[i])

  file.close()
  #print(cranQry)

#take the cran.all.1400 file and split
#its contents up into individual files
#and save them in the crandocs list
def splitCranDocs():

  f = open("cran.all.1400", "r", encoding='utf-8')
  global cranDocs
  #used to keep track of what document we are currently on
  #used in loop
  global numberDocs
  #read the file
  cranDocs = f.read()

  #split each document into it's own index
  cranDocs = cranDocs.split(".I")

  #get rid of first blank string that comes from split
  del cranDocs[0]


  #clean unnecessary words out of document
  for numberDocs in range(len(cranDocs)):
    #remove any tags
    cranDocs[numberDocs] = re.sub(r"\.[TAWB]", " ", cranDocs[numberDocs])
    #remove the number from the beginning
    #numberDocs is keeping track of that for us
    cranDocs[numberDocs] = re.sub(r"^ [0-9]+", " ", cranDocs[numberDocs])
    #change any new lines to spaces
    cranDocs[numberDocs] = re.sub(r"\n", r" ", cranDocs[numberDocs])
    #pass the string to be cleaned
    cranDocs[numberDocs] = clean(cranDocs[numberDocs])
    #add the string to the index
    index(cranDocs[numberDocs])
  
  f.close()

#saves all the data we need to use in our query comparison
#to files so we can access later
def saveData():
    #saveUrls()
    saveVectors()
    saveIdf()
    saveInvInd()
    
def saveUrls():
    f = open("urlSeen.txt", "w", encoding='utf-8')
    global urlSeen
    #printing index to the file
    for site in urlSeen:
      f.write(site + "\n")

    f.close()

def saveVectors():
    f = open("docVector.txt", "w", encoding='utf-8')
    global docVector
    #printing index to the file
    for doc in docVector:
        for key in doc:
            f.write(key + " " + str(doc[key]) + "\n")
        f.write("\n")

    f.close()

def saveIdf():
    f = open("idf.txt", "w", encoding='utf-8')
    global idf
    #printing index to the file
    for key in idf:
      f.write(key + " " + str(idf[key]) + "\n")
    f.close()

def saveInvInd():
    f = open("invind.txt", "w", encoding='utf-8')
    global invind
    #printing index to the file
    for key in invind:
      f.write(key + " " + str(invind[key]) + "\n")

    f.close()

#retrieves the information we saved in documents
#to represent our corpus
def loadData():
    #loadUrls()
    loadVectors()
    loadIdf()
    loadInvInd()
    
def loadUrls():
    global urlSeen
    f = open("urlSeen.txt", "r", encoding='utf-8')
    urlSeen = f.readlines()
    f.close()
    
def loadVectors():
    global docVector
    global urlSeen
    f = open("docVector.txt", "r", encoding='utf-8')
    data = f.readlines()
    lineCounter = 0
    #loading vector for each doc
    #for i in range(len(urlSeen)):
    for i in range(1400):
        docVector.append(dict())
        while lineCounter < len(data):
            if data[lineCounter] == "\n":
                lineCounter = lineCounter + 1
                break;
            else:
                l = data[lineCounter].split()
                docVector[i][l[0]] = float(l[1])
                lineCounter = lineCounter + 1
    f.close()
                
def loadIdf():
    global idf
    f = open("idf.txt", "r", encoding='utf-8')
    data = f.readlines()
    for lineCounter in range(len(data)):
        l = data[lineCounter].split()
        idf[l[0]] = float(l[1])
    f.close()

def loadInvInd():
    global invind
    f = open("invind.txt", "r", encoding='utf-8')
    data = f.readlines()
    for lineCounter in range(len(data)):
        l = data[lineCounter]
        split = l.find(" ")
        key = l[0:split]
        docs = l[split+1:]
        docList = ast.literal_eval(docs)
        invind[key] = docList
    f.close()

#create a list of the results file for our cran queries
#to use in testing performance measures
def indexcranqrel():
  global relDict
  queryNum = 0
  file = open("cranqrel", "r", encoding='utf-8')
  #open cranqrel file and separate it by lines
  data = file.readlines()

  #go through line by line
  for line in data:
    #each line contains three numbers
    #query number, document number, relevancy of document
    line = line.split()
    #save query number
    queryNum = line[0]
    queryNum = str(queryNum)
    #remove the query number from the line
    del line[0]
    #save the doc and the relevancy
    relDoc = str(line[0])
    relevency = str(line[1])
    #create a tuple to be added to list
    tup = (relDoc, relevency)
    #only adding relevancies of 1, 2, or 3
    if relevency == "3" or relevency == "2" or relevency == "1":
      keyFound = relDict.get(queryNum, 0)
      #if their is not a list for this query number
      #create it and add the tuple we saved
      if keyFound == 0:
        relDict[queryNum] = [tup]
      #else, append the tuple to the existing list
      else:
        relDict[queryNum].append(tup)


  #print("rel" , relDict["1"])
      
#function to count the number of true positives,
#false positives, and false negatives to be used
#to measure our performace
def cranCompare(queryNumber):
  global relDict
  global cossim
  #true pos = this document was found and it is in our expected results
  global tp
  #false negative - in expected results, but we didn't find it in our search
  global fn
  #false pos - document was found, but it is not our expected results
  global fp

  tpList = []

  #print("expeted results")
  #for rel in relDict[queryNumber]:
   #print(rel[0])

  #print("retrieved")
  #for doc in cossim:
    #docnum = str(doc[1] + 1)
    #print(docnum)
          
  #print(newlist)
  #loop through our list of documents that were found
  for doc in cossim:
    docTP = False
    #adjust number, since it refers to position in list, must add 1 to make them compare
    #change to string type for comparison
    docnum = str(doc[1] + 1)
    #loop through each expected document for the given query number
    for rel in relDict[queryNumber]:
      #doc is found by the search and is in the expected results, so true positive
      if docnum == rel[0]:
        tp = tp + 1
        #keep track of tps in a list to check for 
        #false negatives after loop is complete
        tpList.append(rel[0])
        docTP = True   
        
    #if the doc is not a tp, it must be a false pos
    if docTP == False:
      fp = fp + 1
      docTP == True

  #print("tplist: ", tpList)
  #loop through expected results to determine false negatives
  for rel in relDict[queryNumber]:
    #check each tp val we found
    if rel[0] not in tpList:
      #if relevant doc wasn't a tp, must be a false neg
      fn = fn + 1

  


  #print("tp",tp)
  #print("fn",fn)
  #print("fp",fp)




def main():
    #print("main start!!!!!!!!!!!!!!!!")
    
    #startlink = "https://www.muhlenberg.edu"
    #websites = [startlink]
    #crawl(websites)
    splitCranDocs()
    splitCranQs()

    buildVectors()

    indexcranqrel()

    #write contents of urlSeen, vectors, idf, and invind to files
    #saveData()

    #load the contents of our saved files for our corpus
    #loadData()

    for qNum in cranQry:
      if str(qNum) in relDict:
        qString = cranQry[qNum]
        qvector = getQuery(qString)
        calcCosSim(qvector)
        cranCompare(str(qNum))

    print("tp: ", tp)
    print("fn: ", fn)
    print("fp: ", fp)

    precision = tp / (tp+fp)
    recall = tp / (tp+fn)

    print("precision:", precision)
    print("recall:", recall)

    global docIndex
    print("len of doc index", len(docIndex))

main()