from dataclasses import fields

from pydantic import ValidationError
import pytest
import pytest_cases as pc

from omnipy.modules.general.models import NotIterableExceptStrOrBytesModel

from ..helpers.classes import CaseInfo


def test_not_iterable_except_str_model():
    assert NotIterableExceptStrOrBytesModel().contents is None
    assert NotIterableExceptStrOrBytesModel(None).contents is None
    assert NotIterableExceptStrOrBytesModel(1234).contents == 1234
    assert NotIterableExceptStrOrBytesModel(True).contents is True

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel((1, 2, 3, 4))

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel([1, 2, 3, 4])

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel({1: 2, 3: 4})

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel({1, 2, 3, 4})

    assert NotIterableExceptStrOrBytesModel('1234').contents == '1234'
    assert NotIterableExceptStrOrBytesModel('æøå'.encode('utf8')).contents == 'æøå'.encode('utf8')


@pc.parametrize_with_cases('case', cases='.cases.frozen_data')
def test_nested_frozen_models(case: CaseInfo) -> None:
    for field in fields(case.data_points):
        name = field.name
        for model_cls in case.model_classes_for_data_point(name):
            data = getattr(case.data_points, name)

            print('\n---')
            print(f'Field name: {name}')
            print(f'Model class: {model_cls.__name__}')
            print(f'Data input: {data}')

            if case.data_point_should_fail(name):
                with pytest.raises(ValidationError) as e:
                    model_cls(data)
                print(f'Error: {e}')
            else:

                model_obj = model_cls(data)
                print(f'repr(model_obj): {repr(model_obj)}')
                print(f'model_obj.contents: {model_obj.contents}')
                print(f'model_obj.to_data(): {model_obj.to_data()}')
