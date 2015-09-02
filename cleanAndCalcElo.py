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

debug = True
eloCache = {}
gameDateCache = {}

def getPrevGameForTeam(team, date):
    global games
    game = games[((games['home']==team) | (games['away']==team)) & (games['date'] < date)].tail(1)
    return game


def getPrevEloForTeam(team, date):
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

def doEloUpdate(game):
    date = game['date']
    homePre = getPrevEloForTeam(game['home'], date)
    awayPre = getPrevEloForTeam(game['away'], date)

    #if its been two months since your last game, lets adjust that to norm (end of season breaks)
    if game['home'] in gameDateCache and (date - gameDateCache[game['home']]).days > 60:
            homePre = math.floor(.75*homePre + 375)
    if game['away'] in gameDateCache and (date - gameDateCache[game['away']]).days > 60:
        awayPre = math.floor(.75*awayPre + 375)

    k = getKForCompetition(game['comp'], game['rnd'], game['country'])
    tup = calcPostElo(homePre, awayPre, game['hScore'], game['aScore'], game['neutralSite'], k)

    #store these for quick retrieval (eloCache was already declared as global)
    eloCache[game['home']], eloCache[game['away']] = tup
    game['hElo'] , game['aElo'] = tup

    return game

if __name__ == "__main__":

    translate = {"ecosse": "scotland", "angleterre":"england", "espagne": "spain", "italie": "italy", "allemagne": "germany", "pays-de-galles": "wales", "croatie" : "croatia", "pays-bas" : "holland"}
    frames = []
    for i in range(0, 99):
        csv = "data/games"+str(i)+".csv"
        try:
            toAdd = pd.read_csv(csv)
        except IOError:
            if debug:  
                print("nofile", csv)
            continue
        frames.append(toAdd)
    games = pd.concat(frames)

    #mid's are not unique on website, filter by teams as well
    games = games.drop_duplicates(subset = ['mid', 'home', 'away'])
    if debug:
        print("dropped dups", len(games))



    ##make the dateStrings datetimes and sort the db by that
    games['date'] = pd.to_datetime(games.pop('date'))
    games = games.sort("date")
    games['country'] = games['country'].apply(lambda x: translate[x] if x in translate else x)

    count = 0
    if debug:
        print("calculating elo", len(games))
    games = games.apply(doEloUpdate, axis = 1)
    games.to_csv("data/games.csv", index=False)     
