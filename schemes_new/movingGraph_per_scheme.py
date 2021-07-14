from util import *
import statsmodels.api as sm

def findArticlesOnTimePeriod(collection, startdate = '2010-05-20', enddate = now.strftime('%Y-%m-%d'), keywords:str = ''):
	startDate = datetime.strptime(startdate, '%Y-%m-%d')
	endDate = datetime.strptime(enddate, '%Y-%m-%d')
	perYearArticles = []
	while(startDate.year < endDate.year):
		__enddate = (startDate + relativedelta(years = 1)).strftime('%Y-%m-%d')
		__startdate = startDate.strftime('%Y-%m-%d')
		kwargs = {'startdate' : __startdate, 'enddate' : __enddate}
		if(keywords): kwargs['keywords'] = keywords
		articles = fetch_articles(collection, **kwargs)
		perYearArticles.append(articles.count())
		startDate += relativedelta(years = 1)
	return perYearArticles

if __name__ == '__main__':
	filename = 'Schemes_divided.xlsx'

	article_collection = db['articles']
	startdate = '2010-05-20'
	enddate = now.strftime('%Y-%m-%d')
	startDate = datetime.strptime(startdate, '%Y-%m-%d')
	endDate = datetime.strptime(enddate, '%Y-%m-%d')
	perYearArticles = []
	yearRange = []
	while(startDate.year < endDate.year):
		__enddate = (startDate + relativedelta(years = 1)).strftime('%Y-%m-%d')
		__startdate = startDate.strftime('%Y-%m-%d')
		yearRange.append(startDate.year)
		kwargs = {'startdate' : __startdate, 'enddate' : __enddate}
		articles = fetch_articles(article_collection, **kwargs)
		perYearArticles.append(articles.count())
		startDate += relativedelta(years = 1)
	perYearArticles = np.array(perYearArticles, dtype = 'float64').reshape(-1,1)
	for coll in top5Schemes:
		divided_scheme = divide_schemes(filename, coll)
		collection = db[coll + '_schemes']
		for scheme_name, keywords in divided_scheme.items():
			perYearArticlesPerScheme = np.array(findArticlesOnTimePeriod(collection, keywords = keywords), \
				dtype = 'float64').reshape(-1,1)
			perYearArticlesPerScheme *= np.max(perYearArticles)
			perYearArticlesPerScheme /= perYearArticles
			plt.figure(figsize = (10, 5))
			plt.title(coll + ' : ' + scheme_name)
			plt.plot(yearRange, perYearArticlesPerScheme, label = 'articles count per year')
			plt.axvline(x=2014, color='red', linestyle='--')
			plt.axvline(x=2019, color='red', linestyle='--')
			plt.xlabel('Years')
			plt.ylabel('Articles Count')
			plt.legend()
			plt.tight_layout()
			output = args.output+'temp_schemes/'+coll
			make_dir(output)
			plt.savefig(output + '/' + scheme_name+'.png')
			plt.clf()