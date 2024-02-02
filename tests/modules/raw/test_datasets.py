import os
from textwrap import dedent

from pydantic import ValidationError
import pytest

from omnipy import JoinItemsModel, SplitToItemsModel
from omnipy.modules.raw.datasets import (BytesDataset,
                                         JoinColumnsToLinesDataset,
                                         JoinItemsDataset,
                                         JoinLinesDataset,
                                         SplitLinesToColumnsDataset,
                                         SplitToItemsDataset,
                                         SplitToLinesDataset,
                                         StrDataset)


def test_bytes_dataset():
    assert BytesDataset(dict(a=b''))['a'].contents == b''
    assert BytesDataset(
        dict(a=b'\xc3\xa6\xc3\xb8\xc3\xa5'))['a'].contents == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    assert BytesDataset(dict(a=''))['a'].contents == b''
    assert BytesDataset(dict(a='æøå'))['a'].contents == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    assert BytesDataset(
        dict(a='æøå'), encoding='utf-8')['a'].contents == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    assert BytesDataset(dict(a='æøå'), encoding='latin-1')['a'].contents == b'\xe6\xf8\xe5'

    with pytest.raises(LookupError):
        BytesDataset(dict(a='æøå'), encoding='my-encoding')


def test_str_dataset():
    assert StrDataset(dict(a=''))['a'].contents == ''
    assert StrDataset(dict(a='æøå'))['a'].contents == 'æøå'
    assert StrDataset(dict(a=b''))['a'].contents == ''
    assert StrDataset(dict(a=b'\xc3\xa6\xc3\xb8\xc3\xa5'))['a'].contents == 'æøå'
    assert StrDataset(dict(a=b'\xc3\xa6\xc3\xb8\xc3\xa5'), encoding='utf-8')['a'].contents == 'æøå'
    assert StrDataset(dict(a=b'\xe6\xf8\xe5'), encoding='latin-1')['a'].contents == 'æøå'
    assert StrDataset(
        dict(a=b'\xef\xbb\xbfsomething'), encoding='utf-8-sig')['a'].contents == 'something'

    with pytest.raises(ValidationError):
        StrDataset(dict(a=b'\xe6\xf8\xe5'), encoding='utf-8')

    with pytest.raises(LookupError):
        StrDataset(dict(a=b'\xe6\xf8\xe5'), encoding='my-encoding')


def test_split_to_and_join_lines_dataset():
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

    lines_stripped = SplitToLinesDataset(dict(monologue=data))
    assert lines_stripped['monologue'][0] == 'Alas, poor Yorick! I knew him, Horatio: a fellow'

    lines_unstripped = SplitToLinesDataset(dict(monologue=data), strip=False)
    assert lines_unstripped['monologue'][0] == '        '
    assert lines_unstripped['monologue'][1] == \
           '        Alas, poor Yorick! I knew him, Horatio: a fellow'
    assert lines_unstripped['monologue'][-1] == '        '

    lines_stripped['last_lines'] = lines_stripped['monologue'][3:]
    assert lines_stripped['last_lines'][-1] == 'now, to mock your own grinning? quite chap-fallen.'

    for data_file, lines in lines_stripped.items():
        lines_stripped[data_file] = lines[0:2]

    assert (lines_stripped['last_lines'].contents == [
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know'
    ])

    joined_lines = JoinLinesDataset(lines_stripped)
    assert joined_lines['monologue'].contents == dedent("""\
        Alas, poor Yorick! I knew him, Horatio: a fellow
        of infinite jest, of most excellent fancy: he hath""")
    assert joined_lines['last_lines'].contents == dedent("""\
        abhorred in my imagination it is! my gorge rises at
        it. Here hung those lips that I have kissed I know""")

    assert joined_lines['last_lines'][:joined_lines['last_lines'].index(' ')].contents == 'abhorred'
    assert JoinLinesDataset(SplitToLinesDataset(dict(monologue=data))).to_data() == \
           {'monologue': os.linesep.join([line.strip() for line in data.strip().split(os.linesep)])}

    assert JoinLinesDataset(SplitToLinesDataset(dict(monologue=data), strip=False)).to_data() == {
        'monologue': data
    }


