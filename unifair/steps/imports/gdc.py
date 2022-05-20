import time

import requests

from unifair.core.data import JsonDocumentCollection
from unifair.core.data import NoData
from unifair.core.workflow import WorkflowStep


class ImportGDCMetadataFromApi(WorkflowStep):
    GDC_BASE_URL = 'https://api.gdc.cancer.gov/'

    def __init__(self):
        pass

    @staticmethod
    def _get_name():
        return '1_import_GDC_metadata_from_api'

    def _get_input_data_cls(self):
        return NoData

    def _get_output_data_cls(self):
        return JsonDocumentCollection

    def _run(self, input_data):
        output = JsonDocumentCollection()
        for obj_type in ['projects', 'cases', 'files', 'annotations']:
            json_output = self.gdc_api(object_type=obj_type, starting_point='0', size='25')
            # output.add_object(table_name, pd.json_normalize(json_output))
            output[obj_type] = json_output
            time.sleep(1)  # Sleep to not overload servers
        return output

    @classmethod
    def gdc_api(cls, object_type='projects', starting_point=None, size=None):
        api_url = cls.GDC_BASE_URL + object_type + '/' + '?' + \
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
