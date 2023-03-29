#!/usr/bin/env python

import json
import sys
from typing import cast, Dict, List, Optional, Union

from pydantic import BaseModel
import requests

from omnipy.modules.json.types import Json, JsonDict

#########################################################
# user parameters
#######################################################
download_all_projects = False
download_all_cases = False
number_of_projects = 2
number_of_cases = 2
number_of_files = 2
# NB very few annotations per case, get all

#######################################################
# endpoints definition
########################################################
projects_endpt = 'https://api.gdc.cancer.gov/projects'
cases_endpt = 'https://api.gdc.cancer.gov/cases'
annotations_endpt = 'https://api.gdc.cancer.gov/annotations'

###########################################################
# step1: get total number of TCGA projects (program.name)
###########################################################


class Content(BaseModel):
    field: str
    value: List[str]


class Filter(BaseModel):
    op: str = 'in'
    content: Content


def create_filter(field: str, value: List[str]) -> Filter:
    return Filter(content=Content(field=field, value=value))


def call_endpoint(endpoint: str, filters: Optional[Filter] = None, **kwargs: object) -> Json:
    if filters:
        kwargs['filters'] = json.dumps(filters.dict())
    return requests.get(endpoint, params=kwargs).json()  # type: ignore


def get_project_count_for_program(program: str) -> Optional[int]:
    response = call_endpoint(
        projects_endpt,
        facets='program.name',
        size=0,
        **{'from': 0},  # due to 'from' being a reserved keyword
    )
    buckets = response['data']['aggregations']['program.name']['buckets']

    for bucket in buckets:
        if bucket['key'] == program:
            project_count = bucket['doc_count']
            return project_count
        raise ValueError(f'Program with name "{program}" could not be found')


size_max = cast(int, get_project_count_for_program('TCGA'))

if download_all_projects:
    size = size_max
else:
    size = min(size_max, number_of_projects)

##############################################################
# step 2: filtered query to get the UIDs of each TCGA project
##############################################################
fields = ','.join(['summary.case_count', 'summary.file_count', 'program.name'])
response = call_endpoint(projects_endpt, filters=create_filter('program.name', ['TCGA']), fields=fields, size=size)
response2 = call_endpoint(projects_endpt, fields=fields, size=size)
projects = response['data']['hits']
if len(projects) != size:
    print('size mismatch')
    sys.exit()

##########################################################################
# Step3: filtered query on 'cases' (filter on project_id) to get cases ID for each TCGA project
#      the IDs for all the files are also available form this endpoint
########################################################################

for project in projects:
    if download_all_cases:
        size = project['summary']['case_count']
    else:
        size = min(project['summary']['case_count'], number_of_cases)
    response = call_endpoint(
        cases_endpt, filter=create_filter('project.project_id', [project['id']]),
        fields=','.join(['files.file_id', 'summary.file_count', 'annotation']), size=size)
    project['cases'] = response['data']['hits']

##############################################################################
# step4: filtered query on 'annotations' (filter on case_id) to get cases
#        ID for each TCGA project the IDs for all the files are also available
#        form this endpoint
##############################################################################

for project in projects:
    for case in project['cases']:
        response = call_endpoint(
            annotations_endpt, filter=create_filter('case_id', [case['id']]),
            fields=['annotation_id'], size=size)
        case['annotations'] = response['data']['hits']

############################################################################
# step 5: create list of IDs for projects, cases, files and annotations
#         Use these lists to define filters and write them to file
###########################################################################

proj_id_list = []
case_id_list = []
file_id_list = []
annotation_id_list = []

for project in projects:
    proj_id_list.append(project['id'])
    for case in project['cases']:
        case_id_list.append(case['id'])
        for i, file in enumerate(case['files']):
            if i >= number_of_files:
                continue
            file_id_list.append(file['file_id'])
        for annotation in case['annotations']:
            annotation_id_list.append(annotation['annotation_id'])

id_dict = {
    'projects': proj_id_list,
    'cases': case_id_list,
    'files': file_id_list,
    'annotations': annotation_id_list,
}

for entry in ['cases', 'projects', 'files', 'annotations']:
    filters = {
        'op': 'in',
        'content': {
            'field': entry[0:-1] + '_id',
            'value': id_dict[entry],
        },
    }
    with open(entry + '_filter.json', 'w') as outfile:
        json.dump(filters, outfile, indent=4)
