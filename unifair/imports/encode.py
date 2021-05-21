import json
import requests

HEADERS = {'accept': 'application/json'}
ENCODE_BASE_URL = 'https://www.encodeproject.org/search/'


def search_encode(search_terms, object_type=None, limit=None, format='json', out_file_path=None):
    response = requests.get(ENCODE_BASE_URL + '?' +
                            ('&'.join(search_terms) if search_terms else '') +
                            ('&type=' + object_type if object_type else '') +
                            ('&limit=' + limit if limit else '') +
                            ('&format=' + format if format else ''), headers=HEADERS)
    if response.status_code == 200:
        results = response.json()
        if results['notification'] == 'Success':
            graph = results['@graph']
            if out_file_path:
                with open(out_file_path, 'w') as out_file:
                    json.dump(graph, out_file, indent=4)
            else:
                print(json.dumps(graph, indent=4))
            return graph
    else:
        print('No result found')

