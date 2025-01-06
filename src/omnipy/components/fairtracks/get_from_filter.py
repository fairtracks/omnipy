#!/usr/bin/env python

import json

import requests


def get_from_filter():
    for endpt_str in ['projects', 'cases', 'files', 'annotations']:
        endpt = 'https://api.gdc.cancer.gov/' + endpt_str
        endpt_map = endpt + '/_mapping'
        response = requests.get(endpt_map)
        fields = response.json()['fields']
        fields = ','.join(fields)

        with open(endpt_str + '_filter.json', 'r') as infile:
            filters = json.load(infile)
            params = {  # 'fields': fields,
                'filters': json.dumps(filters),
            }
        response = requests.get(endpt, params=params)
        print(endpt_str, 'status code', response.status_code)
        with open(endpt_str + '.json', 'w') as outfile:
            json.dump(response.json()['data'], outfile, indent=4)
