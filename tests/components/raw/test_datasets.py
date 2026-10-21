"""Tests for raw dataset models and split-join behavior."""

from collections.abc import Iterable
import os
from textwrap import dedent
from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.components.raw.datasets import (
    BytesDataset,
    JoinColumnsToLinesDataset,
    JoinItemsDataset,
    JoinLinesDataset,
    SplitLinesToColumnsDataset,
    SplitToItemsDataset,
    SplitToLinesDataset,
    SplitToLinesNoStripDataset,
    StrDataset,
    StrictBytesDataset,
    StrictStrDataset,
)
from omnipy.data.model import Model
from omnipy.util.pydantic import ValidationError

from ...helpers.protocols import AssertModelOrValFunc


def test_bytes_dataset() -> None:
    assert BytesDataset(dict(a=b''))['a'].content == b''
    assert (
        BytesDataset(dict(a=b'\xc3\xa6\xc3\xb8\xc3\xa5'))['a'].content
        == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    )
    assert BytesDataset(dict(a=''))['a'].content == b''
    assert BytesDataset(dict(a='æøå'))['a'].content == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    assert BytesDataset(dict(a='æøå'))['a'].content == b'\xc3\xa6\xc3\xb8\xc3\xa5'

    BytesDatasetLatin1 = BytesDataset.adjust(
        'BytesDatasetLatin1', 'BytesModelLatin1', encoding='latin-1'
    )
    assert BytesDatasetLatin1(dict(a='æøå'))['a'].content == b'\xe6\xf8\xe5'

    BytesDatasetMyEncoding = BytesDataset.adjust(
        'BytesDatasetMyEncoding', 'BytesModelMyEncoding', encoding='my-encoding'
    )
    with pytest.raises(LookupError):
        BytesDatasetMyEncoding(dict(a='æøå'))


def test_strict_bytes_dataset() -> None:
    assert StrictBytesDataset(dict(a=b''))['a'].content == b''
    assert (
        StrictBytesDataset(dict(a=b'\xc3\xa6\xc3\xb8\xc3\xa5'))['a'].content
        == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    )

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
        'StrDatasetUtf8Sig', 'StrModelUtf8Sig', encoding='utf-8-sig'
    )
    assert StrDatasetUtf8Sig(dict(a=b'\xef\xbb\xbfsomething'))['a'].content == 'something'
    with pytest.raises(ValidationError):
        StrDatasetUtf8Sig(dict(a=b'\xe6\xf8\xe5'))

    StrDatasetMyEncoding = StrDataset.adjust(
        'StrDatasetMyEncoding', 'StrModelMyEncoding', encoding='my-encoding'
    )
    with pytest.raises(LookupError):
        StrDatasetMyEncoding(dict(a=b'\xe6\xf8\xe5'))


def test_strict_str_dataset() -> None:
    assert StrictStrDataset(dict(a=''))['a'].content == ''
    assert StrictStrDataset(dict(a='æøå'))['a'].content == 'æøå'

    with pytest.raises(ValidationError):
        StrictStrDataset(dict(a=b''))

    with pytest.raises(ValidationError):
        StrictStrDataset(dict(a=b'\xc3\xa6\xc3\xb8\xc3\xa5'))


