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
	
	for coll in tqdm(top5Schemes, desc = 'schemes', leave = False):
		divided_scheme = divide_schemes(filename, coll)
		collection = db[coll + '_schemes']
		scheme_articles_count_after = []
		scheme_articles_count_before = []

		for scheme_name, keywords in tqdm(divided_scheme.items(), desc = coll, leave = False):
			count_after = fetch_articles(collection, keywords = keywords, startdate = '2014-05-20').count()
			count_before = fetch_articles(collection, keywords = keywords, enddate = '2014-05-20').count()
			scheme_articles_count_before.append((count_before, scheme_name))
			scheme_articles_count_after.append((count_after, scheme_name))
		
		scheme_articles_count_after.sort(reverse = True)
		scheme_articles_count_before.sort(reverse = True)
		
		plt.figure(figsize = (10, 5))
		def plot(plt, track, divided_scheme, collection, perYearArticles, yearRange, typ):
			for scheme_name in tqdm(track, desc = coll + ' top 3', leave = False):
				keywords = divided_scheme[scheme_name]
				perYearArticlesPerScheme = np.array(findArticlesOnTimePeriod(collection, keywords = keywords), \
					dtype = 'float64').reshape(-1,1)
				perYearArticlesPerScheme *= np.max(perYearArticles)
				perYearArticlesPerScheme /= perYearArticles

				plt.plot(yearRange, perYearArticlesPerScheme, label = scheme_name, linestyle = typ)
		
		before_track = set()
		for _, scheme_name in scheme_articles_count_before[:3]:
			before_track.add(scheme_name)

		after_track = set()
		for _, scheme_name in scheme_articles_count_after[:3]:
			after_track.add(scheme_name)


		plot(plt, before_track - after_track, divided_scheme, collection, perYearArticles, yearRange, '--')
		plot(plt, after_track - before_track, divided_scheme, collection, perYearArticles, yearRange, '-.')
		plot(plt, after_track.intersection(before_track), divided_scheme, collection, perYearArticles, yearRange, '-')
		plt.title(coll)
		plt.axvline(x=2014, color='lightcoral', linestyle='-')
		plt.axvline(x=2019, color='lightcoral', linestyle='-')
		plt.xlabel('Years')
		plt.ylabel('Articles Count')
		plt.legend()
		plt.tight_layout()
		output = args.output+'temp_schemes/top3/combined/coral_'

		plt.savefig(output + coll + '.png')
		plt.clf()