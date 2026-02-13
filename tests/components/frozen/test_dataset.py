from dataclasses import fields

import pytest
import pytest_cases as pc

from omnipy.util._pydantic import ValidationError

from ..helpers.classes import CaseInfo


@pc.parametrize_with_cases('case', cases='.cases.frozen_data')
def test_nested_frozen_datasets(case: CaseInfo) -> None:
    for field in fields(case.data_points):
        name = field.name
        for dataset_cls in case.dataset_classes_for_data_point(name):
            data = getattr(case.data_points, name)

            # print('\n---')
            # print(f'Field name: {name}')
            # print(f'Dataset class: {dataset_cls.__name__}')
            # print(f'Data input: {data}')

            if case.data_point_should_fail(name):
                with pytest.raises(ValidationError):  # as e:
                    dataset = dataset_cls()
                    dataset[name] = data

                # print(f'Error: {e}')
            else:
                dataset = dataset_cls()
                dataset[name] = data

                # print(f'repr(dataset): {repr(dataset)}')
                # print(f'dataset.to_data(): {dataset.to_data()}')
