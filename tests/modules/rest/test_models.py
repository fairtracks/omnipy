from typing import Annotated

from pydantic import ValidationError
import pytest

from omnipy import Model
from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.modules.rest.models import HostType, HttpUrlModel, QueryParamsModel


def test_query_params_model():
    empty_params = QueryParamsModel()
    assert empty_params.contents == {}
    assert empty_params.to_data() == str(empty_params) == ''

    params = QueryParamsModel('a=1&b=2&c=3')
    assert params.contents == {'a': '1', 'b': '2', 'c': '3'}
    assert params.to_data() == str(params) == 'a=1&b=2&c=3'

    QueryParamsModel('a=1=b')


def test_http_model_validation_errors():
    with pytest.raises(ValidationError):
        HttpUrlModel()

    with pytest.raises(ValidationError):
        HttpUrlModel('/abc/def')

    with pytest.raises(ValidationError):
        HttpUrlModel('file:///abc/def')

    with pytest.raises(ValidationError):
        HttpUrlModel('http:///abc/def')


def test_http_model_parse_simple():
    url = HttpUrlModel('http://abc.net/def')
    assert url.scheme == 'http'
    assert url.user is None
    assert url.password is None
    assert url.host == 'abc.net'
    assert url.path == '/def'
    assert url.query == QueryParamsModel()
    assert url.fragment is None

    assert url.port == 80
    assert url.tld == 'net'
    assert url.host_type == HostType.DOMAIN

    assert url.to_data() == str(url) == 'http://abc.net/def'


def test_http_model_modify_mutable_fields(runtime: Annotated[IsRuntime, pytest.fixture]):
    url = HttpUrlModel('http://abc.net/def')
    url.scheme = 'https'
    url.user = 'user'
    url.password = 'pass'
    url.host = 'cba.net'
    url.path = '/def/ghi'
    url.query = 'jkl=mno&pqr=stu'
    url.fragment = 'anchor'

    assert url.to_data() == str(url) == 'https://user:pass@cba.net/def/ghi?jkl=mno&pqr=stu#anchor'

    url.query |= {'xyz': '123'}

    assert url.to_data() == str(
        url) == 'https://user:pass@cba.net/def/ghi?jkl=mno&pqr=stu&xyz=123#anchor'

    with pytest.raises(ValidationError):
        url.scheme = 'ftp'

    if not runtime.config.data.interactive_mode:
        # Manual reset of invalid modification above
        url.scheme = 'https'

    assert url.to_data() == str(
        url) == 'https://user:pass@cba.net/def/ghi?jkl=mno&pqr=stu&xyz=123#anchor'

    with pytest.raises(ValidationError):
        url.host = 'not-a-domain'

    if not runtime.config.data.interactive_mode:
        # Manual reset of invalid modification above
        url.host = 'cba.net'


def test_http_model_query_params(runtime: Annotated[IsRuntime, pytest.fixture]):
    url = HttpUrlModel('http://abc.net/def')

    # TODO: When type-dependent conversion is implemented, make QueryParamsModel convertable to both
    #       str and dict[str, str] types
    # Model[dict[str, str]](url.query).contents = {}
    Model[str](url.query).contents = ''

    url.query |= {'jkl': 'mno'}
    url.query['pqr'] = 123
    assert url.query.contents == {'jkl': 'mno', 'pqr': '123'}

    # Model[dict[str, str]](url.query).contents = {'jkl': 'mno', 'pqr': '123'}
    Model[str](url.query).contents = 'jkl=mno&pqr=123'

    assert url.to_data() == str(url) == 'http://abc.net/def?jkl=mno&pqr=123'

    url.query |= {456: 'abc'}
    del url.query['jkl']

    # Model[dict[str, str]](url.query).contents = {'pqr': '123', '456': 'abc'}
    Model[str](url.query).contents = 'pqr=123&456=abc'

    assert url.to_data() == str(url) == 'http://abc.net/def?pqr=123&456=abc'


def test_http_model_modify_immutable_fields(runtime: Annotated[IsRuntime, pytest.fixture]):
    url = HttpUrlModel('http://abc.net/def')

    url.tld = 'com'
    assert url.tld == 'net'
    assert url.host == 'abc.net'

    url.host = 'abc.com'
    assert url.tld == 'com'

    url.host_type = HostType.IPv4
    assert url.host_type == HostType.DOMAIN

    url.host = '127.0.0.1'
    assert url.host_type == HostType.IPv4
    assert url.tld is None
