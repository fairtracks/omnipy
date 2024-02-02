import os
from textwrap import dedent

from pydantic import ValidationError
import pytest

from omnipy.modules.raw.models import (BytesModel,
                                       JoinColumnsToLinesModel,
                                       JoinItemsModel,
                                       JoinLinesModel,
                                       SplitLinesToColumnsModel,
                                       SplitToItemsModel,
                                       SplitToLinesModel,
                                       StrModel)


def test_bytes_model():
    assert BytesModel(b'').contents == b''
    assert BytesModel(b'\xc3\xa6\xc3\xb8\xc3\xa5').contents == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    assert BytesModel('').contents == b''
    assert BytesModel('æøå').contents == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    assert BytesModel('æøå', encoding='utf-8').contents == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    assert BytesModel('æøå', encoding='latin-1').contents == b'\xe6\xf8\xe5'

    with pytest.raises(LookupError):
        BytesModel('æøå', encoding='my-encoding')


def test_str_model():
    assert StrModel('').contents == ''
    assert StrModel('æøå').contents == 'æøå'
    assert StrModel(b'').contents == ''
    assert StrModel(b'\xc3\xa6\xc3\xb8\xc3\xa5').contents == 'æøå'
    assert StrModel(b'\xc3\xa6\xc3\xb8\xc3\xa5', encoding='utf-8').contents == 'æøå'
    assert StrModel(b'\xe6\xf8\xe5', encoding='latin-1').contents == 'æøå'
    assert StrModel(b'\xef\xbb\xbfsomething', encoding='utf-8-sig').contents == 'something'

    with pytest.raises(ValidationError):
        StrModel(b'\xe6\xf8\xe5', encoding='utf-8')

    with pytest.raises(LookupError):
        StrModel(b'\xe6\xf8\xe5', encoding='my-encoding')


def test_split_to_and_join_lines_model():
    data = """\
        
        Alas, poor Yorick! I knew him, Horatio: a fellow
        of infinite jest, of most excellent fancy: he hath
        borne me on his back a thousand times; and now, how
        abhorred in my imagination it is! my gorge rises at
        it. Here hung those lips that I have kissed I know
        not how oft. Where be your gibes now? your
        gambols? your songs? your flashes of merriment,
        that were wont to set the table on a roar? Not one
        now, to mock your own grinning? quite chap-fallen.
        """  # noqa: W293

    lines_stripped = SplitToLinesModel(data)
    assert lines_stripped[0] == 'Alas, poor Yorick! I knew him, Horatio: a fellow'

    lines_unstripped = SplitToLinesModel(data, strip=False)
    assert lines_unstripped[0] == '        '
    assert lines_unstripped[1] == '        Alas, poor Yorick! I knew him, Horatio: a fellow'
    assert lines_unstripped[-1] == '        '

    last_lines = lines_stripped[3:]
    assert last_lines[0:2].contents == [
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know'
    ]
    assert last_lines[-1] == 'now, to mock your own grinning? quite chap-fallen.'

    joined_lines = JoinLinesModel(last_lines[0:2])
    assert joined_lines.contents == dedent("""\
        abhorred in my imagination it is! my gorge rises at
        it. Here hung those lips that I have kissed I know""")

    assert joined_lines[:joined_lines.index(' ')].contents == 'abhorred'
    assert JoinLinesModel(SplitToLinesModel(data)).contents == \
           os.linesep.join([line.strip() for line in data.strip().split(os.linesep)])

    assert JoinLinesModel(SplitToLinesModel(data, strip=False)).contents == data


def test_split_to_and_join_items_model():
    data_tab = 'abc\t def \tghi\tjkl'

    items_stripped_tab = SplitToItemsModel(data_tab)
    assert items_stripped_tab.contents == ['abc', 'def', 'ghi', 'jkl']
    assert items_stripped_tab[1] == 'def'
    assert items_stripped_tab[-2:].contents == ['ghi', 'jkl']

    items_unstripped_tab = SplitToItemsModel(data_tab, strip=False)
    assert items_unstripped_tab.contents == ['abc', ' def ', 'ghi', 'jkl']
    assert items_unstripped_tab[1] == ' def '
    assert items_unstripped_tab[-2:].contents == ['ghi', 'jkl']

    data_comma = 'abc, def, ghi, jkl'

    items_stripped_comma = SplitToItemsModel(data_comma, delimiter=',')
    assert items_stripped_comma.contents == ['abc', 'def', 'ghi', 'jkl']
    assert items_stripped_comma[1] == 'def'
    assert items_stripped_comma[-2:].contents == ['ghi', 'jkl']

    tab_joined_items = JoinItemsModel(items_stripped_tab[1:3])
    assert tab_joined_items.contents == 'def\tghi'
    assert tab_joined_items[1:-1].contents == 'ef\tgh'

    comma_space_joined_items = JoinItemsModel(items_stripped_comma[1:3], delimiter=', ')
    assert comma_space_joined_items.contents == 'def, ghi'
    assert comma_space_joined_items[1:-1].contents == 'ef, gh'


def test_split_lines_to_columns_and_join_columns_to_lines_model():
    data_tab = ['abc\t def \tghi\t jkl', 'mno\t pqr\tstu\t vwx', 'yz']

    cols_stripped_tab = SplitLinesToColumnsModel(data_tab)
    assert cols_stripped_tab[0].contents == ['abc', 'def', 'ghi', 'jkl']
    assert cols_stripped_tab[0][1] == 'def'
    assert cols_stripped_tab[1:2].contents == [SplitToItemsModel('mno\t pqr\tstu\t vwx')]
    assert cols_stripped_tab[1:].to_data() == [['mno', 'pqr', 'stu', 'vwx'], ['yz']]

    cols_unstripped_tab = SplitLinesToColumnsModel(data_tab, strip=False)
    assert cols_unstripped_tab[0].contents == ['abc', ' def ', 'ghi', ' jkl']
    assert cols_unstripped_tab[0][1] == ' def '
    assert cols_unstripped_tab[1:2].contents \
           == [SplitToItemsModel('mno\t pqr\tstu\t vwx', strip=False)]
    assert cols_unstripped_tab[1:].to_data() == [['mno', ' pqr', 'stu', ' vwx'], ['yz']]

    data_comma = ['abc, def, ghi, jkl', 'mno, pqr, stu, vwx', 'yz']

    cols_stripped_comma = SplitLinesToColumnsModel(data_comma, delimiter=',')
    assert cols_stripped_comma[0].contents == ['abc', 'def', 'ghi', 'jkl']
    assert cols_stripped_comma[0][1] == 'def'
    assert cols_stripped_comma[1:2].contents \
           == [SplitToItemsModel('mno, pqr, stu, vwx', delimiter=',')]
    assert cols_stripped_comma[1:].to_data() == [['mno', 'pqr', 'stu', 'vwx'], ['yz']]

    joined_cols = JoinColumnsToLinesModel(cols_stripped_tab[1:])
    assert joined_cols.contents \
           == [JoinItemsModel('mno\tpqr\tstu\tvwx'), JoinItemsModel('yz')]
    assert joined_cols[1:].contents == [JoinItemsModel('yz')]
    assert joined_cols.to_data() == ['mno\tpqr\tstu\tvwx', 'yz']

    joined_cols = JoinColumnsToLinesModel(cols_stripped_comma[1:], delimiter=', ')
    assert joined_cols.contents \
           == [JoinItemsModel('mno, pqr, stu, vwx'), JoinItemsModel('yz')]
    assert joined_cols[1:].contents == [JoinItemsModel('yz')]
    assert joined_cols.to_data() == ['mno, pqr, stu, vwx', 'yz']
