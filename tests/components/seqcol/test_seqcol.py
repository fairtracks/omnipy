from omnipy.components.seqcol.models import SeqColLevel2Model


def test_sequence_collection_model() -> None:
    seqcol_level_2 = {
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
    seqcol_level_2_model = SeqColLevel2Model(seqcol_level_2)
    assert seqcol_level_2_model.to_data() == seqcol_level_2
    assert seqcol_level_2_model.lengths == [8, 4, 4]  # type: ignore[attr-defined]
    assert seqcol_level_2_model.names == ['X', '1', '2']  # type: ignore[attr-defined]
    assert seqcol_level_2_model.sequences == [  # type: ignore[attr-defined]
        'SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw',
        'SQ.YBbVX0dLKG1ieEDCiMmkrTZFt_Z5Vdaj',
        'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6'
    ]
    assert seqcol_level_2_model.sorted_sequences == [  # type: ignore[attr-defined]
        'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6',
        'SQ.YBbVX0dLKG1ieEDCiMmkrTZFt_Z5Vdaj',
        'SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw'
    ]
    assert seqcol_level_2_model.name_length_pairs == [  # type: ignore[attr-defined]
        {
            'length': 8, 'name': 'X'
        }, {
            'length': 4, 'name': '1'
        }, {
            'length': 4, 'name': '2'
        }
    ]

    # seqcol_level_1 = {
    #     'lengths': 'cGRMZIb3AVgkcAfNv39RN7hnT5Chk7RX',
    #     'names': 'lrCv6NNXom7AC9tKFWqhcLLZsrcgJIqq',
    #     'sequences': '0uDQVLuHaOZi1u76LjV__yrVUIz9Bwhr',
    #     'sorted_sequences': 'KgWo6TT1Lqw6vgkXU9sYtCU9xwXoDt6M',
    #     'name_length_pairs': 'm88geMfgGBZ7VpYgQKCB4P9z-mhKJ-nj',
    #     'sorted_name_length_pairs': '1FQEGOQQ-m0NmZ0R-eeJEfnH1ayqJQ0T'
    # }
    #
    # seqcol_level_0 = 'QvT5tAQ0B8Vkxd-qFftlzEk2QyfPtgOv'


schema = {
    'description': 'A collection of biological sequences.',
    'type': 'object',
    'properties': {
        'lengths': {
            'type':
                'array',
            'collated':
                True,
            'description':
                'Number of elements, such as nucleotides or amino acids, in each sequence.',
            'items': {
                'type': 'integer'
            }
        },
        'names': {
            'type': 'array',
            'collated': True,
            'description': 'Human-readable labels of each sequence (chromosome names).',
            'items': {
                'type': 'string'
            }
        },
        'sequences': {
            'type': 'array',
            'collated': True,
            'items': {
                'type': 'string', 'description': 'Refget sequences v2 identifiers for sequences.'
            }
        },
        'accessions': {
            'type': 'array',
            'collated': True,
            'items': {
                'type': 'string', 'description': 'Unique external accessions for the sequences'
            }
        },
        'sorted_sequences': {
            'type': 'array',
            'collated': False,
            'items': {
                'type': 'string',
                'description': 'Refget sequences v2 identifiers for sequences, sorted by digest.'
            }
        },
        'name_length_pairs': {
            'type': 'array',
            'collated': True,
            'items': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string'
                    }, 'length': {
                        'type': 'integer'
                    }
                }
            }
        },
        'sorted_name_length_pairs': {
            'type': 'array',
            'collated': False,
            'items': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string'
                    }, 'length': {
                        'type': 'integer'
                    }
                }
            }
        }
    }
}
