import os
import time
import json
from io import BytesIO
from tarfile import TarFile, TarInfo
from typing import Dict

import prefect
import pandas as pd
from prefect.executors import LocalExecutor
from pydantic import BaseModel
from prefect import task, Flow


# Extract from ENCODE and TCGA APIs
from prefect.engine.results import LocalResult
from unifair.steps.imports.encode import ImportEncodeMetadataFromApi


class JsonObjects(BaseModel):
    objects: Dict[str, str] = {}


class JsonObjectsSerializer(prefect.engine.serializers.Serializer):
    def serialize(self, value: JsonObjects) -> bytes:
        # transform a Python object into bytes
        output = ''
        for key, obj in value.objects.items():
            output += json.dumps(obj, indent=4) + os.linesep
        return output.encode('utf8')

    def deserialize(self, value: bytes) -> JsonObjects:
        # recover a Python object from bytes
        pass


PREFECT_RESULTS=LocalResult(dir="../data_prefect", serializer=JsonObjectsSerializer())


@task(target="testing.txt", checkpoint=True, result=PREFECT_RESULTS)
def extract_encode_api() -> JsonObjects:
    output = JsonObjects()
    for obj_type in ['experiments', 'biosample']:
        output.objects[obj_type] = ImportEncodeMetadataFromApi.encode_api(obj_type, limit='25')
        time.sleep(1)  # Sleep to not overload ENCODE servers
    # PREFECT_RESULTS.write(output)
    return output


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
    encode_data_api = extract_encode_api()
    # encode_data_clean = json_cleanup(encode_data_api)
    # encode_data_normalised = transform_first_normal(encode_data_clean)
    # encode_data_fair = transform_fair(encode_data_normalised)

encode_flow.run(executor=LocalExecutor())

# with Flow("Unifair - Gsuit") as gsuit_flow:

bytes_io = BytesIO()
bytes_io_file = BytesIO(b'Contents')
bytes_io_file.seek(0)
ti = TarInfo(name='mydir/myfile')
ti.size = len(bytes_io_file.getbuffer())

tf = TarFile(fileobj=bytes_io, mode='w')
tf.addfile(ti, bytes_io_file)
tf.close()

with open('testfile.tar', 'wb') as outfile:
    outfile.write(bytes_io.getbuffer())
