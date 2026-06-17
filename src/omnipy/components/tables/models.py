from abc import abstractmethod
from collections import defaultdict
from collections.abc import Generator, Iterator, Mapping
from copy import copy
import functools
from typing import Callable, cast, Generic, get_args, overload, Protocol, Sized, TypeAlias

from typing_extensions import NamedTuple, override, Self, TypeVar

from omnipy.data.helpers import MethodInfo, TypeVarStore
from omnipy.data.model import (is_model_instance,
                               is_pure_pydantic_model,
                               Model,
                               ModelMetaclass,
                               prepare_value_for_validation_if_dataset_or_model)
from omnipy.shared.exceptions import AssumedToBeImplementedException
from omnipy.shared.protocols.content import (IsConcatenableItemSequenceLikeColumnContent,
                                             IsConcatenableItemSequenceLikeContent,
                                             IsDictOfConcatenableItemSequenceLikeColumnContent,
                                             IsDictOfDictsContent,
                                             IsListContent,
                                             IsListOfDictsContent,
                                             IsListOfListsContent,
                                             SupportsKeysAndGetItem)
from omnipy.shared.protocols.data import HasContent
from omnipy.shared.protocols.stdlib_ext import IsItemSequenceLike
from omnipy.shared.protocols.typing import IsMapping
from omnipy.shared.typing import TYPE_CHECKING
from omnipy.util.helpers import all_type_variants, ensure_plain_type, first_key_in_mapping, is_union
from omnipy.util.pydantic import ValidationError
import omnipy.util.pydantic as pyd

from ..general.models import Chain3
from ..json.typedefs import JsonDictOfScalars, JsonListOfScalars, JsonScalar
from ..raw.models import (SplitLinesToColumnsByCommaModel,
                          SplitLinesToColumnsModel,
                          SplitToLinesModel)

if TYPE_CHECKING:
    from omnipy.data._typing.mimic_models import PlainModel

_ColumnT = TypeVar('_ColumnT', bound=IsItemSequenceLike)
_ItemT = TypeVar('_ItemT')
_ColModelT = TypeVar(
    '_ColModelT',
    bound='ColumnModel',
    default='JsonScalarColumnModel',
)
_ColModelItemT = TypeVar(
    '_ColModelItemT',
    default='JsonScalar',
)
_ColWiseTableModelT = TypeVar(
    '_ColWiseTableModelT', default='JsonScalarColumnWiseTableWithColNamesModel')
_ConcatColumnModelT = TypeVar(
    '_ConcatColumnModelT', bound=IsConcatenableItemSequenceLikeColumnContent)

if TYPE_CHECKING:  # noqa: C901

    class ConcatByAddArrayAdapterModel(
            PlainModel[_ColumnT],
            IsConcatenableItemSequenceLikeContent[_ItemT],
            Generic[_ColumnT, _ItemT],
    ):
        _allowed_special_methods = frozenset()

        @staticmethod
        def _as_item_list(values: _ColumnT) -> list[_ItemT]:
            ...

        @classmethod
        def _concat_column_values(cls, left: _ColumnT, right: _ColumnT) -> _ColumnT:
            ...

else:

    class ConcatByAddArrayAdapterModel(Model[_ColumnT | IsItemSequenceLike[_ItemT]
                                             | Generator[_ItemT]],
                                       Generic[_ColumnT, _ItemT]):
        _allowed_special_methods = frozenset({
            '__len__',
            '__length_hint__',
            '__getitem__',
            '__setitem__',
            '__delitem__',
            '__iter__',
            '__reversed__',
            '__contains__',
            '__copy__',
            '__deepcopy__',
            '__str__',
            '__format__',
        })

        @classmethod
        def _get_special_methods_info_dict(cls) -> dict[str, MethodInfo]:
            special_methods = super()._get_special_methods_info_dict()
            return {
                method_name: special_methods[method_name]
                for method_name in cls._allowed_special_methods
                if method_name in special_methods
            }

        @staticmethod
        def _as_item_list(values: _ColumnT) -> list[_ItemT]:
            return list(values)

        @classmethod
        def _concat_column_values(cls, left: _ColumnT, right: _ColumnT) -> _ColumnT:
            print(f'{cls.__name__}: default concat fallback via list conversion')
            return cls(cls._as_item_list(left) + cls._as_item_list(right)).content

        def __add__(self, other: object):
            other_content = self.__class__(other).content
            return self.__class__(self._concat_column_values(self.content, other_content))

        @classmethod
        @functools.cache
        def _get_column_cls(cls) -> type[_ColModelT]:
            type_variant = all_type_variants(cls.outer_type(with_args=True))
            assert len(type_variant) == 3, ('Expected exactly 3 type variants '
                                            'in ConcatByAddArrayAdapterModel type')
            return type_variant[0]

        @classmethod
        def _parse_data(
                cls, data: _ColumnT | IsItemSequenceLike[_ItemT] | Generator[_ItemT]) -> _ColumnT:
            column_cls = cls._get_column_cls()
            if isinstance(data, column_cls):
                return data
            else:
                return column_cls(list(data))


