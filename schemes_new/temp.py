from util import *
import statsmodels.api as sm

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
			name = keywords[0]
			keyword = keywords[1:] if keywords[0].startswith('#') else keywords
			scheme[name] = joinKeywordList(get_schemes(keywords))
			keywords = []
			continue
		keywords.append(i)
	if keywords:
		scheme[keywords[0]] = joinKeywordList(get_schemes(keywords))
	return scheme	

def findArticlesOnTimePeriod(collection, startdate = '2010-20-05', enddate = now.strftime('%Y-%d-%m'), keywords:str = ''):
	startDate = datetime.strptime(startdate, '%Y-%d-%m')
	endDate = datetime.strptime(enddate, '%Y-%d-%m')
	perYearArticles = []
	while(startDate.year < endDate.year):
		__enddate = (startDate + relativedelta(years=1)).strftime('%Y-%d-%m')
		kwargs = {'startdate' : startDate.strftime('%Y-%d-%m'), 'enddate' : __enddate}
		if(keywords): kwargs['keywords'] = keywords
		articles = fetch_articles(collection, **kwargs)
		perYearArticles.append(articles.count())
		startDate += relativedelta(months=6)
	return perYearArticles

if __name__ == '__main__':
	filename = 'Schemes_divided.xlsx'
	for coll in top5Schemes:
		divided_scheme = divide_schemes(filename, coll)
		collection = db[coll + '_schemes']
		perYearOverallArticles = findArticlesOnTimePeriod(collection)
		perYearArticles = {}
		for scheme in tqdm(divided_scheme, desc = coll, leave = False):
			perYearArticles[scheme] = findArticlesOnTimePeriod(collection, keywords=divided_scheme[scheme])
		dump(args.cache + coll + '_2_perYearOverallArticles', perYearOverallArticles)
		dump(args.cache + coll + '_2_perYearArticles', perYearArticles)
		perYearArticles = np.array(list(load(args.cache + coll + '_2_perYearArticles').values())).T
		perYearOverallArticles = np.array(load(args.cache + coll + '_2_perYearOverallArticles'))
		# print(perYearOverallArticles.shape, perYearArticles.shape)
		regressor_OLS = sm.WLS(perYearOverallArticles,perYearArticles).fit()
		print(regressor_OLS.summary())
		# print(perYearOverallArticles)
		# print(perYearArticles)