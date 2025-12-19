import typing
from typing import Any, cast, Generic, get_args, Iterable, Iterator, Mapping, overload

from typing_extensions import override, TypeVar

from omnipy.data.model import Model
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import first_key_in_mapping

from ...shared.protocols.builtins import (IsItemsView,
                                          IsKeysView,
                                          IsValuesView,
                                          SupportsKeysAndGetItem)
from ..general.models import Chain3
from ..json.models import JsonListOfScalarsModel
from ..json.typedefs import JsonScalar
from ..raw.models import (SplitLinesToColumnsByCommaModel,
                          SplitLinesToColumnsModel,
                          SplitToLinesModel)


class IterRow(Mapping[str, JsonScalar]):
    def __init__(self, content: dict[str, list[JsonScalar]]) -> None:
        self._content = content
        self.row_number: int = -1

    def __getitem__(self, key):
        if key not in self._content:
            raise KeyError(f'Key {key} is not a column name')
        if self.row_number == -1:
            raise KeyError('Row number not set')
        return self._content[key][self.row_number]

    def __iter__(self):
        return iter(self._content)

    def __len__(self):
        return len(self._content)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, IterRow):
            return self._content == other._content and self.row_number == other.row_number
        return False


class RowWiseTableListOfListsModel(Model[list[list[JsonScalar]]]):
    ...


class RowWiseTableListOfDictsModel(
        Model['list[dict[str, JsonScalar]] | ColumnWiseTableDictOfListsNoConvertModel']):
    @classmethod
    def _parse_data(
        cls, data: 'list[dict[str, JsonScalar]] | ColumnWiseTableDictOfListsNoConvertModel'
    ) -> list[dict[str, JsonScalar]]:
        if isinstance(data, ColumnWiseTableDictOfListsNoConvertModel):
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


class RowWiseTableListOfDictsNoConvertModel(Model[list[dict[str, JsonScalar]]]):
    ...


class ColumnWiseTableDictOfDictsModel(Model[dict[str, dict[str, JsonScalar]]]):
    ...


class _ColumnWiseTableDictOfListsModel(
        Model['dict[str, list[JsonScalar]] | RowWiseTableListOfDictsNoConvertModel']):
    @classmethod
    def _parse_data(
        cls, data: 'dict[str, list[JsonScalar]] | RowWiseTableListOfDictsNoConvertModel'
    ) -> dict[str, list[JsonScalar]]:
        if isinstance(data, RowWiseTableListOfDictsNoConvertModel):
            row_wise_data = cast(list[dict[str, JsonScalar]], data)
            # Convert row-wise to column-wise
            column_wise_data: dict[str, list[JsonScalar]] = {}

            row: dict[str, JsonScalar]
            for i, row in enumerate(row_wise_data):
                for col_name, value in row.items():
                    if col_name not in column_wise_data:
                        # New column, need to create new list and pad previous rows with None
                        column_wise_data[col_name] = [None] * i
                    column_wise_data[col_name].append(value)
                for col_name_not_in_row in column_wise_data.keys() - row.keys():
                    # Pad missing columns with None
                    column_wise_data[col_name_not_in_row].append(None)

            return column_wise_data
        else:
            return data

    @property
    def _content(self) -> dict[str, list[JsonScalar]]:
        return cast(dict[str, list[JsonScalar]], self.content)

    def __len__(self) -> int:
        try:
            first_key = first_key_in_mapping(self._content)
            return len(self._content[first_key])
        except KeyError:
            return 0

    @override
    def __iter__(self) -> Iterator[Mapping[str, JsonScalar]]:  # type: ignore[override]
        _iter_row = IterRow(self._content)

        for i in range(len(self)):
            _iter_row.row_number = i
            yield _iter_row

    @overload
    def __getitem__(self, item: str) -> list[JsonScalar]:
        ...

    @overload
    def __getitem__(self, item: int) -> Mapping[str, JsonScalar]:
        ...

    def __getitem__(self, item: str | int) -> list[JsonScalar] | Mapping[str, JsonScalar]:
        if isinstance(item, str):
            return self._content[item]

        if item >= len(self) or item < -len(self):
            raise IndexError('Row index out of range')
        _iter_row = IterRow(self._content)
        _iter_row.row_number = item
        return _iter_row

    def __setitem__(self, key: str, value: list[JsonScalar]) -> None:
        super().__setitem__(key, value)  # type: ignore[misc]