if TYPE_CHECKING:  # noqa: C901

    class ColumnModel(
            PlainModel[_ColumnT],
            IsConcatenableItemSequenceLikeColumnContent[_ItemT],
            Generic[_ColumnT, _ItemT],
    ):
        @classmethod
        def default_value(cls) -> _ItemT:
            raise AssumedToBeImplementedException

        @classmethod
        def filled(cls, value: _ItemT, length: int) -> Self:
            raise AssumedToBeImplementedException

else:

    class ColumnModel(Model[_ColumnT], Generic[_ColumnT, _ItemT]):
        @classmethod
        @functools.cache
        def default_value(cls) -> _ItemT:
            _TYPE_DEFAULT_ORDER = (None, float, int, str, list, dict, set)

            if not cls.is_nested_type():
                raise TypeError('ColumnModel type must be nested, with explicit inner '
                                'type. Current type: ' + str(cls.full_type()))

            inner_type = cls.inner_type(with_args=True)

            if is_union(inner_type):
                union_type = tuple(ensure_plain_type(_) for _ in get_args(inner_type))

                for _type in _TYPE_DEFAULT_ORDER:
                    if _type is None and any(pyd.is_none_type(_) for _ in union_type):
                        return None
                    elif _type in union_type:
                        if _type is float:
                            return float('nan')
                        else:
                            return _type()
            else:
                try:
                    return inner_type()
                except Exception as e:
                    raise TypeError(f'Unsupported type: {inner_type}') from e

            raise TypeError(f'Unsupported type: {inner_type}')

        @classmethod
        def filled(cls, value: _ItemT, length: int) -> Self:
            return cls(value for _ in range(length))


class JsonScalarColumnModel(ColumnModel[list[JsonScalar], JsonScalar]):
    ...


JsonMaxLevel1Types: TypeAlias = JsonScalar | JsonDictOfScalars | JsonListOfScalars

JsonMaxLevel2Types: TypeAlias = (
    JsonScalar | list[JsonScalar | JsonDictOfScalars | JsonListOfScalars]
    | dict[str, JsonScalar | JsonDictOfScalars | JsonListOfScalars])


class JsonMaxLevel1ColumnModel(ColumnModel[list[JsonMaxLevel1Types], JsonMaxLevel1Types]):
    ...


class JsonMaxLevel2ColumnModel(ColumnModel[list[JsonMaxLevel2Types], JsonMaxLevel2Types]):
    ...


class IterRow(Mapping[str, _ColModelT], Generic[_ColModelT, _ColModelItemT]):
    def __init__(
        self,
        content: Mapping[str, _ColModelT | IsItemSequenceLike[_ColModelItemT]],
    ) -> None:
        self._content = {
            key: value.content if is_model_instance(value) else value
            for key, value in content.items()
        }
        self.row_number: int = -1

    @override
    def __getitem__(self, key) -> _ColModelItemT:  # type: ignore[override]
        if key not in self._content:
            raise KeyError(f'Key {key} is not a column name')
        if self.row_number == -1:
            raise KeyError('Row number not set')
        return self._content[key][self.row_number]

    @override
    def __iter__(self) -> Iterator[str]:
        return iter(self._content)

    def __len__(self) -> int:
        return len(self._content)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, IterRow):
            return self._content == other._content and self.row_number == other.row_number
        return False

    def __str__(self) -> str:
        arg_str = ', '.join(f'{repr(key)}: {repr(self[key])}' for key in self._content.keys())
        return f'{self.__class__.__name__}({arg_str})'


