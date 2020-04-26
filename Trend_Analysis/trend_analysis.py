import os
import json
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import TransportError

DIR = '/home/apurv/top1millionlists/'

class ElasticSearchPipeline(object):
    def __init__(self):
        self._es = Elasticsearch()

    def process_item(self, data, list_type):
        print('In Elastic Pipeline')
        if self._es.indices.exists(list_type):
            try:
                print("Adding bulk data to index")
                # self._es.index(index=list_type, body=data)
                resp = helpers.bulk(self._es, data, index=list_type, doc_type='_doc')
                print ("helpers.bulk() RESPONSE:", json.dumps(resp, indent=4))
            except TransportError as e:
                print("Elasticsearch helpers.bulk() ERROR:", e)


def get_filepaths(file_name_expr):
    filepaths = []
    for subdir, dirs, files in os.walk(DIR):
        for filename in files:
            filepath = subdir + os.sep + filename
            if filepath.endswith(file_name_expr):
                filepaths.append(filepath)
    return filepaths

def get_majestic_data(path):
    domains_majestic = []
    with open(path, 'r') as f:
        lines = f.readlines()
        lines = lines[:1000000]
        for line in lines:
            domains_majestic.append(line.split(',')[1].strip('\n'))
    return domains_majestic

def get_alexa_data(path):
    domains_alexa = []
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines[:1000000]:
            domains_alexa.append(line.split(',')[1].strip('\n'))
    return domains_alexa

def get_tranco_data(path):
    domains_tranco = []
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines[:1000000]:
            domains_tranco.append(line.split(',')[1].strip('\n'))
    return domains_tranco

def calculate_rank(list1, list2):
    rank = []
    for i in list2:
        if i in list1:
            rank.append(list2.index(i))
        elif i not in list1:
            rank.append(-1)
    return rank

def modify_dict(dict_data):
    return [dict([(i, dict_data[i][j]) for i in dict_data.keys()] + [('_id', j)]) for j in range(len(dict_data['domains']))]


# Majestic Rank Calculation
majestic_data = {}
majestic_filepaths = get_filepaths('majestic_list.csv')
majestic_filepaths.sort()
majestic_data['domains'] = get_majestic_data(majestic_filepaths[0])
for path in majestic_filepaths[1:]:
    print(path)
    temp = get_majestic_data(path)
    day = path.split('/')[4]
    rank = calculate_rank(majestic_data['domains'], temp)
    majestic_data[day] = rank

majestic_data = modify_dict(majestic_data)
with open('/home/apurv/top1millionlists/majestic_initial_results', 'w+') as f:
    f.write(json.dumps(majestic_data, indent=4, sort_keys=True, default=str))

# Alexa Rank Calculation
alexa_data = {}
alexa_filepaths = get_filepaths('alexa_list.csv')
alexa_filepaths.sort()
alexa_data['domains'] = get_alexa_data(alexa_filepaths[0])
for path in alexa_filepaths[1:]:
    print(path)
    temp = get_alexa_data(path)
    day = path.split('/')[4]
    rank = calculate_rank(alexa_data['domains'], temp)
    alexa_data[day] = rank

alexa_data = modify_dict(alexa_data)
with open('/home/apurv/top1millionlists/alexa_initial_results', 'w+') as f:
    f.write(json.dumps(alexa_data, indent=4, sort_keys=True, default=str))

#Tranco Rank Calculation
tranco_data = {}
tranco_filepaths = get_filepaths('tranco_list.csv')
tranco_filepaths.sort()
tranco_data['domains'] = get_alexa_data(tranco_filepaths[0])
for path in tranco_filepaths[1:]:
    print(path)
    temp = get_tranco_data(path)
    day = path.split('/')[4]
    rank = calculate_rank(tranco_data['domains'], temp)
    tranco_data[day] = rank

tranco_data = modify_dict(tranco_data)
with open('/home/apurv/top1millionlists/tranco_initial_results', 'w+') as f:
    f.write(json.dumps(tranco_data, indent=4, sort_keys=True, default=str))


# Adding data to ES
ES_pipeline = ElasticSearchPipeline()
ES_pipeline.process_item(majestic_data, 'majestic')
ES_pipeline.process_item(alexa_data, 'alexa')
ES_pipeline.process_item(tranco_data, 'tranco')

