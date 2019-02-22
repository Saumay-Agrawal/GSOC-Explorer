import requests
from bs4 import BeautifulSoup
import logging
import pymongo
import sys
import os
from pprint import pprint
import json

if(os.path.exists('./scrapper2.log')):
    os.remove('./scrapper2.log')

SEED = sys.argv[1]
DBNAME = sys.argv[2]
COLNAME = ''

logging.basicConfig(filename='scrapper2.log', format='%(asctime)s [%(levelname)s]\t: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

logging.info('Seed link: {}'.format(SEED))
logging.info('Database name: {}'.format(DBNAME))
# logging.info('Collection name: {}'.format(COLNAME))

client = pymongo.MongoClient('mongodb://localhost:27017/')
db =  client[DBNAME]
col = None

def scrapeArchive(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    for element in soup.select('span.mdl-list__item-primary-content a'):
        scrapeOrgList('https://www.google-melange.com' + element['href'], element.text)

def scrapeOrgList(link, year):
    COLNAME = 'year' + year
    col = db[COLNAME]
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    org_count = 0
    for element in soup.select('span.mdl-list__item-primary-content a'):
        org_count += 1
        scrapeOrgPage('https://www.google-melange.com' + element['href'], org_count, col)

def scrapeOrgPage(link, org_id, col):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    soup = soup.select('div.main')[0]
    org = {}
    org['_id'] = org_id
    org['name'] = soup.select('h3')[0].text
    if (soup.select('img')):
        org['logo'] = 'https://www.google-melange.com' + soup.select('img')[0]['src']
    org['num_projects'] = len(soup.select('span.mdl-list__item-primary-content'))
    p = soup.select('p')
    if (p[0].text.find('License')<0):
        p = [''] + p
    if (p[1].text.find('Website')>=0):
        org['website'] = p[1].select('a')[0]['href']
    else:
        p = [''] + p
    org['mailing_list'] = p[2].text
    org['mailing_list'] = org['mailing_list'][org['mailing_list'].find(':')+1:]
    org['description'] = ' '.join([i.text for i in p[3:]])
    x = col.insert_one(org)
    print(x.inserted_id)


scrapeArchive(SEED)