class PrintableTable:
    ...


# TODO: Make RowWiseTable (and family) generic

if TYPE_CHECKING:

    class RowWiseTableModel(
            PlainModel[list[list[JsonScalar]]],
            IsListOfListsContent[list[JsonScalar], JsonScalar],
    ):
        ...

else:

    class RowWiseTableModel(Model[list[list[JsonScalar]]]):
        ...


class _RowWiseColNamesMixin:
    @property
    def col_names(self) -> tuple[str, ...]:
        """
        The column names in the table, in the order they first appear in the rows.
        """
        col_names = {}
        for row in self:  # type: ignore[attr-defined]
            col_names.update(dict.fromkeys(row.keys()))
        return tuple(col_names.keys())


class _RowWiseTableWithColNamesModel(
        Model['list[dict[str, JsonScalar]] | ColumnWiseTableWithColNamesNoConvertModel']):
    @classmethod
    def _parse_data(
        cls, data: 'list[dict[str, JsonScalar]] | ColumnWiseTableWithColNamesNoConvertModel'
    ) -> list[dict[str, JsonScalar]]:
        if isinstance(data, ColumnWiseTableWithColNamesNoConvertModel):
            # Convert column-wise to row-wise
            converted_data: list[dict[str, JsonScalar]] = []
            for col_name, col_values in data.content.items():
                for i, value in enumerate(col_values):
                    if i >= len(converted_data):
                        converted_data.append({})
                    converted_data[i][col_name] = value
            return converted_data
        else:
            return data


if TYPE_CHECKING:

    class RowWiseTableWithColNamesModel(
            _RowWiseColNamesMixin,
            PlainModel[list[dict[str, JsonScalar]]],
            IsListOfDictsContent[IsMapping[str, JsonScalar], str, JsonScalar],
            PrintableTable,
    ):
        ...
else:

    class RowWiseTableWithColNamesModel(
            _RowWiseColNamesMixin,
            _RowWiseTableWithColNamesModel,
            PrintableTable,
    ):
        ...


class RowWiseTableWithColNamesNoConvertModel(Model[list[dict[str, JsonScalar]]]):
    ...


if TYPE_CHECKING:

    class ColumnWiseTableWithColNamesAndIndexModel(
            PlainModel[dict[str, Mapping[str, JsonScalar]]],
            IsDictOfDictsContent[str, IsMapping[str, JsonScalar], str, JsonScalar],
    ):
        ...
else:

    class ColumnWiseTableWithColNamesAndIndexModel(Model[dict[str, Mapping[str, JsonScalar]]]):
        ...


class _IsColumnWiseTableWithColNames(HasContent,
                                     Sized,
                                     SupportsKeysAndGetItem,
                                     Protocol[_ColModelT, _ColModelItemT]):
    @property
    def _content(self) -> Mapping[str, _ColModelT]:
        ...

    def _get_iter_row(self) -> IterRow[_ColModelT, _ColModelItemT]:
        ...

    def _common_add(
        self,
        other: '_IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT] | ColWiseAddOtherType',
        reverse: bool,
    ) -> 'ColumnWiseTableWithColNamesModel[_ColModelT, _ColModelItemT]':
        ...


