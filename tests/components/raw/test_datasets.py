import os
from textwrap import dedent
from typing import Annotated, Iterable

import pytest
import pytest_cases as pc

from omnipy.components.raw.datasets import (BytesDataset,
                                            JoinColumnsToLinesDataset,
                                            JoinItemsDataset,
                                            JoinLinesDataset,
                                            SplitLinesToColumnsDataset,
                                            SplitToItemsDataset,
                                            SplitToLinesDataset,
                                            StrDataset,
                                            StrictBytesDataset,
                                            StrictStrDataset)
from omnipy.data.model import Model
from omnipy.shared.protocols.hub.runtime import IsRuntime
from omnipy.util.pydantic import ValidationError

from ...helpers.protocols import AssertModelOrValFunc


def test_bytes_dataset() -> None:
    assert BytesDataset(dict(a=b''))['a'].content == b''
    assert BytesDataset(
        dict(a=b'\xc3\xa6\xc3\xb8\xc3\xa5'))['a'].content == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    assert BytesDataset(dict(a=''))['a'].content == b''
    assert BytesDataset(dict(a='æøå'))['a'].content == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    assert BytesDataset(dict(a='æøå'))['a'].content == b'\xc3\xa6\xc3\xb8\xc3\xa5'

    BytesDatasetLatin1 = BytesDataset.adjust(
        'BytesDatasetLatin1', 'BytesModelLatin1', encoding='latin-1')
    assert BytesDatasetLatin1(dict(a='æøå'))['a'].content == b'\xe6\xf8\xe5'

    BytesDatasetMyEncoding = BytesDataset.adjust(
        'BytesDatasetMyEncoding', 'BytesModelMyEncoding', encoding='my-encoding')
    with pytest.raises(LookupError):
        BytesDatasetMyEncoding(dict(a='æøå'))


def test_strict_bytes_dataset() -> None:
    assert StrictBytesDataset(dict(a=b''))['a'].content == b''
    assert StrictBytesDataset(
        dict(a=b'\xc3\xa6\xc3\xb8\xc3\xa5'))['a'].content == b'\xc3\xa6\xc3\xb8\xc3\xa5'

    with pytest.raises(ValidationError):
        StrictBytesDataset(dict(a=''))

    with pytest.raises(ValidationError):
        StrictBytesDataset(dict(a='æøå'))


def test_str_dataset() -> None:
    assert StrDataset(dict(a=''))['a'].content == ''
    assert StrDataset(dict(a='æøå'))['a'].content == 'æøå'
    assert StrDataset(dict(a=b''))['a'].content == ''
    assert StrDataset(dict(a=b'\xc3\xa6\xc3\xb8\xc3\xa5'))['a'].content == 'æøå'

    with pytest.raises(ValidationError):
        StrDataset(dict(a=b'\xe6\xf8\xe5'))

    StrDatasetLatin1 = StrDataset.adjust('StrDatasetLatin1', 'StrModelLatin1', encoding='latin-1')
    assert StrDatasetLatin1(dict(a=b'\xe6\xf8\xe5'))['a'].content == 'æøå'

    StrDatasetUtf8Sig = StrDataset.adjust(
        'StrDatasetUtf8Sig', 'StrModelUtf8Sig', encoding='utf-8-sig')
    assert StrDatasetUtf8Sig(dict(a=b'\xef\xbb\xbfsomething'))['a'].content == 'something'
    with pytest.raises(ValidationError):
        StrDatasetUtf8Sig(dict(a=b'\xe6\xf8\xe5'))

    StrDatasetMyEncoding = StrDataset.adjust(
        'StrDatasetMyEncoding', 'StrModelMyEncoding', encoding='my-encoding')
    with pytest.raises(LookupError):
        StrDatasetMyEncoding(dict(a=b'\xe6\xf8\xe5'))


def test_strict_str_dataset() -> None:
    assert StrictStrDataset(dict(a=''))['a'].content == ''
    assert StrictStrDataset(dict(a='æøå'))['a'].content == 'æøå'

    with pytest.raises(ValidationError):
        StrictStrDataset(dict(a=b''))

    with pytest.raises(ValidationError):
        StrictStrDataset(dict(a=b'\xc3\xa6\xc3\xb8\xc3\xa5'))


