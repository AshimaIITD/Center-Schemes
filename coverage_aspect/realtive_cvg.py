from pymongo import MongoClient
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import re
from dateutil import parser
from datetime import datetime
from collections import namedtuple
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint




client  = MongoClient('mongodb://localhost:27017/')
db=client['media-db2']


large_states = ['andhra pradesh',
  'kerala',
  'maharashtra',
  'odisha',
  'rajasthan',
  'tamil nadu',
  'uttar pradesh',
  'madhya pradesh',
  'nct of delhi']

medium_states = ['assam',
  'bihar',
  'chhattisgarh',
  'gujarat',
  'haryana',
  'jammu & kashmir',
  'jharkhand',
  'karnataka',
  'punjab',
  'west bengal']

small_states = ['arunachal pradesh',
  'himachal pradesh',
  'goa',
  'manipur',
  'meghalaya',
  'mizoram',
  'nagaland',
  'puducherry',
  'sikkim',
  'tripura',
  'uttarakhand']


states  = medium_states + small_states + large_states

category = ["agriculture", "health_hygiene", "humanDevelopment"]

def get_toatl_article_count(collName, startDate, endDate):
    collection=db[collName]
    return  collection.count_documents({'$and':[{'publishedDate':{'$gte':startDate}},{'publishedDate':{'$lte':endDate}}]})

def get_state_article_count(collName, startDate, endDate, state):
    collection=db[collName]
    return  collection.count_documents({'$and':[{'states':{'$in':[state]}},{'publishedDate':{'$gte':startDate}},{'publishedDate':{'$lte':endDate}}]})




df = pd.read_excel('top5_perCapita.xlsx', sheet_name = ['Population', 'humanDevelopment', 'health_hygiene', 'agriculture'])
density  = {}
for den, sts in zip(df['Population']['total']/1000000,df['Population']['State']):
    density[sts] = den


with open('state_caolition_date', 'rb') as f:
    state_caolition_date = pickle.load(f)

def overlap_year(s1,e1, s2,e2):

    Range = namedtuple('Range', ['start', 'end'])

    r1 = Range(start=datetime.strptime(s1,'%Y-%m-%d'), end=datetime.strptime(e1,'%Y-%m-%d'))
    r2 = Range(start=datetime.strptime(s2,'%Y-%m-%d'), end=datetime.strptime(e2,'%Y-%m-%d'))
    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)

    return str(latest_start).split(" ")[0], str(earliest_end).split(" ")[0]

timeline = {'2009-2014':{'center':'UPA', 'start':'2009-05-15', 'end':'2014-05-15'}, \
            '2014-2019':{'center': 'NDA' , 'start':'2014-05-16', 'end':'2019-05-22'}}

data_dict = {}
for scheme in category:
    data_dict[scheme] = {}
    for time in timeline:
        print(time)
        data = state_caolition_date[time]
        center = timeline[time]['center']


        for st in data:
            state_count_al,total_count_al = 0,0
            state_count_nl, total_count_nl = 0, 0
            if st not in data_dict[scheme]:
                data_dict[scheme][st] = {}
            for party in data[st]:
                # print(party, center)
                statDate , endDate = overlap_year(timeline[time]['start'], timeline[time]['end'],data[st][party][0], data[st][party][1] )
                # print(statDate , endDate)
                if party == center:

                    state_count_al+= get_state_article_count(scheme + '_schemes_' + center.lower(),statDate, endDate, st)
                    total_count_al += get_toatl_article_count(scheme + '_schemes_' + center.lower(),statDate, endDate)

                else:

                    state_count_nl += get_state_article_count(scheme + '_schemes_' + center.lower(),statDate, endDate, st)
                    total_count_nl += get_toatl_article_count(scheme + '_schemes_' + center.lower(),statDate, endDate)

            if 'aligned' not in data_dict[scheme][st]:
                data_dict[scheme][st]['aligned'] = {'cnt':0, 'total':0}
            if 'non_aligned' not in data_dict[scheme][st]:
                data_dict[scheme][st]['non_aligned'] = {'cnt':0, 'total':0}
            data_dict[scheme][st]['aligned']['cnt'] += state_count_al
            data_dict[scheme][st]['aligned']['total'] += total_count_al
            data_dict[scheme][st]['non_aligned']['cnt'] += state_count_nl
            data_dict[scheme][st]['non_aligned']['total'] += total_count_nl
        # pprint(data_dict[scheme])