if typing.TYPE_CHECKING:  # noqa: C901

    class ColumnWiseTableDictOfListsModel(Model[dict[str, list[JsonScalar]]]):
        def __new__(
            cls,
            *args: Any,
            **kwargs: Any,
        ) -> 'ColumnWiseTableDictOfListsModel':
            ...

        # TODO: Figure a better way to type ColumnWiseTableDictOfListsModel.
        #       Main issue is that PyCharm has special treatment of Mapping
        #       then iterating, so that the type of the iterator is str.
        #       Thus, inheriting from dict through Model_dict does not work
        #       properly in PyCharm.

        @overload
        def get(self, key: str, /) -> list[JsonScalar] | None:
            ...

        @overload
        def get(self, key: int, /) -> Mapping[str, JsonScalar] | None:
            ...

        def get(self, key: str | int, /) -> list[JsonScalar] | Mapping[str, JsonScalar] | None:
            """
            D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
            """
            ...

        def keys(self) -> 'IsKeysView[str]':
            """
            D.keys() -> a set-like object providing a view on D's keys
            """
            ...

        def items(self) -> 'IsItemsView[str, list[JsonScalar]]':
            """
            D.items() -> a set-like object providing a view on D's items
            """
            ...

        def values(self) -> 'IsValuesView[list[JsonScalar]]':
            """
            D.values() -> an object providing a view on D's values
            """
            ...

        def pop(self, key: str, /) -> list[JsonScalar]:
            """
            D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
            If key is not found, d is returned if given, otherwise KeyError is raised.
            """
            ...

        def popitem(self) -> tuple[str, list[JsonScalar]]:
            """
            D.popitem() -> (k, v), remove and return some (key, value) pair
               as a 2-tuple; but raise KeyError if D is empty.
            """
            ...

        def clear(self) -> None:
            """
            D.clear() -> None.  Remove all items from D.
            """
            ...

        @overload
        def update(self,
                   other: SupportsKeysAndGetItem[str, list[JsonScalar]],
                   /,
                   **kwargs: list[JsonScalar]) -> None:
            ...

        @overload
        def update(self,
                   other: Iterable[tuple[str, list[JsonScalar]]],
                   /,
                   **kwargs: list[JsonScalar]) -> None:
            ...

        @overload
        def update(self, /, **kwargs: list[JsonScalar]) -> None:
            ...

        def update(self, other: Any = None, /, **kwargs: list[JsonScalar]) -> None:
            """
            D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
            If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
            If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
            In either case, this is followed by: for k, v in F.items(): D[k] = v
            """
            ...

        def setdefault(self, key: str, default: list[JsonScalar], /):
            """
            D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
            """
            ...

        def __contains__(self, key: str) -> bool:
            ...

        def __len__(self) -> int:
            ...

        def __eq__(self, other: object) -> bool:
            ...

        @override
        def __iter__(self) -> Iterator[Mapping[str, JsonScalar]]:  # type: ignore[override]
            ...

        @overload
        def __getitem__(self, item: str) -> list[JsonScalar]:
            ...

        @overload
        def __getitem__(self, item: int) -> Mapping[str, JsonScalar]:
            ...

        def __getitem__(self, item: str | int) -> list[JsonScalar] | Mapping[str, JsonScalar]:
            ...

        def __setitem__(self, key: str, value: list[JsonScalar]) -> None:
            ...

        def __delitem__(self, key: str) -> None:
            ...

else:

    class ColumnWiseTableDictOfListsModel(_ColumnWiseTableDictOfListsModel):
        ...


