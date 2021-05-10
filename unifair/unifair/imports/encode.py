import json
import requests

HEADERS = {'accept': 'application/json'}
ENCODE_BASE_URL = 'https://www.encodeproject.org/search/'


def search_encode(search_term, object_type, basedir='.'):
    response = requests.get(ENCODE_BASE_URL + '?searchTerm=' + search_term + '&type=' + object_type, headers=HEADERS)
    if response.status_code == 200:
        biosample = response.json()
        if (biosample['notification'] == 'Success'):
            graph = biosample['@graph']
            print(json.dumps(graph, indent=4))
    else:
        print('No result found')