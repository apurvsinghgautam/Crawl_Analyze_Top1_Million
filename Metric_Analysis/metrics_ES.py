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
        for line in lines:
            domains_tranco.append(line.split(',')[1].strip('\n'))
    return domains_tranco

def calculate_metric(list1, list2):
    metric = []
    for i in list2:
        if i.split(' ')[0] in list1:
            metric.append(i.split(' ')[1].strip('\n'))
        elif i not in list1:
            metric.append('error')
    return metric

def modify_dict(dict_data):
    return [dict([(i, dict_data[i][j]) for i in dict_data.keys()] + [('_id', j)]) for j in range(len(dict_data['domains']))]


tranco_data = {}
tranco_filepaths = get_filepaths('tranco_list.csv')
tranco_filepaths.sort()
tranco_data['domains'] = get_tranco_data(tranco_filepaths[0])
http2_lines = []
ipv6_lines = []
tls_lines = []
with open('/home/apurv/top1millionlists/HTTP_2_Check/http2_check_results/allresult', 'r') as f:
    http2_lines = f.readlines()
http2_metric = calculate_metric(tranco_data['domains'], http2_lines)

with open('/home/apurv/top1millionlists/IPV_6_CHECK/ipv6_check_results/allresult', 'r') as f:
    ipv6_lines = f.readlines()
ipv6_metric = calculate_metric(tranco_data['domains'], ipv6_lines)

with open('/home/apurv/top1millionlists/TLS_Ver_Check/tls_ver_check_results/allresult', 'r') as f:
    tls_lines = f.readlines()
tls_metric = calculate_metric(tranco_data['domains'], tls_lines)

tranco_data['http2_metric'] = http2_metric
tranco_data['ipv6_metric'] = ipv6_metric
tranco_data['tls_metric'] = tls_metric
tranco_data = modify_dict(tranco_data)

with open('/home/apurv/top1millionlists/tranco_metrics_results', 'w+') as f:
    f.write(json.dumps(tranco_data, indent=4, sort_keys=True, default=str))


# # Adding data to ES
# ES_pipeline = ElasticSearchPipeline()
# ES_pipeline.process_item(tranco_data, 'metrics')

