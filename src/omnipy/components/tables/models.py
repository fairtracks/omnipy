from abc import abstractmethod
from collections.abc import Iterator, Mapping
from copy import copy
from typing import (Callable,
                    cast,
                    Generic,
                    get_args,
                    NamedTuple,
                    overload,
                    Protocol,
                    Sized,
                    TypeAlias)

from pydantic import BaseModel
from typing_extensions import override, TypeVar

from omnipy.data.helpers import TypeVarStore
from omnipy.data.model import Model, ModelMetaclass
from omnipy.shared.protocols.builtins import IsDict, IsList, SupportsKeysAndGetItem
from omnipy.shared.protocols.data import HasContent
from omnipy.shared.typing import TYPE_CHECKING
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import first_key_in_mapping

from ..general.models import Chain3
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


class PrintableTable:
    ...


if TYPE_CHECKING:
    from omnipy.data._mimic_models import RevertModelMimicTypingHack

    class RowWiseTableModel(IsList[list[JsonScalar]], Model[list[list[JsonScalar]]]):
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
            RevertModelMimicTypingHack['RowWiseTableWithColNamesModel'],
            IsList[dict[str, JsonScalar]],
            Model[list[dict[str, JsonScalar]]],
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


class ColumnWiseTableWithColNamesAndIndexModel(Model[dict[str, dict[str, JsonScalar]]]):
    ...


class _IsColumnWiseTableWithColNames(HasContent, Sized, SupportsKeysAndGetItem, Protocol):
    @property
    def _content(self) -> dict[str, list[JsonScalar]]:
        ...

    def _common_add(
        self,
        other: 'ColWiseAddOtherType',
        reverse: bool,
    ) -> 'ColumnWiseTableWithColNamesModel':
        ...


class _ColumnWiseTableWithColNamesMixin:
    @property
    def col_names(self: _IsColumnWiseTableWithColNames) -> tuple[str, ...]:
        """
        The column names in the table, in the order they first appear in the rows.
        """
        return tuple(self.keys())

    @property
    def _content(self: _IsColumnWiseTableWithColNames) -> dict[str, list[JsonScalar]]:
        return cast(dict[str, list[JsonScalar]], self.content)

    def __len__(self: _IsColumnWiseTableWithColNames) -> int:
        try:
            first_key = first_key_in_mapping(self._content)
            return len(self._content[first_key])
        except KeyError:
            return 0

    def __iter__(self: _IsColumnWiseTableWithColNames) -> Iterator[Mapping[str, JsonScalar]]:
        _iter_row = IterRow(self._content)

        for i in range(len(self)):
            _iter_row.row_number = i
            yield _iter_row

    @overload
    def __getitem__(self: _IsColumnWiseTableWithColNames, item: str) -> list[JsonScalar]:
        ...

    @overload
    def __getitem__(self: _IsColumnWiseTableWithColNames, item: int) -> Mapping[str, JsonScalar]:
        ...

    def __getitem__(self: _IsColumnWiseTableWithColNames,
                    item: str | int) -> list[JsonScalar] | Mapping[str, JsonScalar]:
        if isinstance(item, str):
            return self._content[item]

        if item >= len(self) or item < -len(self):
            raise IndexError('Row index out of range')
        _iter_row = IterRow(self._content)
        _iter_row.row_number = item
        return _iter_row

    def _common_add(
        self: _IsColumnWiseTableWithColNames,
        other: 'ColWiseAddOtherType',
        reverse: bool,
    ) -> 'ColumnWiseTableWithColNamesModel':
        if isinstance(other, ColumnWiseTableWithColNamesModel):
            _other: _IsColumnWiseTableWithColNames = other
        else:
            _other = ColumnWiseTableWithColNamesModel(other)

        def _concat_self_and_other(
            self_value: list[JsonScalar],
            value: list[JsonScalar],
            reverse: bool,
        ) -> list[JsonScalar]:
            return value + self_value if reverse else self_value + value

        new_content = dict(self._content)
        for key, value in _other._content.items():
            if key in new_content:
                self_value: list[JsonScalar] = copy(new_content[key])
            else:
                self_value = [None] * len(self)
            new_content[key] = _concat_self_and_other(self_value, value, reverse)

        for missing_key in new_content.keys() - _other._content.keys():
            new_content[missing_key] = _concat_self_and_other(
                copy(new_content[missing_key]), [None] * len(_other), reverse)

        return ColumnWiseTableWithColNamesModel(new_content)

    def __add__(
        self: _IsColumnWiseTableWithColNames,
        other: 'ColWiseAddOtherType',
    ) -> 'ColumnWiseTableWithColNamesModel':
        return self._common_add(other, reverse=False)

    def __radd__(
        self: _IsColumnWiseTableWithColNames,
        other: 'ColWiseAddOtherType',
    ) -> 'ColumnWiseTableWithColNamesModel':
        return self._common_add(other, reverse=True)


