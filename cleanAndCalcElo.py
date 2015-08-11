'''
    File name: cleanAndCalcElo.py
    Author: cdepeuter

    This file takes all the games in the games##.csv files (0-99), puts them in one dataframe, 
    converts the dates to datetimes, sorts by date, then starting from the first date it calculates the 
    post match elo ratings for each team, for every game. It then stores the cleaned/elo calculated data
    in games.csv

'''

import pandas as pd
import numpy as np
import math
import time
from datetime import datetime
import pandas as pd

def getPrevGameForTeam(team, date):
    global games
    game = games[((games['home']==team) | (games['away']==team)) & (games['date'] < date)].tail(1)
    return game


def getPrevEloForTeam(team, date):
    global eloCache
    if team in eloCache:
        return eloCache[team]
    g = getPrevGameForTeam(team, date)
    if len(g) == 0:
        #if this is their first game then their elo starts at 1500
        return 1500
    return g['hElo'].values[0] if team == g['home'].values[0] else g['aElo'].values[0]
    

def calcPostElo(homeElo, awayElo, homeScore, awayScore, neutral, k):
    if homeScore > awayScore:
        w = 1.0
    elif homeScore == awayScore:
        w = .5
    else:
        w = 0

    we = 1/(10**-((homeElo+(not neutral)*100-awayElo)*1.0/400) + 1)
    if abs(homeScore - awayScore) <= 1:
        g = 1
    elif abs(homeScore - awayScore) == 2:
        g = 1.5
    else:
        g = (11 +  abs(homeScore - awayScore))*1.0/8.0

    
    diff = math.floor(k*g*(w-we))
    return (homeElo + diff, awayElo - diff)


def getKForCompetition(comp, rnd, country):
    if comp == "(c1)-ligue-des-champions" or comp =="coupe-du-monde":
        if rnd == "finale":
            return 60
        else:
            return 50  
    elif comp == "(c3)-coupe-uefa" or (comp == "premier-league" and country == "england") or \
        (comp.find("elimin") and country == "international") or \
        (comp == "primera-division" and country == "spain") or \
        (comp == "serie-a" and country == "italy") or \
        (comp == "bundesliga" and country == "germany"):
        return 40

    elif "friendly" in comp:
        return 20
    else: 
        return 30


#keep track of how much time spent doing each task
setVals= 0
getElos = 0


def doUpdate(game):
    global count
    global setVals
    global getElos
    #t = time.time()
    date = game['date']
    homePre = getPrevEloForTeam(game['home'], date)
    awayPre = getPrevEloForTeam(game['away'], date)

    
    if game['home'] in gameDateCache and (date - gameDateCache[game['home']]).days > 60:
            homePre = math.floor(.75*homePre + 375)
    if game['away'] in gameDateCache and (date - gameDateCache[game['away']]).days > 60:
        awayPre = math.floor(.75*awayPre + 375)


    k = getKForCompetition(game['comp'], game['rnd'], game['country'])
    tup = calcPostElo(homePre, awayPre, game['hScore'], game['aScore'], game['neutralSite'], k)
    eloCache[game['home']], eloCache[game['away']] = tup
    #newTime = time.time()
    #getElos = getElos + newTime-t
    #if its been over a month and half since your last game, lets adjust that to norm (end of season breaks)

        
    #print("settin values")
    game['hElo'] , game['aElo'] = tup
    #finalTime = time.time()
    #setVals = setVals + finalTime - newTime
    #print(count, date, getElos, setVals)
    count = count +1
    #print("Se4")
       

    return game


translate = {"ecosse": "scotland", "angleterre":"england", "espagne": "spain", "italie": "italy", "allemagne": "germany", "pays-de-galles": "wales", "croatie" : "croatia", "pays-bas" : "holland"}


frames = []
i = 0
for i in range(0, 99):
    csv = "data/games"+str(i)+".csv"
    try:
        toAdd = pd.read_csv(csv)
    except IOError:
        print("nofile", csv)
        continue
    frames.append(toAdd)
    print(len(toAdd))
    i += len(toAdd)
    #d.append(toAdd)
    print(csv, len(frames))
#print(d)
games = pd.concat(frames)

print("before dups", len(games))
#mid's are not unique on website, filter by teams as well
games = games.drop_duplicates(subset = ['mid', 'home', 'away'])
print("dropped dups", len(games))


eloCache = {}
gameDateCache = {}

##make the dateStrings datetimes and sort the db by that
games['date'] = pd.to_datetime(games.pop('date'))
print(games.head())
games = games.sort("date")
print("translating country")
games['country'] = games['country'].apply(lambda x: translate[x] if x in translate else x)
print(games.head())

count = 0
print("looping through games")

games = games.apply(doUpdate, axis = 1)
games.to_csv("data/games.csv", index=False)     


print("done")