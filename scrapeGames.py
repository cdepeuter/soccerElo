'''
    File name: scrapeGames.py
    Author: cdepeuter
    Inputs Int lowerBound, Int upperBound, Int fileNr

    This file loops through all rounds in the allRounds.csv file and scrapes all games of each round.
    As there are over 100,000 individual webpages to scrape it is recommended to use the inputs of 
    this function and split the work across multiple processes. 
    Ex: "python scrapeGames.py 10000 20000 14 will put the games from the 10000th to 20000th rounds in
    data/games14.csv
'''

import requests
import sys
from StringIO import StringIO
import numpy as np
import pandas as pd # pandas
import matplotlib.pyplot as plt # module for plotting 
import datetime as dt # module for manipulating dates and times
import numpy
import urllib2
import cookielib
import urlparse
from datetime import datetime
import pymongo
from pymongo import MongoClient
import csv as csv
import fr


allRounds = []
csvfile = "data/allRounds.csv"
with open(csvfile, 'r') as f:
    for line in f.readlines():
        allRounds.append(line)

print(len(allRounds))

gameId = 0
col = ["mid", "date","ref","home","hScore","aScore","away","comp","country","rnd","ot","pks","homePks","awayPks","hElo","aElo","compType","neutralSite","url"]
games = pd.DataFrame(columns=col)
missedRounds = []
print games
c = None


debug = True

def getGamesForRound(s):
    global db
    global debug
    global getAllYears
    global gameId
    global missedRounds


    comp, country, year, rnd = s.split(".")[2:6]
    rnd2 = "" if rnd is None else rnd
    soup = fr.read("http://www.footballdatabase.eu/"+s)


    gamesThisRound = 0
    s = s.encode('ascii','ignore')
    sSp = s.split(".")
    gameTable = soup.find("table", class_="fondsoustitrembleu488")
    if gameTable is not None:
        rows = gameTable.find_all("tr")
        badYears = [str(y) for y in range(1860,1900)]
        for i, g in enumerate(rows):

            #while looping through rows keep track of current date
            dateFind = g.find("td", class_="styledatebleu")
            if dateFind != None:
                dfTxt = dateFind.text
                if " ovember" in dfTxt:
                    print("ovember november")
                    dfTxt = dfTxt.replace(" ovember", "November")
                if "In " in dfTxt:
                    #sometimes date just says "in june 2015", just make it first of month/year

                    if len(dfTxt.strip("In "))==4:
                        #just a year "in 1995"
                        dfTxt = dfTxt.strip("In ")
                        d = datetime.strptime(dfTxt, "%Y")
                    else:
                        dfTxt = "01 "+dfTxt.strip("In").strip()
                        d = datetime.strptime(dfTxt, "%d %B %Y")
                elif any(x in dfTxt for x in badYears):
                    print("WOW EARLY ROUND")
                    d = datetime(1900,01,01)
                else:  
                    d = datetime.strptime(dfTxt, "%A %d %B %Y")
            else:
                #this isnt a daterow, its a game
                home = away = ref = homeScore = awayScore = season = compType = url = ""
                ot = pks = neutral = False
                homePks = awayPks = det = tds2 = None
                mid=0

                tds = g.find_all("td")
                if len(tds) > 10:
                    refT = tds[0]; homeT = tds[5]; homeS = tds[6]; awayS = tds[7]; awayT = tds[8];
                    home = homeT.a['href'].split(".")[2]
                    homeScore = int(homeS.getText())
                    awayScore = int(awayS.getText())
                    away = awayT.a['href'].split(".")[2]
                    if refT.a["href"] is not "":
                        ref = refT.a["href"].strip("football.arbitres.").strip(".en.html")
                        #print ref

                    #check the next row, if its another stlemneutre there might be game details (pks or et)
                    if i < len(rows)-1:
                        nextGame = rows[i+1]
                        det = nextGame.find("span", class_="detailsr")
                        if det is not None:
                            det = det.getText()
                            if "on penalties" in det:
                                ot = True
                                pks = True
                                tds2 = nextGame.find_all("td")
                                homePks = int(tds2[2].getText())
                                awayPks = int(tds2[3].getText())
                            elif "After Extra Time" in det:
                                ot = True
                    
                    #is the game at a neutral site???
                    #if cup ???, i guess non cup would just have round nrs
                    #friendls too ughh
                    if True:
                        if rnd.startswith('fina'):
                            neutral = True
                        else:
                            neutral =  False
                    else:
                        neutral = False
                    
                    #get url and footballdatabase mid
                    url = homeS["onclick"].strip("window.location=")
                    mid = int(homeS["onclick"].strip("window.location=").split(".")[-3])
                    #print(mid, url)
                    #col = ["date", "ref", "home", "hs", "aways", "away", "comp", "country", "rnd", "ot", "pks", "homePks", "awayPks", "hElo", "aElo", "compType", "neutralSite", "url"]
                    row = [mid, d.strftime("%d/%m/%Y"), ref, home, homeScore, awayScore, away, comp, country, rnd,  ot, pks, homePks, awayPks, 0, 0, "club-domestic", neutral, url]
                    #tdb.insert_one({"date": d.strftime("%d/%m/%y"), "ref": ref, "home":home, "hs": homeScore, "aways":awayScore,\
                                #  "away": away, "comp":league, "ot":ot, "pks":pks, "homePks":homePks, "awayPks":awayPks, "hElo":0, "aElo":0})
                    #print gameId
                    #print(row)
                    games.loc[gameId] = row
                    gameId += 1
                    gamesThisRound += 1
    if gamesThisRound == 0:
        #print("no games in this one", rnd)
        missedRounds += [s]
    if debug:
        print("number of games ", gamesThisRound)
    return games


#grab params from input or default
if len(sys.argv) > 3:
    args = sys.argv
elif len(sys.argv) == 3:
    args = sys.arg.append(99)
else:
    args = ["", 0, len(allRounds), 98]
lowerBound, upperBound , fileNr = args[1:4]
csvfile = "games"+str(fileNr)+".csv"



print("going through rounds: ", lowerBound, upperBound)
for i, rnd in enumerate(allRounds):
    if i in range(int(lowerBound), int(upperBound)):
        if i % 100 == 0:
            print(i, rnd, len(games))
        rnd = rnd.strip('"')
        if rnd != "" and len(rnd) > 5:
            #print(tup, r, i, gameId)
            getGamesForRound(rnd)
        
    if i % 5000 == 0:
        print("dumping to csv")
        games.to_csv("data/dump"+ csvfile, encoding='utf-8')

        ms = pd.Series(missedRounds)
        ms.to_csv("data/missedDump" + csvfile, encoding='utf-8')

print("b4 dups", len(games))
games.drop_duplicates()
print("aftr dups", len(games))

print("printing to file:", csvfile)
games.to_csv("data/"+csvfile, encoding='utf-8', index=False)

ms.to_csv("data/missed"+csvfile, encoding='utf-8', index=False)
print("OK ALL DONE")


