import os
from textwrap import dedent
from typing import Annotated

from pydantic import ValidationError
import pytest

from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.data.helpers import Params
from omnipy.data.model import Model
from omnipy.modules.raw.models import (BytesModel,
                                       JoinColumnsToLinesModel,
                                       JoinItemsModel,
                                       JoinLinesModel,
                                       SplitLinesToColumnsModel,
                                       SplitToItemsModel,
                                       SplitToItemsModelNew,
                                       SplitToLinesModel,
                                       StrModel)

from ...helpers.protocols import AssertModelOrValFunc  # type: ignore[misc]


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


@pytest.mark.parametrize('use_str_model', [False, True], ids=['str', 'Model[str]'])
def test_split_to_and_join_lines_model(
    use_str_model: bool,
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

    lines_stripped = SplitToLinesModel(data)
    assert_model_if_dyn_conv_else_val(
        lines_stripped[0],  # type: ignore[index]
        str,
        'Alas, poor Yorick! I knew him, Horatio: a fellow')

    lines_unstripped = SplitToLinesModel(data, strip=False)
    assert_model_if_dyn_conv_else_val(lines_unstripped[0], str, '        ')  # type: ignore[index]
    assert_model_if_dyn_conv_else_val(
        lines_unstripped[1],  # type: ignore[index]
        str,
        '        Alas, poor Yorick! I knew him, Horatio: a fellow')
    assert_model_if_dyn_conv_else_val(lines_unstripped[-1], str, '        ')  # type: ignore[index]

    last_lines = lines_stripped[3:]  # type: ignore[index]
    assert last_lines[0:2].contents == [
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know'
    ]
    assert_model_if_dyn_conv_else_val(
        last_lines[-1],  # type: ignore[index]
        str,
        'now, to mock your own grinning? quite chap-fallen.')

    joined_lines = JoinLinesModel(last_lines[0:2])
    assert joined_lines.contents == dedent("""\
        abhorred in my imagination it is! my gorge rises at
        it. Here hung those lips that I have kissed I know""")
    assert joined_lines[:joined_lines.index(' ')].contents == 'abhorred'  # type: ignore[index]

    assert JoinLinesModel(SplitToLinesModel(data)).contents == os.linesep.join(
        [line.strip() for line in data.strip().split(os.linesep)])  # type: ignore[attr-defined]

    assert JoinLinesModel(SplitToLinesModel(data, strip=False)).contents == raw_data


@pytest.mark.parametrize('use_str_model', [False, True], ids=['str', 'Model[str]'])
def test_split_to_and_join_items_model(
    use_str_model: bool,
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    raw_data_tab = 'abc\t def \tghi\tjkl'

    data_tab = Model[str](raw_data_tab) if use_str_model else raw_data_tab

    items_stripped_tab = SplitToItemsModel(data_tab)
    assert items_stripped_tab.contents == ['abc', 'def', 'ghi', 'jkl']

    assert_model_if_dyn_conv_else_val(items_stripped_tab[1], str, 'def')  # type: ignore[index]
    assert items_stripped_tab[-2:].contents == ['ghi', 'jkl']  # type: ignore[index]

    items_unstripped_tab = SplitToItemsModel(data_tab, strip=False)
    assert items_unstripped_tab.contents == ['abc', ' def ', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_unstripped_tab[1], str, ' def ')  # type: ignore[index]
    assert items_unstripped_tab[-2:].contents == ['ghi', 'jkl']  # type: ignore[index]

    raw_data_comma = 'abc, def, ghi, jkl'

    data_comma = Model[str](raw_data_comma) if use_str_model else raw_data_comma

    items_stripped_comma = SplitToItemsModel(data_comma, delimiter=',')
    assert items_stripped_comma.contents == ['abc', 'def', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_stripped_comma[1], str, 'def')  # type: ignore[index]
    assert items_stripped_comma[-2:].contents == ['ghi', 'jkl']  # type: ignore[index]

    tab_joined_items = JoinItemsModel(items_stripped_tab[1:3])  # type: ignore[index]
    assert tab_joined_items.contents == 'def\tghi'
    assert tab_joined_items[1:-1].contents == 'ef\tgh'  # type: ignore[index]

    comma_space_joined_items = JoinItemsModel(
        items_stripped_comma[1:3], delimiter=', ')  # type: ignore[index]
    assert comma_space_joined_items.contents == 'def, ghi'
    assert comma_space_joined_items[1:-1].contents == 'ef, gh'  # type: ignore[index]


@pytest.mark.parametrize('use_str_model', [False, True], ids=['str', 'Model[str]'])
def test_split_to_and_join_items_new_model(
    use_str_model: bool,
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    raw_data_tab = 'abc\t def \tghi\tjkl'

    data_tab = Model[str](raw_data_tab) if use_str_model else raw_data_tab

    items_stripped_tab = SplitToItemsModelNew(data_tab)
    assert items_stripped_tab.contents == ['abc', 'def', 'ghi', 'jkl']

    assert_model_or_val(dyn_convert, items_stripped_tab[1], str, 'def')  # type: ignore[index]
    assert items_stripped_tab[-2:].contents == ['ghi', 'jkl']  # type: ignore[index]

    items_unstripped_tab = SplitToItemsModelNew[Params[{'strip': False}]](data_tab)
    assert items_unstripped_tab.contents == ['abc', ' def ', 'ghi', 'jkl']
    assert_model_or_val(dyn_convert, items_unstripped_tab[1], str, ' def ')  # type: ignore[index]
    assert items_unstripped_tab[-2:].contents == ['ghi', 'jkl']  # type: ignore[index]

    raw_data_comma = 'abc, def, ghi, jkl'

    data_comma = Model[str](raw_data_comma) if use_str_model else raw_data_comma

    items_stripped_comma = SplitToItemsModelNew[Params[{'delimiter': ','}]](data_comma)
    assert items_stripped_comma.contents == ['abc', 'def', 'ghi', 'jkl']
    assert_model_or_val(dyn_convert, items_stripped_comma[1], str, 'def')  # type: ignore[index]
    assert items_stripped_comma[-2:].contents == ['ghi', 'jkl']  # type: ignore[index]

    tab_joined_items = JoinItemsModel(items_stripped_tab[1:3])  # type: ignore[index]
    assert tab_joined_items.contents == 'def\tghi'
    assert tab_joined_items[1:-1].contents == 'ef\tgh'  # type: ignore[index]

    comma_space_joined_items = JoinItemsModel(
        items_stripped_comma[1:3], delimiter=', ')  # type: ignore[index]
    assert comma_space_joined_items.contents == 'def, ghi'
    assert comma_space_joined_items[1:-1].contents == 'ef, gh'  # type: ignore[index]


@pytest.mark.parametrize('use_str_model', [False, True], ids=['str', 'Model[str]'])
def test_split_lines_to_columns_and_join_columns_to_lines_model(
    use_str_model: bool,
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    raw_data_tab = ['abc\t def \tghi\t jkl', 'mno\t pqr\tstu\t vwx', 'yz']
    data_tab = [Model[str](line) for line in raw_data_tab] if use_str_model else raw_data_tab

    cols_stripped_tab = SplitLinesToColumnsModel(data_tab)
    assert cols_stripped_tab[0].contents == ['abc', 'def', 'ghi', 'jkl']  # type: ignore[index]
    assert_model_if_dyn_conv_else_val(cols_stripped_tab[0][1], str, 'def')  # type: ignore[index]
    assert cols_stripped_tab[1:2].contents == [  # type: ignore[index]
        SplitToItemsModel('mno\t pqr\tstu\t vwx')
    ]
    assert cols_stripped_tab[1:].to_data() == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx'], ['yz']
    ]

    cols_unstripped_tab = SplitLinesToColumnsModel(data_tab, strip=False)
    assert cols_unstripped_tab[0].contents == ['abc', ' def ', 'ghi', ' jkl']  # type: ignore[index]
    assert_model_if_dyn_conv_else_val(cols_unstripped_tab[0][1], str,
                                      ' def ')  # type: ignore[index]
    assert cols_unstripped_tab[1:2].contents == [  # type: ignore[index]
        SplitToItemsModel('mno\t pqr\tstu\t vwx', strip=False)
    ]
    assert cols_unstripped_tab[1:2].contents == [  # type: ignore[index]
        SplitToItemsModel('mno\t pqr\tstu\t vwx', strip=False)
    ]
    assert cols_unstripped_tab[1:].to_data() == [  # type: ignore[index]
        ['mno', ' pqr', 'stu', ' vwx'], ['yz']
    ]

    raw_data_comma = ['abc, def, ghi, jkl', 'mno, pqr, stu, vwx', 'yz']
    data_comma = [Model[str](line) for line in raw_data_comma] if use_str_model else raw_data_comma

    cols_stripped_comma = SplitLinesToColumnsModel(data_comma, delimiter=',')
    assert cols_stripped_comma[0].contents == ['abc', 'def', 'ghi', 'jkl']  # type: ignore[index]
    assert_model_if_dyn_conv_else_val(cols_stripped_comma[0][1], str, 'def')  # type: ignore[index]

    assert cols_stripped_comma[1:2].contents == [  # type: ignore[index]
        SplitToItemsModel('mno, pqr, stu, vwx', delimiter=',')
    ]
    assert cols_stripped_comma[1:].to_data() == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx'], ['yz']
    ]

    joined_cols = JoinColumnsToLinesModel(cols_stripped_tab[1:])  # type: ignore[index]
    assert joined_cols.contents == [JoinItemsModel('mno\tpqr\tstu\tvwx'), JoinItemsModel('yz')]
    assert joined_cols[1:].contents == [JoinItemsModel('yz')]  # type: ignore[index]
    assert joined_cols.to_data() == ['mno\tpqr\tstu\tvwx', 'yz']

    joined_cols = JoinColumnsToLinesModel(
        cols_stripped_comma[1:], delimiter=', ')  # type: ignore[index]
    assert joined_cols.contents == [JoinItemsModel('mno, pqr, stu, vwx'), JoinItemsModel('yz')]
    assert joined_cols[1:].contents == [JoinItemsModel('yz')]  # type: ignore[index]
    assert joined_cols.to_data() == ['mno, pqr, stu, vwx', 'yz']
