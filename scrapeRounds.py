'''
    File name: scrapeRounds.py
    Author: cdepeuter

    This file reads the csv file competitions.csv, and for each competition in the file
    it finds the years in which that competition happened. For each competition-year pair, 
    it then finds each individual round (Both are done using dropdowns on each page).  
    Finally, every round to scrape is saved in a file called allRounds.csv.

'''


import requests
from StringIO import StringIO
import numpy as np
import pandas as pd # pandas
import matplotlib.pyplot as plt # module for plotting 
import datetime as dt # module for manipulating dates and times
import numpy
import urlparse
from datetime import datetime
import pymongo
from pymongo import MongoClient
import csv as csv
from unidecode import unidecode
import urllib
import fr




competitions = []
csvfile = "data/competitions.csv"
with open(csvfile, 'r') as f:
    for line in f.readlines():
        competitions.append(line)
debug = True


def getRelatedYearsForCompetition(s):
    #for each competition, we need to get the years which this competition happened 
    #theres a dropdwon for that
    global debug
    global missed
    url = "http://www.footballdatabase.eu/"+s
    years = []
    if debug:
        print("get related years for ", url)
    soup = fr.read(url)
    #print soup
    
    select = soup.find("select", {"name": "num__division"})
    #print select
    if select is not None:
        vals =  select.findChildren()
        for v in vals:
            if v["value"] is not None and v["value"] is not "":
                years.append(v["value"])
    else:
        #dont forget if it only happens once
        years.append(s)
    if debug:
        print("these are the related years for ", years)
    return years


newRounds = []
print("getting years for each comp", len(competitions))
for s in competitions:
    #print("getting new years for ", s[0]+"."+s[1])
    newRounds += getRelatedYearsForCompetition(s)
print(len(newRounds))


def getRoundsForCompetitionYear(s):
    #for each competition + year, there differ specific rounds
    #theres also a dropdown for that
    global missedRC
    url = "http://www.footballdatabase.eu/"+s
    rounds = []
    soup = fr.read(url)
    select = soup.find("select", class_="choixjournee")
    if select is not None:
        vals =  select.findChildren()
        for v in vals:
            if v["value"] is not None and v["value"] is not "":
                rounds.append(v["value"])
    return rounds


toAdd = []
allRounds = []
print("getting rounds for each compYear", len(newRounds))
for q, rnd in enumerate(newRounds):
    if q in range(0,10000):
        if q % 100 == 0:
            print(q, rnd)
        toAdd = getRoundsForCompetitionYear(rnd)
        if len(toAdd) == 0:
            #no year dropdown, but this page probably has games
            toAdd = [rnd]
        for r in toAdd:
            r = unidecode(r)
            r = r.replace(" ", "%20")
            allRounds.append(r)
        #print("Adding this many rounds", rnd, len(toAdd))

    
print("done")

csvfile = "data/allRounds.csv"
#lets save all these urls to read from 
import csv
comps = pd.Series(allRounds)
comps.to_csv(csvfile, index = False)

print("CSV saved")

