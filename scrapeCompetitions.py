'''
    File name: scrapeCompetitions.py
    Author: cdepeuter

    This file scrapes all competitions from module_choixcompet and puts them in a file called competitions.csv
'''


import requests
from StringIO import StringIO
import pandas as pd 
import numpy as np 
import datetime as dt # module for manipulating dates and times
import urlparse
from datetime import datetime
#import pymongo
#from pymongo import MongoClient
import csv
from unidecode import unidecode
import urllib
import fr

opener = fr.getOpener()

#collect all the countries using the module_choixcompet
countries = []
for i in range(0,10):
    for q in range(0,57, 7):
        url ="http://www.footballdatabase.eu/module_choixcompet.php?cont="+str(i)+"&paysaff="+str(q)
        print url
        s = fr.read(url)
        a = s.find_all("iframe")
        for ab in a:
            if ab['src'] != "":
                countries += [ab['src']]
        


# In[37]:
#for each country find all the competitions
competitions = []
for c in countries:
    for r in range(0,42,7):
        #print(r, c)
        #theyve got french chars
        c = unidecode(c)
        url = "http://www.footballdatabase.eu/"+c+"&compaff="+str(r)
        url = url.replace(" ", "%20")
        #print url
        s = fr.read(url)
        added = 0
        sq = s.find_all("a", class_="lienbascompetition")
        for a in sq:
            if "module_choixcompet" not in a['href']:
                if a['href'] not in competitions:
                    added += 1 
                    print("added this comp", a['href'])
                    competitions += [a['href']]
                #else:
                    
                    #print("duplicate", c)
        if added == 0:
            if r > 21:
                #not too many comps even get close, but the impt ones do
                break
                print("forget this country", c)
    r = 0
    
    #print("tot", len(competitions))
#print(competitions, len(competitions))

print("done")

csvfile = "data/competitions.csv"
#lets save all these urls to read from 
competitions = np.asarray(competitions)
np.savetxt(csvfile, competitions, delimiter=",", fmt="%s")
print("CSV saved")

