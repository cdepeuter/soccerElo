'''
    File name: scrapeCompetitions.py
    Author: cdepeuter

    This file scrapes all competitions from module_choixcompet and puts them in data/competitions.csv
'''

import numpy as np 
import urlparse
from datetime import datetime
import csv
from unidecode import unidecode
import fr

if __name__ == "__main__":
    debug = True
    opener = fr.getOpener()

    #collect all the countries using the module_choixcompet
    countries = []
    for i in range(0,10):
        for q in range(0,57, 7):
            url ="http://www.footballdatabase.eu/module_choixcompet.php?cont="+str(i)+"&paysaff="+str(q)

            if debug:
                print(url)
                
            s = fr.read(url)
            a = s.find_all("iframe")
            countries += [ab['src'] for ab in a if ab['src']!= ""]
            
    #for each country, collect all the competitions
    competitions = []
    for c in countries:
        for r in range(0,42,7):
            #theyve got french chars
            c = unidecode(c)
            url = "http://www.footballdatabase.eu/"+c+"&compaff="+str(r)
            url = url.replace(" ", "%20")

            if debug:
                print(url)

            s = fr.read(url)
            sq = s.find_all("a", class_="lienbascompetition")
            competitions += [a['href'] for a in sq if "module_choixcompet" not in a['href'] and a['href'] not in competitions]
    
    #lets save all these urls to read from 
    competitions = np.asarray(competitions)
    np.savetxt("data/competitions.csv", competitions, delimiter=",", fmt="%s")
    if debug:
        print("CSV saved, # of comps: ",  len(competitions))

