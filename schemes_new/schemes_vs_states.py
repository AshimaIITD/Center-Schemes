from util import *

def get_articles_count_before_after_nda(split_dates, filename, term):
	'''
	return dict: articles_count -> party -> coll -> scheme -> state -> 2014/2019
	'''
	cacheName = args.cache+'articles_count_upa_nda'
	# if os.path.exists(cacheName + '.pkl'):
	# 	print('found pickle for before after nda')
	# 	return load(cacheName)
	articles_count = {}
	for party in term:
		if party not in articles_count: articles_count[party] = {}

		for coll in tqdm(top5Schemes, desc = party, leave = False):
			collection = db[coll + '_schemes_upa']
			if coll not in articles_count: articles_count[party][coll] = {}
			# if coll != 'humanDevelopment': continue
			divided_scheme = divide_schemes_on_party(filename, coll, party)
			# print(divided_scheme)
			# return divided_scheme
			for scheme in tqdm(divided_scheme, desc = coll, leave = True):
				if scheme not in articles_count[party][coll]: articles_count[party][coll][scheme] = {}
				for i in trange(len(term)):
					articles = fetch_articles(collection, keywords=divided_scheme[scheme], \
												startdate=split_dates[i], enddate=split_dates[i+1])

					for art in tqdm(articles, desc = scheme, leave = False):
						try: states = art['states']
						except Exception as e: continue

						for state in states:
							if state not in articles_count[party][coll][scheme]: 
								articles_count[party][coll][scheme][state] = [0]*len(term)
							articles_count[party][coll][scheme][state][i]+=1
	dump(cacheName, articles_count)
	return articles_count

if __name__ == '__main__':
	term = ['upa', 'nda']
	filename = 'Schemes_divided.xlsx'
	split_dates = ['2009-05-05', '2014-05-22', '2019-05-22']
	handpicked_schemes = []
	articles_count = get_articles_count_before_after_nda(split_dates, filename, term)
	path = 'output/'
	width = 0.35
	pprint(articles_count)
	exit()
	for party in articles_count:
		party_path = path + party + '/'
		for coll in articles_count[party]:
			column_path = party_path + coll + '/'
			make_dir(column_path)

			for scheme_name in articles_count[party][coll]:
				percentage_change = []
				states = []
				for state in articles_count[party][coll][scheme_name]:
					if articles_count[party][coll][scheme_name][state][0]:
						articles_count[party][coll][scheme_name][state][1]/=5 # NDA
						articles_count[party][coll][scheme_name][state][0]/=3 # UPA
						change = 100*(articles_count[party][coll][scheme_name][state][1]-\
							articles_count[party][coll][scheme_name][state][0])/articles_count[party][coll][scheme_name][state][0]
						states.append(state)
						percentage_change.append(change)
				plt.figure(figsize=(12, 8))
				plt.bar(states, percentage_change, color='g', width = width, label = 'percentage_change')

				plt.title(coll + ': Percentage change in article coverage for ' + scheme_name)
				plt.xticks(rotation = 75)
				plt.xlabel('States')
				plt.ylabel('Percentage Change')
				plt.legend()
				plt.tight_layout()
				plt.savefig(column_path + scheme_name + '.png')
				plt.clf()
