"""Settings of the LifeWatch ERIC catalogue import."""

from .enums import ResourceType

SEARCH_URL = 'https://metadatacatalogue.lifewatch.eu/srv/api/search/records/_search'

# Above the number of records of any resource type. The search response validator rejects a
# response that does not contain all matching records.
MAX_HITS_PER_SEARCH = 1000


# Tables created by default, keyed by table name
CATALOGUE_TABLES = {
    'services': ResourceType.SERVICE,
    'workflows': ResourceType.WORKFLOW,
    'vres': ResourceType.VRE,
    'training': ResourceType.TRAINING,
}