class ColumnWiseTableDictOfListsNoConvertModel(Model[dict[str, list[JsonScalar]]]):
    ...


RowWiseTableListOfDictsModel.update_forward_refs()


class ColNamesMixin:
    @property
    def col_names(self) -> tuple[str, ...]:
        col_names = {}
        for row in self:  # type: ignore[attr-defined]
            col_names.update(dict.fromkeys(row.keys()))
        return tuple(col_names.keys())


if typing.TYPE_CHECKING:
    from omnipy.data._mimic_models import Model_list

    class _RowWiseTableFirstRowAsColNamesModel(  # type: ignore[misc]
            ColNamesMixin,
            Model_list[dict[str, JsonScalar]],
    ):
        ...


class RowWiseTableFirstRowAsColNamesModel(ColNamesMixin,
                                          Model[list[dict[str, JsonScalar]]
                                                | RowWiseTableListOfListsModel]):
    if typing.TYPE_CHECKING:

        def __new__(  # type: ignore[misc]
            cls,
            *args: Any,
            **kwargs: Any,
        ) -> '_RowWiseTableFirstRowAsColNamesModel':
            ...

    @classmethod
    def _parse_data(
        cls, data: list[dict[str, JsonScalar]] | RowWiseTableListOfListsModel
    ) -> list[dict[str, JsonScalar]]:
        if isinstance(data, RowWiseTableListOfListsModel):
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


_PydBaseModelT = TypeVar('_PydBaseModelT', bound=pyd.BaseModel)
_PydRecordT = TypeVar('_PydRecordT', bound=pyd.BaseModel)


class PydanticRecordModel(Model[_PydBaseModelT | JsonListOfScalarsModel], Generic[_PydBaseModelT]):
    @classmethod
    def _parse_data(cls, data: _PydBaseModelT | JsonListOfScalarsModel) -> _PydBaseModelT:
        match data:
            case JsonListOfScalarsModel():
                pydantic_model = get_args(cls.outer_type(with_args=True))[0]
                headers = pydantic_model.__fields__

                num_required_fields = -1
                for i, header_field in enumerate(headers.values()):
                    if not header_field.required:
                        if num_required_fields == -1:
                            num_required_fields = i
                        continue
                    elif num_required_fields != -1 and i > num_required_fields:
                        raise ValueError('Required fields must not come after optional fields')

                assert len(headers) >= len(data) >= num_required_fields, \
                    (f'Incorrect number of data elements: '
                     f'{len(headers)} >= {len(data)} >= {num_required_fields}')

                return pydantic_model(**dict(zip(headers, data)))
            case _:
                return data


if typing.TYPE_CHECKING:
    from omnipy.data._mimic_models import Model_list

    class TableOfPydanticRecordsModel(Model_list[PydanticRecordModel[_PydRecordT]],
                                      Generic[_PydRecordT]):
        ...
else:

    class TableOfPydanticRecordsModel(Chain3[SplitToLinesModel,
                                             SplitLinesToColumnsModel,
                                             Model[list[PydanticRecordModel[_PydRecordT]]]],
                                      Generic[_PydRecordT]):
        ...


class TsvTableModel(Chain3[
        SplitToLinesModel,
        SplitLinesToColumnsModel,
        RowWiseTableFirstRowAsColNamesModel,
]):
    if typing.TYPE_CHECKING:

        def __new__(  # type: ignore[misc]
            cls,
            *args: Any,
            **kwargs: Any,
        ) -> '_RowWiseTableFirstRowAsColNamesModel':
            ...


class CsvTableModel(Chain3[
        SplitToLinesModel,
        SplitLinesToColumnsByCommaModel,
        RowWiseTableFirstRowAsColNamesModel,
]):
    if typing.TYPE_CHECKING:

        def __new__(  # type: ignore[misc]
            cls,
            *args: Any,
            **kwargs: Any,
        ) -> '_RowWiseTableFirstRowAsColNamesModel':
            ...
