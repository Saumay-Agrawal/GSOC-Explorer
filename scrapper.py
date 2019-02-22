import requests
from bs4 import BeautifulSoup
import logging
import pymongo
import sys
import os
from pprint import pprint
import json

if(os.path.exists('./scrapper.log')):
    os.remove('./scrapper.log')

SEED = sys.argv[1]
DBNAME = sys.argv[2]
COLNAME = sys.argv[3]

logging.basicConfig(filename='scrapper.log', format='%(asctime)s [%(levelname)s]\t: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

logging.info('Seed link: {}'.format(SEED))
logging.info('Database name: {}'.format(DBNAME))
logging.info('Collection name: {}'.format(COLNAME))

client = pymongo.MongoClient('mongodb://localhost:27017/')
db =  client[DBNAME]
col = db[COLNAME]

def scrapeArchive(archive_link):
    page = requests.get(archive_link)
    soup = BeautifulSoup(page.content, 'html.parser')
    org_count = 0
    for org in soup.select('a.organization-card__link'):
        org_link = 'https://summerofcode.withgoogle.com' + org['href']
        org_count += 1
        logging.info('Org link #{} - {}'.format(org_count, org_link))
        scrapeOrgPage(org_link, org_count)

def scrapeOrgPage(org_link, org_id):
    page = requests.get(org_link)
    soup = BeautifulSoup(page.content, 'html.parser')
    org = {}
    org['_id'] = org_id
    org['name'] = soup.select('h3.banner__title')[0].text
    org['website'] = soup.select('a.org__link')[0]['href']
    org['logo'] = json.loads(soup.select('org-logo')[0]['data'].replace("'", "\""))
    org['logo']['image_url'] = 'http:' + org['logo']['image_url']
    org['tagline'] = soup.select('h4.org__tagline')[0].text
    org['description'] = soup.select('div.org__long-description')[0].text
    org['technologies'] = list(map(lambda x: x.text, soup.select('li.organization__tag--technology')))
    org['category'] = soup.select('li.organization__tag--category')[0].text
    org['topics'] = list(map(lambda x: x.text, soup.select('li.organization__tag--topic')))
    org['num_projects'] = len(soup.select('md-card.archive-project-card'))
    x = col.insert_one(org)
    print(x.inserted_id)
    # pprint(org)

scrapeArchive(SEED)
