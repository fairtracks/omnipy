"""Serializer registry helpers for Omnipy component packages."""

from omnipy.shared.protocols.data import IsSerializerRegistry


def register_serializers(registry: IsSerializerRegistry):
    """Register the built-in component serializers with a registry."""

    from .json.serializers import JsonDatasetToTarFileSerializer
    from .pandas.serializers import PandasDatasetToTarFileSerializer
    from .raw.serializers import (RawBytesDatasetToTarFileSerializer,
                                  RawStrDatasetToTarFileSerializer)

    registry.register(RawStrDatasetToTarFileSerializer)
    registry.register(RawBytesDatasetToTarFileSerializer)
    registry.register(JsonDatasetToTarFileSerializer)
    registry.register(PandasDatasetToTarFileSerializer)


def get_serializer_registry():
    """Return the active serializer registry, creating it on demand if needed."""

    from omnipy.data.serializer import SerializerRegistry
    from omnipy.hub.runtime import runtime

    serializer_registry = SerializerRegistry() if runtime is None else \
        runtime.objects.serializers
    if len(serializer_registry.serializers) == 0:
        register_serializers(serializer_registry)
    return serializer_registry
