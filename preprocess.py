import re
from nltk.stem.porter import *

stemmer = PorterStemmer()
#takes html code and extracts text that appears on the
#webpage that a user would be searching for
#cleans the text to shrink the number of unique tokens
# f = filename
def preprocess(f):
  global doStem
  global doStopWords
  #tags we want to get rid of
  #may contain text in tags that will be caught by our regex

  #open our webpage we crawled
  d = open(f, "r")
  #tokenize by tags
  doc = d.read()
  contents = doc.split("<")
  #close the file and reopen in write mode
  #to add text we find to 
  d.close()
  
  #for now, opening file under another name
  cf = re.sub(r"\.txt", r"clean.txt", f)
  cleandoc = open(cf, "w")
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
        #fixing some html language
        text = re.sub(r"&amp;|&\s", r"and", text)
        text = re.sub(r"&rsquo;", r"'", text)
        text = re.sub(r"&lsquo;", r"'", text)
        #copyright logo - remove
        text = re.sub(r"&copy;", r"", text)
        #getting rid of possessives
        text = re.sub(r"'s", r"", text)
        #remove puncuation
        text = re.sub(r"[\(\)\[\]\{\},';:\"?!\|\<\>]", r"", text)
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
          #call the porter stemmer
          text = stemmer.stem(text)

        #write it to the doc
        cleandoc.write(text)
        cleandoc.write("\n")

  #close the new doc
  cleandoc.close()
  #call the index function to add to our inverted index
  index(cf)