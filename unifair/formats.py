from io import StringIO
from collections import OrderedDict, namedtuple

import pandas as pd
from dpath import util as du

# Data structures

JsonDataset = namedtuple('JsonDataset', ('data', 'headers'))


# Functions

def convert_dataframe_to_dict(df):
    temp_dict = df.to_dict(orient='index', into=OrderedDict)

    out = []
    for county_precinct, cols in temp_dict.items():
        row = OrderedDict()
        row[df.index.names[0]] = county_precinct[0]
        row[df.index.names[1]] = county_precinct[1]

        top_headers = [_ for _ in list(set(header[0] for header in cols.keys()))]
        sorted_top_header = get_top_headers_sorted_by_std_order(top_headers)
        for top_header in sorted_top_header:
            row[top_header] = OrderedDict()

        for header, val in cols.items():
            if header[1] == '':
                header = [header[0]]
            du.new(row, list(header), val)
        out.append(row)

    return out


def convert_dataframe_to_json(df):
    df = get_dataframe_with_top_headers_sorted_by_std_order(df)
    df_dict = convert_dataframe_to_dict(df)
    header_list = [[header] for header in df.index.names] + list(df.columns)
    return JsonDataset(df_dict, header_list)


def convert_dataframe_to_csv(df):
    df = get_dataframe_with_top_headers_sorted_by_std_order(df)
    csv_content = df.to_csv()
    return csv_content


def convert_json_to_dataframe(json_dataset):
    data, headers = json_dataset
    df = pd.json_normalize(data, meta=headers)
    df = df.set_index(headers[0] + headers[1])  # use county and prefix and index
    df.columns = df.columns.str.split('.', expand=True)  # create hierarchical columns
    df = get_dataframe_with_top_headers_sorted_by_std_order(df)
    return df


def convert_csv_to_dataframe(csv_content, header='infer', index_cols=None):
    df = pd.read_csv(StringIO(csv_content), header=header)
    if index_cols:
        df = df.set_index([df.columns[i] for i in index_cols])
    df = get_dataframe_with_top_headers_sorted_by_std_order(df)
    return df


# Util functions

def get_dataframe_with_top_headers_sorted_by_std_order(df):
    level, top_headers = (0, df.columns.levels[0]) if hasattr(df.columns, 'levels') \
        else (None, df.columns)
    sorted_top_headers = get_top_headers_sorted_by_std_order(top_headers)
    return df.reindex(sorted_top_headers, level=level, axis=1)


def get_top_headers_sorted_by_std_order(top_headers):
    col_order = STD_COL_ORDER + sorted([_ for _ in top_headers if _ not in STD_COL_ORDER])
    sorted_top_headers = sorted(top_headers, key=lambda x: col_order.index(x))
    return sorted_top_headers