class _ColumnWiseTableWithColNamesMixin(Generic[_ColModelT, _ColModelItemT]):
    @property
    def col_names(
            self: _IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT]) -> tuple[str, ...]:
        """
        The column names in the table, in the order they first appear in the rows.
        """
        return tuple(self.keys())

    @property
    def _content(
        self: _IsColumnWiseTableWithColNames[_ColModelT,
                                             _ColModelItemT]) -> Mapping[str, _ColModelT]:
        return cast(Mapping[str, _ColModelT], self.content)

    def __len__(self: _IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT]) -> int:
        try:
            first_key = first_key_in_mapping(self._content)
            return len(self._content[first_key])
        except KeyError:
            return 0

    def __contains__(self: _IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT],
                     item: str) -> bool:
        return item in self._content

    def _get_iter_row(
        self: _IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT]
    ) -> IterRow[_ColModelT, _ColModelItemT]:

        return IterRow[_ColModelT, _ColModelItemT](self._content)

    def __iter__(
        self: _IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT]
    ) -> Iterator[IterRow[_ColModelT, _ColModelItemT]]:
        _iter_row = self._get_iter_row()

        for i in range(len(self)):
            _iter_row.row_number = i
            yield _iter_row

    @overload
    def __getitem__(self: _IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT],
                    item: str) -> _ColModelT:
        ...

    @overload
    def __getitem__(self: _IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT],
                    item: int) -> IterRow[_ColModelT, _ColModelItemT]:
        ...

    def __getitem__(self: _IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT],
                    item: str | int) -> _ColModelT | IterRow[_ColModelT, _ColModelItemT]:
        if isinstance(item, str):
            return self._content[item]

        if item >= len(self) or item < -len(self):
            raise IndexError('Row index out of range')
        _iter_row = IterRow[_ColModelT, _ColModelItemT](self._content)
        _iter_row.row_number = item
        return _iter_row

    def _common_add(
        self: _IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT],
        other: '_IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT] | ColWiseAddOtherType',
        reverse: bool,
    ) -> 'ColumnWiseTableWithColNamesModel[_ColModelT, _ColModelItemT]':
        self_model = cast(
            type[ColumnWiseTableWithColNamesModel[_ColModelT, _ColModelItemT]],
            self.__class__,
        )

        if isinstance(other, ColumnWiseTableWithColNamesModel):
            _other = cast(ColumnWiseTableWithColNamesModel[_ColModelT, _ColModelItemT], other)
        else:
            _other = self_model(other)

        def _concat_self_and_other(
            self_value: _ColModelT,
            value: _ColModelT,
            reverse: bool,
        ) -> _ColModelT:
            return value + self_value if reverse else self_value + value

        new_content = dict(self._content)
        other_content = _other.content

        for key, value in other_content.items():
            if key in new_content:
                self_value: _ColModelT = copy(new_content[key])
            else:
                self_value = value.filled(value.default_value(), len(self))
            new_content[key] = _concat_self_and_other(self_value, value, reverse)

        for missing_key in new_content.keys() - other_content.keys():
            new_content[missing_key] = _concat_self_and_other(
                copy(new_content[missing_key]),
                new_content[missing_key].filled(
                    new_content[missing_key].default_value(),
                    len(_other),
                ),
                reverse,
            )

        return self_model(new_content)

    def __add__(
        self: _IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT],
        other: '_IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT] | ColWiseAddOtherType',
    ) -> 'ColumnWiseTableWithColNamesModel[_ColModelT, _ColModelItemT]':
        return self._common_add(other, reverse=False)

    def __radd__(
        self: _IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT],
        other: '_IsColumnWiseTableWithColNames[_ColModelT, _ColModelItemT] | ColWiseAddOtherType',
    ) -> 'ColumnWiseTableWithColNamesModel[_ColModelT, _ColModelItemT]':
        return self._common_add(other, reverse=True)


