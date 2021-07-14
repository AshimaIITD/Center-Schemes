import os, sys, argparse
from pymongo import MongoClient
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.abspath("../freq/"))
from freq import get_schemes
from const import *
from univ import *

now = datetime.now()

parser = argparse.ArgumentParser(description='Extract no. of articles in each category',
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--startdate', nargs='?', default='2010-03-03', help='date from when you want to process the articles')
parser.add_argument('--enddate', nargs='?', default=now.strftime('%Y-%m-%d'), help='date till when you want to process the articles')
parser.add_argument('--path', nargs='?', default='schemes/', help='path where the schemes to be evaluated are stored')
args = parser.parse_args()
path = args.path

client = MongoClient('localhost', 27017)
db = client['media-db2']

schemes_clubbed = get_schemes(path)

states = large_states + medium_states + small_states

def no_of_articles(collection, state, keywords_list, startdate, enddate):
    keywords = '|'.join(keywords_list)
    scheme_articles = collection.find({'$and': [ \
        {'text': {'$regex': keywords, '$options': 'i'}}, \
        {'publishedDate': {'$gte': startdate}}, \
        {'publishedDate': {'$lt': enddate}}, \
        {'sourceName': {'$in': newsSource}}, \
        {'states': {'$in': state}}\
        ]}, no_cursor_timeout = True)
    count = scheme_articles.count()
    return count

def no_of_articles_in_scheme(collection, schemes, startdate, enddate):
    global newsSource
    keywords_list = []
    for _, keywords in schemes.items():
        keywords_list += keywords
    keywords = '|'.join(keywords_list)
    scheme_articles = collection.find({'$and': [ \
        {'text': {'$regex': keywords, '$options': 'i'}}, \
        {'publishedDate': {'$gte': startdate}}, \
        {'publishedDate': {'$lt': enddate}}, \
        {'sourceName': {'$in': newsSource}}, \
        ]}, no_cursor_timeout = True)
    count = scheme_articles.count()
    return count

def plot(state_category, keywords, coll, scheme_name):
    max_score = 0
    plt.subplots(figsize=(15, 7))
    total = {}
    for state_type, states in state_category.items():
        startdate = datetime.strptime(args.startdate, '%Y-%m-%d')
        total_articles, X_axis = [], []
        while(startdate.year < now.year):
            count = no_of_articles(collection, states, keywords, startdate.strftime('%Y-%m-%d'), \
                (startdate + relativedelta(years=1)).strftime('%Y-%m-%d'))
            key = str(startdate.year) + ' - ' + str(startdate.year+1)
            X_axis.append(key)
            if key not in total:
                total[key] = no_of_articles_in_scheme(collection, schemes, startdate.strftime('%Y-%m-%d'), \
                    (startdate + relativedelta(years=1)).strftime('%Y-%m-%d'))
                max_score = max(max_score, total[key])
            if total[key] != 0:
                total_articles.append(count/total[key])
            else:
                total_articles.append(0)
            startdate += relativedelta(years=1)
        total_articles = np.array(total_articles, dtype='float64')
        plt.plot(X_axis, total_articles*max_score, label=state_type + ' states')
    plt.axvline(x='2013 - 2014', color='red', linestyle='--')
    plt.axvline(x='2018 - 2019', color='red', linestyle='--')
    plt.title(coll + ' : ' + scheme_name)
    plt.xlabel('years')
    plt.ylabel('Article Count')
    plt.xticks(rotation=90)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    plt.tight_layout()
    path = 'output_graphs/v2/State Categories/' + coll + '/'
    make_dir(path)
    plt.savefig(path + scheme_name+'.png')
    plt.clf()
    
state_category = {'small':small_states, "medium":medium_states, "large":large_states}

for coll, schemes in tqdm(schemes_clubbed.items(), desc = 'schemes', leave = True):
    collection = db[coll + '_schemes']
    for scheme_name, keywords in tqdm(schemes.items(), desc = coll, leave = False):
        if scheme_name not in top5Schemes[coll]: continue
        plot(state_category, keywords, coll, scheme_name)