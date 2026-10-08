"""Tests for raw models and nested split-join behavior."""
import datetime
from enum import Enum
import os
from textwrap import dedent
from typing import Annotated, Callable, cast, Iterable, TypeAlias

import pytest
import pytest_cases as pc

from omnipy.components.raw.enums import NewLine
from omnipy.components.raw.models import (BytesModel,
                                          DateModel,
                                          DateTimeModel,
                                          JoinColumnsByCommaToLinesModel,
                                          JoinColumnsToLinesModel,
                                          JoinItemsModel,
                                          JoinLinesModel,
                                          MatchItemsModel,
                                          NestedJoinItemsModel,
                                          NestedSplitToItemsModel,
                                          SplitLinesToColumnsByCommaModel,
                                          SplitLinesToColumnsModel,
                                          SplitToItemsByTabModel,
                                          SplitToItemsModel,
                                          SplitToLinesModel,
                                          SplitToLinesNoStripModel,
                                          StrictBytesModel,
                                          StrictStrModel,
                                          StrModel,
                                          TimeDeltaModel,
                                          TimeModel)
from omnipy.data.model import Model
from omnipy.util.pydantic import ValidationError

from ...helpers.protocols import AssertModelOrValFunc
from .helpers.protocols import AssertLineOfOsLinesepSplitCrlfTextFunc


def test_bytes_model() -> None:
    assert BytesModel(b'').content == b''
    assert BytesModel(b'\xc3\xa6\xc3\xb8\xc3\xa5').content == b'\xc3\xa6\xc3\xb8\xc3\xa5'
    assert BytesModel('').content == b''
    assert BytesModel('æøå').content == b'\xc3\xa6\xc3\xb8\xc3\xa5'

    BytesModelLatin1 = BytesModel.adjust('BytesModelLatin1', encoding='latin-1')
    assert BytesModelLatin1('æøå').content == b'\xe6\xf8\xe5'

    BytesModelMyEncoding = BytesModel.adjust('BytesModelMyEncoding', encoding='my-encoding')
    with pytest.raises(LookupError):
        BytesModelMyEncoding('æøå')


def test_strict_bytes_model() -> None:
    assert StrictBytesModel(b'').content == b''
    assert StrictBytesModel(b'\xc3\xa6\xc3\xb8\xc3\xa5').content == b'\xc3\xa6\xc3\xb8\xc3\xa5'

    with pytest.raises(ValidationError):
        StrictBytesModel('')

    with pytest.raises(ValidationError):
        StrictBytesModel('æøå')


def test_str_model():
    assert StrModel('').content == ''
    assert StrModel('æøå').content == 'æøå'
    assert StrModel(b'').content == ''
    assert StrModel(b'\xc3\xa6\xc3\xb8\xc3\xa5').content == 'æøå'

    with pytest.raises(ValidationError):
        StrModel(b'\xe6\xf8\xe5')

    StrModelLatin1 = StrModel.adjust('StrModelLatin1', encoding='latin-1')
    assert StrModelLatin1(b'\xe6\xf8\xe5').content == 'æøå'

    StrModelUtf8Sig = StrModel.adjust('StrModelUtf8Sig', encoding='utf-8-sig')
    assert StrModelUtf8Sig(b'\xef\xbb\xbfsomething').content == 'something'

    with pytest.raises(ValidationError):
        StrModelUtf8Sig(b'\xe6\xf8\xe5')

    StrModelMyEncoding = StrModel.adjust('StrModelMyEncoding', encoding='my-encoding')
    with pytest.raises(LookupError):
        StrModelMyEncoding(b'\xe6\xf8\xe5')


def test_strict_str_model():
    assert StrictStrModel('').content == ''
    assert StrictStrModel('æøå').content == 'æøå'

    with pytest.raises(ValidationError):
        StrictStrModel(b'')

    with pytest.raises(ValidationError):
        StrictStrModel(b'\xc3\xa6\xc3\xb8\xc3\xa5')


def test_date_model() -> None:
    date_model_from_date = DateModel(datetime.date(2020, 5, 17))
    assert date_model_from_date.content == datetime.date(2020, 5, 17)
    assert date_model_from_date.to_data() == '2020-05-17'

    date_model_from_iso = DateModel('2022-01-01')
    assert date_model_from_iso.content == datetime.date(2022, 1, 1)
    assert date_model_from_iso.to_data() == '2022-01-01'


