#!/usr/bin/env python

import json
import sys
from typing import List, Optional

from pydantic import BaseModel, HttpUrl
import requests

from omnipy import create_row_index_from_column, Model
from omnipy.compute.flow import LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.modules.json.datasets import JsonDataset, JsonDictOfDictsOfScalarsDataset
from omnipy.modules.json.models import JsonDictOfDictsOfScalarsModel, JsonModel
from omnipy.modules.json.typedefs import JsonScalar
from omnipy.modules.remote.models import HttpUrlModel

#########################################################
# user parameters
#######################################################
DOWNLOAD_ALL_PROJECTS = False
DOWNLOAD_ALL_CASES = False
NUMBER_OF_PROJECTS = 2
NUMBER_OF_CASES = 2
NUMBER_OF_FILES = 2
# NB very few annotations per case, get all

#######################################################
# endpoints definition
########################################################
TOP_LEVEL_URL = 'https://api.gdc.cancer.gov/'
CASES_ENDPT = 'https://api.gdc.cancer.gov/cases'
ANNOTATIONS_ENDPT = 'https://api.gdc.cancer.gov/annotations'
PROJECTS_ENDPT = 'https://api.gdc.cancer.gov/projects'

###########################################################
# step1: get total number of TCGA projects (program.name)
###########################################################


def create_gdc_api_url(endpoint: str) -> HttpUrlModel:
    url = HttpUrlModel(TOP_LEVEL_URL)
    url.path // endpoint
    return url


class Content(BaseModel):
    field: str
    value: List[str]


class Filter(BaseModel):
    op: str = 'in'
    content: Content


def create_filter(field: str, value: List[str]) -> Filter:
    return Filter(content=Content(field=field, value=value))


def call_endpoint(top_level_url: HttpUrl,
                  endpoint: str,
                  filters: Optional[Filter] = None,
                  **kwargs: JsonScalar) -> JsonModel:
    if filters:
        kwargs['filters'] = json.dumps(filters.dict())
    # full_endpoint = top_level_url + endpoint
    return JsonModel(requests.get(endpoint, params=kwargs).json())


class ProjectCountDataset(Model[int]):
    ...


@TaskTemplate()
def get_project_counts(top_level_url: HttpUrl = HttpUrl(url=TOP_LEVEL_URL)) -> ProjectCountDataset:
    response = call_endpoint(
        'projects',
        facets='program.name',
        size=0,
        **{'from': 0},  # type: ignore[arg-type]  # needed as 'from' being a reserved keyword
    )
    buckets = response['data']['aggregations']['program.name']['buckets']  # type: ignore[index]

    return ProjectCountDataset(buckets)


@TaskTemplate()
def rest_of_the_steps(  # noqa: C901
        project_count_per_program: JsonDictOfDictsOfScalarsDataset) -> JsonDataset:
    ##############################################################
    # step 2: filtered query to get the UIDs of each TCGA project
    ##############################################################
    program_info_dict = project_count_per_program['buckets']['TCGA'].contents
    size_max = program_info_dict['doc_count']

    if DOWNLOAD_ALL_PROJECTS:
        size = size_max
    else:
        size = min(size_max, NUMBER_OF_PROJECTS)

    fields = ','.join(['summary.case_count', 'summary.file_count'])
    response = call_endpoint(
        PROJECTS_ENDPT, filters=create_filter('program.name', ['TCGA']), fields=fields, size=size)
    projects = response['data']['hits']
    if len(projects) != size:
        print('size mismatch')
        sys.exit()

    ##########################################################################
    # Step3: filtered query on 'cases' (filter on project_id) to get cases ID for each TCGA project
    #        the IDs for all the files are also available form this endpoint
    ##############################################################################################

    for project in projects:
        if DOWNLOAD_ALL_CASES:
            size = project['summary']['case_count']
        else:
            size = min(project['summary']['case_count'], NUMBER_OF_CASES)
        response = call_endpoint(
            CASES_ENDPT,
            filter=create_filter('project.project_id', [project['id']]),
            fields=','.join(['files.file_id', 'summary.file_count', 'annotation']),
            size=size)
        project['cases'] = response['data']['hits']

    ##############################################################################
    # step4: filtered query on 'annotations' (filter on case_id) to get cases
    #        ID for each TCGA project the IDs for all the files are also available
    #        form this endpoint
    ##############################################################################

    for project in projects:
        for case in project['cases']:
            response = call_endpoint(
                ANNOTATIONS_ENDPT,
                filter=create_filter('case_id', [case['id']]),
                fields=['annotation_id'],
                size=size)
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
                if i >= NUMBER_OF_FILES:
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

    dataset = JsonDataset()
    for entry in ['cases', 'projects', 'files', 'annotations']:
        dataset[entry] = create_filter(entry[0:-1] + '_id', id_dict[entry])
    return dataset


@LinearFlowTemplate(
    get_project_counts,
    create_row_index_from_column.refine(
        name='create_dict_of_dicts_from_list_of_dicts_using_key_field',
        fixed_params=dict(field_whose_values_will_be_new_keys='key')),
    rest_of_the_steps)
def get_filters_for_tcga() -> JsonDictOfDictsOfScalarsModel:
    ...


get_filters_for_tcga.run()
