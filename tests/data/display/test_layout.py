from dataclasses import dataclass
from typing import Annotated

import pytest

from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import Panel

from .panel.helpers.classes import MockPanel


@dataclass
class SimpleLayoutCase:
    layout: Layout
    first_panel: Panel
    second_panel: Panel


def test_empty_layout(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    layout = Layout()

    # Check contents
    assert len(layout) == 0
    assert list(layout) == []

    # Check grid dimensions
    assert layout.grid.dims == Dimensions(width=0, height=0)

    # Check that accessing any grid position raises IndexError
    with pytest.raises(IndexError):
        layout.grid[0, 0]


@pytest.fixture
def simple_layout() -> SimpleLayoutCase:
    """Create a layout with two panels for testing."""
    layout = Layout()
    first_panel = MockPanel()
    second_panel = MockPanel()

    layout['first'] = first_panel
    layout['second'] = second_panel

    return SimpleLayoutCase(
        layout=layout,
        first_panel=first_panel,
        second_panel=second_panel,
    )


def test_layout_hashable(
    simple_layout: Annotated[SimpleLayoutCase, pytest.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    layout_1 = Layout()
    layout_2 = Layout()

    assert hash(layout_1) == hash(layout_2)

    layout_3 = Layout()
    layout_3['first'] = MockPanel()

    layout_4 = Layout()
    layout_4['first'] = MockPanel()

    assert hash(layout_1) != hash(layout_3)
    assert hash(layout_3) == hash(layout_4)

    layout_4['first'] = MockPanel('contents')

    assert hash(layout_3) != hash(layout_4)


def test_basic_layout_dict_operations(
    simple_layout: Annotated[SimpleLayoutCase, pytest.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    """Test basic layout operations: adding, retrieving, counting and containment."""
    case = simple_layout

    # Access by name and check for object identity
    assert case.layout['first'] is case.first_panel
    assert case.layout['second'] is case.second_panel

    # Check count
    assert len(case.layout) == 2

    # Check containment
    assert 'first' in case.layout
    assert 'second' in case.layout
    assert 'third' not in case.layout


def test_layout_iteration(
    simple_layout: Annotated[SimpleLayoutCase, pytest.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    """Test various ways of iterating over the layout panels."""
    case = simple_layout

    for i, (key, value) in enumerate(case.layout.items()):
        match i:
            case 0:
                assert key == 'first'
                assert value is case.first_panel
            case 1:
                assert key == 'second'
                assert value is case.second_panel

    assert tuple(case.layout.keys()) == ('first', 'second')
    assert tuple(case.layout.values()) == (case.first_panel, case.second_panel)
    assert list(case.layout) == ['first', 'second']
    assert tuple(reversed(case.layout)) == ('second', 'first')


def test_layout_insertion_and_deletion(
    simple_layout: Annotated[SimpleLayoutCase, pytest.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    """Test insertion and deletion of panels in the layout."""
    case = simple_layout

    third_panel = MockPanel()
    case.layout['third'] = third_panel

    # Test insertion
    assert len(case.layout) == 3
    assert 'third' in case.layout
    assert case.layout['third'] is third_panel
    assert list(case.layout) == ['first', 'second', 'third']

    # Test del()
    del case.layout['third']

    assert len(case.layout) == 2
    assert 'third' not in case.layout
    with pytest.raises(KeyError):
        case.layout['third']
    assert list(case.layout) == ['first', 'second']

    with pytest.raises(KeyError):
        del case.layout['third']

    # Test pop() and popitem()
    with pytest.raises(KeyError):
        case.layout.pop('third')
    third = case.layout.pop('third', third_panel)
    assert third == third_panel

    first = case.layout.popitem()
    assert first == ('first', case.first_panel)

    second = case.layout.pop('second')
    assert second == case.second_panel

    assert len(case.layout) == 0


def test_layout_default_methods(
    simple_layout: Annotated[SimpleLayoutCase, pytest.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    """
    Test common dictionary methods:  get() and setdefault()
    as well as binary operations.
    """
    case = simple_layout

    # Test get() method
    assert case.layout.get('first') is case.first_panel
    assert case.layout.get('missing') is None
    other_panel = MockPanel()
    assert case.layout.get('missing', other_panel) is other_panel

    # Test setdefault()
    third_panel = MockPanel()
    result = case.layout.setdefault('third', third_panel)
    assert case.layout['third'] is third_panel
    assert result is third_panel

    # Test setdefault() with existing key
    result = case.layout.setdefault('first', MockPanel())
    assert case.layout['first'] is case.first_panel
    assert result is case.first_panel  # Should return existing value


def test_layout_update_methods_and_operators(
    simple_layout: Annotated[SimpleLayoutCase, pytest.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    """Test update() and binary operators."""
    case = simple_layout

    # Test update() with another dict
    new_third_panel = MockPanel()
    fourth_panel = MockPanel()
    case.layout.update({'third': new_third_panel, 'fourth': fourth_panel})
    assert case.layout['third'] is new_third_panel
    assert case.layout['fourth'] is fourth_panel

    # Test update() with keyword arguments
    fifth_panel = MockPanel()
    case.layout.update(fifth=fifth_panel)
    assert case.layout['fifth'] is fifth_panel

    # Test update() with iterable of key-value pairs
    sixth_panel = MockPanel()
    iterable = [('sixth', sixth_panel)]
    case.layout.update(iterable)
    assert case.layout['sixth'] is sixth_panel

    # Test |= operator
    new_sixth_panel = MockPanel()
    seventh_panel = MockPanel()
    case.layout |= {'sixth': new_sixth_panel, 'seventh': seventh_panel}
    assert case.layout['sixth'] is new_sixth_panel
    assert case.layout['seventh'] is seventh_panel

    # Test | operator
    new_seventh_panel = MockPanel()
    eighth_panel = MockPanel()
    other_dict = {'seventh': new_seventh_panel, 'eighth': eighth_panel}
    combined = case.layout | other_dict
    assert combined['seventh'] is new_seventh_panel
    assert combined['eighth'] is eighth_panel
    assert len(combined) == 8
    assert len(case.layout) == 7


def test_layout_dict_comparison(
    simple_layout: Annotated[SimpleLayoutCase, pytest.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    """Test dictionary comparison operations."""
    case = simple_layout

    # Create a dict with the same contents
    same_dict = {'first': case.first_panel, 'second': case.second_panel}

    # Check equality
    assert dict(case.layout) == same_dict

    # Check with different content
    different_dict = {'first': case.first_panel, 'different': MockPanel()}
    assert dict(case.layout) != different_dict


def test_layout_dict_copy_and_clear(
    simple_layout: Annotated[SimpleLayoutCase, pytest.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    """Test copy() and clear() methods."""
    case = simple_layout

    # Check copy()
    layout_copy = case.layout.copy()
    assert layout_copy == case.layout
    assert layout_copy is not case.layout

    # Modifying copy shouldn't affect original
    new_panel = MockPanel()
    layout_copy['new'] = new_panel
    assert 'new' in layout_copy
    assert 'new' not in case.layout

    # Check clear
    case.layout.clear()
    assert len(case.layout) == 0
    assert list(case.layout) == []

    # Original panels should still exist
    assert case.first_panel is not None
    assert case.second_panel is not None


def test_layout_simple_grid_queries(
    simple_layout: Annotated[SimpleLayoutCase, pytest.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    """Test simple grid queries."""
    case = simple_layout

    assert case.layout.grid.dims == Dimensions(width=2, height=1)
    assert case.layout.grid[0, 0] == 'first'
    assert case.layout.grid[0, 1] == 'second'

    with pytest.raises(IndexError):
        case.layout.grid[1, 0]

    with pytest.raises(IndexError):
        case.layout.grid[0, 2]

    with pytest.raises(IndexError):
        case.layout.grid[1, 0]

    with pytest.raises(IndexError):
        case.layout.grid[-1, 0]

    with pytest.raises(IndexError):
        case.layout.grid[0, -1]


def test_layout_simple_grid_insert_and_delete(
    simple_layout: Annotated[SimpleLayoutCase, pytest.fixture],
    skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],
) -> None:
    """Test simple grid queries."""
    case = simple_layout

    third_panel = MockPanel()
    case.layout['third'] = third_panel

    assert case.layout.grid.dims == Dimensions(width=3, height=1)
    assert case.layout.grid[0, 2] == 'third'

    with pytest.raises(IndexError):
        case.layout.grid[0, 3]

    with pytest.raises(IndexError):
        case.layout.grid[1, 0]

    del case.layout['second']
    assert case.layout.grid.dims == Dimensions(width=2, height=1)
    assert case.layout.grid[0, 0] == 'first'
    assert case.layout.grid[0, 1] == 'third'

    with pytest.raises(IndexError):
        case.layout.grid[0, 2]

    with pytest.raises(IndexError):
        case.layout.grid[1, 0]