def test_datetime_model() -> None:
    datetime_model_from_datetime = DateTimeModel(datetime.datetime(2020, 5, 17, 12, 15, 00))
    assert datetime_model_from_datetime.content == datetime.datetime(2020, 5, 17, 12, 15, 00)
    assert datetime_model_from_datetime.to_data() == '2020-05-17T12:15:00'

    datetime_model_from_iso = DateTimeModel('2022-01-01T12:15:00Z')
    assert datetime_model_from_iso.content == datetime.datetime(
        2022, 1, 1, 12, 15, 00, tzinfo=datetime.timezone.utc)
    assert datetime_model_from_iso.to_data() == '2022-01-01T12:15:00+00:00'

    datetime_model_from_unix_secs = DateTimeModel(1786640576)
    assert datetime_model_from_unix_secs.content == datetime.datetime(
        2026, 8, 13, 17, 2, 56, tzinfo=datetime.timezone.utc)
    assert datetime_model_from_unix_secs.to_data() == '2026-08-13T17:02:56+00:00'


def test_time_model() -> None:
    time_model_from_time = TimeModel(datetime.time(12, 15, 00))
    assert time_model_from_time.content == datetime.time(12, 15, 00)
    assert time_model_from_time.to_data() == '12:15:00'

    time_model_from_iso = TimeModel('12:15Z')
    assert time_model_from_iso.content == datetime.time(12, 15, tzinfo=datetime.timezone.utc)
    assert time_model_from_iso.to_data() == '12:15:00+00:00'


def test_timedelta_model() -> None:
    timedelta_model_from_timedelta = TimeDeltaModel(datetime.timedelta(days=1, hours=12))
    assert timedelta_model_from_timedelta.content == datetime.timedelta(days=1, hours=12)
    assert timedelta_model_from_timedelta.to_data() == '1 day, 12:00:00'

    timedelta_model_from_seconds = TimeDeltaModel(3601)
    assert timedelta_model_from_seconds.content == datetime.timedelta(hours=1, seconds=1)
    assert timedelta_model_from_seconds.to_data() == '1:00:01'

    timedelta_model_from_str = TimeDeltaModel('12:34:56.789')
    assert timedelta_model_from_str.content == datetime.timedelta(
        hours=12, minutes=34, seconds=56, microseconds=789000)
    assert timedelta_model_from_str.to_data() == '12:34:56.789000'

    timedelta_model_from_iso = TimeDeltaModel('P182DT12H30M5S')
    assert timedelta_model_from_iso.content == datetime.timedelta(
        days=182, hours=12, minutes=30, seconds=5)
    assert timedelta_model_from_iso.to_data() == '182 days, 12:30:05'


def test_date_and_time_model_operations() -> None:
    date_model_1 = DateModel('2020-05-17')
    date_model_2 = DateModel('2021-06-19')
    timedelta_1_2 = date_model_2 - date_model_1
    assert timedelta_1_2 == TimeDeltaModel(datetime.timedelta(days=398))
    assert date_model_1 + timedelta_1_2 == date_model_2

    datetime_model_1 = DateTimeModel('2020-05-17T12:15:00')
    datetime_model_2 = DateTimeModel('2020-05-18T13:16:01')

    timedelta_1_2 = datetime_model_2 - datetime_model_1
    assert timedelta_1_2 == TimeDeltaModel(
        datetime.timedelta(days=1, hours=1, minutes=1, seconds=1))
    assert datetime_model_1 + timedelta_1_2 == datetime_model_2


