import sys
from pymongo import MongoClient
from util import *
# ---------- Fixed Params ------------
client = MongoClient('mongodb://localhost:27017/')
db = client['media-db2']
# -----------------------------------

if __name__ == '__main__':
	filename = 'Schemes_divided.xlsx'
	fetch_from = 'humanDevelopment_schemes'
	insert_into = 'PDS'
	read_collection = db[fetch_from]
	write_collection = db[insert_into]

	art_map = set()
	for article in read_collection.find():
		art_map.add(article['articleUrl'])

	for article in tqdm(write_collection.find()):
		if article['articleUrl'] not in art_map:
			art_map.add(article['articleUrl'])
			read_collection.insert(article, check_keys = False)