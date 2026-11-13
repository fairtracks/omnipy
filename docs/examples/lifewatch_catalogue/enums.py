"""Enumerations of LifeWatch ERIC catalogue vocabularies."""

from enum import Enum


class ResourceType(str, Enum):
    """Resource types of the catalogue, as found in the 'resourceType' field of records."""

    SERVICE = 'service'
    WORKFLOW = 'workflow'
    VRE = 'vre'
    TRAINING = 'training'
