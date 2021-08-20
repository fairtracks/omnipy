import json
import time
import pandas as pd
from abc import ABC

import requests

from unifair.core.data import NoData, PandasDataFrameCollection
from unifair.core.workflow import WorkflowStep


class ImportEncodeMetadataFromApi(WorkflowStep):
    HEADERS = {'accept': 'application/json'}
    ENCODE_BASE_URL = 'https://www.encodeproject.org/'

    def __init__(self):
        pass

    @staticmethod
    def _get_name():
        return "1_import_encode_metadata_from_api"

    def _get_input_data_cls(self):
        return NoData

    def _get_output_data_cls(self):
        return PandasDataFrameCollection

    def _run(self, input_data):
        output = PandasDataFrameCollection()
        for table_name in ['experiments', 'biosample']:
            json_output = self.encode_api(table_name, limit='25')
            output.add_object(table_name, pd.json_normalize(json_output))
            time.sleep(1)  # Sleep to not overload ENCODE servers
        return output

    @classmethod
    def encode_api(cls, object_type='experiments', id=None, limit=None, format='json', frame='object'):
        api_url = cls.ENCODE_BASE_URL + object_type + '/' + \
                                (id if id else '@@listing') + '?' + \
                                '&'.join((['limit=' + limit] if limit else []) +
                                         (['format=' + format] if format else []) +
                                         (['frame=' + frame] if frame else []))
        print(api_url)
        response = requests.get(api_url, headers=cls.HEADERS)
        if response.status_code == 200:
            results = response.json()
            if results['notification'] == 'Success':
                graph = results['@graph']
                return graph
        else:
            print('No result found')

