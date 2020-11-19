# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 15:06:00 2019

@author: max kirin
"""

#creating a function to crawl a website
#and grab more links to crawl
#to create a document corpus
#demonstrating this method in the main function

import requests
from requests.exceptions import SSLError
import re

def crawl(websites, urlSeen):
    print("Crawling in process...")
    #counters for total url statistics
    totalabs = 0
    totalrel = 0
    #list of all redirection errors we come across, so we can abort them in the future
    urlError = []
    while len(urlSeen) < 20:
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
                
    print("Crawling complete")
    print("Number of pages retrieved: ", len(urlSeen))
    print("Relative URLs found: ", totalrel)
    print("Absolute URLs found: ", totalabs)
    print("Total URLs found: ", totalrel+totalabs)
    print("url errors: ", urlError)


def main():
    startlink = "https://www.muhlenberg.edu"
    websites = [startlink]
    urlSeen = []
    crawl(websites, urlSeen)
    
main()