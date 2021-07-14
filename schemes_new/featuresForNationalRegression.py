from util import *
from collections import namedtuple 
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.decomposition import PCA

def getStaticFeatures(InputVariables, cols = ['State', 'Total 2011', 'MP', 'MLA']):
	staticFeatures = pd.read_excel(args.input + InputVariables, usecols=cols)
	staticFeatures.rename(columns = {'Total 2011': 'Total'}, inplace = True)
	staticFeatures.set_index('State', inplace = True)
	return staticFeatures

def overlap_year(s1,e1, s2,e2):
    Range = namedtuple('Range', ['start', 'end'])
    r1 = Range(start=datetime.strptime(s1,'%Y-%m-%d'), end=datetime.strptime(e1,'%Y-%m-%d'))
    r2 = Range(start=datetime.strptime(s2,'%Y-%m-%d'), end=datetime.strptime(e2,'%Y-%m-%d'))
    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)
    if latest_start < earliest_end:
    	return latest_start.strftime('%Y-%m-%d'), earliest_end.strftime('%Y-%m-%d'), (earliest_end-latest_start).days

def state_wise_aligned_notAligned_articles(collection, stateInfo):
	new_overlaped = {}
	for state in stateInfo:
		if state not in new_overlaped: new_overlaped[state] = {}
		for times in stateInfo[state]:
			for times_center in center:
				years = overlap_year(times[0], times[1], times_center[0], times_center[1])
				if years:
					if (stateInfo[state][times] == center[times_center]) not in new_overlaped[state]: 
						new_overlaped[state][stateInfo[state][times] == center[times_center]] = np.zeros(2)
					new_overlaped[state][stateInfo[state][times] == center[times_center]] += \
					np.array([fetch_articles(collection, states = [state], \
						startdate = years[0], enddate = years[1]).count(), years[2]], dtype = 'float64')
	return new_overlaped

if __name__ == '__main__':
	ElectionDates = 'Election Date.xlsx'
	InputVariables = 'MP_MLA.xlsx'
	staticFeatures = getStaticFeatures(InputVariables)
	state_party = load(args.input + 'state_caolition_date')
	# for every gap -> aligned?, total_number_of_articles, number_of_years_passed, 
	center = {('2011-05-20', '2014-05-20'): 'UPA', ('2014-05-20', '2021-05-20'): 'NDA'}
	stateInfo = {}
	for state_val in state_party.values():
		for state, party_times in state_val.items():
			if state not in stateInfo: stateInfo[state] = {}
			for party in party_times:
				stateInfo[state][tuple(party_times[party])] = party
	collection = db['humanDevelopment_schemes']
	stana = state_wise_aligned_notAligned_articles(collection, stateInfo)
	features = []
	feature_output = []
	states = []
	for state in staticFeatures.index:
		# if state != 'nct of delhi': continue
		x = staticFeatures.loc[state].values.tolist()
		for t, variation in stana[state].items():
			# print(type(variation))
			features.append(x + [t, variation[1]])
			feature_output.append(variation[0])
			states.append(state)
			# features.append(x + variation.tolist())
	data1 = np.array(feature_output)
	data2 = np.array(features)
	featureNames = list(staticFeatures.keys()) + ['alignment', 'years']
	# print(np.min(data2, axis=0))
	# exit()
	# print(data2.shape)

	# data2 = (data2 - np.min(data2))/(np.max(data2) - np.min(data2, axis=0))
	n = data2.shape[0]

	trainingData = data2[data2[:,3] == 1]
	trainingOutput = data1[data2[:,3] == 1]
	testData = data2[data2[:,3] == 0]
	testOutput = data1[data2[:,3] == 0]
	data2[n//10]
	for i in range(data2.shape[1]):
		corr, _ = spearmanr(data1[n//10:], data2[n//10:, i])
		print('Correlation between input and output features for ', featureNames[i], corr)
	# print(data2.shape)
	regr = RandomForestRegressor(n_estimators = 50, random_state = 5)

	# regr.fit(trainingData, trainingOutput)
	# print('Accuracy on test data for not aligned when trained on aligned', regr.score(testData, testOutput))


	# regr.fit(testData, testOutput)
	# print('Accuracy on test data for aligned when trained on not aligned', regr.score(trainingData, trainingOutput))
	

	regr.fit(data2[n//10:, :], data1[n//10:])
	print('Accuracy on test data', regr.score(data2[:n//10, :], data1[:n//10]))

	# pca = PCA(n_components=2, svd_solver = 'randomized')
	# X_train_pca = pca.fit_transform(data2)
	# 