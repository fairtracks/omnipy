from dataclasses import fields

from pydantic import ValidationError
import pytest
import pytest_cases as pc

from modules.helpers.classes import CaseInfo
from omnipy.data.model import Model
from omnipy.modules.frozen.typedefs import FrozenDict


def test_frozendict_of_none() -> None:
    class NoneModel(Model[None]):
        ...

    class FrozenDictOfInt2NoneModel(Model[FrozenDict[int, NoneModel]]):
        ...

    assert FrozenDictOfInt2NoneModel().contents == FrozenDict()
    assert FrozenDictOfInt2NoneModel().contents == FrozenDict()

    with pytest.raises(ValidationError):
        FrozenDictOfInt2NoneModel(None)

    with pytest.raises(ValidationError):
        FrozenDictOfInt2NoneModel([None])

    assert FrozenDictOfInt2NoneModel({1: None}).contents == FrozenDict({1: NoneModel(None)})
    assert FrozenDictOfInt2NoneModel(FrozenDict({1: None
                                                 })).contents == FrozenDict({1: NoneModel(None)})

    with pytest.raises(ValidationError):
        FrozenDictOfInt2NoneModel({'hello': None})


@pc.parametrize_with_cases('case', cases='.cases.frozen_data')
def test_nested_frozen_models(case: CaseInfo) -> None:
    for field in fields(case.data_points):
        name = field.name
        for model_cls in case.model_classes_for_data_point(name):
            data = getattr(case.data_points, name)

            # print('\n---')
            # print(f'Field name: {name}')
            # print(f'Model class: {model_cls.__name__}')
            # print(f'Data input: {data}')

            if case.data_point_should_fail(name):
                with pytest.raises(ValidationError) as e:
                    model_cls(data)
                # print(f'Error: {e}')
            else:
                model_obj = model_cls(data)

                # print(f'repr(model_obj): {repr(model_obj)}')
                # print(f'model_obj.contents: {model_obj.contents}')
                # print(f'model_obj.to_data(): {model_obj.to_data()}')
