from typing import Annotated

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
def seqcol_level_2_data() -> dict:
    return {
        'lengths': [8, 4, 4],
        'names': ['X', '1', '2'],
        'sequences': [
            'SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw',
            'SQ.YBbVX0dLKG1ieEDCiMmkrTZFt_Z5Vdaj',
            'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6'
        ],
        'sorted_sequences': [
            'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6',
            'SQ.YBbVX0dLKG1ieEDCiMmkrTZFt_Z5Vdaj',
            'SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw'
        ],
        'name_length_pairs': [{
            'length': 8, 'name': 'X'
        }, {
            'length': 4, 'name': '1'
        }, {
            'length': 4, 'name': '2'
        }]
    }


def test_seqcol_level_2_model(seqcol_level_2_data: Annotated[dict, pytest.fixture]) -> None:
    seqcol_level_2_model = SeqColLevel2Model(seqcol_level_2_data)
    assert seqcol_level_2_model.to_data() == seqcol_level_2_data
    assert seqcol_level_2_model.lengths == [8, 4, 4]  # type: ignore[attr-defined]
    assert seqcol_level_2_model.names == ['X', '1', '2']  # type: ignore[attr-defined]
    assert (seqcol_level_2_model.sequences[0]  # type: ignore[attr-defined]
            == 'SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw')
    assert (seqcol_level_2_model.sorted_sequences[0]  # type: ignore[attr-defined]
            == 'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6')
    assert seqcol_level_2_model.name_length_pairs[0].length == 8  # type: ignore[attr-defined]
    assert seqcol_level_2_model.name_length_pairs[0].name == 'X'  # type: ignore[attr-defined]
