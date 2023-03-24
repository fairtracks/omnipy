#!/usr/bin/env python

import json
import sys
from typing import cast, Dict, List, Optional, Union

from numpy import arange
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


def call_endpoint(endpoint: str, filter: Optional[Filter] = None, **kwargs: object) -> Json:
    if filter:
        kwargs['filter'] = filter.dict()
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
fields = ','.join(['summary.case_count', 'summary.file_count'])

response = call_endpoint(
    projects_endpt, filter=create_filter('program.name', ['TCGA']), fields=fields, size=size)

if len(response['data']['hits']) != size:
    print('size mismatch')
    sys.exit()

projects_list = response['data']['hits']

##########################################################################
# Step3: filtered query on 'cases' (filter on project_id) to get cases ID for each TCGA project
#      the IDs for all the files are also available form this endpoint
########################################################################

fields = ['files.file_id', 'summary.file_count', 'annotation']
fields = ','.join(fields)

for proj in projects_list:
    if download_all_cases:
        size = proj['summary']['case_count']
    else:
        size = min(proj['summary']['case_count'], number_of_cases)
    filters = {
        'op': 'in',
        'content': {
            'field': 'project.project_id',
            'value': proj['id'],
        },
    }
    params = {
        'filters': json.dumps(filters),
        'fields': fields,
        'size': size,
    }
    response = requests.get(cases_endpt, params=params)
    cases = (response.json()['data']['hits'])
    proj['cases'] = cases

##############################################################################
# step4: filtered query on 'annotations' (filter on case_id) to get cases
#        ID for each TCGA project the IDs for all the files are also available
#        form this endpoint
##############################################################################

fields = ['annotation_id']

for proj in projects_list:
    for case in proj['cases']:
        filters = {
            'op': 'in',
            'content': {
                'field': 'case_id',
                'value': case['id'],
            },
        }
        params = {
            'fields': fields,
            'filters': json.dumps(filters),
        }
        response = requests.get(annotations_endpt, params=params)
        annotations = response.json()['data']['hits']
        case['annotations'] = annotations

############################################################################
# step 5: create list of IDs for projects, cases, files and annotations
#         Use these lists to define filters and write them to file
###########################################################################

proj_id_list = []
case_id_list = []
file_id_list = []
ant_id_list = []

for proj in projects_list:
    proj_id_list.append(proj['id'])
    for case in proj['cases']:
        case_id_list.append(case['id'])
        for i, file in enumerate(case['files']):
            if i >= number_of_files:
                continue
            file_id_list.append(file['file_id'])
        for ant in case['annotations']:
            ant_id_list.append(ant['annotation_id'])

id_dict = {
    'projects': proj_id_list,
    'cases': case_id_list,
    'files': file_id_list,
    'annotations': ant_id_list,
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
