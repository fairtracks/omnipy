from enum import Enum
import os
from textwrap import dedent
from typing import Annotated, Callable, Iterator, TypeAlias

import pytest
import pytest_cases as pc

from omnipy.components.raw.models import (BytesModel,
                                          JoinColumnsToLinesModel,
                                          JoinItemsModel,
                                          JoinLinesModel,
                                          MatchItemsModel,
                                          NestedJoinItemsModel,
                                          NestedSplitToItemsModel,
                                          SplitLinesToColumnsModel,
                                          SplitToItemsModel,
                                          SplitToLinesModel,
                                          StrictBytesModel,
                                          StrictStrModel,
                                          StrModel)
from omnipy.data.model import Model
from omnipy.util._pydantic import ValidationError

from ...helpers.protocols import AssertModelOrValFunc


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
    assert last_lines[0:2].content == [
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know'
    ]
    assert_model_if_dyn_conv_else_val(last_lines[-1],
                                      str,
                                      'now, to mock your own grinning? quite chap-fallen.')

    joined_lines = JoinLinesModel(last_lines[0:2])
    assert joined_lines.content == dedent("""\
        abhorred in my imagination it is! my gorge rises at
        it. Here hung those lips that I have kissed I know""")
    assert joined_lines[:joined_lines.index(' ')].content == 'abhorred'  # type: ignore[index]

    assert JoinLinesModel(SplitToLinesModel(data)).content == '\n'.join(
        [line.strip() for line in data.strip().split('\n')])  # type: ignore[attr-defined]

    assert JoinLinesModel(SplitToLinesNoStripModel(data)).content == raw_data

    JoinLinesByOsLinesepModel = JoinLinesModel.adjust(
        'JoinLinesByOsLinesepModel', delimiter=os.linesep)

    os_linesep_joined_lines = JoinLinesByOsLinesepModel(last_lines[0:2])
    assert os_linesep_joined_lines.content == os.linesep.join([
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
    assert items_stripped_comma.content == ['abc', 'def', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_stripped_comma[1], str, 'def')  # type: ignore[index]
    assert items_stripped_comma[-2:].content == ['ghi', 'jkl']  # type: ignore[index]

    SplitToItemsNoStripModel = SplitToItemsModel.adjust('SplitToItemsNoStripModel', strip=False)

    items_unstripped_tab = SplitToItemsNoStripModel(data_comma)
    assert items_unstripped_tab.content == ['abc', ' def ', 'ghi', 'jkl']
    assert_model_if_dyn_conv_else_val(items_unstripped_tab[1], str, ' def ')  # type: ignore[index]
    assert items_unstripped_tab[-2:].content == ['ghi', 'jkl']  # type: ignore[index]

    raw_data_tab = 'abc\t def \tghi\tjkl'

    data_tab = Model[str](raw_data_tab) if use_str_model else raw_data_tab

    SplitToItemsByTabModel = SplitToItemsModel.adjust('SplitToItemsByTabModel', delimiter='\t')

    items_stripped_tab = SplitToItemsByTabModel(data_tab)
    assert items_stripped_tab.content == ['abc', 'def', 'ghi', 'jkl']

    assert_model_if_dyn_conv_else_val(items_stripped_tab[1], str, 'def')  # type: ignore[index]
    assert items_stripped_tab[-2:].content == ['ghi', 'jkl']  # type: ignore[index]

    comma_space_joined_items = JoinItemsModel(items_stripped_comma[1:3])  # type: ignore[index]
    assert comma_space_joined_items.content == 'def,ghi'
    assert comma_space_joined_items[1:-1].content == 'ef,gh'  # type: ignore[index]

    JoinItemsByCommaSpaceModel = JoinItemsModel.adjust('JoinItemsByCommaSpaceModel', delimiter=', ')

    comma_space_joined_items = JoinItemsByCommaSpaceModel(
        items_stripped_tab[1:3])  # type: ignore[index]
    assert comma_space_joined_items.content == 'def, ghi'
    assert comma_space_joined_items[1:-1].content == 'ef, gh'  # type: ignore[index]


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
    assert cols_stripped_tab[1:2].content == [  # type: ignore[index]
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
    assert cols_unstripped_tab[1:2].content == [  # type: ignore[index]
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
    assert cols_stripped_comma[1:2].content == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx']
    ]
    assert cols_stripped_comma[1:].to_data() == [  # type: ignore[index]
        ['mno', 'pqr', 'stu', 'vwx'], ['yz']
    ]

    joined_cols = JoinColumnsToLinesModel(cols_stripped_tab[1:])  # type: ignore[index]

    assert joined_cols.content == ['mno\tpqr\tstu\tvwx', 'yz']
    assert joined_cols[1:].content == ['yz']  # type: ignore[index]
    assert joined_cols.to_data() == ['mno\tpqr\tstu\tvwx', 'yz']

    JoinColumnsByCommaToLinesModel = JoinColumnsToLinesModel.adjust(
        'JoinColumnsByCommaToLinesModel', delimiter=', ')

    joined_cols_by_comma = JoinColumnsByCommaToLinesModel(
        cols_stripped_comma[1:])  # type: ignore[index]
    assert joined_cols_by_comma.content == ['mno, pqr, stu, vwx', 'yz']
    assert joined_cols_by_comma[1:].content == ['yz']  # type: ignore[index]
    assert joined_cols_by_comma.to_data() == ['mno, pqr, stu, vwx', 'yz']


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
    raw_data = 'abc=def&ghi=jkl&pqr=stu&xyz=123;x=1&y=2'
    data: SplittableDataType

    if not pre_split == PreSplitEnum.FALSE:
        split_data = raw_data.split(';')
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
    empty_model: Model
    for empty_model in [model_cls(), model_cls(''), model_cls([])]:
        assert empty_model.content == empty_model.to_data() == default_value


def test_nested_split_to_items_model_default(
        splittable_data: Annotated[SplittableDataReturnType, pc.fixture]) -> None:

    _assert_empty_model(NestedSplitToItemsModel, '')

    pre_split, raw_data, data = splittable_data

    if pre_split == PreSplitEnum.FALSE:
        default_no_split = NestedSplitToItemsModel(data)
        assert default_no_split.content == default_no_split.to_data() == raw_data

    elif pre_split == PreSplitEnum.LEVEL_1:
        with pytest.raises(ValidationError):
            NestedSplitToItemsModel(data)


def test_nested_split_to_items_model_one_level(
        splittable_data: Annotated[SplittableDataReturnType, pc.fixture]) -> None:

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
