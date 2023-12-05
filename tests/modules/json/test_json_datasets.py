from dataclasses import fields

from pydantic import ValidationError
import pytest
import pytest_cases as pc

from tests.modules.json.helpers.classes import CaseInfo


@pc.parametrize_with_cases('case', cases='.cases.json_data')
def test_json_datasets(case: CaseInfo) -> None:
    for field in fields(case.data_points):
        name = field.name
        for dataset_cls in case.dataset_classes_for_data_point(name):
            data = getattr(case.data_points, name)

            print('\n---')
            print(f'Field name: {name}')
            print(f'Dataset class: {dataset_cls.__name__}')
            print(f'Data input: {data}')

            if case.data_point_should_fail(name):
                with pytest.raises(ValidationError) as e:
                    dataset = dataset_cls()
                    dataset[name] = data

                print(f'Error: {e}')
            else:
                dataset = dataset_cls()
                dataset[name] = data

                print(f'repr(dataset): {repr(dataset)}')
                print(f'dataset.to_data(): {dataset.to_data()}')
                print(f'dataset.to_json(): {dataset.to_json(pretty=True)}')