class _ColumnWiseTableWithColNamesModel(
        Model[dict[str, _ColModelT]
              | RowWiseTableWithColNamesNoConvertModel],
        Generic[_ColModelT, _ColModelItemT],
):
    @classmethod
    @functools.cache
    def _get_column_model_cls(cls) -> type[_ColModelT]:
        type_variant = all_type_variants(cls.outer_type(with_args=True))
        for _type in type_variant:
            if ensure_plain_type(_type) is dict:
                key_type, val_type = get_args(_type)
                assert key_type is str
                return cast(type[_ColModelT], val_type)
        raise TypeError(f'No ColumnModel found in: {cls}')

    @classmethod
    def _parse_data(
        cls, data: 'dict[str, _ColModelT] | RowWiseTableWithColNamesNoConvertModel'
    ) -> dict[str, _ColModelT]:
        column_model_cls = cls._get_column_model_cls()

        if isinstance(data, RowWiseTableWithColNamesNoConvertModel):
            row_wise_data = cast(list[dict[str, JsonScalar]], data)
            # Convert row-wise to column-wise
            column_wise_data: defaultdict[str, _ColModelT] = defaultdict(column_model_cls)
            column_wise_list_data: defaultdict[str, list[_ColModelItemT]] = defaultdict(list)

            row: dict[str, JsonScalar]
            for i, row in enumerate(row_wise_data):
                for col_name, value in row.items():
                    if col_name not in column_wise_data:
                        # New column, need to create new list and pad previous rows with default val
                        column_wise_data[col_name] = column_model_cls.filled(
                            column_model_cls.default_value(),
                            i,
                        )
                    column_wise_list_data[col_name].append(value)
                for col_name_not_in_row in column_wise_data.keys() - row.keys():
                    # Pad missing columns with default val
                    column_wise_list_data[col_name_not_in_row].append(
                        column_model_cls.default_value())

            for col_name, col_list in column_wise_list_data.items():
                column_wise_data[col_name] += col_list

            # That dict is not covariant in the value type is no problem
            # here as the dict is temporary and vil not change after this
            return cast(dict[str, _ColModelT], column_wise_data)
        else:
            return data


if TYPE_CHECKING:

    class ColumnWiseTableWithColNamesModel(  # type: ignore[misc]
            _ColumnWiseTableWithColNamesMixin[_ColModelT, _ColModelItemT],
            PlainModel[dict[str, _ColModelT]],
            IsDictOfConcatenableItemSequenceLikeColumnContent[_ColModelT, _ColModelItemT],
            PrintableTable,
            Generic[_ColModelT, _ColModelItemT],
    ):
        ...

else:

    class ColumnWiseTableWithColNamesModel(
            _ColumnWiseTableWithColNamesMixin[_ColModelT, _ColModelItemT],
            _ColumnWiseTableWithColNamesModel[_ColModelT, _ColModelItemT],
            PrintableTable,
            Generic[_ColModelT, _ColModelItemT],
    ):
        ...


class JsonScalarColumnWiseTableWithColNamesModel(ColumnWiseTableWithColNamesModel[
        JsonScalarColumnModel,
        JsonScalar,
]):
    ...


class JsonMaxLevel1ColumnWiseTableWithColNamesModel(ColumnWiseTableWithColNamesModel[
        JsonMaxLevel1ColumnModel,
        JsonMaxLevel1Types,
]):
    ...


class JsonMaxLevel2ColumnWiseTableWithColNamesModel(ColumnWiseTableWithColNamesModel[
        JsonMaxLevel2ColumnModel,
        JsonMaxLevel2Types,
]):
    ...


ColWiseAddOtherType: TypeAlias = (
    RowWiseTableWithColNamesModel
    | IsItemSequenceLike[IsMapping[str, JsonScalar]]
    | Generator[IsMapping[str, JsonScalar]]
    | IsMapping[str, IsItemSequenceLike[JsonScalar] | Generator[JsonScalar]])


class ColumnWiseTableWithColNamesNoConvertModel(Model[dict[str, JsonScalarColumnModel]]):
    ...


RowWiseTableWithColNamesModel.update_forward_refs()


class _RowWiseTableFirstRowAsColNamesModel(Model[list[dict[str, JsonScalar]] | RowWiseTableModel]):
    @classmethod
    def _parse_data(
            cls,
            data: list[dict[str, JsonScalar]] | RowWiseTableModel) -> list[dict[str, JsonScalar]]:
        if isinstance(data, RowWiseTableModel):
            data_list_of_lists = data.content

            if len(data_list_of_lists) > 0:
                first_row_as_colnames = Model[list[str]](data_list_of_lists[0]).content

                return cls._convert_list_of_lists_to_list_of_dicts(data_list_of_lists,
                                                                   first_row_as_colnames)
            else:
                return []
        else:
            return data

    @classmethod
    def _convert_list_of_lists_to_list_of_dicts(
        cls,
        data: list[list[JsonScalar]],
        first_row_as_colnames: list[str],
    ) -> list[dict[str, JsonScalar]]:
        # TODO: Fix auto-formatting. Current setting is relatively ugly many places
        return [
            {
                col_name: (row[i] if i < len(row) else None)
                for (i, col_name) in enumerate(first_row_as_colnames)
            }
            for (j, row) in enumerate(data)  # noqa: E126
            if j > 0
        ]


