# import
import os, sys, argparse, pickle
import numpy as np
import pandas as pd
from pymongo import MongoClient
from matplotlib import pyplot as plt
from pprint import pprint
from tqdm import tqdm, trange
from datetime import datetime
from dateutil.relativedelta import relativedelta

from const import *
sys.path.append(os.path.abspath("../"))

now = datetime.now()

parser = argparse.ArgumentParser(description='Extract top5 policies per state',
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--input', nargs='?', default='input/', help='relative path for the input')
parser.add_argument('--output', nargs='?', default='output/', help='relative path where you want to store the output')
parser.add_argument('--type', nargs='?', default='mp', help='mp/mla')
parser.add_argument('--cache', nargs='?', default='cache/', help='path of the cache stored')
args = parser.parse_args()

client = MongoClient('mongodb://localhost:27017/')
db = client['media-db2']

def fetch_articles(collection, states:list = [], startdate = '', \
	enddate = '', newsSource:list = [], keywords:str = ''):
	query = []
	if states: query.append({'states': {'$in': states}})
	if startdate: query.append({'publishedDate': {'$gte': startdate}})
	if newsSource: query.append({'sourceName': {'$in': newsSource}})
	if enddate: query.append({'publishedDate': {'$lt': enddate}})
	if keywords: query.append({'text': {'$regex': keywords, '$options': 'i'}})
	if query: scheme_articles = collection.find({'$and': query}, no_cursor_timeout = True)
	else: scheme_articles = collection.find(no_cursor_timeout=True)
	return scheme_articles

def make_dir(s):
	x = ''
	for i in s.split('/'):
		if i == '': continue
		x += i + '/'
		if not os.path.exists(x):
			os.mkdir(x)

def load(filepath):
	with open(filepath+'.pkl', 'rb') as file:
		return pickle.load(file)

def dump(filepath, variable):
	with open(filepath+'.pkl', 'wb') as file:
		pickle.dump(variable, file)

def get_states_count(filepath:str = 'cache/', collName = 'articles'):
	'''
	return dict
	'''
	filepath += 'states_count/'
	make_dir(filepath)
	filename = filepath + collName
	if os.path.exists(filename + '.pkl'):
		print('found pickle for collection:', collName)
		return load(filename)
	print('*********************', 'started storing states values for collection:', collName, '*********************')
	state_articles_count = {'total': 0}
	collection = db[collName]
	for art in tqdm(fetch_articles(collection), leave=False):
		if 'states' not in art: continue
		state_articles_count['total'] += 1
		for state in art['states']:
			if state not in state_articles_count: state_articles_count[state] = 1
			else: state_articles_count[state] += 1
	
	dump(filename, state_articles_count)
	return state_articles_count


def getAllStatesCount():
	states_count = {}
	states_count['total'] = get_states_count()
	for coll in top5Schemes:
		states_count[coll] = get_states_count(collName = coll+'_schemes')
	return states_count

def get_schemes(keywords):
	'''
	return list -> returns the modified list with some additions to few errors that can be found in the newspapers.
	'''
	keywords_list = []
	for keyword in keywords:
		keyword = keyword.lower()
		if 'scheme' in keyword or 'schemes' in keyword:
			keywords_list.append(keyword.replace('schemes', 'yojana').replace('scheme', 'yojana'))
			keywords_list.append(keyword.replace('schemes', 'yojna').replace('scheme', 'yojna'))
		elif 'yojana' in keyword:
			keywords_list.append(keyword.replace('yojana', 'scheme'))
			keywords_list.append(keyword.replace('yojana', 'schemes'))
			keywords_list.append(keyword.replace('yojana', 'yojna'))
		elif 'yojna' in keyword:
			keywords_list.append(keyword.replace('yojna', 'scheme'))
			keywords_list.append(keyword.replace('yojna', 'schemes'))
			keywords_list.append(keyword.replace('yojna', 'yojana'))
		keywords_list.append(keyword)	
	return keywords_list

def joinKeywordList(keywords_list):
	'''
	return str -> returns the regex which will be helpful in finding of articles in mongoDB
	'''
	simple = ' |'.join(keywords_list)
	full_stop = '\\.|'.join(keywords_list)
	comma = ',|'.join(keywords_list)
	return simple + ' |'+ full_stop + '\\.|' + comma + ','

def divide_schemes(filename:str, coll:str):
	'''
	return dict
	'''
	reader = pd.read_excel(args.input + filename, sheet_name = coll, usecols = ['Scheme Name', 'Govt'])
	reader.set_index('Scheme Name', inplace = True)
	keywords = []
	scheme = {}
	for x, i in enumerate(reader.index.values):
		if i == '-':
			if not keywords: continue
			name = keywords[0].replace('#', '')
			keyword = keywords[1:] if keywords[0].startswith('#') else keywords
			scheme[name] = joinKeywordList(get_schemes(keywords))
			keywords = []
			continue
		keywords.append(i)
	if keywords:
		scheme[keywords[0]] = joinKeywordList(get_schemes(keywords))
	return scheme

def divide_schemes_on_party(filename:str, coll:str, party:str):
	'''
	return dict
	'''
	party = party.upper()
	reader = pd.read_excel(args.input + filename, sheet_name = coll, usecols = ['Scheme Name', 'Govt'])
	# reader = pd.concat([reader[reader['Govt'] == party.upper()], reader[reader['Govt'] == 'TF'], reader[reader['Scheme Name'] == '-']], axis = 0)
	reader.set_index('Scheme Name', inplace = True)
	keywords = []
	scheme = {}
	# print(reader)
	# return 0
	for x, i in enumerate(reader.index.values):
		# print(reader['Govt'][x], party, reader['Govt'][x] != party and reader['Govt'][x] != 'TF' and reader.index.values[x] != '-')
		if reader['Govt'][x] != party and reader['Govt'][x] != 'TF' and reader.index.values[x] != '-': continue
		if i == '-':
			if not keywords: continue
			name = keywords[0]
			keyword = keywords[1:] if keywords[0].startswith('#') else keywords
			scheme[name] = joinKeywordList(get_schemes(keywords))
			keywords = []
			continue
		keywords.append(i)
	if keywords:
		scheme[keywords[0]] = joinKeywordList(get_schemes(keywords))
	return scheme	
