"""Tests for data display helpers."""

from omnipy.data._display.helpers import char_cell_width, only_single_width_chars, soft_wrap_words


def test_char_cell_width() -> None:
    assert char_cell_width('\0') == 0
    assert char_cell_width('\x1f') == 0
    assert char_cell_width(' ') == 1
    assert char_cell_width('A') == 1
    assert char_cell_width('a') == 1
    assert char_cell_width('1') == 1
    assert char_cell_width('~') == 1
    assert char_cell_width('\x7f') == 0
    assert char_cell_width('\x80') == 0
    assert char_cell_width('\x9f') == 0
    assert char_cell_width('\xa0') == 1
    assert char_cell_width('中') == 2


def test_only_single_width_chars() -> None:
    assert only_single_width_chars('')
    assert only_single_width_chars(' Abc ~123')
    assert not only_single_width_chars('a\tb')
    assert not only_single_width_chars('a\x7fb')
    assert not only_single_width_chars('æøå')
    assert not only_single_width_chars('中')


def test_soft_wrap_words_no_wrap_needed():
    """Tests when input fits entirely on one line"""
    words = ['short', 'sentence', 'no', 'wrap']
    result = soft_wrap_words(words, 30)
    assert result == ['short sentence no wrap']


def test_soft_wrap_words_basic_wrapping():
    """Tests basic wrapping functionality at appropriate points"""
    words = ['this', 'line', 'needs', 'to', 'be', 'wrapped']
    result = soft_wrap_words(words, 10)
    assert result == ['this line', 'needs to', 'be wrapped']


def test_soft_wrap_words_dims_and_edge_cases():
    """Tests empty input and single long word scenarios"""
    # Empty input
    assert soft_wrap_words([], 10) == []

    # Single word longer than max_width
    words = ['supercalifragilistic']
    assert soft_wrap_words(words, 10) == ['supercalifragilistic']


def test_soft_wrap_words_boundary_conditions():
    """Tests exact width boundary conditions"""
    # Exact fit at boundary
    words = ['one', 'two', 'three']  # "one two" = 7 chars
    wrap_at_7 = soft_wrap_words(words, 7)
    assert wrap_at_7 == ['one two', 'three']

    wrap_at_6 = soft_wrap_words(words, 6)
    assert wrap_at_6 == ['one', 'two', 'three']

    # Multiple long words
    words = ['longword1', 'longword2']
    result = soft_wrap_words(words, 9)
    assert result == ['longword1', 'longword2']
