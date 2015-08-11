'''
    File name: fr.py
    Author: cdepeuter

    This file contains the cookie storing and url reading functions
'''


import urllib2
import cookielib
from bs4 import BeautifulSoup


c = None
opener = None
def getCookieJar():
    #get my cookies
    global c
    if c is None:
        url = "http://www.footballdatabase.eu/index.php?m=cdepeuter&autolog=c097b7115c69b22950cf665cafe0c8ff" 
        print url
        c = cookielib.CookieJar()  
        opener = getOpener()
        home = opener.open(url)    
    return c

def getOpener():
    global opener
    cj = getCookieJar()
    if opener is None:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    return opener

def read(url):
    
    opener = getOpener()
    soup = BeautifulSoup(opener.open(url).read(), "html.parser")
    return soup
