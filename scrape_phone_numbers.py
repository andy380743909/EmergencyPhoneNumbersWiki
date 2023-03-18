#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import os.path
import shutil
from pathlib import Path
try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x: x

import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString, Tag
import csv
   

def get_country_name(element):
    name = get_text_withouttag(element, 'span')
    return name

def get_all_phonenumbers(element):
    phones = element.find_all('b')
    result = []
    for phone in phones:
        text = get_text(phone)
        # Angola ambulance is "112/116", need split it
        split = text.split('/')
        result += split
    return result

def get_text_withouttag(element, tag):
    texts = []
    for t in element.children:
        if isinstance(t, NavigableString):
            texts.append(t)
        elif t.name == tag:
            continue
        else:
            texts.append(t.text)
    text = "".join(texts)
    return text

def get_text(element):
    text = "".join([t for t in element.contents if isinstance(t, NavigableString)])
    return text


URL = "https://en.wikipedia.org/wiki/List_of_emergency_telephone_numbers"
r = requests.get(URL)
   
soup = BeautifulSoup(r.content, 'html5lib')
   
countries=[]
   
tables = soup.find_all('table', attrs = {'class':'wikitable'}) 

for table in tables:
    
    tbody = table.tbody
    
    for row in tbody.find_all('tr'):
        
        tds = row.find_all('td')

        # print(row)
        print(tds)

        if len(tds) < 3:
            continue
        # if len(tds) < 3:
            # raise Exception(f'Error number of tds {len(tds)}')

        country = {}

        country_name = get_country_name(tds[0]).strip()
        country['country_name'] = country_name

        police = []
        ambulance = []
        fire = []
        notes = get_text_withouttag(tds[-1], 'sup').strip()

        td1 = tds[1]
        colspan = td1.get('colspan','1')
        print(colspan)
        if colspan == '1':
            print(1)
            police = get_all_phonenumbers(td1)
            td2 = tds[2]
            colspan = td2.get('colspan', '1')
            if colspan == '1':
                ambulance = get_all_phonenumbers(td2)
                td3 = tds[3]
                text = get_all_phonenumbers(td3)
                fire = text
            elif colspan == '2':
                td2 = tds[2]
                text = get_all_phonenumbers(td2)
                ambulance = text
                fire = text

        elif colspan == '2':
            print(2)
            text = get_all_phonenumbers(td1)
            police = text
            ambulance = text
            
            td2 = tds[2]
            fire = get_all_phonenumbers(td2)
        elif colspan == '3':
            print(3)
            text = get_all_phonenumbers(td1)
            police = text
            ambulance = text
            fire = text
        else:
            print(colspan)

        print(f"{country_name}, {police}, {ambulance}, {fire}, {notes}")

        country['country_name'] = country_name
        country['police'] = police
        country['ambulance'] = ambulance
        country['fire'] = fire
        country['notes'] = notes
        
        countries.append(country)

dst_path = Path(os.path.dirname(__file__))
with open(dst_path / 'wiki_emergency_phone_numbers.json', 'w', encoding='utf-8') as f:
    json.dump(countries, f, ensure_ascii=False, indent=4)

# filename = 'inspirational_quotes.csv'
# with open(filename, 'w', newline='') as f:
#     w = csv.DictWriter(f,['theme','url','img','lines','author'])
#     w.writeheader()
#     for quote in quotes:
#         w.writerow(quote)