@pytest.mark.parametrize('use_str_model', [False, True], ids=['str', 'Model[str]'])
def test_split_to_and_join_lines_dataset(
    use_str_model: bool,
    mock_linesep_variants: Annotated[Iterable[None], pc.fixture],
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    raw_data = """\
        
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
    data = Model[str](raw_data) if use_str_model else raw_data

    lines_stripped = SplitToLinesDataset(dict(monologue=data))
    assert_model_if_dyn_conv_else_val(lines_stripped['monologue'][0],
                                      str,
                                      'Alas, poor Yorick! I knew him, Horatio: a fellow')

    SplitToLinesNoStripDataset = SplitToLinesDataset.adjust(
        'SplitToLinesNoStripDataset', 'SplitToLinesNoStripModel', strip=False)

    lines_unstripped = SplitToLinesNoStripDataset(dict(monologue=data))

    assert_model_if_dyn_conv_else_val(lines_unstripped['monologue'][0], str, '        ')
    assert_model_if_dyn_conv_else_val(lines_unstripped['monologue'][1],
                                      str,
                                      '        Alas, poor Yorick! I knew him, Horatio: a fellow')
    assert_model_if_dyn_conv_else_val(lines_unstripped['monologue'][-1], str, '        ')

    lines_stripped['last_lines'] = lines_stripped['monologue'][3:]
    assert_model_if_dyn_conv_else_val(lines_stripped['last_lines'][-1],
                                      str,
                                      'now, to mock your own grinning? quite chap-fallen.')

    for data_file, lines in lines_stripped.items():
        lines_stripped[data_file] = lines[0:2]

    assert (lines_stripped['last_lines'].content == [
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know'
    ])

    joined_lines = JoinLinesDataset(lines_stripped)

    assert joined_lines['monologue'].content == dedent("""\
        Alas, poor Yorick! I knew him, Horatio: a fellow
        of infinite jest, of most excellent fancy: he hath""")
    assert joined_lines['last_lines'].content == dedent("""\
        abhorred in my imagination it is! my gorge rises at
        it. Here hung those lips that I have kissed I know""")

    assert joined_lines['last_lines'][:joined_lines['last_lines'].index(' ')].content == 'abhorred'
    assert JoinLinesDataset(SplitToLinesDataset(dict(monologue=data))).to_data() == {
        'monologue': '\n'.join([line.strip() for line in raw_data.strip().split('\n')])
    }
    assert JoinLinesDataset(SplitToLinesNoStripDataset(dict(monologue=data))).to_data() == {
        'monologue': raw_data
    }

    JoinLinesByOsLinesepDataset = JoinLinesDataset.adjust(
        'JoinLinesByOsLinesepDataset', 'JoinLinesByOsLinesepModel', delimiter=os.linesep)

    os_linesep_joined_lines = JoinLinesByOsLinesepDataset(lines_stripped)

    assert os_linesep_joined_lines['last_lines'].content == os.linesep.join([
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know'
    ])


@pytest.mark.parametrize('use_str_model', [False, True], ids=['str', 'Model[str]'])
def test_split_to_and_join_items_dataset(
    use_str_model: bool,
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    raw_data_comma_start = 'abc, def ,ghi,jkl'
    data_comma_start = Model[str](raw_data_comma_start) if use_str_model else raw_data_comma_start

    raw_data_comma_end = 'mno, pqr ,stu,vwx,yz '
    data_comma_end = Model[str](raw_data_comma_end) if use_str_model else raw_data_comma_end

    items_stripped_comma = SplitToItemsDataset(dict(start=data_comma_start, end=data_comma_end))

    assert items_stripped_comma['start'].content == ['abc', 'def', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_stripped_comma['start'][1], str, 'def')
    assert items_stripped_comma['end'][-2:].content == ['vwx', 'yz']

    SplitToItemsNoStripDataset = SplitToItemsDataset.adjust(
        'SplitToItemsNoStripDataset',
        'SplitToItemsNoStripModel',
        strip=False,
    )

    items_unstripped_comma = SplitToItemsNoStripDataset(
        dict(start=data_comma_start, end=data_comma_end))

    assert items_unstripped_comma['start'].content == ['abc', ' def ', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_unstripped_comma['start'][1], str, ' def ')
    assert items_unstripped_comma['end'][-2:].content == ['vwx', 'yz ']

    data_tab_start = 'abc\t def \tghi\tjkl'
    data_tab_end = 'mno\t pqr \tstu\tvwx\tyz '

    SplitToItemsByTabDataset = SplitToItemsDataset.adjust(
        'SplitToItemsByTabDataset',
        'SplitToItemsByTabModel',
        delimiter='\t',
    )

    items_stripped_tab = SplitToItemsByTabDataset(dict(start=data_tab_start, end=data_tab_end))

    assert items_stripped_tab['start'].content == ['abc', 'def', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_stripped_tab['start'][1], str, 'def')
    assert items_stripped_tab['end'][-2:].content == ['vwx', 'yz']

    for data_file, items in items_stripped_tab.items():
        items_stripped_tab[data_file] = items[1:3]

    comma_joined_items = JoinItemsDataset(items_stripped_tab)
    assert comma_joined_items['start'].content == 'def,ghi'
    assert comma_joined_items['end'][1:-1].content == 'qr,st'

    JoinItemsByCommaSpaceDataset = JoinItemsDataset.adjust(
        'JoinItemsByCommaSpaceDataset',
        'JoinItemsByCommaSpaceModel',
        delimiter=', ',
    )

    comma_space_joined_items = JoinItemsByCommaSpaceDataset(items_stripped_tab)

    assert comma_space_joined_items['start'].content == 'def, ghi'
    assert comma_space_joined_items['end'][1:-1].content == 'qr, st'


@pytest.mark.parametrize('use_str_model', [False, True], ids=['str', 'Model[str]'])
def test_split_lines_to_columns_and_join_columns_to_lines_dataset(
    use_str_model: bool,
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    raw_data_tab_fw = ['abc\t def \tghi\t jkl', 'mno\t pqr\tstu\t vwx', 'yz']
    data_tab_fw = [Model[str](_) for _ in raw_data_tab_fw] if use_str_model else raw_data_tab_fw

    raw_data_tab_rev = ['zyx\twvu\t tsr \t pqo', ' nml\t kji\thgf\t edc', 'ab ']
    data_tab_rev = [Model[str](_) for _ in raw_data_tab_rev] if use_str_model else raw_data_tab_rev

    cols_stripped_tab = SplitLinesToColumnsDataset(dict(forward=data_tab_fw, reverse=data_tab_rev))

    assert_model_if_dyn_conv_else_val(
        cols_stripped_tab['forward'][0],
        list[str],
        ['abc', 'def', 'ghi', 'jkl'],
    )
    assert_model_if_dyn_conv_else_val(cols_stripped_tab['forward'][0][1], str, 'def')
    assert cols_stripped_tab['reverse'][1:2].content == [['nml', 'kji', 'hgf', 'edc']]
    assert cols_stripped_tab['reverse'][1:].to_data() == [['nml', 'kji', 'hgf', 'edc'], ['ab']]

    SplitLinesToColumnsNoStripDataset = SplitLinesToColumnsDataset.adjust(
        'SplitLinesToColumnsNoStripDataset',
        'SplitLinesToColumnsNoStripModel',
        strip=False,
    )

    cols_unstripped_tab = SplitLinesToColumnsNoStripDataset(
        dict(forward=data_tab_fw, reverse=data_tab_rev))

    assert_model_if_dyn_conv_else_val(
        cols_unstripped_tab['forward'][0],
        list[str],
        ['abc', ' def ', 'ghi', ' jkl'],
    )
    assert_model_if_dyn_conv_else_val(cols_unstripped_tab['forward'][0][1], str, ' def ')
    assert cols_unstripped_tab['reverse'][1:2].content == [[' nml', ' kji', 'hgf', ' edc']]
    assert cols_unstripped_tab['reverse'][1:].to_data() \
           == [[' nml', ' kji', 'hgf', ' edc'], ['ab ']]

    raw_data_comma_fw = ['abc, def, ghi, jkl', 'mno, pqr, stu, vwx', 'yz']
    data_comma_fw = [Model[str](_) for _ in raw_data_comma_fw] \
        if use_str_model else raw_data_comma_fw

    raw_data_comma_rev = ['zyx, wvu, tsr, pqo', 'nml, kji, hgf, edc', 'ab']
    data_comma_rev = [Model[str](_) for _ in raw_data_comma_rev] \
        if use_str_model else raw_data_comma_rev

    SplitLinesToColumnsByCommaDataset = SplitLinesToColumnsDataset.adjust(
        'SplitLinesToColumnsByCommaDataset',
        'SplitLinesToColumnsByCommaModel',
        delimiter=',',
    )

    cols_stripped_comma = SplitLinesToColumnsByCommaDataset(
        dict(forward=data_comma_fw, reverse=data_comma_rev))

    assert_model_if_dyn_conv_else_val(
        cols_stripped_comma['forward'][0],
        list[str],
        ['abc', 'def', 'ghi', 'jkl'],
    )
    assert_model_if_dyn_conv_else_val(cols_stripped_comma['forward'][0][1], str, 'def')
    assert cols_stripped_comma['reverse'][1:2].content == [['nml', 'kji', 'hgf', 'edc']]
    assert cols_stripped_comma['reverse'][1:].to_data() == [['nml', 'kji', 'hgf', 'edc'], ['ab']]

    for data_file, items in cols_stripped_comma.items():
        cols_stripped_comma[data_file] = items[1:]

    for data_file, items in cols_stripped_tab.items():
        cols_stripped_tab[data_file] = items[1:]

    joined_cols = JoinColumnsToLinesDataset(cols_stripped_tab)

    assert joined_cols['forward'].content == ['mno\tpqr\tstu\tvwx', 'yz']
    assert joined_cols['forward'][1:].content == ['yz']
    assert joined_cols['reverse'].to_data() == ['nml\tkji\thgf\tedc', 'ab']

    JoinColumnsToLinesByCommaDataset = JoinColumnsToLinesDataset.adjust(
        'JoinColumnsToLinesByCommaDataset',
        'JoinColumnsToLinesByCommaModel',
        delimiter=', ',
    )

    joined_cols_by_comma = JoinColumnsToLinesByCommaDataset(cols_stripped_comma)

    assert joined_cols_by_comma['forward'].content == ['mno, pqr, stu, vwx', 'yz']
    assert joined_cols_by_comma['forward'][1:].content == ['yz']
    assert joined_cols_by_comma['reverse'].to_data() == ['nml, kji, hgf, edc', 'ab']
