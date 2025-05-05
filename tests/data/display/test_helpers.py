from omnipy.data._display.helpers import soft_wrap_words, UnicodeCharWidthMap


def test_unicode_char_width_map() -> None:
    map = UnicodeCharWidthMap()
    assert map['\0'] == 0
    assert map['\x1f'] == 0
    assert map[' '] == 1
    assert map['A'] == 1
    assert map['a'] == 1
    assert map['1'] == 1
    assert map['~'] == 1
    assert map['\x7f'] == 0
    assert map['\x80'] == 0
    assert map['\x9f'] == 0
    assert map['\xa0'] == 1
    assert map['中'] == 2


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
