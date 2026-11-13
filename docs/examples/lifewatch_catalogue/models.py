"""Catalogue record schemas, the ES search API contract, and their conversions."""

from html import unescape
import re
from typing import Literal, TypedDict

import pandas as pd

import omnipy as om
import omnipy.util.pydantic as pyd

from .constants import MAX_HITS_PER_SEARCH
from .enums import ResourceType
from .helpers import (
    as_list,
    codelist_value,
    contained_service_name,
    default_text,
    single_value,
    unique,
)

# Catalogue records: one row each in the pandas tables


class CatalogueRecordSchema(pyd.BaseModel):
    """Fields shared by the services, workflows and VREs of the catalogue (ISO 19139 schema)."""

    resource_type: ResourceType = pyd.Field(alias='resourceType')
    uuid: str = pyd.Field(min_length=1)
    title: str = pyd.Field(alias='resourceTitleObject', min_length=1)
    abstract: str | None = pyd.Field(None, alias='resourceAbstractObject')
    status: str | None = pyd.Field(None, alias='cl_status')
    organisations: list[str] = pyd.Field([], alias='OrgForResource')
    keywords: list[str] = pyd.Field([], alias='keywordsKpi')
    links: list[pyd.AnyUrl] = pyd.Field([], alias='linkUrl')
    year: int | None = pyd.Field(None, alias='publicationYearForResource')

    @pyd.validator('resource_type', pre=True)
    def _single_resource_type(cls, value: object) -> object:
        return single_value(value)

    @pyd.validator('title', 'abstract', 'status', pre=True)
    def _default_text(cls, value: object) -> object:
        return default_text(value)

    @pyd.validator('organisations', 'keywords', 'links', pre=True)
    def _as_list(cls, value: object) -> object:
        return as_list(value)

    @pyd.validator('organisations')
    def _unique_organisations(cls, organisations: list[str]) -> list[str]:
        return unique(organisations)

    @pyd.validator('year', pre=True)
    def _empty_year_as_none(cls, value: object) -> object:
        return value or None


class ServiceRecordSchema(CatalogueRecordSchema):
    """A service of the catalogue."""

    resource_type: Literal[ResourceType.SERVICE] = pyd.Field(alias='resourceType')
    categories: list[str] = pyd.Field([], alias='serviceCategory_service')
    topics: list[str] = pyd.Field([], alias='topicCategory_service')
    readiness_level: str | None = pyd.Field(None, alias='serviceTRL_service')
    helpdesk: str | None = pyd.Field(None, alias='serviceHelpdesk_service')
    user_manual: str | None = pyd.Field(None, alias='serviceUserManual_service')

    @pyd.validator('categories', 'topics', pre=True)
    def _codelist_values(cls, value: object) -> object:
        return unique([codelist_value(item) for item in as_list(value)])

    @pyd.validator('readiness_level', 'helpdesk', 'user_manual', pre=True)
    def _empty_text_as_none(cls, value: object) -> object:
        return value or None


class WorkflowRecordSchema(CatalogueRecordSchema):
    """A workflow of the catalogue, composed of services."""

    resource_type: Literal[ResourceType.WORKFLOW] = pyd.Field(alias='resourceType')
    services: list[str] = pyd.Field([], alias='containServices_workflow')
    helpdesk: str | None = pyd.Field(None, alias='workflowHelpdesk_workflow')

    @pyd.validator('services', pre=True)
    def _service_names(cls, value: object) -> object:
        return [contained_service_name(item) for item in as_list(value)]

    @pyd.validator('helpdesk', pre=True)
    def _empty_text_as_none(cls, value: object) -> object:
        return value or None


class VreRecordSchema(CatalogueRecordSchema):
    """A Virtual Research Environment (VRE) of the catalogue, giving access to services."""

    resource_type: Literal[ResourceType.VRE] = pyd.Field(alias='resourceType')
    services: list[str] = pyd.Field([], alias='containServices_vre')
    helpdesk: str | None = pyd.Field(None, alias='vreHelpdesk_vre')
    user_manual: str | None = pyd.Field(None, alias='vreUserManual_vre')

    @pyd.validator('services', pre=True)
    def _service_names(cls, value: object) -> object:
        return [contained_service_name(item) for item in as_list(value)]

    @pyd.validator('helpdesk', 'user_manual', pre=True)
    def _empty_text_as_none(cls, value: object) -> object:
        return value or None