class _ColumnWiseTableWithColNamesModel(
        Model['dict[str, list[JsonScalar]] | RowWiseTableWithColNamesNoConvertModel']):
    @classmethod
    def _parse_data(
        cls, data: 'dict[str, list[JsonScalar]] | RowWiseTableWithColNamesNoConvertModel'
    ) -> dict[str, list[JsonScalar]]:
        if isinstance(data, RowWiseTableWithColNamesNoConvertModel):
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


if TYPE_CHECKING:

    class ColumnWiseTableWithColNamesModel(  # type: ignore[misc]
            _ColumnWiseTableWithColNamesMixin,
            RevertModelMimicTypingHack['ColumnWiseTableWithColNamesModel'],
            IsDict[str, list[JsonScalar]],
            Model[dict[str, list[JsonScalar]]],
            PrintableTable,
    ):
        ...

else:

    class ColumnWiseTableWithColNamesModel(
            _ColumnWiseTableWithColNamesMixin,
            _ColumnWiseTableWithColNamesModel,
            PrintableTable,
    ):
        ...


ColWiseAddOtherType: TypeAlias = (
    ColumnWiseTableWithColNamesModel | RowWiseTableWithColNamesModel | dict[str, list[JsonScalar]]
    | list[dict[str, JsonScalar]])


class ColumnWiseTableWithColNamesNoConvertModel(Model[dict[str, list[JsonScalar]]]):
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
            RevertModelMimicTypingHack['RowWiseTableFirstRowAsColNamesModel'],
            IsList[dict[str, JsonScalar]],
            Model[list[dict[str, JsonScalar]]],
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
_DataWithColNamesModelT = TypeVar(
    '_DataWithColNamesModelT',
    dict[str, JsonScalar],
    ColumnWiseTableWithColNamesModel,
)
_DataWithoutColNamesModelT = TypeVar(
    '_DataWithoutColNamesModelT',
    list[JsonScalar],
    RowWiseTableModel,
)
_PydRecordT = TypeVar('_PydRecordT', bound=pyd.BaseModel)


class _HeaderInfo(NamedTuple):
    pydantic_model: type[pyd.BaseModel]
    header_names: tuple[str, ...]
    num_required_fields: int


class PydanticRecordModelMetaclass(ModelMetaclass):
    def __init__(cls, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        cls._header_info: _HeaderInfo | None = None

    @property
    def header_info(cls) -> _HeaderInfo:
        if cls._header_info is None:
            type_var_store = get_args(cast(type[Model], cls).outer_type(with_args=True))[0]
            pydantic_model = get_args(type_var_store)[0]
            if hasattr(pydantic_model, '__pydantic_model__'):
                pydantic_model = pydantic_model.__pydantic_model__

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
        header_names: tuple[str, ...],
    ) -> pyd.BaseModel | _DataWithColNamesModelT:
        ...

    @override
    @classmethod
    def _parse_data(  # pyright: ignore [reportIncompatibleMethodOverride]
        cls,
        data: _DataWithColNamesModelT | _DataWithoutColNamesModelT,
    ) -> pyd.BaseModel | _DataWithColNamesModelT:
        pyd_model, header_names, num_required_fields = cls.header_info
        if isinstance(data, (dict, ColumnWiseTableWithColNamesModel)):
            # cls._validate_and_set_value(data)
            return cls._validate_record_model_with_col_names(pyd_model, data, header_names)
            return pyd_model(**data)

        if isinstance(data, (list, RowWiseTableModel)):
            if isinstance(data, RowWiseTableModel):
                num_data_cols = len(data.content[0]) if len(data.content) > 0 else 0
            else:
                num_data_cols = len(data)

            assert len(header_names) >= num_data_cols >= num_required_fields, \
                (f'Incorrect number of data elements: '
                 f'{len(header_names)} >= {num_data_cols} >= {num_required_fields}')

            return cls._validate_record_model_without_col_names(pyd_model, data, header_names)
            return pyd_model(**dict(zip(header_names, data)))


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
        header_names: tuple[str, ...],
    ) -> pyd.BaseModel | dict[str, JsonScalar]:
        return pyd_model(**dict(zip(header_names, data)))


