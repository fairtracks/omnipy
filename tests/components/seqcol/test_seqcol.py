from copy import copy
from typing import Annotated, Any

import pytest

from omnipy.components.seqcol.models import SeqColLevel2Model

# *1. As a user, I wish to know what sequences are inside a specific
# collection, so that I can further access those sequences:
#   i. level 0 digest
#      -> /collections/{digest} endpoint
#      -> level 2 "sequences" list
#     (-> level 1 "sequences" digest as a variant/extension?)
#  ii. for each level 2 sequence
#      -> the actual sequence string (e.g. from refget Sequences API)
#
# 2. As a user, I want to compare two sequence collections used by two
# separate analyses so I can understand how comparable and compatible
# their resulting data are.
#   i. 2x level 0 digests
#      -> /comparison/:digest1/:digest2 endpoint
#      -> summary output (machine-readable)
#   (ii. interpretation of summary output for human readability)
#
# 3. As a user, I am interested in a genome sequence collection, but I want
# to extract sequences that compose the chromosomes/karyotype of a genome.
#  i. level 0 digest
#     -> /collections/{digest} endpoint
#     -> level 2 "names" list
#  (ii. select sequences of interest (no automatic way to do this yet))
#
# 4. As a submission system, I want to be able to validate a data file
# submission. To do so, I need to know what exactly a sequence collection
# contains.
#  i. level 0 digest
#     -> /collections/{digest} endpoint
#     -> level 2 "name_length_pairs" list
#  (ii. (in the tool) validate that the submitted file are consistent with
#     the expected sequence names and lengths)
#
# *5. As a software developer, I want to embed a sequence collection digest
# in my tool's output so that downstream tools can identify the exact
# sequence collection that was used.
#  i. one or more FASTA files
#     -> level 2 data (name, length, sequence)
#     -> compute level 0 digest
#     -> embed in output (e.g. in header or metadata)
#  (ii. level 0 digest
#     -> /collections/{digest} endpoint
#     -> extract extra parameters (e.g. accession numbers) to embed in
#        output metadata)
#  variant: start with remote URL to FASTA file(s) instead of local files
#
# *6. I have a chromosome sizes file (a set of lengths and names), and I want
# to ask whether a given sequence collection is length-compatible with
# and/or name-compatible with my file.
#   i. name_length_pairs serialized as a tabular file (e.g. TSV)
#      -> level 2 "name_length_pairs" list
#      -> calculate level 1 digests for "names" and "lengths"
#   ii. Depends on exactly what "compatible" means:
#     a. lengths and/or names are the same and in the same order:
#        -> fetch level 1 "lengths" and "names" digests from level 0 digest
#           of "given sequence collection"
#        -> compare level 1 "lengths" and or "names" digest
#     b. Coordinate systems are compatible if they contain the same names
#        and lengths, regardless or order:
#        -> compare level 1 "sorted_name_length_pairs" digests
#     c. Coordinate systems are compatible if they contain the same names and
#        lengths, in the same order:
#        -> compare level 1 "name_length_pairs" digests
#     d. Coordinate systems are compatible if one is the subset of the other:
#        -> fetch level 2 "name_length_pairs" list for "given sequence
#        collection" and manually compare with the name_length_pairs from
#        the file (e.g. by converting both to sets and checking for
#        subset/superset relationship)
#
# 7. As a genome browser, I have a sequence collection that defines the
# coordinate system displayed. I want to know if a digest representing the
# coordinate system of a given BED file is compatible with the browser.
#  i.  level 0 digest of "given sequence collection" defining genome browser
#  ii. level 1 digest of "sorted_name_length_pairs" associated with BED file
#      (e.g. in header or metadata)
#  iii. Retrieve level 1 digest of "sorted_name_length_pairs" from
#       /collections/{digest} endpoint and compare.
#  (advanced): Check for subset relationships
#
# 8. As a data processor, my input data didn't include information about the
# reference genome used. I want to generate a sequence collection digest
# and attach it so that further processing can benefit from the sequence
# collection features.
#  i. one or more FASTA files
#     -> level 2 data (name, length, sequence)
#     -> compute level 0 digest
#     -> embed in output (e.g. in header or metadata)
#  variant: If you do have the FASTA files, there is no clear-cut way to
#           solve this in general, depends on exactly what data you have


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


def test_extract_seqcol_level_2_data_from_level_0_digest(
        seqcol_level_0_digest: Annotated[str, pytest.fixture],
        seqcol_level_2_full_data: Annotated[dict, pytest.fixture]) -> None:

    # seqcol_level2_sequences = extract_level_2_sequences(seqcol_level_0_digest, level=2)

    # alt1: just model, user needs to call the api - not what we want, not convenient
    # alt2: a model and a more or less loose config
    # alt3: Python client, wrapping each API call to a method, 1:1 (or close to it)

    from omnipy import runtime

    server_urls = ['https://seqcolapi.databio.org/']
    runtime.config.data.seqcol.server_urls = server_urls
    seqcol_model = SeqColModel(level_0=seqcol_level_0_digest)
    assert seqcol_model.level_2.to_data() == seqcol_level_2_full_data