def test_split_to_and_join_items_dataset():
    data_tab_start = 'abc\t def \tghi\tjkl'
    data_tab_end = 'mno\t pqr \tstu\tvwx\tyz '

    items_stripped_tab = SplitToItemsDataset(dict(start=data_tab_start, end=data_tab_end))
    assert items_stripped_tab['start'].contents == ['abc', 'def', 'ghi', 'jkl']
    assert items_stripped_tab['start'][1] == 'def'
    assert items_stripped_tab['end'][-2:].contents == ['vwx', 'yz']

    items_unstripped_tab = SplitToItemsDataset(
        dict(start=data_tab_start, end=data_tab_end), strip=False)
    assert items_unstripped_tab['start'].contents == ['abc', ' def ', 'ghi', 'jkl']
    assert items_unstripped_tab['start'][1] == ' def '
    assert items_unstripped_tab['end'][-2:].contents == ['vwx', 'yz ']

    data_comma_start = 'abc, def, ghi, jkl'
    data_comma_end = 'mno, pqr, stu, vwx, yz'

    items_stripped_comma = SplitToItemsDataset(
        dict(start=data_comma_start, end=data_comma_end), delimiter=',')
    assert items_stripped_comma['start'].contents == ['abc', 'def', 'ghi', 'jkl']
    assert items_stripped_comma['start'][1] == 'def'
    assert items_stripped_comma['end'][-2:].contents == ['vwx', 'yz']

    for data_file, items in items_stripped_comma.items():
        items_stripped_comma[data_file] = items[1:3]

    for data_file, items in items_stripped_tab.items():
        items_stripped_tab[data_file] = items[1:3]

    tab_joined_items = JoinItemsDataset(items_stripped_comma)
    assert tab_joined_items['start'].contents == 'def\tghi'
    assert tab_joined_items['end'][1:-1].contents == 'qr\tst'

    comma_space_joined_items = JoinItemsDataset(items_stripped_tab, delimiter=', ')
    assert comma_space_joined_items['start'].contents == 'def, ghi'
    assert comma_space_joined_items['end'][1:-1].contents == 'qr, st'


def test_split_lines_to_columns_and_join_columns_to_lines_dataset():
    data_tab_forward = ['abc\t def \tghi\t jkl', 'mno\t pqr\tstu\t vwx', 'yz']
    data_tab_reverse = ['zyx\twvu\t tsr \t pqo', ' nml\t kji\thgf\t edc', 'ab ']

    cols_stripped_tab = SplitLinesToColumnsDataset(
        dict(forward=data_tab_forward, reverse=data_tab_reverse))
    assert cols_stripped_tab['forward'][0].contents == ['abc', 'def', 'ghi', 'jkl']
    assert cols_stripped_tab['forward'][0][1] == 'def'
    assert cols_stripped_tab['reverse'][1:2].contents \
           == [SplitToItemsModel(' nml\t kji\thgf\t edc')]
    assert cols_stripped_tab['reverse'][1:].to_data() \
           == [['nml', 'kji', 'hgf', 'edc'], ['ab']]

    cols_unstripped_tab = SplitLinesToColumnsDataset(
        dict(forward=data_tab_forward, reverse=data_tab_reverse), strip=False)
    assert cols_unstripped_tab['forward'][0].contents == ['abc', ' def ', 'ghi', ' jkl']
    assert cols_unstripped_tab['forward'][0][1] == ' def '
    assert cols_unstripped_tab['reverse'][1:2].contents \
           == [SplitToItemsModel(' nml\t kji\thgf\t edc', strip=False)]
    assert cols_unstripped_tab['reverse'][1:].to_data() \
           == [[' nml', ' kji', 'hgf', ' edc'], ['ab ']]

    data_comma_forward = ['abc, def, ghi, jkl', 'mno, pqr, stu, vwx', 'yz']
    data_comma_reverse = ['zyx, wvu, tsr, pqo', 'nml, kji, hgf, edc', 'ab']

    cols_stripped_comma = SplitLinesToColumnsDataset(
        dict(forward=data_comma_forward, reverse=data_comma_reverse), delimiter=',')
    assert cols_stripped_comma['forward'][0].contents == ['abc', 'def', 'ghi', 'jkl']
    assert cols_stripped_comma['forward'][0][1] == 'def'
    assert cols_stripped_comma['reverse'][1:2].contents \
           == [SplitToItemsModel('nml, kji, hgf, edc', delimiter=',')]
    assert cols_stripped_comma['reverse'][1:].to_data() == [['nml', 'kji', 'hgf', 'edc'], ['ab']]

    for data_file, items in cols_stripped_comma.items():
        cols_stripped_comma[data_file] = items[1:]

    for data_file, items in cols_stripped_tab.items():
        cols_stripped_tab[data_file] = items[1:]

    joined_cols = JoinColumnsToLinesDataset(cols_stripped_tab)
    assert joined_cols['forward'].contents \
           == [JoinItemsModel('mno\tpqr\tstu\tvwx'), JoinItemsModel('yz')]
    assert joined_cols['forward'][1:].contents == [JoinItemsModel('yz')]
    assert joined_cols['reverse'].to_data() == ['nml\tkji\thgf\tedc', 'ab']

    joined_cols = JoinColumnsToLinesDataset(cols_stripped_comma, delimiter=', ')
    assert joined_cols['forward'].contents \
           == [JoinItemsModel('mno, pqr, stu, vwx'), JoinItemsModel('yz')]
    assert joined_cols['forward'][1:].contents == [JoinItemsModel('yz')]
    assert joined_cols['reverse'].to_data() == ['nml, kji, hgf, edc', 'ab']
