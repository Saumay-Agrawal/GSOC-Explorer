import pymongo
import json
from pprint import pprint

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['gsoc-data']
col = db['flat_data']

file = open('gsoc-data.json', mode='w', encoding='utf-8')
file.write('[')

count = 0
for doc in col.find():
    del doc['_id']
    file.write(json.dumps(doc, sort_keys=True) + ',')
    count += 1
    pprint('{} documents written to the file.'.format(count))

file.write(']')
file.close()