from util import *
import statsmodels.api as sm

def findArticlesOnTimePeriod(collection, startdate = '2010-05-20', enddate = now.strftime('%Y-%m-%d'), keywords:str = ''):
	startDate = datetime.strptime(startdate, '%Y-%m-%d')
	endDate = datetime.strptime(enddate, '%Y-%m-%d')
	perYearArticles = []
	while(startDate.year < endDate.year):
		__enddate = (startDate + relativedelta(months = 6)).strftime('%Y-%m-%d')
		kwargs = {'startdate' : startDate.strftime('%Y-%m-%d'), 'enddate' : __enddate}
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