def test_split_to_lines_model(
    hamlet_text_crlf_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    lines_stripped = SplitToLinesModel(hamlet_text_crlf_as_model_or_plain)
    assert_model_if_dyn_conv_else_val(
        lines_stripped[0],
        str,
        'Alas, poor Yorick! I knew him, Horatio: a fellow',
    )
    assert_model_if_dyn_conv_else_val(
        lines_stripped[-1],
        str,
        'now, to mock your own grinning? quite chap-fallen.',
    )

    last_lines = lines_stripped[3:]
    assert last_lines[0:2].content == [
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know'
    ]
    assert_model_if_dyn_conv_else_val(
        last_lines[-1],
        str,
        'now, to mock your own grinning? quite chap-fallen.',
    )


def test_split_to_lines_no_strip_model(
    hamlet_text_crlf_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    lines_no_strip = SplitToLinesNoStripModel(hamlet_text_crlf_as_model_or_plain)

    assert_model_if_dyn_conv_else_val(
        lines_no_strip[1],
        str,
        '        Alas, poor Yorick! I knew him, Horatio: a fellow\r\n',
    )

    assert_model_if_dyn_conv_else_val(lines_no_strip[-1], str, '        ')


def test_split_to_lines_by_os_linesep_model(
    hamlet_text_crlf_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    mock_linesep_variants: Annotated[Iterable[None], pc.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
    assert_line_of_os_linesep_split_crlf_text: Annotated[
        AssertLineOfOsLinesepSplitCrlfTextFunc,
        pytest.fixture,
    ],
) -> None:
    SplitToLinesByOsLinesepModel = SplitToLinesModel.adjust(
        'SplitToLinesByOsLinesepModel',
        strip_chars=os.linesep,
        delimiter=os.linesep,
    )

    lines_split_by_os_linesep = SplitToLinesByOsLinesepModel(hamlet_text_crlf_as_model_or_plain)

    assert_line_of_os_linesep_split_crlf_text(
        lines_split_by_os_linesep[1],
        '        Alas, poor Yorick! I knew him, Horatio: a fellow',
        with_newline=False,
    )

    last_line_exp = '        '
    if os.linesep == NewLine.CR:
        last_line_exp = NewLine.LF + last_line_exp
    assert_model_if_dyn_conv_else_val(lines_split_by_os_linesep[-1], str, last_line_exp)


def test_split_to_lines_by_os_linesep_no_strip_model(
    hamlet_text_crlf_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    mock_linesep_variants: Annotated[Iterable[None], pc.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
    assert_line_of_os_linesep_split_crlf_text: Annotated[
        AssertLineOfOsLinesepSplitCrlfTextFunc,
        pytest.fixture,
    ],
) -> None:
    SplitToLinesByOsLinesepNoStripModel = SplitToLinesModel.adjust(
        'SplitToLinesByOsLinesepNoStripModel',
        strip=False,
        delimiter=os.linesep,
    )

    data = hamlet_text_crlf_as_model_or_plain
    lines_split_by_os_linesep_no_strip = SplitToLinesByOsLinesepNoStripModel(data)

    assert_line_of_os_linesep_split_crlf_text(
        lines_split_by_os_linesep_no_strip[1],
        '        Alas, poor Yorick! I knew him, Horatio: a fellow',
        with_newline=True,
    )

    last_line_exp = '        '
    if os.linesep == NewLine.CR:
        last_line_exp = NewLine.LF + last_line_exp
    assert_model_if_dyn_conv_else_val(lines_split_by_os_linesep_no_strip[-1], str, last_line_exp)


def test_join_lines_model(last_hamlet_lines_stripped: Annotated[list[str], pytest.fixture]) -> None:
    joined_lines = JoinLinesModel(last_hamlet_lines_stripped[0:2])

    assert joined_lines.content == dedent("""\
        abhorred in my imagination it is! my gorge rises at
        it. Here hung those lips that I have kissed I know""")
    assert joined_lines[:joined_lines.index(' ')].content == 'abhorred'  # type: ignore


def test_join_lines_by_os_linesep_model(
    last_hamlet_lines_stripped: Annotated[list[str], pytest.fixture],
    mock_linesep_variants: Annotated[Iterable[None], pc.fixture],
) -> None:

    JoinLinesByOsLinesepModel = JoinLinesModel.adjust(
        'JoinLinesByOsLinesepModel', delimiter=os.linesep)

    os_linesep_joined_lines = JoinLinesByOsLinesepModel(last_hamlet_lines_stripped[0:2])

    assert os_linesep_joined_lines.content == os.linesep.join([
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know'
    ])


def test_join_lines_model_of_split_to_lines_model(
    hamlet_text_crlf: Annotated[str, pytest.fixture],
    hamlet_lines_stripped: Annotated[list[str], pytest.fixture],
    mock_linesep_variants: Annotated[Iterable[None], pc.fixture],
) -> None:
    assert JoinLinesModel(
        SplitToLinesModel(hamlet_text_crlf)).content == '\n'.join(hamlet_lines_stripped)

    SplitToLinesByOsLinesepModel = SplitToLinesModel.adjust(
        'SplitToLinesByOsLinesepModel',
        strip_chars=os.linesep,
        delimiter=os.linesep,
    )

    assert JoinLinesModel(SplitToLinesByOsLinesepModel(hamlet_text_crlf)).content == '\n'.join(
        hamlet_text_crlf.split(os.linesep))


def test_split_to_lines_models_support_universal_newlines(
    text_with_mixed_newlines_as_model_or_plain: (Annotated[
        Model[str] | str,
        pytest.fixture,
    ]),
) -> None:
    data = text_with_mixed_newlines_as_model_or_plain

    assert SplitToLinesModel(data).content == [
        'first',
        'second',
        'third',
        'fourth',
    ]
    assert SplitToLinesNoStripModel(data).content == [
        'first \n',
        ' second  \r\n',
        'third\r',
        'fourth\n',
    ]


def test_split_to_items_model(
    first_text_with_comma_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    items_stripped_comma = SplitToItemsModel(first_text_with_comma_as_model_or_plain)

    assert items_stripped_comma.content == ['abc', 'def', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_stripped_comma[1], str, 'def')  # type: ignore[index]
    assert items_stripped_comma[-2:].content == ['ghi', 'jkl']


def test_split_to_items_no_strip_model(
    first_text_with_comma_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    SplitToItemsNoStripModel = SplitToItemsModel.adjust('SplitToItemsNoStripModel', strip=False)

    items_unstripped_tab = SplitToItemsNoStripModel(first_text_with_comma_as_model_or_plain)

    assert items_unstripped_tab.content == ['abc', ' def ', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_unstripped_tab[1], str, ' def ')  # type: ignore[index]
    assert items_unstripped_tab[-2:].content == ['ghi', 'jkl']  # type: ignore[index]


def test_split_to_items_by_space_and_tab_model(
    first_text_with_tabs_as_model_or_plain: Annotated[Model[str] | str, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    data_tab = first_text_with_tabs_as_model_or_plain

    SplitToItemsBySpaceModel = SplitToItemsModel.adjust('SplitToItemsBySpaceModel', delimiter=' ')

    items_stripped_space = SplitToItemsBySpaceModel(data_tab)
    assert items_stripped_space.content == ['abc', 'def', 'ghi\tjkl']

    items_stripped_tab = SplitToItemsByTabModel(data_tab)
    assert items_stripped_tab.content == ['abc', 'def', 'ghi', 'jkl']

    assert_model_if_dyn_conv_else_val(items_stripped_tab[1], str, 'def')  # type: ignore[index]
    assert items_stripped_tab[-2:].content == ['ghi', 'jkl']  # type: ignore[index]


def test_join_items_model(first_item_list: Annotated[list[str], pytest.fixture]) -> None:
    comma_joined_items = JoinItemsModel(first_item_list)  # type: ignore[index]

    assert comma_joined_items.content == 'abc,def,ghi,jkl'
    assert comma_joined_items[1:-1].content == 'bc,def,ghi,jk'  # type: ignore[index]


def test_join_items_by_comma_space_model(
        first_item_list: Annotated[list[str], pytest.fixture]) -> None:
    JoinItemsByCommaSpaceModel = JoinItemsModel.adjust('JoinItemsByCommaSpaceModel', delimiter=', ')

    comma_space_joined_items = JoinItemsByCommaSpaceModel(first_item_list)  # type: ignore[index]
    assert comma_space_joined_items.content == 'abc, def, ghi, jkl'
    assert comma_space_joined_items[1:-1].content == 'bc, def, ghi, jk'  # type: ignore[index]


def test_split_lines_to_columns_model(
    forward_list_of_texts_with_tabs: Annotated[list[Model[str]] | list[str], pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    cols_stripped_tab = SplitLinesToColumnsModel(forward_list_of_texts_with_tabs)

    assert_model_if_dyn_conv_else_val(
        cols_stripped_tab[0],  # type: ignore[index]
        list[str],
        ['abc', 'def', 'ghi', 'jkl'])
    assert_model_if_dyn_conv_else_val(cols_stripped_tab[0][1], str, 'def')  # type: ignore[index]
    assert cols_stripped_tab[1:2].content == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx']
    ]
    assert cols_stripped_tab[1:].to_data() == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx'], ['yz']
    ]


def test_split_lines_to_columns_no_strip_model(
    forward_list_of_texts_with_tabs: Annotated[list[Model[str]] | list[str], pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    SplitLinesToColumnsNoStripModel = SplitLinesToColumnsModel.adjust(
        'SplitLinesToColumnsNoStripModel', strip=False)

    cols_unstripped_tab = SplitLinesToColumnsNoStripModel(forward_list_of_texts_with_tabs)

    assert_model_if_dyn_conv_else_val(
        cols_unstripped_tab[0],  # type: ignore[index]
        list[str],
        ['abc', ' def ', 'ghi', ' jkl'])
    assert_model_if_dyn_conv_else_val(
        cols_unstripped_tab[0][1],  # type: ignore[index]
        str,
        ' def ')
    assert cols_unstripped_tab[1:2].content == [  # type: ignore[index]
        ['mno', ' pqr', 'stu', ' vwx']
    ]
    assert cols_unstripped_tab[1:].to_data() == [  # type: ignore[index]
        ['mno', ' pqr', 'stu', ' vwx'], ['yz']
    ]


def test_split_lines_to_columns_by_comma_model(
    forward_list_of_texts_with_comma: Annotated[list[Model[str]] | list[str], pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    cols_stripped_comma = SplitLinesToColumnsByCommaModel(forward_list_of_texts_with_comma)

    assert_model_if_dyn_conv_else_val(
        cols_stripped_comma[0],  # type: ignore[index]
        list[str],
        ['abc', 'def', 'ghi', 'jkl'])
    assert_model_if_dyn_conv_else_val(
        cols_stripped_comma[0][1],  # type: ignore[index]
        str,
        'def',
    )
    assert cols_stripped_comma[1:2].content == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx']
    ]
    assert cols_stripped_comma[1:].to_data() == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx'], ['yz']
    ]


def test_join_columns_to_lines_model(
        forward_list_of_lists_of_items: Annotated[list[list[str]], pytest.fixture]) -> None:
    joined_cols = JoinColumnsToLinesModel(forward_list_of_lists_of_items)  # type: ignore[index]

    assert joined_cols.content == ['mno\tpqr\tstu\tvwx', 'yz']
    assert joined_cols[1:].content == ['yz']  # type: ignore[index]
    assert joined_cols.to_data() == ['mno\tpqr\tstu\tvwx', 'yz']


def test_join_columns_to_lines_by_comma_models(
        forward_list_of_lists_of_items: Annotated[list[list[str]], pytest.fixture]) -> None:
    joined_cols_by_comma = JoinColumnsByCommaToLinesModel(forward_list_of_lists_of_items)

    assert joined_cols_by_comma.content == ['mno,pqr,stu,vwx', 'yz']
    assert joined_cols_by_comma[1:].content == ['yz']  # type: ignore[index]
    assert joined_cols_by_comma.to_data() == ['mno,pqr,stu,vwx', 'yz']


def test_join_columns_to_lines_by_comma_space_models(
        forward_list_of_lists_of_items: Annotated[list[list[str]], pytest.fixture]) -> None:
    JoinColumnsByCommaSpaceToLinesModel = JoinColumnsToLinesModel.adjust(
        'JoinColumnsByCommaToLinesModel', delimiter=', ')

    joined_cols_by_comma_space = JoinColumnsByCommaSpaceToLinesModel(forward_list_of_lists_of_items)

    assert joined_cols_by_comma_space.content == ['mno, pqr, stu, vwx', 'yz']
    assert joined_cols_by_comma_space[1:].content == ['yz']  # type: ignore[index]
    assert joined_cols_by_comma_space.to_data() == ['mno, pqr, stu, vwx', 'yz']


class PreSplitEnum(str, Enum):
    FALSE = 'False'
    LEVEL_1 = 'level_1'
    LEVEL_2 = 'level_2'
    MIXED_1_2 = 'mixed_1_2'
    LEVEL_3 = 'level_3'


SplittableDataType: TypeAlias = (str | list[str] | list[list[str]] | list[str | list[str]]
                                 | list[list[list[str]]] | Model[str] | Model[list[str]]
                                 | Model[list[list[str]]]
                                 | Model[list[str | list[str]]]) | Model[list[list[list[str]]]]

SplittableDataReturnType: TypeAlias = tuple[
    PreSplitEnum,
    str,
    SplittableDataType,
]


@pc.fixture(scope='function')
@pc.parametrize(
    pre_split=[
        PreSplitEnum.FALSE,
        PreSplitEnum.LEVEL_1,
        PreSplitEnum.LEVEL_2,
        PreSplitEnum.MIXED_1_2,
        PreSplitEnum.LEVEL_3,
    ],
    use_model=[False, True],
)
def splittable_data(
    pre_split: PreSplitEnum,
    use_model: bool,
) -> SplittableDataReturnType:
    """Return splittable data prepared at varying nesting levels."""
    raw_data = cast(str, 'abc=def&ghi=jkl&pqr=stu&xyz=123;x=1&y=2')  # type: ignore[redundant-cast]
    data: SplittableDataType

    if not pre_split == PreSplitEnum.FALSE:
        split_data = list(raw_data.split(';'))
        doubly_split_data = [item.split('&') for item in split_data]
        match (pre_split):
            case PreSplitEnum.LEVEL_1:
                data = Model[list[str]](split_data) if use_model else split_data
            case PreSplitEnum.LEVEL_2:
                data = Model[list[list[str]]](doubly_split_data) if use_model else doubly_split_data
            case PreSplitEnum.MIXED_1_2:
                mixed_split_data: list[str | list[str]] = [split_data[0].split('&'), split_data[1]]
                data = Model[list[str
                                  | list[str]]](mixed_split_data) if use_model else mixed_split_data
            case PreSplitEnum.LEVEL_3:
                triply_split_data = [[item.split('=') for item in x] for x in doubly_split_data]
                data = Model[list[list[list[str]]]](
                    triply_split_data) if use_model else triply_split_data
    else:
        data = Model[str](raw_data) if use_model else raw_data

    return pre_split, raw_data, data


def _assert_empty_model(model_cls: type[Model], default_value: object) -> None:
    """Assert that empty model variants produce the expected default value."""
    empty_model: Model
    for empty_model in [model_cls(), model_cls(''), model_cls([])]:
        assert empty_model.content == empty_model.to_data() == default_value


def test_nested_split_to_items_model_default(
        splittable_data: Annotated[SplittableDataReturnType, pc.fixture]) -> None:
    """Test default nested item splitting without explicit delimiters."""

    _assert_empty_model(NestedSplitToItemsModel, [])

    pre_split, raw_data, data = splittable_data

    if pre_split == PreSplitEnum.FALSE:
        default_no_split = NestedSplitToItemsModel(data)
        assert default_no_split.content == default_no_split.to_data() == [raw_data]

    elif pre_split == PreSplitEnum.LEVEL_1:
        with pytest.raises(ValidationError):
            NestedSplitToItemsModel(data)


def test_nested_split_to_items_model_one_level(
        splittable_data: Annotated[SplittableDataReturnType, pc.fixture]) -> None:
    """Test nested item splitting with one delimiter level."""

    pre_split, raw_data, data = splittable_data

    OneLevelNestedSplitToItemsModel = NestedSplitToItemsModel.adjust(
        'OneLevelNestedSplitToItemsModel',
        delimiters=(';',),
    )

    _assert_empty_model(OneLevelNestedSplitToItemsModel, [])

    if pre_split in [PreSplitEnum.FALSE, PreSplitEnum.LEVEL_1]:
        top_level_split = OneLevelNestedSplitToItemsModel(data)
        assert top_level_split.content == top_level_split.to_data() == [
            'abc=def&ghi=jkl&pqr=stu&xyz=123', 'x=1&y=2'
        ]
    else:
        with pytest.raises(ValidationError):
            OneLevelNestedSplitToItemsModel(data)


def test_nested_split_to_items_model_two_levels(
        splittable_data: Annotated[SplittableDataReturnType, pc.fixture]) -> None:
    """Test nested item splitting with two delimiter levels."""

    pre_split, raw_data, data = splittable_data

    TwoLevelNestedSplitToItemsModel = NestedSplitToItemsModel.adjust(
        'TwoLevelNestedSplitToItemsModel',
        delimiters=(';', '&'),
    )

    _assert_empty_model(TwoLevelNestedSplitToItemsModel, [])

    if pre_split != PreSplitEnum.LEVEL_3:
        two_level_split = TwoLevelNestedSplitToItemsModel(data)
        assert two_level_split.content == two_level_split.to_data() == [
            ['abc=def', 'ghi=jkl', 'pqr=stu', 'xyz=123'],
            ['x=1', 'y=2'],
        ]
    else:
        with pytest.raises(ValidationError):
            TwoLevelNestedSplitToItemsModel(data)


def test_nested_split_to_items_model_three_levels(
        splittable_data: Annotated[SplittableDataReturnType, pc.fixture]) -> None:
    """Test nested item splitting with three delimiter levels."""

    pre_split, raw_data, data = splittable_data

    ThreeLevelNestedSplitToItemsModel = NestedSplitToItemsModel.adjust(
        'TwoLevelNestedSplitToItemsModel',
        delimiters=(';', '&', '='),
    )

    _assert_empty_model(ThreeLevelNestedSplitToItemsModel, [])

    three_level_split = ThreeLevelNestedSplitToItemsModel(data)
    assert three_level_split.content == three_level_split.to_data() == [
        [['abc', 'def'], ['ghi', 'jkl'], ['pqr', 'stu'], ['xyz', '123']],
        [['x', '1'], ['y', '2']],
    ]


def test_nested_split_to_items_model_mixed_levels() -> None:
    VarSpecNestedSplitToItemsModel = NestedSplitToItemsModel.adjust(
        'VarSpecNestedSplitToItemsModel',
        delimiters=(';', '='),
    )

    with pytest.raises(ValidationError):
        VarSpecNestedSplitToItemsModel('a=1;b=2;c')
    with pytest.raises(ValidationError):
        VarSpecNestedSplitToItemsModel(['a=1', 'b=2', 'c'])
    with pytest.raises(ValidationError):
        VarSpecNestedSplitToItemsModel(['a=1', 'b=2', ['c']])

    assert VarSpecNestedSplitToItemsModel('a=1;b=2;c=3').to_data() == \
        [['a', '1'], ['b', '2'], ['c', '3']]
    assert VarSpecNestedSplitToItemsModel(['a=1', 'b=2', 'c=3']).to_data() == \
        [['a', '1'], ['b', '2'], ['c', '3']]
    assert VarSpecNestedSplitToItemsModel(['a=1', 'b=2', ['c', '3']]).to_data() == \
        [['a', '1'], ['b', '2'], ['c', '3']]


def test_nested_split_to_items_model_parse_to_str() -> None:
    ThreeLevelNestedSplitToItemsModel = NestedSplitToItemsModel.adjust(
        'ThreeLevelNestedSplitToItemsModel',
        delimiters=(';', '&', '='),
    )

    data = [
        [
            [1, 2.0],
            [2, 4.0],
        ],
        [[3, 6.0]],
    ]
    split_model = ThreeLevelNestedSplitToItemsModel(data)
    assert split_model.content == split_model.to_data() == [
        [
            ['1', '2.0'],
            ['2', '4.0'],
        ],
        [['3', '6.0']],
    ]


def test_nested_join_items_model_default(
        splittable_data: Annotated[SplittableDataReturnType, pc.fixture]) -> None:
    """Test default nested item joining without explicit delimiters."""

    _assert_empty_model(NestedJoinItemsModel, '')

    pre_split, raw_data, data = splittable_data

    if pre_split == PreSplitEnum.FALSE:
        default_no_join = NestedJoinItemsModel(data)
        assert default_no_join.content == default_no_join.to_data() == raw_data

    elif pre_split == PreSplitEnum.LEVEL_1:
        with pytest.raises(ValidationError):
            NestedJoinItemsModel(data)


def test_nested_join_items_model_one_level(
        splittable_data: Annotated[SplittableDataReturnType, pc.fixture]) -> None:
    """Test nested item joining with one delimiter level."""

    pre_split, raw_data, data = splittable_data

    OneLevelNestedJoinItemsModel = NestedJoinItemsModel.adjust(
        'OneLevelNestedJoinItemsModel',
        delimiters=(';',),
    )

    _assert_empty_model(OneLevelNestedJoinItemsModel, '')

    if pre_split in [PreSplitEnum.FALSE, PreSplitEnum.LEVEL_1]:
        top_level_join = OneLevelNestedJoinItemsModel(data)
        assert top_level_join.content == top_level_join.to_data() == raw_data
    else:
        with pytest.raises(ValidationError):
            OneLevelNestedJoinItemsModel(data)


def test_nested_join_items_model_two_levels(
        splittable_data: Annotated[SplittableDataReturnType, pc.fixture]) -> None:
    """Test nested item joining with two delimiter levels."""

    pre_split, raw_data, data = splittable_data

    TwoLevelNestedJoinItemsModel = NestedJoinItemsModel.adjust(
        'TwoLevelNestedJoinItemsModel',
        delimiters=(';', '&'),
    )

    _assert_empty_model(TwoLevelNestedJoinItemsModel, '')

    if pre_split != PreSplitEnum.LEVEL_3:
        two_level_join = TwoLevelNestedJoinItemsModel(data)
        assert two_level_join.content == two_level_join.to_data() == raw_data
    else:
        with pytest.raises(ValidationError):
            TwoLevelNestedJoinItemsModel(data)


def test_nested_join_items_model_three_levels(
        splittable_data: Annotated[SplittableDataReturnType, pc.fixture]) -> None:
    """Test nested item joining with three delimiter levels."""

    pre_split, raw_data, data = splittable_data

    ThreeLevelNestedJoinItemsModel = NestedJoinItemsModel.adjust(
        'TwoLevelNestedJoinItemsModel',
        delimiters=(';', '&', '='),
    )

    _assert_empty_model(ThreeLevelNestedJoinItemsModel, '')

    three_level_join = ThreeLevelNestedJoinItemsModel(data)
    assert three_level_join.content == three_level_join.to_data() == raw_data


def test_nested_join_items_model_mixed_levels() -> None:
    VarSpecNestedJoinItemsModel = NestedJoinItemsModel.adjust(
        'VarSpecNestedJoinItemsModel',
        delimiters=(';', '='),
    )

    with pytest.raises(ValidationError):
        VarSpecNestedJoinItemsModel('a=1;b=2;c')
    with pytest.raises(ValidationError):
        VarSpecNestedJoinItemsModel(['a=1', 'b=2', 'c'])
    with pytest.raises(ValidationError):
        VarSpecNestedJoinItemsModel([['a', '1'], ['b', '2'], ['c']])

    assert (VarSpecNestedJoinItemsModel(['a=1;b=2;c=3']).to_data() == 'a=1;b=2;c=3')
    assert (VarSpecNestedJoinItemsModel(['a=1', 'b=2', 'c=3']).to_data() == 'a=1;b=2;c=3')
    assert (VarSpecNestedJoinItemsModel([['a', '1'], ['b', 2], ['c',
                                                                '3']]).to_data() == 'a=1;b=2;c=3')


def test_nested_join_items_model_parse_to_str() -> None:
    ThreeLevelNestedJoinItemsModel = NestedJoinItemsModel.adjust(
        'ThreeLevelNestedJoinItemsModel',
        delimiters=(';', '&', '='),
    )

    data = [
        [
            [1, 2.0],
            [2, 4.0],
        ],
        [[3, 6.0]],
    ]
    joined_model = ThreeLevelNestedJoinItemsModel(data)
    assert joined_model.content == joined_model.to_data() == '1=2.0&2=4.0;3=6.0'


def test_match_items_model_default() -> None:
    data = ('abc', 123, 13.0)

    matched_model = MatchItemsModel(data)
    assert matched_model.content == matched_model.to_data() == ['abc', '123', '13.0']


def test_match_items_model_one_func() -> None:
    match_comments_func: Callable[[str], bool] = lambda x: x.startswith('#')

    data = ['# comment 1', 'line 1', '# comment 2', 'line 2']

    MatchCommentsModel = MatchItemsModel.adjust(
        'FilterCommentsModel', match_functions=(match_comments_func,), invert_matches=False)

    matched_model = MatchCommentsModel(data)
    assert matched_model.content == matched_model.to_data() == ['# comment 1', '# comment 2']

    FilterCommentsModel = MatchItemsModel.adjust(
        'FilterCommentsModel', match_functions=(match_comments_func,), invert_matches=True)

    filtered_model = FilterCommentsModel(data)
    assert filtered_model.content == filtered_model.to_data() == ['line 1', 'line 2']


def test_match_items_model_two_funcs() -> None:
    match_lowercase_func: Callable[[str], bool] = lambda x: x.islower()
    match_alphanum_func: Callable[[str], bool] = lambda x: x.isalnum()

    data = ['abc123', 'ABC123', 'xyz-123', 'XYZ-123']

    MatchLowerCaseAndAlphaNumModel = MatchItemsModel.adjust(
        'FilterCommentsModel',
        match_functions=(match_lowercase_func, match_alphanum_func),
        invert_matches=False,
        match_all=True)

    matched_model = MatchLowerCaseAndAlphaNumModel(data)
    assert matched_model.content == matched_model.to_data() == ['abc123']

    MatchLowerCaseOrAlphaNumModel = MatchItemsModel.adjust(
        'FilterCommentsModel',
        match_functions=(match_lowercase_func, match_alphanum_func),
        invert_matches=False,
        match_all=False)

    matched_model = MatchLowerCaseOrAlphaNumModel(data)
    assert matched_model.content == matched_model.to_data() == ['abc123', 'ABC123', 'xyz-123']

    FilterLowerCaseAndAlphaNumModel = MatchItemsModel.adjust(
        'FilterCommentsModel',
        match_functions=(match_lowercase_func, match_alphanum_func),
        invert_matches=True,
        match_all=True)

    matched_model = FilterLowerCaseAndAlphaNumModel(data)
    assert matched_model.content == matched_model.to_data() == ['ABC123', 'xyz-123', 'XYZ-123']

    FilterLowerCaseOrAlphaNumModel = MatchItemsModel.adjust(
        'FilterCommentsModel',
        match_functions=(match_lowercase_func, match_alphanum_func),
        invert_matches=True,
        match_all=False)

    matched_model = FilterLowerCaseOrAlphaNumModel(data)
    assert matched_model.content == matched_model.to_data() == ['XYZ-123']