class IteratingPydanticRecordsModel(
        PydanticRecordModelBase[
            _PydBaseModelT,
            ColumnWiseTableWithColNamesModel,
            RowWiseTableModel,
        ],
        Generic[_PydBaseModelT],
):
    @classmethod
    def _validate_over_all_rows(
        cls,
        input_model: ColumnWiseTableWithColNamesModel | RowWiseTableModel,
        output_model: ColumnWiseTableWithColNamesModel,
        pyd_model: type[BaseModel],
        to_row_dict_func: Callable[[list[JsonScalar]], dict[str, JsonScalar]] | None = None,
    ):
        def _init_col(
                content: dict[str, list[JsonScalar]],
                pyd_model: type[pyd.BaseModel],
                key: str,
                col_len: int = len(input_model),
        ) -> None:
            content[key] = [pyd_model.__fields__[key].get_default()] * col_len

        content = output_model.content
        for key, field in pyd_model.__fields__.items():
            if field.required and key not in content:
                _init_col(content, pyd_model, key)

        for i, row in enumerate(input_model):
            values, _fields_set, error = pyd.validate_model(
                pyd_model,
                to_row_dict_func(row) if to_row_dict_func else row,  # pyright: ignore
            )
            if error:
                raise error
            for key, val in values.items():
                if key not in content:
                    _init_col(content, pyd_model, key)

                content[key][i] = val

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
        header_names: tuple[str, ...],
    ) -> pyd.BaseModel | ColumnWiseTableWithColNamesModel:
        output = ColumnWiseTableWithColNamesModel()
        cls._validate_over_all_rows(
            input_model=data,
            output_model=output,
            pyd_model=pyd_model,
            to_row_dict_func=lambda row: dict(zip(header_names, row)),
        )
        return output


# read header line as param, somehow?

if TYPE_CHECKING:
    from omnipy.data._mimic_models import Model_list

    class TableOfPydanticRecordsModel(RevertModelMimicTypingHack['TableOfPydanticRecordsModel'],
                                      Model_list[PydanticRecordModel[_PydRecordT]],
                                      PrintableTable,
                                      Generic[_PydRecordT]):
        ...
else:

    class TableOfPydanticRecordsModel(Chain3[SplitToLinesModel,
                                             SplitLinesToColumnsModel,
                                             Model[list[PydanticRecordModel[_PydRecordT]]]],
                                      PrintableTable,
                                      Generic[_PydRecordT]):
        ...


if TYPE_CHECKING:

    class CsvTableOfPydanticRecordsModel(
            RevertModelMimicTypingHack['CsvTableOfPydanticRecordsModel'],
            Model_list[PydanticRecordModel[_PydRecordT]],
            PrintableTable,
            Generic[_PydRecordT]):
        ...
else:

    class CsvTableOfPydanticRecordsModel(Chain3[SplitToLinesModel,
                                                SplitLinesToColumnsByCommaModel,
                                                Model[list[PydanticRecordModel[_PydRecordT]]]],
                                         PrintableTable,
                                         Generic[_PydRecordT]):
        ...


# TODO: Support CSV and TSV fully according to standards
#       (e.g. https://datatracker.ietf.org/doc/html/rfc4180,
#       https://en.wikipedia.org/wiki/Tab-separated_values)

if TYPE_CHECKING:

    class TsvTableModel(
            RevertModelMimicTypingHack['TsvTableModel'],
            Model_list[list[str]],
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
            RevertModelMimicTypingHack['CsvTableModel'],
            Model_list[list[str]],
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


class ColumnModel(Model[list[JsonScalar]]):
    pass
