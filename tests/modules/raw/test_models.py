import os
from textwrap import dedent
from typing import Annotated, Iterator

from pydantic import ValidationError
import pytest
import pytest_cases as pc

from omnipy.data.model import Model
from omnipy.modules.raw.models import (BytesModel,
                                       JoinColumnsToLinesModel,
                                       JoinItemsModel,
                                       JoinLinesModel,
                                       SplitLinesToColumnsModel,
                                       SplitToItemsModel,
                                       SplitToLinesModel,
                                       StrModel)

from ...helpers.protocols import AssertModelOrValFunc


def test_bytes_model() -> None:
    assert BytesModel(b'').contents == b''
    assert BytesModel(b'\xc3\xa6\xc3\xb8\xc3\xa5').contents == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    assert BytesModel('').contents == b''
    assert BytesModel('æøå').contents == b'\xc3\xa6\xc3\xb8\xc3\xa5'

    BytesModelLatin1 = BytesModel.adjust('BytesModelLatin1', encoding='latin-1')
    assert BytesModelLatin1('æøå').contents == b'\xe6\xf8\xe5'

    BytesModelMyEncoding = BytesModel.adjust('BytesModelMyEncoding', encoding='my-encoding')
    with pytest.raises(LookupError):
        BytesModelMyEncoding('æøå')


def test_str_model():
    assert StrModel('').contents == ''
    assert StrModel('æøå').contents == 'æøå'
    assert StrModel(b'').contents == ''
    assert StrModel(b'\xc3\xa6\xc3\xb8\xc3\xa5').contents == 'æøå'

    with pytest.raises(ValidationError):
        StrModel(b'\xe6\xf8\xe5')

    StrModelLatin1 = StrModel.adjust('StrModelLatin1', encoding='latin-1')
    assert StrModelLatin1(b'\xe6\xf8\xe5').contents == 'æøå'

    StrModelUtf8Sig = StrModel.adjust('StrModelUtf8Sig', encoding='utf-8-sig')
    assert StrModelUtf8Sig(b'\xef\xbb\xbfsomething').contents == 'something'

    with pytest.raises(ValidationError):
        StrModelUtf8Sig(b'\xe6\xf8\xe5')

    StrModelMyEncoding = StrModel.adjust('StrModelMyEncoding', encoding='my-encoding')
    with pytest.raises(LookupError):
        StrModelMyEncoding(b'\xe6\xf8\xe5')


