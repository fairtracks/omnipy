"""Pytest fixtures for pandas component table cases."""

import pytest_cases as pc

from omnipy.components.json.typedefs import JsonListOfListsOfScalars


@pc.fixture
def table_age_firstname_lastname() -> JsonListOfListsOfScalars:
    """Return a table with age, firstname, and lastname columns."""
    return [
        ['age', 'firstname', 'lastname'],
        [7, 'Bob', 'Duck'],
        [39, 'Donald', 'Duck'],
        [41, 'Mickey', 'Mouse'],
    ]


@pc.fixture
def table_weight_firstname_height_all_match() -> JsonListOfListsOfScalars:
    """Return a table whose firstname values all match the age table."""
    return [
        ['weight', 'firstname', 'height'],
        [37.2, 'Bob', 127],
        [75.4, 'Donald', 165],
        [69.8, 'Mickey', 171],
    ]


@pc.fixture
def table_weight_firstname_height_partial_match() -> JsonListOfListsOfScalars:
    """Return a table whose firstname values partially match the age table."""
    return [
        ['weight', 'firstname', 'height'],
        [37.2, 'Bob', 127],
        [75.4, 'Donald', 165],
    ]


@pc.fixture
def table_weight_firstname_height_partial_match_plus_extra() -> JsonListOfListsOfScalars:
    """Return a partial-match table with one extra firstname row."""
    return [
        ['weight', 'firstname', 'height'],
        [37.2, 'Bob', 127],
        [75.4, 'Donald', 165],
        [71.1, 'Minnie', 168],
    ]


@pc.fixture
def table_firstname_lastname_adult_all_match() -> JsonListOfListsOfScalars:
    """Return a table whose name pairs all match the age table."""
    return [
        ['firstname', 'lastname', 'adult'],
        ['Donald', 'Duck', True],
        ['Mickey', 'Mouse', True],
        ['Bob', 'Duck', False],
    ]


@pc.fixture
def table_adult_lastname_firstname_all_match() -> JsonListOfListsOfScalars:
    """Return an all-match table with reordered adult and name columns."""
    return [
        ['adult', 'lastname', 'firstname'],
        [True, 'Duck', 'Donald'],
        [True, 'Mouse', 'Mickey'],
        [False, 'Duck', 'Bob'],
    ]


@pc.fixture
def table_firstname_lastname_adult_double_match() -> JsonListOfListsOfScalars:
    """Return a table containing a duplicate matching name pair."""
    return [
        ['firstname', 'lastname', 'adult'],
        ['Bob', 'Duck', True],
        ['Donald', 'Duck', True],
        ['Mickey', 'Mouse', True],
        ['Bob', 'Duck', False],
    ]


@pc.fixture
def table_firstname_lastname_adult_partial_match() -> JsonListOfListsOfScalars:
    """Return a table with only some matching firstname and lastname pairs."""
    return [
        ['firstname', 'lastname', 'adult'],
        ['Donald', 'Duck', True],
        ['Bob', 'Duck', False],
    ]


@pc.fixture
def table_firstname_lastname_adult_partial_match_plus_extra() -> JsonListOfListsOfScalars:
    """Return a partial-match table with one extra name pair."""
    return [
        ['firstname', 'lastname', 'adult'],
        ['Donald', 'Duck', True],
        ['Minnie', 'Mouse', True],
        ['Bob', 'Duck', False],
    ]


@pc.fixture
def table_firstname_lastname_adult_all_match_plus_extra() -> JsonListOfListsOfScalars:
    """Return an all-match table with one additional matched row."""
    return [
        ['firstname', 'lastname', 'adult'],
        ['Donald', 'Duck', True],
        ['Mickey', 'Mouse', True],
        ['Minnie', 'Mouse', True],
        ['Bob', 'Duck', False],
    ]


@pc.fixture
def table_firstname_lastname_adult_no_match_when_paired() -> JsonListOfListsOfScalars:
    """Return a table whose name pairs do not match when combined."""
    return [
        ['firstname', 'lastname', 'adult'],
        ['Mickey', 'Duck', True],
        ['Donald', 'Mouse', True],
        ['Bob', 'Mouse', False],
        ['Mickey', 'Duck', False],
    ]


@pc.fixture
def table_last_first_weight_height() -> JsonListOfListsOfScalars:
    """Return a table with renamed first and last name columns."""
    return [
        ['last', 'first', 'weight', 'height'],
        ['Duck', 'Bob', 37.2, 127],
        ['Duck', 'Donald', 75.4, 165],
        ['Mouse', 'Mickey', 69.8, 171],
    ]
