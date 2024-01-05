from omnipy.api.protocols.public.data import IsSerializerRegistry


def register_serializers(registry: IsSerializerRegistry):
    from .json.serializers import JsonDatasetToTarFileSerializer
    from .pandas.serializers import PandasDatasetToTarFileSerializer
    from .raw.serializers import (RawBytesDatasetToTarFileSerializer,
                                  RawStrDatasetToTarFileSerializer)

    registry.register(RawStrDatasetToTarFileSerializer)
    registry.register(RawBytesDatasetToTarFileSerializer)
    registry.register(JsonDatasetToTarFileSerializer)
    registry.register(PandasDatasetToTarFileSerializer)


def get_serializer_registry():
    from omnipy.data.serializer import SerializerRegistry
    from omnipy.hub.runtime import runtime

    serializer_registry = SerializerRegistry() if runtime is None else \
        runtime.objects.serializers
    if len(serializer_registry.serializers) == 0:
        register_serializers(serializer_registry)
    return serializer_registry


# TODO: Add module with helper classes/functions/takss to make it simpler to contact REST apis
#       Augmentation service should have some attempts at this.
