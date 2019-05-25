from requests_html import HTMLSession
from bs4 import BeautifulSoup
import time
import json
import pandas as pd
from collections import defaultdict
import sys
import os
import random

def main():
    session = HTMLSession()
    playersFile = os.path.dirname(sys.argv[0])+"\Alertas.txt"
    eventName='cambioprecio'
    eventKey='maQ1nRPA8kfhWsT83ogV_IqGw6d55k7JCVRNUW72rHb'
    #eventName=input("\nPor favor, ingresa el nombre de tu evento IFTTT\n")
    #eventKey=input("\nPor favor, ingresa el código de tu evento IFTTT\n")
    a = 'OK'
    b = 1
    sleep = 20
    while a == 'OK':
        print('Chequeando...\n')
        parseFile(playersFile,session, alert=True,eventName=eventName,eventKey=eventKey)
        hora = time.strftime("%H:%M")
        print('\nFinalizado. En', sleep, 'minutos comenzará un nuevo chequeo. Hora último chequeo:', hora, '\n')
        time.sleep(sleep*60)      
        b += 1
        
def parseFile(playersFile,session,**kwargs):
    players = open(playersFile, "r")
    player = players.readline()
    if 'alert' in kwargs:
        while player:
            playersAtTargetPrice={}
            data = player.split()
            try:
                infoAdicional = data[0]
                if infoAdicional == '@':
                    player = players.readline()
                    continue
                playerID = data[1]
                console = data[2]
                condition = data[3]
                condition = condition.upper()
                targetAlertPrice = float(data[4])
                player_name,livePrice,photo=price_scrape(playerID,console,session)
                print(player_name)
                if condition == "MENOR" and livePrice<=targetAlertPrice:
                    playersAtTargetPrice["value1"] = player_name
                    playersAtTargetPrice["value2"]= "{:,}".format(livePrice).replace(",",".") + ' monedas. ¡Compralo ahora! 🛒'
                    playersAtTargetPrice["value3"] = photo
                if condition == "MAYOR" and livePrice>=targetAlertPrice:
                    playersAtTargetPrice["value1"] = player_name
                    playersAtTargetPrice["value2"]= "{:,}".format(livePrice).replace(",",".") + ' monedas. ¡Vendelo ahora! 💰'
                    playersAtTargetPrice["value3"] = photo
                if len(playersAtTargetPrice)>0:
                    alert(kwargs["eventName"], kwargs["eventKey"], playersAtTargetPrice, session)
            except :
                print("File Not Formatted Properly")
                sys.exit()
            time.sleep(1)
            player = players.readline()
        players.close()
        return playersAtTargetPrice
    
def price_scrape(playerID,console,session):
    link = 'https://www.futbin.com/19/player/'
    link = link + playerID
    r = session.get(link)
    soup = BeautifulSoup(r.content, "lxml")
    tagPrice = soup.find("div", id="page-info")
    tagName = soup.find("span", {"class": "header_name"})
    tagRating = soup.find("div", id="page_comment_description")
    tagPicture = soup.find("div", id="page_comment_picture")
    tagVersion = soup.find("div", id="version0")
    photo = tagPicture["data-picture"]
    preRating = tagRating["data-description"]
    version = tagVersion["data-version"]
    version = version.upper()
    version = version.replace(" GOLD","")
    version = version.replace(" SILVER","")
    version = version.replace(" BRONZE","")
    version = version.replace("UCL_TOTT","TOTGS")
    version = version.replace("UCL_NON_RARE","UCL")
    version = version.replace("UCL_RARE","UCL")
    version = version.replace("_"," ")
    version = ' ' + version
    if version == " ":
        version = ''
    rating = "".join([x for x in preRating if x.isdigit()])
    playerNamePrevio = tagName.text
    player_name = playerNamePrevio + version + ' - ' + rating
    player_id = tagPrice["data-player-resource"]
    prices = json.loads(session.get(link[:26]+"playerPrices?player=" + player_id).text)
    livePrice = int(prices[player_id]["prices"][console]["LCPrice"].replace(",", ""))
    r.close()
    return player_name, livePrice, photo

def alert(eventName,eventKey,playersAtTargetPrice,session):
    session.post(f"https://maker.ifttt.com/trigger/{eventName}/with/key/{eventKey}",data=playersAtTargetPrice)

if __name__=="__main__":
    main()
