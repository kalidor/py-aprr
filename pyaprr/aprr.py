#!/usr/bin/env python3

"""
# (c) 2020 Gregory Charbonneau
# distributes under the terms of the wtfpl (sam.zoy.org/wtfpl/)
#
"""
import requests
import urllib3
import sys, re, csv, json
from os.path import isfile, dirname, abspath
from os.path import join as pathjoin
from os import getenv
from datetime import datetime
from pkg_resources import resource_stream
from codecs import getreader

urllib3.disable_warnings()
# requests: http://docs.python-requests.org/en/master/

# https://www.data.gouv.fr/fr/datasets/r/ab5153d6-4ca4-483c-837e-611067e1fe65
# From https://www.data.gouv.fr/fr/datasets/gares-de-peage-du-reseau-routier-national-concede/

Exceptions = {}
Exceptions['STE HELENE'] = 'SAINT-HELENE'
Exceptions['ST QUENTIN FAL. BARR'] = 'ST QUENTIN FALLAVIER'
Exceptions['ST-GERMAIN-LAXIS'] = 'SAINT GERMAIN LAXIS'
DATA_FILE = 'data/peages-2017.csv'

class Peages():
    def __init__(self):
        print('[+] Peages initialization')
        self.f = resource_stream(__name__, DATA_FILE)
        utf8_reader = getreader("utf-8")
        self.gares = csv.DictReader(utf8_reader(self.f))
        num = 0
        for i in self.gares:
            num += 1
        num -= 1
        print('[+] {} gares'.format(num))

    def search(self, gare):
        self.f.seek(0) # Start from the beginning since csv.DirectReader is ... a reader
        data = None
        if "BARRIERE" in gare:
            gare = gare.replace("BARRIERE", "").strip()
        if gare in Exceptions.keys():
            gare = Exceptions[gare]
        for row in self.gares:
            if gare in row[' Nom gare '].strip():
                data = row[' Autoroute '].strip()
                #return(row[' Autoroute '], row[' Departement '], row[' Echangeur '], row[' Type '], row[' Nom gare '])
        if data:
            return data

    def __del__(self):
        try:
            self.f.close()
            print('[i] Closing peage file')
        except:
            print('[!] Cannot close peage file')

class APRR():
    def __init__(self, download, prox):
        try:
            f = open("{}/.config/aprr.cfg".format(getenv('HOME')))
            self.creds = json.load(f)
            f.close()
        except IOError:
            print("[!] File not accessible")
            sys.exit(1)

        if prox:
            proxy = {
                    'http'  : 'http://127.0.0.1:8080',
                    'https' : 'http://127.0.0.1:8080'
                    }
        else:
            proxy = {}
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'

        headers = {}
        headers['User-Agent'] = user_agent
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        headers['Accept-Language'] = 'en-US,en;q=0.5'

        # Thx cf
        self.s = requests.Session() # allow TCP reuse
        self.s.proxies = proxy
        self.s.verify = False
        self.s.headers = headers
        self.s.cookies.clear() # and cookie are saved automatically !!

        self.download = download
        self.peages = Peages()

        self.s.get('http://espaceclient.aprr.fr/', allow_redirects=True)
        r = self.s.get('https://espaceclient.aprr.fr/aprr/Pages/connexion.aspx', verify=False)

        pattern = r'<input type="hidden" name="([^"]*)" id="[^"]*" value="([^"]*)" '
        res = re.findall(pattern, r.text)
        a = {}
        for i in res:
            if i[0] == '__EVENTTARGET':
                a[i[0]] = 'ctl00$PlaceHolderMain$ConsoBlocTemplateControl$ConnexionAscx$LbnButtonConnection'
            else:
                a[i[0]] = i[1]
        a['ctl00$LanguagesControl$DdlLanguages'] = 'fr-FR'#https://espaceclient.aprr.fr/aprr/PublishingImages/Multilingue/_t/france_png.jpg'
        a['ctl00$PlaceHolderMain$ConsoBlocTemplateControl$ConnexionAscx$TbxLogin'] = self.creds['username']
        a['ctl00$PlaceHolderMain$ConsoBlocTemplateControl$ConnexionAscx$TbxPassword'] = self.creds['passwd']
        a['__spDummyText1'] = ''
        a['__spDummyText2'] = ''
        a['_wpcmWpid'] = ''
        a['wpcmVal'] = ''
        headers['Origin'] = 'https://espaceclient.aprr.fr'
        headers['Referer'] = 'https://espaceclient.aprr.fr/aprr/Pages/connexion.aspx'
        r = self.s.post('https://espaceclient.aprr.fr/aprr/Pages/connexion.aspx', data=a, allow_redirects=False)

        if (r.status_code == 302):
            print('[+] Authentication success!')
        else:
            print('[-] Authentication failed')
            sys.exit(0)

    def factures(self):
        # Factures
        print('Factures:')
        r = self.s.get('https://espaceclient.aprr.fr/aprr/Pages/MaConsommation/conso_factures.aspx')

        res = re.findall(r'<td class="tableElementCell">\s*(.*)\r\s*</td>\s*<td class="tableElementCell">\s*(.*)\r\s*</td>\s*<td class="tableElementCell">\s*(.*)\r\s*</td>', r.text)
        for i in res:
            print(i)
            # download pdf
            if not self.download:
                continue
            path = 'PDF/%s.pdf' % i[1].replace(' ', '_')
            if isfile(path):
                print('[i] Already got: %s' % path)
                sys.exit(0)
            r = self.s.get('https://espaceclient.aprr.fr/aprr/Pages/MaConsommation/conso_factures.aspx?facture=%s' % i[0])
            f = open(path, 'wb')
            f.write(r.content)
            f.close()
            print('[+] %s saved.' % path)

    def list_unpayed_trip(self):
        # Facture en attente de paiement
        r = self.s.post('https://espaceclient.aprr.fr/aprr/_LAYOUTS/APRR-EDGAR/GetTrajets.aspx', json={'startIndex':"1",'itemsCountInPage':"NaN"})
        if r.status_code != 200:
            print('[-] Received code {}'.format(r.status_code))
            return
        for t in r.json():
            _date = datetime.fromtimestamp(int(t['Date'].split('(')[1].split(')')[0][0:-3])).strftime('%d-%m-%Y %H:%M')
            _gare_entree = t['GareEntreeLibelle'].strip()
            _gare_sortie = t['GareSortieLibelle'].strip()
            _autoroute_entree = self.peages.search(_gare_entree)
            _autoroute_sortie = self.peages.search(_gare_sortie)
            _classe = t['ClasseVehicule'].strip()
            _prix = t['MontantHorsRemiseTTC'].strip()
            print('{}: {}({}) -> {}({}) [{}] - {}'.format(_date, _gare_entree,_autoroute_entree, _gare_sortie,_autoroute_sortie, _classe, _prix))
        #print(r.json())

