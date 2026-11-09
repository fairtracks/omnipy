"""Tests for remote URL and response content models."""

from pathlib import PurePosixPath
from typing import Annotated, Any

import pytest
import pytest_cases as pc

from omnipy.components.json.models import JsonListOrDictModel
from omnipy.components.raw.models import StrictBytesModel, StrictStrModel
from omnipy.components.remote.models import (
    AutoResponseContentModel,
    GeneratePagedUrlsModel,
    HostUrlModel,
    HttpUrlModel,
    PagesInfo,
    PagesInfoRangeModel,
    QueryParamsModel,
    ResponseContentPydModel,
    UrlDataclassModel,
    UrlPathModel,
)
from omnipy.data.model import Model
from omnipy.shared.protocols.hub.runtime import IsRuntime
from omnipy.util.pydantic import ValidationError

from ...helpers.protocols import AssertModelOrValFunc
from .helpers.models import ObservationPagesInfo, ObservationPageUrl


@pytest.mark.parametrize('start_from_one', [False, True])
def test_pages_info_range(start_from_one: bool) -> None:
    pages = PagesInfoRangeModel[PagesInfo](
        start_from_one=start_from_one, num_items=80, items_per_page=25
    )
    first = int(start_from_one)
    assert [page.page for page in pages.content] == list(range(first, first + 4))
    assert [page.items_on_page for page in pages.content] == [25, 25, 25, 5]
    assert [page.items_per_page for page in pages.content] == [25] * 4


def test_pages_info_defaults_steps_and_exact_multiple() -> None:
    assert PagesInfo().num_pages == 1
    assert PagesInfo().page == 0
    assert PagesInfo(start_from_one=True).page == 1
    assert PagesInfo(num_items=50, items_per_page=25, page=1).items_on_page == 25
    pages = PagesInfoRangeModel[PagesInfo](num_pages=7, page=2, step=2)
    assert [page.page for page in pages.content] == [2, 4, 6]
    assert PagesInfo(num_pages=2, items_per_page=25, page=1).items_on_page is None


@pytest.mark.parametrize('start_from_one', [False, True])
def test_empty_pages_info_range(start_from_one: bool) -> None:
    assert (
        PagesInfoRangeModel[PagesInfo](
            start_from_one=start_from_one, num_items=0, items_per_page=25
        ).content
        == []
    )
    assert PagesInfoRangeModel[PagesInfo](start_from_one=start_from_one, num_pages=0).content == []