def test_split_to_lines_dataset(
    hamlet_text_lf_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    data = hamlet_text_lf_as_model_or_plain
    lines_stripped = SplitToLinesDataset(dict(monologue=data))

    assert_model_if_dyn_conv_else_val(
        lines_stripped['monologue'][0],
        str,
        'Alas, poor Yorick! I knew him, Horatio: a fellow',
    )

    lines_stripped['last_lines'] = lines_stripped['monologue'][3:]
    assert_model_if_dyn_conv_else_val(
        lines_stripped['last_lines'][-1],
        str,
        'now, to mock your own grinning? quite chap-fallen.',
    )

    for data_file, lines in lines_stripped.items():
        lines_stripped[data_file] = lines[0:2]

    assert lines_stripped['last_lines'].content == [
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know',
    ]


def test_split_to_lines_no_strip_dataset(
    hamlet_text_lf_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    data = hamlet_text_lf_as_model_or_plain

    SplitToLinesNoStripDataset = SplitToLinesDataset.adjust(
        'SplitToLinesNoStripDataset', 'SplitToLinesNoStripModel', strip=False
    )

    lines_unstripped = SplitToLinesNoStripDataset(dict(monologue=data))

    assert_model_if_dyn_conv_else_val(lines_unstripped['monologue'][0], str, '        \n')
    assert_model_if_dyn_conv_else_val(
        lines_unstripped['monologue'][1],
        str,
        '        Alas, poor Yorick! I knew him, Horatio: a fellow\n',
    )
    assert_model_if_dyn_conv_else_val(lines_unstripped['monologue'][-1], str, '        ')


def test_join_lines_dataset(
    hamlet_text_lf_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
) -> None:
    data = hamlet_text_lf_as_model_or_plain
    lines_stripped = SplitToLinesDataset(dict(monologue=data))

    lines_stripped['last_lines'] = lines_stripped['monologue'][3:]

    for data_file, lines in lines_stripped.items():
        lines_stripped[data_file] = lines[0:2]

    joined_lines = JoinLinesDataset(lines_stripped)

    assert joined_lines['monologue'].content == dedent("""\
        Alas, poor Yorick! I knew him, Horatio: a fellow
        of infinite jest, of most excellent fancy: he hath""")
    assert joined_lines['last_lines'].content == dedent("""\
        abhorred in my imagination it is! my gorge rises at
        it. Here hung those lips that I have kissed I know""")

    assert joined_lines['last_lines'][: joined_lines['last_lines'].index(' ')].content == 'abhorred'


def test_join_lines_dataset_of_split_to_lines_dataset(
    hamlet_text_lf: Annotated[str, pytest.fixture],
    hamlet_text_lf_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    hamlet_lines_stripped: Annotated[list[str], pytest.fixture],
) -> None:
    data = hamlet_text_lf_as_model_or_plain

    assert JoinLinesDataset(SplitToLinesDataset(dict(monologue=data))).to_data() == {
        'monologue': '\n'.join(hamlet_lines_stripped)
    }

    SplitToLinesNoStripDataset = SplitToLinesDataset.adjust(
        'SplitToLinesNoStripDataset', 'SplitToLinesNoStripModel', strip=False
    )

    assert JoinLinesDataset(SplitToLinesNoStripDataset(dict(monologue=data))).to_data() == {
        'monologue': '\n'.join(hamlet_text_lf.splitlines(keepends=True))
    }


def test_join_lines_by_os_linesep_dataset(
    hamlet_text_lf_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    mock_linesep_variants: Annotated[Iterable[None], pc.fixture],
) -> None:
    data = hamlet_text_lf_as_model_or_plain
    lines_stripped = SplitToLinesDataset(dict(monologue=data))

    lines_stripped['last_lines'] = lines_stripped['monologue'][3:]

    for data_file, lines in lines_stripped.items():
        lines_stripped[data_file] = lines[0:2]

    JoinLinesByOsLinesepDataset = JoinLinesDataset.adjust(
        'JoinLinesByOsLinesepDataset', 'JoinLinesByOsLinesepModel', delimiter=os.linesep
    )

    os_linesep_joined_lines = JoinLinesByOsLinesepDataset(lines_stripped)

    assert os_linesep_joined_lines['last_lines'].content == os.linesep.join(
        [
            'abhorred in my imagination it is! my gorge rises at',
            'it. Here hung those lips that I have kissed I know',
        ]
    )


def test_split_to_lines_datasets_support_mixed_universal_newlines(
    text_with_mixed_newlines_as_model_or_plain: (
        Annotated[
            Model[str] | str,
            pytest.fixture,
        ]
    ),
) -> None:

    data = text_with_mixed_newlines_as_model_or_plain

    assert SplitToLinesDataset(dict(lines=data))['lines'].content == [
        'first',
        'second',
        'third',
        'fourth',
    ]
    assert SplitToLinesNoStripDataset(dict(lines=data))['lines'].content == [
        'first \n',
        ' second  \r\n',
        'third\r',
        'fourth\n',
    ]


def test_split_to_items_dataset(
    dict_of_text_with_comma_as_model_or_plain: Annotated[
        dict[str, Model[str] | str],
        pytest.fixture,
    ],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    items_stripped_comma = SplitToItemsDataset(dict_of_text_with_comma_as_model_or_plain)

    assert items_stripped_comma['start'].content == ['abc', 'def', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_stripped_comma['start'][1], str, 'def')
    assert items_stripped_comma['end'][-2:].content == ['vwx', 'yz']


def test_split_to_items_no_strip_dataset(
    dict_of_text_with_comma_as_model_or_plain: Annotated[
        dict[str, Model[str] | str],
        pytest.fixture,
    ],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    SplitToItemsNoStripDataset = SplitToItemsDataset.adjust(
        'SplitToItemsNoStripDataset',
        'SplitToItemsNoStripModel',
        strip=False,
    )

    items_unstripped_comma = SplitToItemsNoStripDataset(dict_of_text_with_comma_as_model_or_plain)

    assert items_unstripped_comma['start'].content == ['abc', ' def ', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_unstripped_comma['start'][1], str, ' def ')
    assert items_unstripped_comma['end'][-2:].content == ['vwx', 'yz ']


def test_split_to_items_by_tab_dataset(
    dict_of_text_with_tabs_as_model_or_plain: Annotated[
        dict[str, Model[str] | str],
        pytest.fixture,
    ],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    SplitToItemsByTabDataset = SplitToItemsDataset.adjust(
        'SplitToItemsByTabDataset',
        'SplitToItemsByTabModel',
        delimiter='\t',
    )

    items_stripped_tab = SplitToItemsByTabDataset(dict_of_text_with_tabs_as_model_or_plain)

    assert items_stripped_tab['start'].content == ['abc', 'def', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_stripped_tab['start'][1], str, 'def')
    assert items_stripped_tab['end'][-2:].content == ['vwx', 'yz']


def test_join_items_dataset(
    dict_of_item_lists: Annotated[dict[str, list[int]], pytest.fixture],
) -> None:

    comma_joined_items = JoinItemsDataset(dict_of_item_lists)
    assert comma_joined_items['start'].content == 'abc,def,ghi,jkl'
    assert comma_joined_items['end'][1:-1].content == 'no,pqr,stu,vwx,y'


def test_join_items_by_comma_space_dataset(
    dict_of_item_lists: Annotated[dict[str, list[int]], pytest.fixture],
) -> None:

    JoinItemsByCommaSpaceDataset = JoinItemsDataset.adjust(
        'JoinItemsByCommaSpaceDataset',
        'JoinItemsByCommaSpaceModel',
        delimiter=', ',
    )

    comma_space_joined_items = JoinItemsByCommaSpaceDataset(dict_of_item_lists)

    assert comma_space_joined_items['start'].content == 'abc, def, ghi, jkl'
    assert comma_space_joined_items['end'][1:-1].content == 'no, pqr, stu, vwx, y'


def test_split_lines_to_columns_dataset(
    dict_of_lists_of_texts_with_tabs_as_model_or_plain: Annotated[
        dict[str, list[Model[str]] | list[str]],
        pytest.fixture,
    ],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    cols_stripped_tab = SplitLinesToColumnsDataset(
        dict_of_lists_of_texts_with_tabs_as_model_or_plain
    )

    assert_model_if_dyn_conv_else_val(
        cols_stripped_tab['forward'][0],
        list[str],
        ['abc', 'def', 'ghi', 'jkl'],
    )
    assert_model_if_dyn_conv_else_val(cols_stripped_tab['forward'][0][1], str, 'def')
    assert cols_stripped_tab['reverse'][1:2].content == [  # type: ignore[attr-defined]
        ['nml', 'kji', 'hgf', 'edc'],
    ]
    assert cols_stripped_tab['reverse'][1:].to_data() == [  # type: ignore[attr-defined]
        ['nml', 'kji', 'hgf', 'edc'],
        ['ab'],
    ]


def test_split_lines_to_columns_no_strip_dataset(
    dict_of_lists_of_texts_with_tabs_as_model_or_plain: Annotated[
        dict[str, list[Model[str]] | list[str]],
        pytest.fixture,
    ],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    SplitLinesToColumnsNoStripDataset = SplitLinesToColumnsDataset.adjust(
        'SplitLinesToColumnsNoStripDataset',
        'SplitLinesToColumnsNoStripModel',
        strip=False,
    )

    cols_unstripped_tab = SplitLinesToColumnsNoStripDataset(
        dict_of_lists_of_texts_with_tabs_as_model_or_plain
    )

    assert_model_if_dyn_conv_else_val(
        cols_unstripped_tab['forward'][0],
        list[str],
        ['abc', ' def ', 'ghi', ' jkl'],
    )
    assert_model_if_dyn_conv_else_val(cols_unstripped_tab['forward'][0][1], str, ' def ')
    assert cols_unstripped_tab['reverse'][1:2].content == [  # type: ignore[attr-defined]
        [' nml', ' kji', 'hgf', ' edc'],
    ]
    assert cols_unstripped_tab['reverse'][1:].to_data() == [  # type: ignore[attr-defined]
        [' nml', ' kji', 'hgf', ' edc'],
        ['ab '],
    ]


def test_split_lines_to_columns_by_comma_dataset(
    dict_of_lists_of_texts_with_comma_as_model_or_plain: Annotated[
        dict[str, list[Model[str]] | list[str]],
        pytest.fixture,
    ],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    SplitLinesToColumnsByCommaDataset = SplitLinesToColumnsDataset.adjust(
        'SplitLinesToColumnsByCommaDataset',
        'SplitLinesToColumnsByCommaModel',
        delimiter=',',
    )

    cols_stripped_comma = SplitLinesToColumnsByCommaDataset(
        dict_of_lists_of_texts_with_comma_as_model_or_plain
    )

    assert_model_if_dyn_conv_else_val(
        cols_stripped_comma['forward'][0],
        list[str],
        ['abc', 'def', 'ghi', 'jkl'],
    )
    assert_model_if_dyn_conv_else_val(cols_stripped_comma['forward'][0][1], str, 'def')
    assert cols_stripped_comma['reverse'][1:2].content == [  # type: ignore[attr-defined]
        ['nml', 'kji', 'hgf', 'edc'],
    ]
    assert cols_stripped_comma['reverse'][1:].to_data() == [  # type: ignore[attr-defined]
        ['nml', 'kji', 'hgf', 'edc'],
        ['ab'],
    ]


def test_join_columns_to_lines_dataset(
    dict_of_list_of_lists_of_items: Annotated[dict[str, list[list[str]]], pytest.fixture],
) -> None:

    joined_cols = JoinColumnsToLinesDataset(dict_of_list_of_lists_of_items)

    assert joined_cols['forward'].content == ['mno\tpqr\tstu\tvwx', 'yz']
    assert joined_cols['forward'][1:].content == ['yz']
    assert joined_cols['reverse'].to_data() == ['nml\tkji\thgf\tedc', 'ab']


def test_join_columns_to_lines_by_comma_dataset(
    dict_of_list_of_lists_of_items: Annotated[dict[str, list[list[str]]], pytest.fixture],
) -> None:

    JoinColumnsToLinesByCommaDataset = JoinColumnsToLinesDataset.adjust(
        'JoinColumnsToLinesByCommaDataset',
        'JoinColumnsToLinesByCommaModel',
        delimiter=', ',
    )

    joined_cols_by_comma = JoinColumnsToLinesByCommaDataset(dict_of_list_of_lists_of_items)

    assert joined_cols_by_comma['forward'].content == ['mno, pqr, stu, vwx', 'yz']
    assert joined_cols_by_comma['forward'][1:].content == ['yz']
    assert joined_cols_by_comma['reverse'].to_data() == ['nml, kji, hgf, edc', 'ab']
