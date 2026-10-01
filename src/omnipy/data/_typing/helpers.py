"""Helpers for expanding model and dataset type variants."""

from types import GenericAlias

from omnipy.shared.protocols.data import IsDataset, IsModel
from omnipy.shared.typing import TYPE_CHECKER, TYPE_CHECKING
from omnipy.util.helpers import all_type_variants


def all_model_type_variants(model: type[IsModel] | IsModel,) -> tuple[type | GenericAlias, ...]:
    return tuple(all_type_variants(model.full_type()))


def all_dataset_type_variants(
        dataset: type[IsDataset] | IsDataset) -> tuple[type | GenericAlias, ...]:
    """Return concrete content-type variants represented by a dataset type."""

    from omnipy.data.dataset import is_dataset_subclass
    from omnipy.data.model import is_model_subclass

    _type = dataset.get_type()

    type_variants: list[type | GenericAlias] = []

    for variant in all_type_variants(_type):
        if is_model_subclass(variant):
            type_variants += all_model_type_variants(variant)
        elif is_dataset_subclass(variant):
            type_variants.append(variant)

    return tuple(type_variants)


def mimics(cls_or_protocol):
    """Type a Model as the intersection of PlainModel and a class/protocol.

    Decorate a concrete Omnipy Model subclass with this helper to indicate
    that it is a Model mimicking a specific class or protocol. This allows
    static type checkers to detect attributes and methods of the wrapped
    class in addition to those of the Omnipy Model.

    Does not work with mypy (as of v2.3.1). Specification of generic type
    parameters for ``cls_or_protocol`` are not supported. E.g.
    ``omnipy_model_of_class(list[str])`` ignores the ``str`` type parameter.

    Examples:
        >>> from typing_extensions import assert_type
        >>> import omnipy.util.pydantic as pyd
        >>> import omnipy as om

        >>> class MyPydModel(pyd.BaseModel):
        ...     x: int
        ...

        >>> @mimics(MyPydModel)
        ... class MyOmnipyModel(om.Model[MyPydModel]): ...
        >>> my_model = MyOmnipyModel(dict(x=4))
        >>> assert_type(my_model.x, int) # check with a static type checker (mypy does not work)

        >>> class IsListOfMyPydModel(IsListContent[MyPydModel]): ...

        >>> @mimics(IsListOfMyPydModel)
        ... class MyOmnipyListModel(om.Model[list[MyPydModel]]): ...
        >>> my_list_model = MyOmnipyListModel([{'x': 4}])
        >>> assert_type(my_list_model[0].x, int) # check with a static type checker (except mypy)

    Args:
        cls_or_protocol: Pydantic BaseModel type that is wrapped by Model
        model_cls: An Omnipy Model wrapping a Pydantic BaseModel type

    Returns:
        type[Model]: Model class, statically typed as the intersection of the Omnipy Model and the
            respective Pydantic BaseModel model.
    """
    if TYPE_CHECKING and TYPE_CHECKER != 'mypy':
        from omnipy.data._typing.mimic_models import PlainModel

        def _decorate(model_cls):
            assert issubclass(model_cls, PlainModel) and issubclass(model_cls, cls_or_protocol)
            return model_cls

        return _decorate

    else:

        return lambda model_cls: model_cls
