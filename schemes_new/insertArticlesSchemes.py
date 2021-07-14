#before running it on gem server check the database name.
import sys
from pymongo import MongoClient
from util import *
# ---------- Fixed Params ------------
client = MongoClient('mongodb://localhost:27017/')
db = client['media-db2']
# -----------------------------------

def printArticles(collName, keywords):
    with open("articles.ignore", 'w+') as file:
        collection = my_db[collName + '_schemes']
        scheme_articles = collection.find({'$and':[{'text': {'$regex': keywords, '$options': 'i'}}]},
                            no_cursor_timeout=True)
        articles = []
        for art in scheme_articles:
            articles.append(art['text'])
            if(len(articles) == 100):
                file.write('\n\n'.join(articles))
                articles = []
                break

if __name__ == '__main__':
    print("Finding articles...")
    schemes_file = 'Schemes_divided.xlsx'
    scheme_keywords = {}
    
    print(selectedSchemes)
    for coll in top5Schemes:
        divided_scheme = divide_schemes(schemes_file, coll)
        for scheme_name in divided_scheme:
            scheme_name = scheme_name.strip()
            if scheme_name in selectedSchemes:
                scheme_keywords[scheme_name] = coll, divided_scheme[scheme_name]
    # print(scheme_keywords.keys())
    # exit()
    print("Storing articles now...")
    for scheme_name, (coll, keywords) in scheme_keywords.items():
        saving_collection = db[scheme_name.replace(' ', '_').replace('-','_').replace('&', 'and')]
        for govt in ['upa', 'nda']:
            fetching_collection = db[coll + '_schemes_' + govt]
            art_map = set()
            for article in tqdm(fetch_articles(fetching_collection, keywords = keywords), desc = scheme_name):
                url = article['articleUrl']
                try:
                    if url not in art_map:
                        art_map.add(url)
                        saving_collection.insert(article, check_keys=False)
                except:
                    continue