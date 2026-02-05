from copy import copy
from typing import Annotated, Any

import pytest

from omnipy.components.seqcol.models import SeqColLevel2Model


@pytest.fixture
def seqcol_level_0_digest() -> str:
    return 'QvT5tAQ0B8Vkxd-qFftlzEk2QyfPtgOv'


@pytest.fixture
def seqcol_level_1_data() -> dict:
    return {
        'lengths': 'cGRMZIb3AVgkcAfNv39RN7hnT5Chk7RX',
        'names': 'lrCv6NNXom7AC9tKFWqhcLLZsrcgJIqq',
        'sequences': '0uDQVLuHaOZi1u76LjV__yrVUIz9Bwhr',
        'sorted_sequences': 'KgWo6TT1Lqw6vgkXU9sYtCU9xwXoDt6M',
        'name_length_pairs': 'm88geMfgGBZ7VpYgQKCB4P9z-mhKJ-nj',
        'sorted_name_length_pairs': '1FQEGOQQ-m0NmZ0R-eeJEfnH1ayqJQ0T'
    }


@pytest.fixture
def seqcol_level_2_required_data() -> dict:
    return {
        'lengths': [8, 4, 4],
        'names': ['X', '1', '2'],
        'sequences': [
            'SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw',
            'SQ.YBbVX0dLKG1ieEDCiMmkrTZFt_Z5Vdaj',
            'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6'
        ],
    }


@pytest.fixture
def seqcol_level_2_full_data(seqcol_level_2_required_data: Annotated[dict, pytest.fixture]) -> dict:
    seqcol_level_2_required_data['sorted_sequences'] = [
        'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6',
        'SQ.YBbVX0dLKG1ieEDCiMmkrTZFt_Z5Vdaj',
        'SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw'
    ]
    seqcol_level_2_required_data['name_length_pairs'] = [{
        'length': 8, 'name': 'X'
    }, {
        'length': 4, 'name': '1'
    }, {
        'length': 4, 'name': '2'
    }]
    return seqcol_level_2_required_data


def test_seqcol_level_2_model(seqcol_level_2_full_data: Annotated[dict, pytest.fixture]) -> None:
    seqcol_level_2_model = SeqColLevel2Model(seqcol_level_2_full_data)
    assert seqcol_level_2_model.to_data() == seqcol_level_2_full_data
    assert seqcol_level_2_model.lengths == [8, 4, 4]  # type: ignore[attr-defined]
    assert seqcol_level_2_model.names == ['X', '1', '2']  # type: ignore[attr-defined]
    assert (seqcol_level_2_model.sequences[0]  # type: ignore[attr-defined]
            == 'SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw')
    assert (seqcol_level_2_model.sorted_sequences[0]  # type: ignore[attr-defined]
            == 'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6')
    assert seqcol_level_2_model.name_length_pairs[0].length == 8  # type: ignore[attr-defined]
    assert seqcol_level_2_model.name_length_pairs[0].name == 'X'  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    'append_data',
    [
        ('lengths', 10),
        ('names', '3'),
        ('sequences', 'SQ.1234567890'),
        ('sorted_sequences', 'SQ.1234567890'),
        ('name_length_pairs', {
            'length': 10, 'name': '3'
        }),
    ],
    ids=['lengths', 'names', 'sequences', 'sorted_sequences', 'name_length_pairs'])
def test_seqcol_level_2_model_validate_equal_length_lists(
    seqcol_level_2_full_data: Annotated[dict, pytest.fixture],
    append_data: tuple[str, Any],
) -> None:
    key, append_val = append_data
    seqcol_level_2_non_equal_length_data = copy(seqcol_level_2_full_data)
    seqcol_level_2_non_equal_length_data[key].append(append_val)  # type: ignore[attr-defined]
    with pytest.raises(ValueError):
        SeqColLevel2Model(seqcol_level_2_non_equal_length_data)


def test_seqcol_level_2_model_validate_sorted_sequences(
        seqcol_level_2_required_data: Annotated[dict, pytest.fixture]) -> None:
    seqcol_level_2_incorrectly_sorted_data = seqcol_level_2_required_data
    seqcol_level_2_incorrectly_sorted_data['sorted_sequences'] = [
        'SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw',
        'SQ.YBbVX0dLKG1ieEDCiMmkrTZFt_Z5Vdaj'
        'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6',
    ]
    with pytest.raises(ValueError):
        SeqColLevel2Model(seqcol_level_2_incorrectly_sorted_data)


def test_seqcol_level_2_model_missing_sorted_sequences(
        seqcol_level_2_required_data: Annotated[dict, pytest.fixture]) -> None:
    seqcol_level_2_model = SeqColLevel2Model(seqcol_level_2_required_data)
    assert (seqcol_level_2_model.sorted_sequences  # type: ignore[attr-defined]
            == [
                'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6',
                'SQ.YBbVX0dLKG1ieEDCiMmkrTZFt_Z5Vdaj',
                'SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw'
            ])


def test_seqcol_level_2_model_validate_name_length_pairs(
        seqcol_level_2_full_data: Annotated[dict, pytest.fixture]) -> None:
    seqcol_level_2_incorrect_name_data = copy(seqcol_level_2_full_data)
    seqcol_level_2_incorrect_name_data['name_length_pairs'][0]['name'] = 'Y'
    with pytest.raises(ValueError):
        SeqColLevel2Model(seqcol_level_2_incorrect_name_data)

    seqcol_level_2_incorrect_length_data = copy(seqcol_level_2_full_data)
    seqcol_level_2_incorrect_length_data['name_length_pairs'][1]['length'] = 10
    with pytest.raises(ValueError):
        SeqColLevel2Model(seqcol_level_2_incorrect_length_data)

    seqcol_level_2_incorrect_list_length_data = copy(seqcol_level_2_full_data)
    seqcol_level_2_incorrect_length_data['name_length_pairs'] = \
        seqcol_level_2_incorrect_length_data['name_length_pairs'][:-1]
    with pytest.raises(ValueError):
        SeqColLevel2Model(seqcol_level_2_incorrect_list_length_data)


def test_seqcol_level_2_model_missing_name_length_pairs(
        seqcol_level_2_required_data: Annotated[dict, pytest.fixture]) -> None:
    seqcol_level_2_model = SeqColLevel2Model(seqcol_level_2_required_data)
    assert (seqcol_level_2_model.name_length_pairs  # type: ignore[attr-defined]
            == [{
                'length': 8, 'name': 'X'
            }, {
                'length': 4, 'name': '1'
            }, {
                'length': 4, 'name': '2'
            }])


def test_seqcol_level_2_model_invalid_data() -> None:
    with pytest.raises(ValueError):
        SeqColLevel2Model({
            'lengths': ['something', 4, 4],
            'names': ['X', '1', '2'],
            'sequences': [
                'SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw',
                'SQ.YBbVX0dLKG1ieEDCiMmkrTZFt_Z5Vdaj',
                'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6'
            ]
        })
