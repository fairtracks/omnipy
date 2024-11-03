from pathlib import PurePosixPath
from typing import cast, Iterable
from urllib.parse import unquote

from pydantic import BaseModel, Field
from pydantic_core import Url

from omnipy.data.model import Model
from omnipy.util.contexts import hold_and_reset_prev_attrib_value

from ..raw.models import NestedJoinItemsModel, NestedSplitToItemsModel

QueryParamsSplitterModel = NestedSplitToItemsModel.adjust(
    'QueryParamsSplitterModel', delimiters=('&', '='))

QueryParamsJoinerModel = NestedJoinItemsModel.adjust(
    'QueryParamsJoinerModel', delimiters=('&', '='))


class QueryParamsModel(Model[dict[str, str] | tuple[tuple[str, str], ...] | tuple[str, ...] | str]):
    @classmethod
    def _parse_data(
        cls, data: dict[str, str] | tuple[tuple[str, str], ...] | tuple[str, ...] | str
    ) -> dict[str, str]:
        if isinstance(data, dict):
            return data

        params_list = QueryParamsSplitterModel(data).contents
        assert all(len(param) == 2 for param in params_list), \
            (f'Each parameter must have 2 elements only: [key, value]. '
             f'Incorrect parameter list: {params_list}')
        return dict(cast(Iterable[tuple[str, str]], params_list))

    def to_data(self) -> str:
        with hold_and_reset_prev_attrib_value(self.config,
                                              'dynamically_convert_elements_to_models'):
            self.config.dynamically_convert_elements_to_models = False
            contents_as_tuple = tuple(cast(dict[str, str], self.contents).items())
            return QueryParamsJoinerModel(contents_as_tuple).to_data()  # type: ignore[return-value]

    def __str__(self) -> str:
        return self.to_data()


class UrlPathModel(Model[PurePosixPath | str]):
    @classmethod
    def _parse_data(cls, data: PurePosixPath | str) -> PurePosixPath:
        return PurePosixPath(data) if isinstance(data, str) else data

    def to_data(self) -> str:
        return str(self.contents)

    def __str__(self) -> str:
        return str(self.contents)

    def __floordiv__(self, other):
        self.contents /= other
        return self

    def __add__(self, other):
        return UrlPathModel(str(self) + other)


DEFAULT_PORTS = {80, 443}


class UrlDataclassModel(BaseModel):
    # Mutable fields
    scheme: str
    username: str | None = None
    password: str | None = None
    host: str = 'localhost'
    port: int | None = None
    path: UrlPathModel | None = None
    query: QueryParamsModel = Field(default_factory=QueryParamsModel)
    fragment: str | None = None

    def __str__(self) -> str:
        kwargs: dict[str, str | int] = {}
        for key, val in self.dict().items():
            if val is None:
                continue
            match key:
                case 'port':
                    if val in DEFAULT_PORTS:
                        continue
                    kwargs[key] = val
                case 'path':
                    # Fix for second problem described in
                    # https://github.com/pydantic/pydantic/issues/7186#issuecomment-1912791497
                    kwargs[key] = val.lstrip('/')
                case 'query':
                    if val:
                        kwargs[key] = str(val)
                case _:
                    kwargs[key] = val

        return str(Url.build(**kwargs))  # type: ignore[arg-type]


class HttpUrlModel(Model[UrlDataclassModel | str]):
    @classmethod
    def _parse_data(cls, data: UrlDataclassModel | str) -> UrlDataclassModel:
        if data == '':
            data = 'http://localhost/'
        if data == 'https://':
            data = 'https://localhost/'
        # For validation only
        url_obj = Url(str(data) if isinstance(data, UrlDataclassModel) else data)

        parts: dict[str, str | int | None] = {}
        for key in UrlDataclassModel.__fields__.keys():
            match key:
                case 'scheme':
                    val = url_obj.scheme
                    assert val in {'http', 'https'}, f'Unsupported scheme: {val}'
                    parts[key] = val
                case 'host':
                    parts[key] = url_obj.unicode_host()
                case 'username' | 'password' | 'path' | 'query' | 'fragment':
                    val = getattr(url_obj, key)
                    parts[key] = unquote(val) if val is not None else None
                case _:
                    parts[key] = getattr(url_obj, key)

        return UrlDataclassModel(**{
            key: val  # type: ignore[arg-type]
            for key, val in parts.items()
            if val is not None
        })

    def __add__(self, other: str) -> 'HttpUrlModel':
        return HttpUrlModel(str(self) + other)

    def to_data(self) -> str:
        return str(self.contents)

    def __str__(self) -> str:
        return str(self.contents)
