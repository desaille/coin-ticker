#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
import epd2in13
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Valeurs des Cryptomonnaies
ETHBAL = float(1)
BTCBAL = float(0.55)
# Investissement initial (euros)
BASE = float(2700)

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

    while True:
        # API call ETH value 
        gETH = requests.get('https://api.coinmarketcap.com/v1/ticker/ethereum/?convert=EUR')
        if gETH.status_code == 200:
            ETH = json.loads(gETH.text)
        else:
            ETH = 0
        gBTC = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert=EUR')
        if gBTC.status_code == 200:
            BTC = json.loads(gBTC.text)
        else: 
            BTC = 0
        gBLK = requests.get('https://blockchain.info/fr/q/getblockcount')
        if gBLK.status_code == 200:
            BTCBLK = gBLK.text
        else:
            BTCBLK = 0  

        # Check si la connexion internet est fonctionnelle
        if connection_check():
            WAN = 'OK'
        else:
            WAN = 'FAIL'
        
        # Traitements et calculs des valeurs 
        # ETHEREUM
        ETH_PRICE_NOW = float(ETH[0]['price_eur'])
        ETH_PRICE_1H = ETH_PRICE_NOW - ((float(ETH[0]['percent_change_1h']) / 100) * ETH_PRICE_NOW)
        ETH_PRICE_24H = ETH_PRICE_NOW - ((float(ETH[0]['percent_change_24h']) / 100) * ETH_PRICE_NOW)
        ETH_PRICE_7D = ETH_PRICE_NOW - ((float(ETH[0]['percent_change_7d']) / 100) * ETH_PRICE_NOW)
        ETH_EUR_NOW = ETHBAL * ETH_PRICE_NOW
        ETH_EUR_1H = ETHBAL * ETH_PRICE_1H
        ETH_EUR_24H = ETHBAL * ETH_PRICE_24H
        ETH_EUR_7D = ETHBAL * ETH_PRICE_7D
        # BITCOIN
        BTC_PRICE_NOW = float(BTC[0]['price_eur'])
        BTC_PRICE_1H = BTC_PRICE_NOW - ((float(BTC[0]['percent_change_1h']) / 100) * BTC_PRICE_NOW)
        BTC_PRICE_24H = BTC_PRICE_NOW - ((float(BTC[0]['percent_change_24h']) / 100) * BTC_PRICE_NOW)
        BTC_PRICE_7D = BTC_PRICE_NOW - ((float(BTC[0]['percent_change_7d']) / 100) * BTC_PRICE_NOW)
        BTC_EUR_NOW = BTCBAL * BTC_PRICE_NOW
        BTC_EUR_1H = BTCBAL * BTC_PRICE_1H
        BTC_EUR_24H = BTCBAL * BTC_PRICE_24H
        BTC_EUR_7D = BTCBAL * BTC_PRICE_7D
        # TOTAL EUR
        TOTALEUR_NOW = ETH_EUR_NOW + BTC_EUR_NOW
        TOTALEUR_1H = ETH_EUR_1H + BTC_EUR_1H
        TOTALEUR_24H = ETH_EUR_24H + BTC_EUR_24H
        TOTALEUR_7D = ETH_EUR_7D + BTC_EUR_7D
        # TOTAL PERCENT VARIATION
        PERCENT_TOTAL_NOW_FROM_BASE = (TOTALEUR_NOW - BASE) / BASE * 100
        PERCENT_TOTAL_NOW_FROM_1H = (TOTALEUR_NOW - TOTALEUR_1H) / TOTALEUR_1H * 100
        PERCENT_TOTAL_NOW_FROM_24H = (TOTALEUR_NOW - TOTALEUR_24H) / TOTALEUR_24H * 100
        PERCENT_TOTAL_NOW_FROM_7D = (TOTALEUR_NOW - TOTALEUR_7D) / TOTALEUR_7D * 100
        # Initialisation Afficheur (mode partial update)
        epd.init(epd.lut_partial_update)
        image = Image.new('1', (255, 128), 255)
        draw = ImageDraw.Draw(image)
        # Gestion Police
        color = 0
        police = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
        big = ImageFont.truetype(police, 60)
        medium = ImageFont.truetype(police, 25)
        small = ImageFont.truetype(police, 16)
        # Generation de l'image a afficher
        draw.text((10, 0), time.strftime('%H:%M'), font = small, fill = 0)
        draw.text((183, 0), 'WAN '+ str(WAN), font = small, fill = 0)
        draw.text((115, 10), 'jour', font = small, fill = color)
        draw.text((70, 20), str("%.2f" % PERCENT_TOTAL_NOW_FROM_24H), font = big, fill = color)
        draw.text((10, 80), 'heure', font = small, fill = color)
        draw.text((10, 95), str("%.2f" % PERCENT_TOTAL_NOW_FROM_1H), font = medium, fill = color)
        draw.text((95, 80), 'semaine', font = small, fill = color)
        draw.text((95, 95), str("%.2f" % PERCENT_TOTAL_NOW_FROM_7D), font = medium, fill = color)
        draw.text((200, 80), 'base', font = small, fill = color)
        draw.text((193, 95), str("%.2f" % PERCENT_TOTAL_NOW_FROM_BASE), font = medium, fill = color)
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