@pytest.mark.parametrize(
    'kwargs',
    [
        {'step': 0},
        {'step': -1},
        {'num_pages': -1},
        {'num_items': -1, 'items_per_page': 25},
        {'num_items': 10},
        {'num_items': 10, 'items_per_page': 0},
        {'num_items': 10, 'items_per_page': 'bad'},
        {'num_items': 10, 'items_per_page': 5, 'num_pages': 3},
        {'start_from_one': True, 'page': 0},
        {'num_pages': 2, 'page': 2},
        {'num_pages': 0, 'page': 1},
        {'page': -1},
        {'page': 'bad'},
        {'num_pages': 'bad'},
        {'items_per_page': 25, 'items_on_page': 26},
        {'num_pages': 2, 'items_per_page': 25, 'items_on_page': 24},
        {'num_items': 30, 'items_per_page': 25, 'page': 1, 'items_on_page': 6},
        {'num_pages': 0, 'items_on_page': 1},
    ],
)
def test_pages_info_rejects_invalid_settings(kwargs: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        PagesInfo(**kwargs)


def test_page_range_preserves_subclass_extra_fields_and_explicit_page_list() -> None:
    settings = ObservationPagesInfo.parse_obj(
        dict(base_url='https://example.com/root?token=keep#fragment', num_pages=2, custom='kept')
    )
    pages = PagesInfoRangeModel[ObservationPagesInfo](settings)
    assert all(type(page) is ObservationPagesInfo for page in pages.content)
    assert all(page.dict()['custom'] == 'kept' for page in pages.content)
    assert PagesInfoRangeModel[ObservationPagesInfo](pages.content).to_data() == pages.to_data()
    assert settings.page == 0


def test_generate_paged_urls_uses_constant_request_capacity() -> None:
    urls = GeneratePagedUrlsModel[ObservationPageUrl, ObservationPagesInfo](
        base_url='https://example.com/root?token=keep#fragment',
        num_items=80,
        items_per_page=25,
    )
    assert urls.to_data() == {
        str(
            page
        ): f'https://example.com/root/api/observations?token=keep&page={page}&limit=25#fragment'
        for page in range(4)
    }
    assert (
        GeneratePagedUrlsModel[ObservationPageUrl, ObservationPagesInfo](
            base_url='https://example.com', num_items=0, items_per_page=25
        ).to_data()
        == {}
    )


def test_query_params_model():
    empty_params = QueryParamsModel()
    assert empty_params.content == {}
    assert empty_params.to_data() == str(empty_params) == ''

    params = QueryParamsModel('a=1&b=2&c=3')
    assert params.content == {'a': '1', 'b': '2', 'c': '3'}
    assert params.to_data() == str(params) == 'a=1&b=2&c=3'

    with pytest.raises(ValidationError):
        QueryParamsModel('a=1=b')


def test_query_params_model_split_before_url_decode():
    params = QueryParamsModel(str(QueryParamsModel(a='1', b='2')))
    assert params.content == {'a': '1', 'b': '2'}
    params = QueryParamsModel(str(QueryParamsModel(a='=', b='&')))
    assert params.content == {'a': '=', 'b': '&'}

    params = QueryParamsModel('a=b%3D3')
    assert params.content == {'a': 'b=3'}

    params = QueryParamsModel('a=b%3D3%26c%3D1')
    assert params.content == {'a': 'b=3&c=1'}


def test_url_path_model():
    empty_path = UrlPathModel()
    assert empty_path.content == PurePosixPath('.')

    base_path = UrlPathModel('/abc/def')
    assert base_path.content == PurePosixPath('/abc/def')
    assert base_path.to_data() == str(base_path) == '/abc/def'

    base_path /= 'ghi'
    assert base_path.content == PurePosixPath('/abc/def/ghi')
    assert base_path.to_data() == str(base_path) == '/abc/def/ghi'

    path = base_path.copy()
    path = path / PurePosixPath('jkl', 'mno')
    assert path.content == PurePosixPath('/abc/def/ghi/jkl/mno')
    assert path.to_data() == str(path) == '/abc/def/ghi/jkl/mno'
    assert path.parts == ('/', 'abc', 'def', 'ghi', 'jkl', 'mno')

    class MyStrData:
        def __init__(self, data: str) -> None:
            self._data = data

        def __str__(self) -> str:
            return self._data

    path = base_path.copy()
    path = path / 'jkl' / MyStrData('mno') / 'pqr'
    assert path.content == PurePosixPath('/abc/def/ghi/jkl/mno/pqr')
    assert path.to_data() == str(path) == '/abc/def/ghi/jkl/mno/pqr'
    assert path.parts == ('/', 'abc', 'def', 'ghi', 'jkl', 'mno', 'pqr')

    path = base_path.copy()
    path // 'jkl' // MyStrData('mno') // 'pqr'
    assert path.content == PurePosixPath('/abc/def/ghi/jkl/mno/pqr')
    assert path.to_data() == str(path) == '/abc/def/ghi/jkl/mno/pqr'
    assert path.parts == ('/', 'abc', 'def', 'ghi', 'jkl', 'mno', 'pqr')

    with pytest.raises(TypeError):
        path = base_path.copy()
        path /= 'jkl' / MyStrData('mno') / 'pqr'  # pyright: ignore[reportOperatorIssue]

    path = base_path.copy()
    path += 'jkl'
    assert path.content == PurePosixPath('/abc/def/ghijkl')
    assert path.to_data() == str(path) == '/abc/def/ghijkl'
    assert path.parts == ('/', 'abc', 'def', 'ghijkl')


@pc.fixture
@pc.parametrize('host_url_model_cls', [HostUrlModel, HttpUrlModel])
def host_url_model_cls(host_url_model_cls: type[HostUrlModel]) -> type[HostUrlModel]:
    return host_url_model_cls


def test_http_url_model_validation_errors():
    with pytest.raises(ValidationError):
        HttpUrlModel('/abc/def')

    with pytest.raises(ValidationError):
        HttpUrlModel('file:///abc/def')


@pytest.mark.usefixtures('host_url_model_cls')
def test_host_url_model_default_localhost():
    url = HttpUrlModel()

    assert url.scheme == 'http'
    assert url.username is None
    assert url.password is None
    assert url.host == 'localhost'
    assert url.port == 80
    assert url.path == UrlPathModel('/')
    assert url.query == QueryParamsModel()
    assert url.fragment is None

    assert url.to_data() == str(url) == 'http://localhost/'

    https_url = HttpUrlModel('https://')
    assert https_url.scheme == 'https'
    assert https_url.port == 443
    assert https_url.to_data() == str(https_url) == 'https://localhost/'


def test_host_url_model_parse_all_fields(
    host_url_model_cls: Annotated[type[HostUrlModel], pytest.fixture],
):
    url = host_url_model_cls('https://user:pass@abc.net:8080/def?ghi=jkl#mno')

    assert url.scheme == 'https'
    assert url.username == 'user'
    assert url.password == 'pass'
    assert url.host == 'abc.net'
    assert url.port == 8080
    assert url.path == UrlPathModel('/def')
    assert url.query == QueryParamsModel(dict(ghi='jkl'))
    assert url.fragment == 'mno'

    assert url.to_data() == str(url) == 'https://user:pass@abc.net:8080/def?ghi=jkl#mno'


def test_host_url_model_parse_international_domains(
    host_url_model_cls: Annotated[type[HostUrlModel], pytest.fixture],
):
    for domain in ('https://www.example.珠宝/', 'https://www.example.xn--pbt977c/'):
        url = host_url_model_cls(domain)
        assert url.host == 'www.example.珠宝'
        assert url.to_data() == str(url) == 'https://www.example.xn--pbt977c/'


def test_host_url_model_url_escape(
    host_url_model_cls: Annotated[type[HostUrlModel], pytest.fixture],
):
    def _assert_fields(url: UrlDataclassModel):
        assert url.username == 'bø'
        assert url.password == 'bø'
        assert url.path == UrlPathModel('/def æ/jkl')
        assert url.query == QueryParamsModel(dict(mnø='pqr å'))
        assert url.fragment == 'vwx yz'

    url = host_url_model_cls('https://bø:bø@abc.net/def æ/jkl?mnø=pqr å#vwx yz')
    _assert_fields(url)
    assert (
        url.to_data()
        == str(url)
        == 'https://b%C3%B8:b%C3%B8@abc.net/def%20%C3%A6/jkl?mn%C3%B8=pqr%20%C3%A5#vwx%20yz'
    )

    url = host_url_model_cls(
        'https://b%C3%B8:b%C3%B8@abc.net/def%20%C3%A6/jkl?mn%C3%B8=pqr%20%C3%A5#vwx%20yz'
    )
    _assert_fields(url)
    assert (
        url.to_data()
        == str(url)
        == 'https://b%C3%B8:b%C3%B8@abc.net/def%20%C3%A6/jkl?mn%C3%B8=pqr%20%C3%A5#vwx%20yz'
    )


def test_host_url_model_modify_direct_fields(
    host_url_model_cls: Annotated[type[HostUrlModel], pytest.fixture],
    runtime: Annotated[IsRuntime, pytest.fixture],
):
    url = host_url_model_cls('http://abc.net/def')
    url.scheme = 'https'
    url.username = 'user'
    url.password = 'pass'
    url.host = 'cba.net'
    url.path /= 'ghi'
    url.query = 'jkl=mno&pqr=stu'  # type: ignore[assignment]
    url.fragment = 'anchor'

    assert url.to_data() == str(url) == 'https://user:pass@cba.net/def/ghi?jkl=mno&pqr=stu#anchor'

    url.query |= {'xyz': '123'}

    assert (
        url.to_data()
        == str(url)
        == 'https://user:pass@cba.net/def/ghi?jkl=mno&pqr=stu&xyz=123#anchor'
    )

    if isinstance(url, HttpUrlModel):
        with pytest.raises(ValidationError):
            url.scheme = 'ftp'

        if not runtime.config.data.model.interactive:
            # Manual reset of invalid modification above
            url.scheme = 'https'
        assert (
            url.to_data()
            == str(url)
            == 'https://user:pass@cba.net/def/ghi?jkl=mno&pqr=stu&xyz=123#anchor'
        )

    else:
        url.scheme = 'ftp'

        assert (
            url.to_data()
            == str(url)
            == 'ftp://user:pass@cba.net/def/ghi?jkl=mno&pqr=stu&xyz=123#anchor'
        )


def test_host_url_model_modify_port(
    host_url_model_cls: Annotated[type[HostUrlModel], pytest.fixture],
):
    url = host_url_model_cls('http://abc.net/def')
    assert url.port == 80

    url.scheme = 'https'
    assert url.port == 443

    url.port = 8080
    assert url.port == 8080
    assert url.to_data() == str(url) == 'https://abc.net:8080/def'

    url.scheme = 'http'
    assert url.port == 8080
    assert url.to_data() == str(url) == 'http://abc.net:8080/def'

    url.scheme = 'https'
    assert url.port == 8080
    assert url.to_data() == str(url) == 'https://abc.net:8080/def'

    url.port = None
    assert url.port == 443
    assert url.to_data() == str(url) == 'https://abc.net/def'

    url.scheme = 'http'
    assert url.port == 80
    assert url.to_data() == str(url) == 'http://abc.net/def'

    url.port = 80
    assert url.port == 80
    assert url.to_data() == str(url) == 'http://abc.net/def'

    url.scheme = 'https'
    assert url.port == 443
    assert url.to_data() == str(url) == 'https://abc.net/def'


def test_host_url_model_query_params(
    host_url_model_cls: Annotated[type[HostUrlModel], pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
):
    url = host_url_model_cls('http://abc.net/def')

    # TODO: When type-dependent conversion is implemented, make QueryParamsModel convertible to both
    #       str and dict[str, str] types
    # Model[dict[str, str]](url.query).content = {}
    Model[str](url.query).content = ''

    url.query |= {'jkl': 'mno'}
    url.query['pqr'] = 123

    assert_model_if_dyn_conv_else_val(url.query['jkl'], str, 'mno')
    assert_model_if_dyn_conv_else_val(url.query['pqr'], str, '123')
    assert url.query.content == {'jkl': 'mno', 'pqr': '123'}

    # Model[dict[str, str]](url.query).content = {'jkl': 'mno', 'pqr': '123'}
    Model[str](url.query).content = 'jkl=mno&pqr=123'

    assert url.to_data() == str(url) == 'http://abc.net/def?jkl=mno&pqr=123'

    url.query |= {456: 'abc'}
    del url.query['jkl']

    # Model[dict[str, str]](url.query).content = {'pqr': '123', '456': 'abc'}
    assert_model_if_dyn_conv_else_val(url.query['pqr'], str, '123')
    assert_model_if_dyn_conv_else_val(url.query['456'], str, 'abc')
    Model[str](url.query).content = 'pqr=123&456=abc'

    assert url.to_data() == str(url) == 'http://abc.net/def?pqr=123&456=abc'


def test_host_url_model_add_operator(
    host_url_model_cls: Annotated[type[HostUrlModel], pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
):
    url = host_url_model_cls('http://abc.net')

    url += 'path/to/file'  # pyright: ignore[reportOperatorIssue]
    assert url.to_data() == str(url) == 'http://abc.net/path/to/file'

    new_url = url + '?query=string'
    assert url.to_data() == str(url) == 'http://abc.net/path/to/file'
    assert new_url.to_data() == str(new_url) == 'http://abc.net/path/to/file?query=string'

    new_url += ' is longer'
    assert_model_if_dyn_conv_else_val(new_url.query['query'], str, 'string is longer')
    assert (
        new_url.to_data()
        == str(new_url)
        == 'http://abc.net/path/to/file?query=string%20is%20longer'
    )

    new_url += '#fragment'
    assert new_url.fragment == 'fragment'
    assert (
        new_url.to_data()
        == str(new_url)
        == 'http://abc.net/path/to/file?query=string%20is%20longer#fragment'
    )

    with pytest.raises(TypeError):
        '#fragment' + new_url  # type: ignore[operator]

    with pytest.raises(TypeError):
        url + new_url  # type: ignore[operator]


def test_auto_response_content_model() -> None:
    model = AutoResponseContentModel(
        ResponseContentPydModel(content_type='text/plain', response='abc')
    )
    assert model.content == StrictStrModel('abc')

    model = AutoResponseContentModel(
        ResponseContentPydModel(content_type='application/octet-stream', response=b'abc')
    )
    assert model.content == StrictBytesModel(b'abc')

    model = AutoResponseContentModel(
        ResponseContentPydModel(content_type='application/json', response=['abc'])
    )
    assert model.content == JsonListOrDictModel(['abc'])
