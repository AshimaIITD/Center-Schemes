import os, sys, argparse
import pandas as pd
from pymongo import MongoClient
sys.path.append(os.path.abspath("../freq/"))
from freq import get_schemes
from const import *
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from pprint import pprint
import numpy as np

now = datetime.now()

parser = argparse.ArgumentParser(description='Extract no. of articles in each category',
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--startdate', nargs='?', default='2011-05-20', help='date from when you want to process the articles')
parser.add_argument('--enddate', nargs='?', default=now.strftime('%Y-%m-%d'), help='date till when you want to process the articles')
parser.add_argument('--path', nargs='?', default='schemes/', help='path where the schemes to be evaluated are stored')
parser.add_argument('--output', nargs='?', default='output_graphs/anotherTry/', help='path where the output will be stored')
parser.add_argument('--input', nargs='?', default='input/Schemes.xlsx', help='input path of xlsx sheet')
args = parser.parse_args()
path = args.path
output = args.output
readFrom = args.input

client = MongoClient('localhost', 27017)
db = client['media-db2']

party_in_power = ['UPA', 'NDA']
timeInterval = [args.startdate, '2014-05-16', args.enddate]
categories = ['agriculture', 'humanDevelopment', 'health_hygiene']

def get_keyword_list(schemes):
	keywords_list = []
	for scheme_name, keywords in schemes.items():
		if scheme_name not in top5Schemes[coll]: continue
		keywords_list += keywords
	return keywords_list

def get_article_count_for_keyword(collection, keywords, startdate, enddate):
	scheme_articles = collection.find({'$and': [ \
	{'text': {'$regex': keywords, '$options': 'i'}}, \
	{'publishedDate': {'$gte': startdate}}, \
	{'publishedDate': {'$lt': enddate}}, \
	]}, no_cursor_timeout = True).count()
	return scheme_articles

def get_article_count_in_state_for_keyword(collection, keywords, state, startdate, enddate):
	scheme_articles = collection.find({'$and': [ \
	{'text': {'$regex': keywords, '$options': 'i'}}, \
	{'publishedDate': {'$gte': startdate}}, \
	{'publishedDate': {'$lt': enddate}}, \
    {'states': {'$in': [state]}}\
	]}, no_cursor_timeout = True).count()
	return scheme_articles

schemes_clubbed = get_schemes(path)
states = large_states + medium_states + small_states

for coll in categories:
	collection = db[coll + '_schemes']
	increase, decrease = 0, 0
	increase_states, decrease_states = {}, {}
	for scheme_name, keywords in schemes_clubbed[coll].items():
		arr = []
		keywords = '|'.join(keywords)
		states_article_count = [[], []]
		for i in range(len(timeInterval)-1):
			article_count = get_article_count_for_keyword(collection, keywords, timeInterval[i], timeInterval[i+1])
			startDate = datetime.strptime(timeInterval[i], '%Y-%m-%d')
			endDate = datetime.strptime(timeInterval[i+1], '%Y-%m-%d')
			years = ((endDate-startDate).days/365.25)
			article_count = (article_count/years)
			arr.append(article_count)
			for state in states:
				count = get_article_count_in_state_for_keyword(collection, keywords, state, timeInterval[i], timeInterval[i+1])
				states_article_count[i].append(count/years)
		if(arr[0] != 0):
			increase += (arr[0] < arr[1])
			decrease += (arr[0] > arr[1])
			inc_sta, dec_sta = 0, 0
			for idx in range(len(states_article_count[0])):
				if states[idx] not in increase_states:
					increase_states[states[idx]] = 0
					decrease_states[states[idx]] = 0
				increase_states[states[idx]] += (states_article_count[0][idx] < states_article_count[1][idx])
				decrease_states[states[idx]] += (states_article_count[0][idx] > states_article_count[1][idx])
				inc_sta = sum(list(increase_states.values()))
				dec_sta = len(increase_states) - inc_sta
			print((scheme_name, arr, increase, decrease, inc_sta, dec_sta))

			# pprint(increase_states)
			# pprint(decrease_states)
		break
	print(coll, increase, decrease)
	break

# 	Aligned NotAligned
# UPA 0 		0
# NDA 0 		0