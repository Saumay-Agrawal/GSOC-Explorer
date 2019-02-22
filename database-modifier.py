import pymongo
from pprint import pprint
import json

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['gsoc-archive']
db_new = client['gsoc-data']
col_new = db_new['flat_data']
# print(db)


col_list = [col['name'] for col in db.list_collections()]
col_list.sort(reverse=True)
# pprint(col_list)

def cleanup(org):
    del org['_id']
    org_clean = {
        'name': None,
        'website': None,
        'description': None,
        'mailing_list': None,
        'logo_image': None,
        'logo_bg': None,
        'tagline': None,
        'technologies': None,
        'category': None,
        'topics': None,
        'num_projects': None,
        'year': None
    }
    for key in org:
        if isinstance(org[key], str):
            org_clean[key] = org[key].strip()
        else:
            org_clean[key] = org[key]
    return org_clean

count = 0
for year in col_list:
    col = db[year]
    for doc in col.find():
        doc['year'] = int(year[-4:])
        pprint(col_new.insert_one(cleanup(doc)).inserted_id)
        count += 1

pprint('{} documents inserted.'.format(count))