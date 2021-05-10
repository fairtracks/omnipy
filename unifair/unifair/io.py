import json
import os
from collections import OrderedDict

from unifair.formats import JsonDataset, convert_dataframe_to_json, \
    convert_dataframe_to_csv, convert_json_to_dataframe, convert_csv_to_dataframe
from unifair.constants import JSON_DATA_SUFFIX, JSON_HEADERS_SUFFIX, \
    CSV_SUFFIX, DATA_DIR, HTML_SUFFIX, REF_DATA_DIR


def read_dataset_from_json(input_dataset, subtype):
    json_dataset = read_json(input_dataset, subtype)
    df = convert_json_to_dataframe(json_dataset)
    return df


def read_dataset_from_csv(input_dataset, subtype, header='infer', index_cols=(0, 1)):
    with open_input_dataset_file(input_dataset, get_csv_filename(subtype)) as csv_file:
        csv_content = csv_file.read()
    return convert_csv_to_dataframe(csv_content, header=header, index_cols=index_cols)


def read_reference_dataset_from_csv(reference_dataset, header='infer', index_cols=(0, 1)):
    with open_input_reference_file(get_csv_filename(reference_dataset)) as csv_file:
        csv_content = csv_file.read()
    return convert_csv_to_dataframe(csv_content, header=header, index_cols=index_cols)


def write_dataset_as_json(df, output_dataset, subtype):
    json_dataset = convert_dataframe_to_json(df)
    write_json(json_dataset, output_dataset, subtype)


def write_dataset_as_csv(df, output_dataset, subtype):
    csv_content = convert_dataframe_to_csv(df)
    with open_output_dataset_file(output_dataset, get_csv_filename(subtype)) as csv_file:
        csv_file.write(csv_content)


def read_json(input_dataset, subtype):
    json_content = {}
    for filetype, filename in get_json_filename_dict(subtype).items():
        with open_input_dataset_file(input_dataset, filename) as json_file:
            json_content[filetype] = json.load(json_file, object_pairs_hook=OrderedDict)
    return JsonDataset(**json_content)


def write_json(json_dataset, output_dataset, subtype):
    json_filename_dict = get_json_filename_dict(subtype)
    for filetype, filename in json_filename_dict.items():
        with open_output_dataset_file(output_dataset, filename) as json_file:
            json_file.write(json.dumps(getattr(json_dataset, filetype), indent=4))


# Util functions

def get_csv_filename(subtype):
    return subtype + CSV_SUFFIX


def get_html_filename(subtype):
    return subtype + HTML_SUFFIX


def get_json_filename_dict(subtype):
    data_filename = subtype + JSON_DATA_SUFFIX
    headers_filename = subtype + JSON_HEADERS_SUFFIX
    return {'data': data_filename, 'headers': headers_filename}


def open_input_dataset_file(input_dataset, filename):
    return open(os.path.join(DATA_DIR, input_dataset, filename), 'r')


def open_output_dataset_file(output_dataset, filename):
    file_path = os.path.join(DATA_DIR, output_dataset, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    return open(file_path, 'w')


def open_input_reference_file(filename):
    return open(os.path.join(REF_DATA_DIR, filename), 'r')