if TYPE_CHECKING:

    class RowWiseTableFirstRowAsColNamesModel(
            _RowWiseColNamesMixin,
            PlainModel[list[dict[str, JsonScalar]]],
            IsListOfDictsContent[IsMapping[str, JsonScalar], str, JsonScalar],
            PrintableTable,
    ):
        ...

else:

    class RowWiseTableFirstRowAsColNamesModel(
            _RowWiseColNamesMixin,
            _RowWiseTableFirstRowAsColNamesModel,
            PrintableTable,
    ):
        ...


_PydBaseModelT = TypeVar('_PydBaseModelT', bound=pyd.BaseModel)
_DataWithColNamesModelT = TypeVar('_DataWithColNamesModelT', bound=IsMapping)
_DataWithoutColNamesModelT = TypeVar('_DataWithoutColNamesModelT', bound=IsItemSequenceLike)
_PydRecordT = TypeVar('_PydRecordT', bound=pyd.BaseModel)


class _HeaderInfo(NamedTuple, Generic[_PydBaseModelT, _DataWithoutColNamesModelT]):
    pydantic_model: type[_PydBaseModelT]
    data_with_col_names_type: type[_DataWithoutColNamesModelT]
    header_names: tuple[str, ...]
    num_required_fields: int


class PydanticRecordModelMetaclass(ModelMetaclass):
    def __init__(cls, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        cls._header_info: _HeaderInfo | None = None

    @property
    def header_info(cls) -> _HeaderInfo:
        if cls._header_info is None:
            type_args = get_args(cast(type[Model], cls).outer_type(with_args=True))
            type_var_store = type_args[0]
            pydantic_model = get_args(type_var_store)[0]
            if hasattr(pydantic_model, '__pydantic_model__'):
                pydantic_model = pydantic_model.__pydantic_model__

            data_with_col_names_type = type_args[1]
            headers = pydantic_model.__fields__

            num_required_fields = -1
            for i, header_field in enumerate(headers.values()):
                if not header_field.required:
                    if num_required_fields == -1:
                        num_required_fields = i
                    continue
                elif num_required_fields != -1 and i > num_required_fields:
                    raise ValueError('Required fields must not come after optional fields')

            if num_required_fields == -1:
                num_required_fields = len(headers)

            cls._header_info = _HeaderInfo(
                pydantic_model,
                data_with_col_names_type,
                tuple(headers.keys()),
                num_required_fields,
            )
        return cls._header_info


class PydanticRecordModelBase(
        Model[TypeVarStore[_PydBaseModelT] | _DataWithColNamesModelT | _DataWithoutColNamesModelT],
        Generic[_PydBaseModelT, _DataWithColNamesModelT, _DataWithoutColNamesModelT],
        metaclass=PydanticRecordModelMetaclass,
):
    @classmethod
    @abstractmethod
    def _validate_record_model_with_col_names(
        cls,
        pyd_model: type[pyd.BaseModel],
        data: _DataWithColNamesModelT,
        header_names: tuple[str, ...],
    ) -> pyd.BaseModel | _DataWithColNamesModelT:
        ...

    @classmethod
    @abstractmethod
    def _validate_record_model_without_col_names(
        cls,
        pyd_model: type[pyd.BaseModel],
        data: _DataWithoutColNamesModelT,
        output_type: type[_DataWithColNamesModelT],
        header_names: tuple[str, ...],
    ) -> pyd.BaseModel | _DataWithColNamesModelT:
        ...

    @override
    @classmethod
    def _parse_data(  # type: ignore[override]
        cls,
        data: _DataWithColNamesModelT | _DataWithoutColNamesModelT,
    ) -> pyd.BaseModel | _DataWithColNamesModelT:
        pyd_model, data_with_col_names_type, header_names, num_required_fields = cls.header_info
        content = data.content if is_model_instance(data) else data
        if isinstance(content, dict) or is_pure_pydantic_model(content):
            # cls._validate_and_set_value(data)
            data_with_col_names = cast(_DataWithColNamesModelT, data)
            return cls._validate_record_model_with_col_names(
                pyd_model,
                data_with_col_names,
                header_names,
            )

        if isinstance(content, list):
            if isinstance(data, RowWiseTableModel):
                num_data_cols = len(content[0]) if len(content) > 0 else 0
            else:
                num_data_cols = len(content)

            assert len(header_names) >= num_data_cols >= num_required_fields, \
                (f'Incorrect number of data elements: '
                 f'{len(header_names)} >= {num_data_cols} >= {num_required_fields}')

            data_without_col_names = cast(_DataWithoutColNamesModelT, data)
            return cls._validate_record_model_without_col_names(
                pyd_model,
                data_without_col_names,
                data_with_col_names_type,
                header_names,
            )
        else:
            raise TypeError(f'Unsupported data type: {type(data)}')


if TYPE_CHECKING:

    class PydanticRecordModel(
            Model[_PydBaseModelT],
            Generic[_PydBaseModelT],
    ):
        ...

else:

    class PydanticRecordModel(
            PydanticRecordModelBase[
                _PydBaseModelT,
                dict[str, JsonScalar],
                list[JsonScalar],
            ],
            Generic[_PydBaseModelT],
    ):
        @override
        @classmethod
        def _validate_record_model_with_col_names(
            cls,
            pyd_model: type[pyd.BaseModel],
            data: dict[str, JsonScalar],
            header_names: tuple[str, ...],
        ) -> pyd.BaseModel | dict[str, JsonScalar]:
            return pyd_model(**data)

        @override
        @classmethod
        def _validate_record_model_without_col_names(
            cls,
            pyd_model: type[pyd.BaseModel],
            data: list[JsonScalar],
            data_type: type[_DataWithColNamesModelT],
            header_names: tuple[str, ...],
        ) -> pyd.BaseModel | dict[str, JsonScalar]:
            return pyd_model(**dict(zip(header_names, data)))


if TYPE_CHECKING:  # noqa: C901

    class IteratingPydanticRecordsModel(
            _ColumnWiseTableWithColNamesMixin,
            PlainModel[_ColWiseTableModelT],
            IsDictOfConcatenableItemSequenceLikeColumnContent[_ColModelT, _ColModelItemT],
            PrintableTable,
            Generic[_PydBaseModelT, _ColWiseTableModelT, _ColModelT, _ColModelItemT],
    ):
        ...

else:

    class IteratingPydanticRecordsModel(
            _ColumnWiseTableWithColNamesMixin,
            PydanticRecordModelBase[
                _PydBaseModelT,
                _ColWiseTableModelT,
                RowWiseTableModel,
            ],
            PrintableTable,
            Generic[_PydBaseModelT, _ColWiseTableModelT, _ColModelT, _ColModelItemT],
    ):
        @classmethod
        def _validate_over_all_rows(
            cls,
            input_model: ColumnWiseTableWithColNamesModel | RowWiseTableModel,
            output_model: ColumnWiseTableWithColNamesModel,
            pyd_model: type[pyd.BaseModel],
            to_row_dict_func: Callable[[_ColModelT], dict[str, JsonScalar]] | None = None,
        ):
            new_cols = set()

            def _init_col(
                content: dict[str, _ColModelT],
                pyd_model: type[pyd.BaseModel],
                key: str,
            ) -> None:
                if key in new_cols:
                    return

                col_len: int = len(input_model)
                # if key not in content:
                content[key] = [pyd_model.__fields__[key].get_default()] * col_len
                # else:
                #     assert len(content[key]) == col_len, \
                #         (f'Incorrect number of rows in {key} column: '
                #          f'{len(content[key])} != {col_len}')
                #     content[key] = [_ for _ in content[key]]

                new_cols.add(key)

            content = output_model.content
            # content = output_model
            for key, field in pyd_model.__fields__.items():
                if field.required and key not in content:
                    _init_col(content, pyd_model, key)

            for i, row in enumerate(input_model):
                row_dict = to_row_dict_func(row) if to_row_dict_func else row
                values, _fields_set, error = pyd.validate_model(pyd_model, row_dict)
                if error:
                    raise error

                for key, validated_val in values.items():
                    if key not in content:
                        _init_col(content, pyd_model, key)

                    if key in new_cols:
                        is_changed_val = True
                    else:
                        is_changed_val = row_dict[key] != validated_val
                        # else:
                        #     is_changed_val = True

                    if is_changed_val:
                        _, prepared_val = prepare_value_for_validation_if_dataset_or_model(
                            validated_val)
                        try:
                            content[key][i] = prepared_val
                        except (TypeError, AssertionError, ValueError, ValidationError):
                            _init_col(content, pyd_model, key)
                            content[key][i] = prepared_val
            output_model.validate_content()

        @override
        @classmethod
        def _validate_record_model_with_col_names(
            cls,
            pyd_model: type[pyd.BaseModel],
            data: ColumnWiseTableWithColNamesModel,
            header_names: tuple[str, ...],
        ) -> pyd.BaseModel | ColumnWiseTableWithColNamesModel:
            cls._validate_over_all_rows(input_model=data, output_model=data, pyd_model=pyd_model)
            return data

        @override
        @classmethod
        def _validate_record_model_without_col_names(
            cls,
            pyd_model: type[pyd.BaseModel],
            data: RowWiseTableModel,
            data_type: type[_DataWithColNamesModelT],
            header_names: tuple[str, ...],
        ) -> pyd.BaseModel | ColumnWiseTableWithColNamesModel:
            output = data_type()
            cls._validate_over_all_rows(
                input_model=data,
                output_model=output,
                pyd_model=pyd_model,
                to_row_dict_func=lambda row: dict(zip(header_names, row)),
            )
            return output


# read header line as param, somehow?

if TYPE_CHECKING:

    class TableOfPydanticRecordsModel(
            PlainModel[list[PydanticRecordModel[_PydRecordT]]],
            IsListContent[PydanticRecordModel[_PydRecordT]],
            PrintableTable,
            Generic[_PydRecordT],
    ):
        ...
else:

    class TableOfPydanticRecordsModel(
            Chain3[SplitToLinesModel,
                   SplitLinesToColumnsModel,
                   Model[list[PydanticRecordModel[_PydRecordT]]]],
            PrintableTable,
            Generic[_PydRecordT],
    ):
        ...


if TYPE_CHECKING:

    class CsvTableOfPydanticRecordsModel(
            PlainModel[list[PydanticRecordModel[_PydRecordT]]],
            IsListContent[PydanticRecordModel[_PydRecordT]],
            PrintableTable,
            Generic[_PydRecordT],
    ):
        ...
else:

    class CsvTableOfPydanticRecordsModel(
            Chain3[SplitToLinesModel,
                   SplitLinesToColumnsByCommaModel,
                   Model[list[PydanticRecordModel[_PydRecordT]]]],
            PrintableTable,
            Generic[_PydRecordT],
    ):
        ...


# TODO: Support CSV and TSV fully according to standards
#       (e.g. https://datatracker.ietf.org/doc/html/rfc4180,
#       https://en.wikipedia.org/wiki/Tab-separated_values)

if TYPE_CHECKING:

    class TsvTableModel(
            RowWiseTableFirstRowAsColNamesModel,
            PrintableTable,
    ):
        ...
else:

    class TsvTableModel(
            Chain3[
                SplitToLinesModel,
                SplitLinesToColumnsModel,
                RowWiseTableFirstRowAsColNamesModel,
            ],
            PrintableTable,
    ):
        ...


if TYPE_CHECKING:

    class CsvTableModel(
            RowWiseTableFirstRowAsColNamesModel,
            PrintableTable,
    ):
        ...
else:

    class CsvTableModel(
            Chain3[
                SplitToLinesModel,
                SplitLinesToColumnsByCommaModel,
                RowWiseTableFirstRowAsColNamesModel,
            ],
            PrintableTable,
    ):
        ...
