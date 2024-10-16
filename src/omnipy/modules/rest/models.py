from enum import Enum

from pydantic import BaseModel, Field, HttpUrl

from omnipy.data.model import Model
from omnipy.util.contexts import hold_and_reset_prev_attrib_value

from ..raw.models import NestedJoinItemsModel, NestedSplitToItemsModel


class HostType(str, Enum):
    DOMAIN = 'domain'
    INTERNATIONAL_DOMAIN = 'int_domain'
    IPv4 = 'ipv4'
    IPv6 = 'ipv6'


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
        return dict(params_list)

    def to_data(self) -> str:
        with hold_and_reset_prev_attrib_value(self.config,
                                              'dynamically_convert_elements_to_models'):
            self.config.dynamically_convert_elements_to_models = False
            return QueryParamsJoinerModel(tuple(self.contents.items())).to_data()

    def __str__(self) -> str:
        return self.to_data()


class UrlDataclassModel(BaseModel):
    # Mutable fields
    scheme: str
    user: str | None = None
    password: str | None = None
    host: str | None = None
    path: str | None = None
    query: QueryParamsModel = Field(default_factory=QueryParamsModel)
    fragment: str | None = None

    # Immutable fields
    tld: str | None = None  # Top-level domain
    host_type: HostType = HostType.DOMAIN
    port: int | None = None

    def __str__(self) -> str:
        return HttpUrl.build(
            **{
                k: str(v) if k != 'query' else v for k,
                v in self.dict().items() if k not in HttpUrl.hidden_parts and v is not None
            })


class HttpUrlModel(Model[UrlDataclassModel | str]):
    @classmethod
    def _parse_data(cls, data: UrlDataclassModel | str) -> UrlDataclassModel:
        assert data, 'URL must be specified at init'

        # For validation only
        url_model = Model[HttpUrl | None](
            str(data) if isinstance(data, UrlDataclassModel) else data)

        field_names = UrlDataclassModel.__fields__.keys()
        parts = {key: getattr(url_model.contents, key) for key in field_names}
        return UrlDataclassModel(**{key: val for key, val in parts.items() if val is not None})

    def to_data(self) -> str:
        return str(self.contents)

    def __str__(self) -> str:
        return str(self.contents)
