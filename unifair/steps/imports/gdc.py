import json
import time
import pandas as pd
from abc import ABC

import requests

from unifair.core.data import NoData, PandasDataFrames
from unifair.core.workflow import WorkflowStep


class ImportGDCMetadataFromApi(WorkflowStep):
    GDC_BASE_URL = 'https://api.gdc.cancer.gov/'

    def __init__(self):
        pass

    @staticmethod
    def _get_name():
        return "1_import_GDC_metadata_from_api"

    def _get_input_data_cls(self):
        return NoData

    def _get_output_data_cls(self):
        return PandasDataFrames

    def _run(self, input_data):
        output = PandasDataFrames()
        for table_name in ['projects','cases','files','annotations']:
            json_output = self.gdc_api(object_type=table_name, starting_point='0', size='25')
            output.add_dataframe(table_name, pd.json_normalize(json_output))
            time.sleep(1)  # Sleep to not overload servers
        return output

    @classmethod
    def gdc_api(cls, object_type='projects', starting_point=None, size=None):
        api_url = cls.GDC_BASE_URL + object_type + '/' + '?' + \
            '&'.join((['from=' + starting_point] if starting_point else []) + \
                     (['size=' + size] if size else [])) 
        print(api_url)
        response = requests.get(api_url)
        if response.status_code == 200:
            results = response.json()
            if len(results['warnings'])==0:
                hits = (results['data']['hits'])
                return hits
            else:
                print("The following warnings have been enocunterted:")
                print(results['warnings'])
        else:
            print('No result found')

