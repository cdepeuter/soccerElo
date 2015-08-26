'''
    File name: scrapeRounds.py
    Author: cdepeuter

    This file reads the csv file competitions.csv, and for each competition in the file
    it finds the years in which that competition happened. For each competition-year pair, 
    it then finds each individual round (Both are done using dropdowns on each page).  
    Finally, every round to scrape is saved in a file called allRounds.csv.

'''

import pandas as pd
from datetime import datetime
import csv as csv
from unidecode import unidecode
import fr


def getRelatedYearsForCompetition(s):
    #for each competition, we need to get the years which this competition happened 
    #theres a dropdown for that
    global debug
    global missed

    url = "http://www.footballdatabase.eu/"+s
    years = []
    soup = fr.read(url)
    
    select = soup.find("select", {"name": "num__division"})
    if select is not None:
        vals =  select.findChildren()
        years += [v['value'] for v in vals if v['value'] is not None and v['value'] is not ""]
    else:
        #dont forget if it only happens once
        years += [s]
    if debug:
        print("num replated comps for " + url, len(years))
    return years


def getRoundsForCompetitionYear(s):
    #for each competition + year, theres specific rounds
    #if we go to the comp default page theres also a dropdown for that
    global missedRC
    url = "http://www.footballdatabase.eu/"+s
    rounds = []
    soup = fr.read(url)
    select = soup.find("select", class_="choixjournee")
    if select is not None:
        vals =  select.findChildren()
        rounds += [v['value'] for v in vals if v["value"] is not None and v["value"] is not ""]
    return rounds


if __name__ == "__main__":
    debug = True
    competitions = []

    with open("data/competitions.csv", 'r') as f:
        for line in f.readlines():
            competitions.append(line)

    newRounds = []
    for s in competitions:
        newRounds += getRelatedYearsForCompetition(s)

    toAdd = []
    allRounds = []
    if debug:
        print("getting rounds for each compYear", len(newRounds))
    for q, rnd in enumerate(newRounds):
        if q in range(0,10000):
            if q % 100 == 0 and debug:
                print(q, rnd)
            toAdd = getRoundsForCompetitionYear(rnd)
            if len(toAdd) == 0:
                #no year dropdown, but this page might have games (one year comp)
                toAdd = [rnd]
            for r in toAdd:
                r = unidecode(r)
                r = r.replace(" ", "%20")
                allRounds.append(r)
            
    comps = pd.Series(allRounds)
    comps.to_csv("data/rounds.csv", index = False)

    if debug:
        print("done", len(allRounds))
