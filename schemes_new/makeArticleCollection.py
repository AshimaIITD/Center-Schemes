from util import *

def store_articles(cursor, coll, govt):
	collection = db[coll + '_schemes_' + govt]
	art_map = {}
	for art in tqdm(cursor, desc = coll + '_' + govt, leave=False):
		url = art['articleUrl']
		if url not in art_map:
			art_map[url] = 1
			collection.insert_one(art)

if __name__ == '__main__':
	filename = 'Schemes.xlsx'
	collection = db['articles']
	for coll in top5Schemes:
		reader = pd.read_excel(args.input + filename, sheet_name = coll, usecols = ['Scheme Name', 'Govt'])
		reader.set_index('Scheme Name', inplace = True)
		upa = reader[reader['Govt'] == 'UPA']
		nda = reader[reader['Govt'] == 'NDA']
		tf = reader[reader['Govt'] == 'TF']
		upa = pd.concat([upa, tf], axis = 0)
		nda = pd.concat([nda, tf], axis = 0)
		keywords_list_upa = joinKeywordList(get_schemes(upa.index.values.tolist()))
		keywords_list_nda = joinKeywordList(get_schemes(nda.index.values.tolist()))
		articles_upa = fetch_articles(collection, keywords=keywords_list_upa)
		articles_nda = fetch_articles(collection, keywords=keywords_list_nda)
		store_articles(articles_upa, coll, 'upa')
		store_articles(articles_nda, coll, 'nda')
	