# pprint(data_dict)

finalData = {}

for scheme in data_dict:
    finalData[scheme] = {}
    for st in data_dict[scheme]:
        finalData[scheme][st] = {}
        if st in density:
            # print(st, density[st], data_dict[scheme][st]['aligned']['total'] , data_dict[scheme][st]['non_aligned']['total'] )
            finalData[scheme][st]['aligned'] = (data_dict[scheme][st]['aligned']['cnt'] / data_dict[scheme][st]['aligned']['total'] if data_dict[scheme][st]['aligned']['total'] !=0 else 0) / density[st]
            finalData[scheme][st]['non_aligned'] = (data_dict[scheme][st]['non_aligned']['cnt'] / data_dict[scheme][st]['non_aligned']['total'] if data_dict[scheme][st]['non_aligned']['total'] !=0 else 0) / density[st]


dataFrame = []
for idx, scheme in enumerate(category):
    dataFrame.append(pd.DataFrame.from_dict(finalData[scheme]).T)



x = pd.concat([dataFrame[0], dataFrame[1], dataFrame[2]], axis = 1)

print(x)
with open('relative_cvg_dataFrame', 'wb') as f:
    pickle.dump(x, f)















































# pprint(data)
# relative_cvg = {}



# for scheme in category:
#     relative_cvg[scheme] = {}
#     # cvg[scheme] = {}
#     for st in data:
#         if st in states:
#             # print(st, end=" : ")
#             total_upa, total_nda, total_tf = 0, 0 , 0
#             state_count_upa, state_count_nda,  state_count_tf= 0, 0, 0
#             relative_cvg[scheme][st] = {}
#             for party in data[st]:
#             # cvg[scheme][st] = get_state_article_count(scheme + "_schemes", '2009-05-14', '2014-05-15', st) / density[st]
#
#                 # print(party, end = ", ")
#                 if party == 'UPA':
#                     total_upa += get_toatl_article_count(scheme + "_schemes", data[st][party][0], data[st][party][1] )
#                     state_count_upa += get_state_article_count(scheme + "_schemes", data[st][party][0], data[st][party][1], st)
#                 elif party == 'NDA':
#                     total_nda += get_toatl_article_count(scheme + "_schemes", data[st][party][0], data[st][party][1] )
#                     state_count_nda += get_state_article_count(scheme + "_schemes", data[st][party][0], data[st][party][1], st)
#                 else:
#                     total_tf += get_toatl_article_count(scheme + "_schemes", data[st][party][0], data[st][party][1] )
#                     state_count_tf += get_state_article_count(scheme + "_schemes", data[st][party][0], data[st][party][1], st)
#             # print('\n')
#             relative_cvg[scheme][st]['UPA_' + scheme] = (state_count_upa / total_upa  if  total_upa!= 0 else 0 ) / density[st]
#             relative_cvg[scheme][st]['NDA_' + scheme] = (state_count_nda / total_nda if  total_nda != 0 else 0)  /density[st]
#             relative_cvg[scheme][st]['tf_' + scheme] = (state_count_tf / total_tf if  total_tf != 0 else 0)/  density[st]
#
# dataFrame = []
# for idx, scheme in enumerate(category):
#     dataFrame.append(pd.DataFrame.from_dict(relative_cvg[scheme]).T)
#     # dataFrame.append(pd.DataFrame.from_records(cvg[scheme], index=[0]).T)
#
#     # print(dataFrame[idx])
#
# finalData = pd.concat([dataFrame[0], dataFrame[1], dataFrame[2]], axis = 1)
# # finalData.columns = [0,1,2]
# with open('perCaptia_rel_cvg', 'wb') as f:
#     pickle.dump(finalData, f)
# pprint(finalData)
