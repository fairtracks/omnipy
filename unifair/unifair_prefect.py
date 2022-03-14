import pandas as pd
import prefect
from prefect import task, Flow
import json


# Extract from ENCODE and TCGA APIs
@task
def extract_api() -> pd.DataFrame:
    # read in the data from an API
    # convert to pandas
    pass


@task
def extract_gsuite() -> pd.DataFrame:
    pass


@task
def extract_sq() -> pd.DataFrame:
    pass


# Transform data -> cleanup and reduce redundancy
@task
def json_cleanup(data: pd.DataFrame) -> pd.DataFrame:
    pass


@task
def transform_first_normal(data: pd.DataFrame) -> pd.DataFrame:
    data.validate()
    pass


@task
def transform_second_normal(data: pd.DataFrame) -> pd.DataFrame:
    pass


@task
def transform_third_normal(data: pd.DataFrame) -> pd.DataFrame:
    pass


@task
def transform_fair(data: pd.DataFrame) -> pd.DataFrame:
    pass


# Load data -> save normalised data into files/ databases
@task
def save_fair_data(data: pd.DataFrame) -> None:
    pass


# The workflow
with Flow("Unifair - ENCODE") as encode_flow:
    encode_data_api = extract_api()
    encode_data_clean = json_cleanup(encode_data_api)
    encode_data_normalised = transform_first_normal(encode_data_clean)
    encode_data_fair = transform_fair(encode_data_normalised)


# with Flow("Unifair - Gsuit") as gsuit_flow:
encode_flow.visualize()
