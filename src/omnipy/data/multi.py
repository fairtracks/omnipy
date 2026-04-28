from typing import Any, Generic, Iterable, Mapping

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.util.pydantic import ValidationError
import omnipy.util.pydantic as pyd

_GeneralModelT = TypeVar('_GeneralModelT', bound='Model')


class MultiModelDataset(Dataset[_GeneralModelT], Generic[_GeneralModelT]):
    """
        Variant of Dataset that allows custom models to be set on individual data files

        Note that the general model still needs to hold for all data files, in addition to any
        custom models.
    """

    # Custom field models should really be a subtype of _GeneralModelT,
    # however this is currently not checkable in the type system. Instead,
    # we rely on the _validate method to ensure that the custom field
    # models are valid.

    _custom_field_models: 'dict[str, type[Model]]' = pyd.PrivateAttr(default={})

    def set_model(self, data_file: str, model: 'type[Model]') -> None:
        try:
            self._custom_field_models[data_file] = model
            if data_file in self.data:
                self._validate_data_file(data_file)
            else:
                self.data[data_file] = model()
        except ValidationError:
            del self._custom_field_models[data_file]
            raise

    def get_model(self, data_file: str) -> type[Model]:
        if data_file in self._custom_field_models:
            return self._custom_field_models[data_file]
        else:
            return self.get_type()

    def from_data(self,
                  data: Mapping[str, Any] | Iterable[tuple[str, Any]],
                  update: bool = True) -> None:
        super().from_data(data, update)
        for data_file in self:
            self._validate_data_file_according_to_custom_field_model(data_file)
        self._force_full_validation()

    def _validate_data_file(self, data_file: str) -> None:
        self._validate_data_file_according_to_custom_field_model(data_file)
        self._force_full_validation()

    def _validate_data_file_according_to_custom_field_model(self, data_file: str):
        from omnipy.data.model import is_model_instance, Model

        if data_file in self._custom_field_models:
            model = self._custom_field_models[data_file]
            if not is_model_instance(model):
                model = Model[model]
            data_obj = self._to_data_if_model(self.data[data_file])
            parsed_data = self._to_data_if_model(model(data_obj))
            self.data[data_file] = parsed_data

    @staticmethod
    def _to_data_if_model(data_obj: Any):
        from omnipy.data.model import is_model_instance

        if is_model_instance(data_obj):
            data_obj = data_obj.to_data()
        return data_obj