class TrainingRecordSchema(pyd.BaseModel):
    """A training resource of the catalogue.

    Apart from the title, the fields of a training record are given as a list of labelled
    values in 'emptySchemaTitleFields', e.g. `[{'Year': '2020'}, {'Language': 'English'}]`.
    """

    resource_type: Literal[ResourceType.TRAINING] = pyd.Field(alias='resourceType')
    uuid: str = pyd.Field(min_length=1)
    title: str = pyd.Field(alias='resourceTitleObject', min_length=1)
    description: str | None = pyd.Field(None, alias='Description')
    organisation: str | None = pyd.Field(None, alias='Organisation')
    authors: list[str] = pyd.Field([], alias='Authors')
    url: pyd.AnyUrl | None = pyd.Field(None, alias='URL')
    keywords: list[str] = pyd.Field([], alias='Keywords')
    year: int | None = pyd.Field(None, alias='Year')
    access_rights: str | None = pyd.Field(None, alias='Access rights')
    target_groups: list[str] = pyd.Field([], alias='Target groups')
    expertise_level: str | None = pyd.Field(None, alias='Expertise level')
    learning_resource_types: list[str] = pyd.Field([], alias='Learning resource types')
    language: str | None = pyd.Field(None, alias='Language')

    @pyd.root_validator(pre=True)
    def _labelled_fields(cls, values: dict[str, object]) -> dict[str, object]:
        labelled_fields = values.get('emptySchemaTitleFields') or []
        assert isinstance(labelled_fields, list)
        return {**values, **{k: v for field in labelled_fields for k, v in field.items()}}

    @pyd.validator('resource_type', pre=True)
    def _single_resource_type(cls, value: object) -> object:
        return single_value(value)

    @pyd.validator('title', pre=True)
    def _default_text(cls, value: object) -> object:
        return default_text(value)

    @pyd.validator('description')
    def _html_as_text(cls, description: str | None) -> str | None:
        return unescape(re.sub(r'<[^>]+>', '', description)).strip() if description else None

    @pyd.validator('authors', 'keywords', 'target_groups', 'learning_resource_types', pre=True)
    def _as_list(cls, value: object) -> object:
        return as_list(value)


CatalogueRecord = (
    ServiceRecordSchema | WorkflowRecordSchema | VreRecordSchema | TrainingRecordSchema
)

RECORD_SCHEMAS: dict[ResourceType, type[CatalogueRecord]] = {
    ResourceType.SERVICE: ServiceRecordSchema,
    ResourceType.WORKFLOW: WorkflowRecordSchema,
    ResourceType.VRE: VreRecordSchema,
    ResourceType.TRAINING: TrainingRecordSchema,
}


# Search API contract (ES search request and response)


class SearchRequestSchema(pyd.BaseModel):
    """An ES search request: the matching records, with the given fields of their source."""

    size: int = pyd.Field(gt=0)
    query: dict[str, object]
    source_fields: list[str] = pyd.Field(alias='_source')

    class Config:
        allow_population_by_field_name = True


class SearchTotalSchema(pyd.BaseModel):
    """The number of matching records of an ES search, exact if `relation` is 'eq'."""

    value: int = pyd.Field(ge=0)
    relation: Literal['eq', 'gte']


class SearchHitSchema(pyd.BaseModel):
    """A matching record of an ES search."""

    source: CatalogueRecord = pyd.Field(alias='_source')


class _SearchHitsValues(TypedDict):
    total: SearchTotalSchema


class SearchHitsSchema(pyd.BaseModel):
    """The matching records of an ES search, which must include all of them."""

    total: SearchTotalSchema
    hits: list[SearchHitSchema]

    @pyd.validator('hits')
    def _all_matching_records(
        cls, hits: list[SearchHitSchema], values: _SearchHitsValues
    ) -> list[SearchHitSchema]:
        if 'total' in values:
            total = values['total']
            if total.relation != 'eq' or total.value != len(hits):
                raise ValueError(
                    f'Got {len(hits)} of {total.value} matching records. Paging is not supported'
                )
        return hits


class SearchResponseSchema(pyd.BaseModel):
    """An ES search response."""

    hits: SearchHitsSchema


# Conversions into search requests and tables


@om.mimics(SearchRequestSchema)
class ResourceTypeToSearchRequestMapper(om.ConverterModel[ResourceType, SearchRequestSchema]):
    """Search request for the published records of a resource type, with the fields it uses."""

    @classmethod
    def _convert(cls, data: ResourceType) -> SearchRequestSchema:
        record_schema = RECORD_SCHEMAS[data]
        published_records_of_type = {
            'bool': {
                'filter': [
                    {'term': {'resourceType': data.value}},
                    {'term': {'isTemplate': 'n'}},
                ],
            },
        }
        source_fields = [field.alias for field in record_schema.__fields__.values()]
        if record_schema is TrainingRecordSchema:
            source_fields.append('emptySchemaTitleFields')

        return SearchRequestSchema(
            size=MAX_HITS_PER_SEARCH,
            query=published_records_of_type,
            source_fields=source_fields,
        )


@om.mimics(pd.DataFrame)
class SearchResponseToTableMapper(om.ConverterModel[om.Model[SearchResponseSchema], pd.DataFrame]):
    """Table of the records in a search response, one column per record field."""

    @classmethod
    def _convert(cls, data: om.Model[SearchResponseSchema]) -> pd.DataFrame:
        records = [hit.source.content.dict(exclude={'resource_type'}) for hit in data.hits.hits]
        return pd.DataFrame(records).convert_dtypes()
