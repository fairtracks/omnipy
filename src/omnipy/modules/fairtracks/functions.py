import requests

ENCODE_HEADERS = {'accept': 'application/json'}
ENCODE_BASE_URL = 'https://www.encodeproject.org/'
GDC_BASE_URL = 'https://api.gdc.cancer.gov/'


# ['experiments', 'biosample']
def encode_api(cls, endpoint='experiments', id=None, limit=None, format='json', frame='object'):
    api_url = ENCODE_BASE_URL + endpoint + '/' + (id if id else '@@listing') + '?' + '&'.join(
        (['limit=' + limit] if limit else []) + (['format=' + format] if format else [])
        + (['frame=' + frame] if frame else []))
    print(api_url)
    response = requests.get(api_url, headers=ENCODE_HEADERS)
    if response.status_code == 200:
        results = response.json()
        if results['notification'] == 'Success':
            graph = results['@graph']
            return graph
    else:
        print('No result found')


# ['projects', 'cases', 'files', 'annotations'], starting_point='0', size='25'
def gdc_api(cls, object_type='projects', starting_point=None, size=None):
    api_url = GDC_BASE_URL + object_type + '/' + '?' + \
              '&'.join(
                  (['from=' + starting_point] if starting_point else [])
                  + (['size=' + size] if size else [])
                  + (['expand=' + 'project'] if object_type == 'cases' else [])
              )
    print(api_url)
    response = requests.get(api_url)
    if response.status_code != 200:
        print('No result found')
        return None

    results = response.json()

    if len(results['warnings']) > 0:
        print('The following warnings have been encountered:')
        print(results['warnings'])
        return None

    hits = (results['data']['hits'])
    return hits
