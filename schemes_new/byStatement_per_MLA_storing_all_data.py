# import
import argparse
from pymongo import MongoClient
import os, sys
from tqdm import tqdm
from datetime import datetime
sys.path.append(os.path.abspath("../../../top5SchemesPerState/"))
from util import *
import numpy as np
import pickle
from pprint import pprint
import pandas as pd
import statsmodels.api as sm

# ------------------------------------------------------------------------------- #
# disable proxy
os.environ['no_proxy'] = '*'

# ------------------------------------MongoDB------------------------------------------- #

# MongoDB Variables
colls = ['agriculture', 'health_hygiene', 'humanDevelopment']

# Connection To MongoDB
client = MongoClient('localhost', 27017)
db = client['media-db2']

now = datetime.now()

def processSentiments(sentiments, startdate = '2010-05-20', enddate = now.strftime('%Y-%m-%d')):
	startDate = datetime.strptime(startdate, '%Y-%m-%d')
	endDate = datetime.strptime(enddate, '%Y-%m-%d')
	perYearSentiments = []
	gap = {'months': 6}
	chhapo = False
	while(startDate.year < endDate.year):
		__enddate = (startDate + relativedelta(**gap)).strftime('%Y-%m-%d')
		temp_end = startDate + relativedelta(**gap)
		__startdate = startDate.strftime('%Y-%m-%d')
		perYearSentiments.append(np.zeros(3))
		for date, sentiment in sentiments.items():
			if(date < __enddate and date >= __startdate):
				perYearSentiments[-1] += sentiment
			temp_date = datetime.strptime(date, '%Y-%m-%d')
			# if chhapo and (startDate.year == temp_date.year or np.abs(startDate.year-temp_date.year) <= 1 or np.abs(temp_end.year-temp_date.year) <= 1): print(date, __startdate, __enddate)
		# if isinstance(perYearSentiments[-1], int) and perYearSentiments[-1] == 0:
		# 	chhapo = True
		startDate += relativedelta(**gap)
	# print(len(perYearSentiments))
	return perYearSentiments

def processArticles(cacheName, startdate, enddate, typ): 
	filename_for_cache = '_senti_mla_cache.pkl'
	with open(cacheName+filename_for_cache, 'rb') as file:
		return pickle.load(file)

def sentiment(article_sentiments, mlas_counted):
	perDateSentiments = {}
	for state_val in article_sentiments.values():
		for party_val in state_val.values():
			for entity_val in party_val.values():
				for date, sentim in entity_val.items():
					if date not in perDateSentiments:
						perDateSentiments[date] = np.zeros(3, dtype='float64')
					perDateSentiments[date] += np.array(sentim)
	return processSentiments(perDateSentiments)

if __name__ == '__main__':
	split_dates = ['2009/05/05', '2014/05/22', '2019/05/22']
	term = ['upa', 'nda']
	typ = args.type.lower()
	total_elections = len(split_dates)
	print('starting for type :', typ)
	path = '/divided/whole_' + typ
	cacheName = 'cache' + path
	senti = {}
	for party in term:
		cn = cacheName + '_' + party
		for i in range(total_elections-1):
			year = split_dates[i].split('/')[0]
			cacheName_year = cn + '_' + str(year)
			for coll in tqdm(colls, desc = year, leave = False):
				cacheNameSchemes = cacheName_year + '_' + coll

				article_sentiments, mlas_counted = processArticles(cacheNameSchemes, \
														split_dates[i], split_dates[i+1], typ)
				if coll not in senti: senti[coll] = np.stack(sentiment(article_sentiments, mlas_counted))
				else: senti[coll] += np.stack(sentiment(article_sentiments, mlas_counted))
	for coll in senti:
		perYearOverallArticles = np.array(load(args.cache + coll + '_2_perYearOverallArticles'), dtype = 'float64')
		print(senti[coll][:,1])
		# print(perYearOverallArticles[:-4].shape, senti[coll][:-4,1].shape)
		regressor_OLS = sm.WLS(perYearOverallArticles[:-4],senti[coll][:-4,]).fit()
		print(regressor_OLS.summary())
		# exit()