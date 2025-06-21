import asyncio
import random

import omnipy as om
from omnipy.shared.enums import (DarkHighContrastColorStyles,
                                 DarkLowContrastColorStyles,
                                 LightHighContrastColorStyles,
                                 LightLowContrastColorStyles,
                                 RecommendedColorStyles)


def set_random_style():
    om.runtime.config.root_log.log_to_stdout = False
    om.runtime.config.data.display.terminal.width = 160
    om.runtime.config.data.display.terminal.color.style = random.choice(
        list(DarkHighContrastColorStyles) + list(DarkLowContrastColorStyles)
        + list(LightHighContrastColorStyles) + list(LightLowContrastColorStyles)
        + list(RecommendedColorStyles))
    om.runtime.config.data.display.terminal.color.transparent_background = False
    print(f'color.style={om.runtime.config.data.display.terminal.color.style}')
    print(f'color.transparent_background='
          f'{om.runtime.config.data.display.terminal.color.transparent_background}')


# Omnipy tasks
@om.TaskTemplate()
def fetch_and_validate_isa_json_files(
    url_list: om.HttpUrlDataset
) -> 'asyncio.Task[om.Dataset[om.IsaJsonModel]] | om.Dataset[om.IsaJsonModel]':
    return om.IsaJsonDataset.load(url_list, as_mime_type='application/json')


# Omnipy dataflows
@om.LinearFlowTemplate(
    om.get_github_repo_urls.refine(fixed_params=dict(file_suffix='.json')),
    fetch_and_validate_isa_json_files,
)
def download_isa_json_files(owner: str, repo: str, branch: str,
                            path: str) -> om.JsonListOfDictsDataset:
    ...


# Run the dataflow
dataset = download_isa_json_files.run(
    owner='fairtracks',
    repo='omnipy_example_data',
    branch='main',
    path='omnipy_example_data/isa-json',
)


def print_all():
    set_random_style()
    print(dataset.list())
    print(dataset.peek())
    print(om.StrModel(dataset[0].to_json()).peek())
    print(om.JsonModel(dataset[0]).peek())


print_all()
