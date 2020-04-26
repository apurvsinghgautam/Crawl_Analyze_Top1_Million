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

def get_tranco_data(path):
    domains_tranco = []
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines[:10000]:
            domains_tranco.append(line.split(',')[1].strip('\n'))
    return domains_tranco

def modify_dict(dict_data):
    return [dict([(i, dict_data[i][j]) for i in dict_data.keys()] + [('_id', j)]) for j in range(len(dict_data['domains']))]


tranco_data = {}
tranco_filepaths = get_filepaths('tranco_list.csv')
tranco_filepaths.sort()
tranco_data['domains'] = get_tranco_data(tranco_filepaths[0])
tranco_lines = []
no_of_subdomains = []
with open('/home/apurv/top1millionlists/Sub Domain Enumeration/subdomain_enum_results/rank_wise_number_of_subdomains', 'r') as f:
    tranco_lines = f.readlines()
for lines in tranco_lines:
    no_of_subdomains.append(lines.strip('\n'))

tranco_data['no_of_subdomains'] = no_of_subdomains
tranco_data = modify_dict(tranco_data)
with open('/home/apurv/top1millionlists/tranco_subdomain_results', 'w+') as f:
    f.write(json.dumps(tranco_data, indent=4, sort_keys=True, default=str))


# Adding data to ES
ES_pipeline = ElasticSearchPipeline()
ES_pipeline.process_item(tranco_data, 'subdomains')

