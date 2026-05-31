"""Pandas-backed data models for tabular Omnipy data files."""

from collections.abc import Iterable
from io import StringIO
from typing import Any

from omnipy.data.model import is_model_instance, Model
from omnipy.shared.exceptions import ShouldNotOccurException
from omnipy.shared.typing import TYPE_CHECKING

from ..tables.models import (ColumnWiseTableWithColNamesAndIndexModel,
                             JsonScalarColumnWiseTableWithColNamesModel,
                             PrintableTable,
                             RowWiseTableModel,
                             RowWiseTableWithColNamesModel)

if TYPE_CHECKING:
    from .lazy_import import pd

__all__ = ['PandasModel']

AnyJsonTableType = (
    RowWiseTableModel | RowWiseTableWithColNamesModel
    | ColumnWiseTableWithColNamesAndIndexModel | JsonScalarColumnWiseTableWithColNamesModel)


class PandasModel(Model['pd.DataFrame | pd.Series | AnyJsonTableType'], PrintableTable):
    """Represent tabular content as a pandas-backed Omnipy model.

    Args:
        data: Pandas ``DataFrame``/``Series`` or a supported JSON-like table
            structure that can be converted to a DataFrame.

    Returns:
        PandasModel: Model instance containing validated pandas tabular data.

    Raises:
        Exception: Propagates conversion and validation errors raised while
            parsing input data.

    Example:
        >>> model = PandasModel([{'id': 1, 'value': 'a'}])
        >>> model.to_data()
        [{'id': 1, 'value': 'a'}]
    """

    if TYPE_CHECKING:

        def __new__(cls, *args: Any, **kwargs: Any) -> 'PandasModel_DataFrame':
            ...

    @classmethod
    def _parse_data(
        cls,
        data: 'pd.DataFrame | pd.Series | AnyJsonTableType',
    ) -> 'pd.DataFrame | pd.Series':
        """Parse supported tabular input into pandas-native content.

        Args:
            data: Pandas object or table-like content accepted by
                ``pandas.DataFrame``.

        Returns:
            Parsed pandas ``DataFrame`` or ``Series``.

        Raises:
            Exception: Propagates conversion errors raised by pandas.

        Example:
            >>> parsed = PandasModel._parse_data([{'a': 1}, {'a': 2}])
            >>> parsed.shape[0]
            2
        """

        from .lazy_import import pd

        if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
            return data

        return cls._from_iterable(data)

    # @staticmethod
    # def _data_column_names_are_strings(data: pd.DataFrame) -> None:
    #     for column in data.columns:
    #         assert isinstance(column, str)

    # @staticmethod
    # def _data_not_empty_object(data: pd.DataFrame) -> None:
    #     assert not any(data.isna().all(axis=1))
    #

    @classmethod
    def _from_iterable(cls, data: Iterable) -> 'pd.DataFrame':
        """Build a DataFrame from iterable tabular data.

        Args:
            data: Iterable rows or a model wrapping iterable row content.

        Returns:
            DataFrame with pandas nullable dtypes inferred.

        Raises:
            Exception: Propagates DataFrame construction errors raised by
                pandas.

        Example:
            >>> df = PandasModel._from_iterable([{'a': 1}, {'a': None}])
            >>> tuple(df.columns)
            ('a',)
        """

        from .lazy_import import pd
        return pd.DataFrame(data.content if is_model_instance(data) else data).convert_dtypes()

    def to_data(self) -> Any:
        """Convert pandas content to plain Python data structures.

        Args:
            self: Model instance to serialize.

        Returns:
            For DataFrames, a list of row dictionaries. For Series, a key-value
            dictionary.

        Raises:
            Exception: Propagates serialization errors raised by pandas.

        Example:
            >>> model = PandasModel([{'a': 1}])
            >>> model.to_data()
            [{'a': 1}]
        """

        from .lazy_import import pd

        df = self.content.replace({pd.NA: None})
        if isinstance(df, pd.DataFrame):
            # return df.to_dict(orient='records')
            return df.to_dict(orient='list')
        elif isinstance(df, pd.Series):
            return df.to_dict()

    def from_data(self, data: Iterable) -> None:
        """Replace model content from iterable table data.

        Args:
            data: Iterable rows that can be converted to a pandas DataFrame.

        Returns:
            None: Updates model content in place.

        Raises:
            Exception: Propagates validation or conversion errors raised during
                update.

        Example:
            >>> model = PandasModel([{'a': 1}])
            >>> model.from_data([{'a': 2}])
            >>> model.to_data()
            [{'a': 2}]
        """

        self._validate_and_set_value(self._from_iterable(data))

    def from_json(self, json_content: str) -> None:
        """Replace model content by parsing JSON table content.

        Args:
            json_content: JSON string accepted by ``pandas.read_json``.

        Returns:
            None: Updates model content in place.

        Raises:
            ValueError: If ``json_content`` cannot be parsed as a table.
            Exception: Propagates pandas parsing or validation errors.

        Example:
            >>> model = PandasModel([{'a': 1}])
            >>> model.from_json('[{"a": 3}]')
            >>> model.to_data()
            [{'a': 3}]
        """

        from .lazy_import import pd

        self._validate_and_set_value(pd.read_json(StringIO(json_content)).convert_dtypes())

    def to_json(self, pretty=True) -> str:
        """Serialize model content to JSON.

        Args:
            pretty: Reserved compatibility argument. The current implementation
                always returns compact pandas JSON output.

        Returns:
            JSON string representation of the underlying pandas object.

        Raises:
            ShouldNotOccurException: If model content is neither DataFrame nor
                Series.

        Example:
            >>> model = PandasModel([{'a': 1}])
            >>> model.to_json()
            '[{"a":1}]'
        """

        from .lazy_import import pd

        if isinstance(self.content, pd.DataFrame):
            return self.content.to_json(orient='records')
        elif isinstance(self.content, pd.Series):
            return self.content.to_json()
        else:
            raise ShouldNotOccurException()


def _update_forward_refs():
    """Resolve postponed type references for ``PandasModel``.

    Args:
        None.

    Returns:
        None: Updates type references in place.

    Raises:
        Exception: Propagates forward-reference resolution errors.

    Example:
        >>> _update_forward_refs()
    """

    from .lazy_import import pd

    PandasModel.update_forward_refs(pd=pd, AnyJsonTableType=AnyJsonTableType)


_update_forward_refs()

if TYPE_CHECKING:

    class PandasModel_DataFrame(PandasModel, pd.DataFrame):
        ...
