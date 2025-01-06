import pytest_cases as pc

from omnipy.components.json.typedefs import JsonListOfListsOfScalars


@pc.fixture
def table_age_firstname_lastname() -> JsonListOfListsOfScalars:
    return [
        ['age', 'firstname', 'lastname'],
        [7, 'Bob', 'Duck'],
        [39, 'Donald', 'Duck'],
        [41, 'Mickey', 'Mouse'],
    ]


@pc.fixture
def table_weight_firstname_height_all_match() -> JsonListOfListsOfScalars:
    return [
        ['weight', 'firstname', 'height'],
        [37.2, 'Bob', 127],
        [75.4, 'Donald', 165],
        [69.8, 'Mickey', 171],
    ]


@pc.fixture
def table_weight_firstname_height_partial_match() -> JsonListOfListsOfScalars:
    return [
        ['weight', 'firstname', 'height'],
        [37.2, 'Bob', 127],
        [75.4, 'Donald', 165],
    ]


@pc.fixture
def table_weight_firstname_height_partial_match_plus_extra() -> JsonListOfListsOfScalars:
    return [
        ['weight', 'firstname', 'height'],
        [37.2, 'Bob', 127],
        [75.4, 'Donald', 165],
        [71.1, 'Minnie', 168],
    ]


@pc.fixture
def table_firstname_lastname_adult_all_match() -> JsonListOfListsOfScalars:
    return [
        ['firstname', 'lastname', 'adult'],
        ['Donald', 'Duck', True],
        ['Mickey', 'Mouse', True],
        ['Bob', 'Duck', False],
    ]


@pc.fixture
def table_adult_lastname_firstname_all_match() -> JsonListOfListsOfScalars:
    return [
        ['adult', 'lastname', 'firstname'],
        [True, 'Duck', 'Donald'],
        [True, 'Mouse', 'Mickey'],
        [False, 'Duck', 'Bob'],
    ]


@pc.fixture
def table_firstname_lastname_adult_double_match() -> JsonListOfListsOfScalars:
    return [
        ['firstname', 'lastname', 'adult'],
        ['Bob', 'Duck', True],
        ['Donald', 'Duck', True],
        ['Mickey', 'Mouse', True],
        ['Bob', 'Duck', False],
    ]


@pc.fixture
def table_firstname_lastname_adult_partial_match() -> JsonListOfListsOfScalars:
    return [
        ['firstname', 'lastname', 'adult'],
        ['Donald', 'Duck', True],
        ['Bob', 'Duck', False],
    ]


@pc.fixture
def table_firstname_lastname_adult_partial_match_plus_extra() -> JsonListOfListsOfScalars:
    return [
        ['firstname', 'lastname', 'adult'],
        ['Donald', 'Duck', True],
        ['Minnie', 'Mouse', True],
        ['Bob', 'Duck', False],
    ]


@pc.fixture
def table_firstname_lastname_adult_all_match_plus_extra() -> JsonListOfListsOfScalars:
    return [
        ['firstname', 'lastname', 'adult'],
        ['Donald', 'Duck', True],
        ['Mickey', 'Mouse', True],
        ['Minnie', 'Mouse', True],
        ['Bob', 'Duck', False],
    ]


@pc.fixture
def table_firstname_lastname_adult_no_match_when_paired() -> JsonListOfListsOfScalars:
    return [
        ['firstname', 'lastname', 'adult'],
        ['Mickey', 'Duck', True],
        ['Donald', 'Mouse', True],
        ['Bob', 'Mouse', False],
        ['Mickey', 'Duck', False],
    ]


@pc.fixture
def table_last_first_weight_height() -> JsonListOfListsOfScalars:
    return [
        ['last', 'first', 'weight', 'height'],
        ['Duck', 'Bob', 37.2, 127],
        ['Duck', 'Donald', 75.4, 165],
        ['Mouse', 'Mickey', 69.8, 171],
    ]
