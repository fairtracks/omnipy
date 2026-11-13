"""Import the LifeWatch ERIC catalogue into pandas tables.

The LifeWatch ERIC Metadata Catalogue (https://metadatacatalogue.lifewatch.eu) is a GeoNetwork
catalogue. It describes, among other resource types, services, workflows, Virtual Research
Environments (VREs) and training resources. Its search API takes Elasticsearch (ES) queries.

The dataflow posts one ES search request per resource type, parses each search response into
typed catalogue records, and converts the records into one pandas table per resource type.
Services, workflows and VREs follow a customised ISO 19139 schema. Training resources follow a
separate schema of labelled fields.

Run from `docs/examples` with `uv run python -m lifewatch_catalogue`.
"""

from .enums import ResourceType
from .flows import import_lifewatch_catalogue

__all__ = ['import_lifewatch_catalogue', 'ResourceType']
