#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
import epd2in13
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def connection_check():
    try:
        requests.get("http://google.com", timeout=3)
        return True
    except requests.ConnectionError:
        pass

    return False

def main():
    # Initialisation de l'afficheur
    epd = epd2in13.EPD()
    epd.init(epd.lut_full_update)
    epd.clear_frame_memory(0xFF)
    # Affichage d'une image noire pour "nettoyer" l'ecran
    image = Image.open('/opt/coin-ticker/start.bmp')
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()

    NH_WALLET   = ''
    NH_API_KEY  = ''
    NH_API_ID   = ''
    ETHOS_ID    = ''

    while True:
        # Check si la connexion internet est fonctionnelle
        if connection_check():
            WAN = 'OK'
        else:
            WAN = 'FAIL'

        # API call BTC value 
        gBTC = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert=EUR')
        if gBTC.status_code == 200:
            BTC = json.loads(gBTC.text)
        else: 
            BTC = 0

        # Recuperation des wallet balances
        gBTCBAL = requests.get('https://api.nicehash.com/api?method=balance&id=' + NH_API_ID + '&key=' + NH_API_KEY)
        if gBTCBAL.status_code == 200:
            BTCBAL = float(json.loads(gBTCBAL.text)['result']['balance_confirmed'])
        else: 
            BTCBAL = 0

        # Recuperation impayés et profitabilité
        gNH = requests.get('https://api.nicehash.com/api?method=stats.provider&addr=' + NH_WALLET)
        if gNH.status_code == 200:
            NH_UNPAID = float(json.loads(gNH.text)['result']['stats'][0]['balance'])
        else: 
            NH_UNPAID = 0

        gNHE = requests.get('https://api.nicehash.com/api?method=stats.provider.ex&addr=' + NH_WALLET)
        if gNHE.status_code == 200:
            NH_PROFITABILITY = float(json.loads(gNHE.text)['result']['current'][0]['profitability']) * 100
        else: 
            NH_PROFITABILITY = 0

        # Recuperation des hashrate ethos
        gETHOS = requests.get('http://' + ETHOS_ID + '.ethosdistro.com/?json=yes')
        if gETHOS.status_code == 200:
            ETHOS = json.loads(gETHOS.text)
        else: 
            ETHOS = 0

        # Traitements et calculs des valeurs 
        # BITCOIN
        BTC_PRICE_NOW = float(BTC[0]['price_eur'])
        BTC_EUR_NOW = BTCBAL * BTC_PRICE_NOW
        NH_PROFITABILITY_EUR_NOW = NH_PROFITABILITY * BTC_PRICE_NOW
        # Initialisation Afficheur (mode partial update)
        epd.init(epd.lut_partial_update)
        image = Image.new('1', (255, 128), 255)
        draw = ImageDraw.Draw(image)
        # Gestion Police
        color = 0
        police = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
        big = ImageFont.truetype(police, 60)
        medium = ImageFont.truetype(police, 25)
        xsmall = ImageFont.truetype(police, 10)
        small = ImageFont.truetype(police, 16)
        smalll = ImageFont.truetype(police, 20)
        # Generation de l'image a afficher
        draw.text((65, 0), time.strftime('%d/%m/%y // %H:%M // WAN ') + str(WAN), font = xsmall, fill = 0)
        draw.text((95, 10), 'hashrate', font = small, fill = color)
        draw.text((70, 20), str(ETHOS['total_hash']) + 'mh/s', font = medium, fill = color)
        draw.text((95, 45), 'balance', font = small, fill = color)
        draw.text((25, 57), str("%.5f" % BTCBAL) + ' btc (' + str("%.2f" % BTC_EUR_NOW) + ' eur)', font = smalll, fill = color)
        draw.text((10, 80), 'unpaid balance', font = small, fill = color)
        draw.text((10, 100), str("%.5f" % NH_UNPAID) + ' btc', font = small, fill = color)
        draw.text((160, 80), str("%.2f" % NH_PROFITABILITY_EUR_NOW) + ' eur/day', font = small, fill = color)
        draw.text((155, 100), str("%.0f" % BTC_PRICE_NOW) + ' eur/btc', font = small, fill = color)
        # Sauvegarde de l'image et rotation
        image.save('/opt/coin-ticker/image.jpg')
        rotate = Image.open('/opt/coin-ticker/image.jpg')
        result = rotate.rotate(90, expand = 1)
        result.save('/opt/coin-ticker/result.jpg')
        # Affichage et attente 
        epd.set_frame_memory(Image.open('/opt/coin-ticker/result.jpg'), 0, 0)
        epd.display_frame()
        epd.delay_ms(2000)
        time.sleep(30)

if __name__ == '__main__':
    # Attente de 30s avant de lancer le programme (temps pour le rapberry de se connecter au réseau au démarrage)
    time.sleep(30)
    main()