@pc.parametrize('use_str_model', [False, True], ids=['str', 'Model[str]'])
def test_split_to_and_join_lines_model(
    use_str_model: bool,
    mock_linesep_variants: Annotated[Iterator[None], pc.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    raw_data = """\
        \r
        Alas, poor Yorick! I knew him, Horatio: a fellow\r
        of infinite jest, of most excellent fancy: he hath\r
        borne me on his back a thousand times; and now, how\r
        abhorred in my imagination it is! my gorge rises at\r
        it. Here hung those lips that I have kissed I know\r
        not how oft. Where be your gibes now? your\r
        gambols? your songs? your flashes of merriment,\r
        that were wont to set the table on a roar? Not one\r
        now, to mock your own grinning? quite chap-fallen.\r
        """  # noqa: W293

    data = Model[str](raw_data) if use_str_model else raw_data

    lines_stripped = SplitToLinesModel(data)
    assert_model_if_dyn_conv_else_val(
        lines_stripped[0],  # type: ignore[index]
        str,
        'Alas, poor Yorick! I knew him, Horatio: a fellow')

    SplitToLinesNoStripModel = SplitToLinesModel.adjust('SplitToLinesNoStripModel', strip=False)

    lines_unstripped = SplitToLinesNoStripModel(data)
    assert_model_if_dyn_conv_else_val(lines_unstripped[0], str, '        \r')  # type: ignore[index]
    assert_model_if_dyn_conv_else_val(
        lines_unstripped[1],  # type: ignore[index]
        str,
        '        Alas, poor Yorick! I knew him, Horatio: a fellow\r')
    assert_model_if_dyn_conv_else_val(lines_unstripped[-1], str, '        ')  # type: ignore[index]

    last_lines = lines_stripped[3:]  # type: ignore[index]
    assert last_lines[0:2].contents == [
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know'
    ]
    assert_model_if_dyn_conv_else_val(last_lines[-1],
                                      str,
                                      'now, to mock your own grinning? quite chap-fallen.')

    joined_lines = JoinLinesModel(last_lines[0:2])
    assert joined_lines.contents == dedent("""\
        abhorred in my imagination it is! my gorge rises at
        it. Here hung those lips that I have kissed I know""")
    assert joined_lines[:joined_lines.index(' ')].contents == 'abhorred'  # type: ignore[index]

    assert JoinLinesModel(SplitToLinesModel(data)).contents == '\n'.join(
        [line.strip() for line in data.strip().split('\n')])  # type: ignore[attr-defined]

    assert JoinLinesModel(SplitToLinesNoStripModel(data)).contents == raw_data

    JoinLinesByOsLinesepModel = JoinLinesModel.adjust(
        'JoinLinesByOsLinesepModel', delimiter=os.linesep)

    os_linesep_joined_lines = JoinLinesByOsLinesepModel(last_lines[0:2])
    assert os_linesep_joined_lines.contents == os.linesep.join([
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know'
    ])


@pytest.mark.parametrize('use_str_model', [False, True], ids=['str', 'Model[str]'])
def test_split_to_and_join_items_model(
    use_str_model: bool,
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    raw_data_comma = 'abc, def ,ghi,jkl'

    data_comma = Model[str](raw_data_comma) if use_str_model else raw_data_comma

    items_stripped_comma = SplitToItemsModel(data_comma)
    assert items_stripped_comma.contents == ['abc', 'def', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_stripped_comma[1], str, 'def')  # type: ignore[index]
    assert items_stripped_comma[-2:].contents == ['ghi', 'jkl']  # type: ignore[index]

    SplitToItemsNoStripModel = SplitToItemsModel.adjust('SplitToItemsNoStripModel', strip=False)

    items_unstripped_tab = SplitToItemsNoStripModel(data_comma)
    assert items_unstripped_tab.contents == ['abc', ' def ', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_unstripped_tab[1], str, ' def ')  # type: ignore[index]
    assert items_unstripped_tab[-2:].contents == ['ghi', 'jkl']  # type: ignore[index]

    raw_data_tab = 'abc\t def \tghi\tjkl'

    data_tab = Model[str](raw_data_tab) if use_str_model else raw_data_tab

    SplitToItemsByTabModel = SplitToItemsModel.adjust('SplitToItemsByTabModel', delimiter='\t')

    items_stripped_tab = SplitToItemsByTabModel(data_tab)
    assert items_stripped_tab.contents == ['abc', 'def', 'ghi', 'jkl']

    assert_model_if_dyn_conv_else_val(items_stripped_tab[1], str, 'def')  # type: ignore[index]
    assert items_stripped_tab[-2:].contents == ['ghi', 'jkl']  # type: ignore[index]

    comma_space_joined_items = JoinItemsModel(items_stripped_comma[1:3])  # type: ignore[index]
    assert comma_space_joined_items.contents == 'def,ghi'
    assert comma_space_joined_items[1:-1].contents == 'ef,gh'  # type: ignore[index]

    JoinItemsByCommaSpaceModel = JoinItemsModel.adjust('JoinItemsByCommaSpaceModel', delimiter=', ')

    comma_space_joined_items = JoinItemsByCommaSpaceModel(
        items_stripped_tab[1:3])  # type: ignore[index]
    assert comma_space_joined_items.contents == 'def, ghi'
    assert comma_space_joined_items[1:-1].contents == 'ef, gh'  # type: ignore[index]


@pytest.mark.parametrize('use_str_model', [False, True], ids=['str', 'Model[str]'])
def test_split_lines_to_columns_and_join_columns_to_lines_model(
    use_str_model: bool,
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    raw_data_tab = ['abc\t def \tghi\t jkl', 'mno\t pqr\tstu\t vwx', 'yz']
    data_tab = [Model[str](line) for line in raw_data_tab] if use_str_model else raw_data_tab

    cols_stripped_tab = SplitLinesToColumnsModel(data_tab)
    assert_model_if_dyn_conv_else_val(
        cols_stripped_tab[0],  # type: ignore[index]
        list[str],
        ['abc', 'def', 'ghi', 'jkl'])
    assert_model_if_dyn_conv_else_val(cols_stripped_tab[0][1], str, 'def')  # type: ignore[index]
    assert cols_stripped_tab[1:2].contents == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx']
    ]
    assert cols_stripped_tab[1:].to_data() == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx'], ['yz']
    ]

    SplitLinesToColumnsNoStripModel = SplitLinesToColumnsModel.adjust(
        'SplitLinesToColumnsNoStripModel', strip=False)

    cols_unstripped_tab = SplitLinesToColumnsNoStripModel(data_tab)

    assert_model_if_dyn_conv_else_val(
        cols_unstripped_tab[0],  # type: ignore[index]
        list[str],
        ['abc', ' def ', 'ghi', ' jkl'])
    assert_model_if_dyn_conv_else_val(
        cols_unstripped_tab[0][1],  # type: ignore[index]
        str,
        ' def ')
    assert cols_unstripped_tab[1:2].contents == [  # type: ignore[index]
        ['mno', ' pqr', 'stu', ' vwx']
    ]
    assert cols_unstripped_tab[1:].to_data() == [  # type: ignore[index]
        ['mno', ' pqr', 'stu', ' vwx'], ['yz']
    ]

    raw_data_comma = ['abc, def, ghi, jkl', 'mno, pqr, stu, vwx', 'yz']
    data_comma = [Model[str](line) for line in raw_data_comma] if use_str_model else raw_data_comma

    SplitLinesToColumnsByCommaModel = SplitLinesToColumnsModel.adjust(
        'SplitLinesToColumnsByCommaModel', delimiter=',')

    cols_stripped_comma = SplitLinesToColumnsByCommaModel(data_comma)

    assert_model_if_dyn_conv_else_val(
        cols_stripped_comma[0],  # type: ignore[index]
        list[str],
        ['abc', 'def', 'ghi', 'jkl'])
    assert_model_if_dyn_conv_else_val(
        cols_stripped_comma[0][1],  # type: ignore[index]
        str,
        'def',
    )
    assert cols_stripped_comma[1:2].contents == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx']
    ]
    assert cols_stripped_comma[1:].to_data() == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx'], ['yz']
    ]

    joined_cols = JoinColumnsToLinesModel(cols_stripped_tab[1:])  # type: ignore[index]

    assert joined_cols.contents == ['mno\tpqr\tstu\tvwx', 'yz']
    assert joined_cols[1:].contents == ['yz']  # type: ignore[index]
    assert joined_cols.to_data() == ['mno\tpqr\tstu\tvwx', 'yz']

    JoinColumnsByCommaToLinesModel = JoinColumnsToLinesModel.adjust(
        'JoinColumnsByCommaToLinesModel', delimiter=', ')

    joined_cols_by_comma = JoinColumnsByCommaToLinesModel(
        cols_stripped_comma[1:])  # type: ignore[index]
    assert joined_cols_by_comma.contents == ['mno, pqr, stu, vwx', 'yz']
    assert joined_cols_by_comma[1:].contents == ['yz']  # type: ignore[index]
    assert joined_cols_by_comma.to_data() == ['mno, pqr, stu, vwx', 'yz']
