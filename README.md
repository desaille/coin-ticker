# coin-ticker
https://desaille.fr/raspberry-pi-bitcoin-ticker/

Installer les dépendances python 

Pillow
Requests
Json
Time

Copier le repo dans /opt/coin-ticker

# Démarrage automatique
Copier le cointicker.sh dans /etc/init.d/
le rendre executable (chmod u+x /etc/init.d/cointicker.sh)
l'ajouter au runlevel default :
update-rc.d cointicker.sh defaults

