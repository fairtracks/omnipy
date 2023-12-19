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


# TODO: Add module with helper classes/functions/takss to make it simpler to contact REST apis
#       Augmentation service should have some attempts at this.
