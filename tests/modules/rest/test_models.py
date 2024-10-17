from typing import Annotated

from pydantic import ValidationError
import pytest

from omnipy import Model
from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.modules.rest.models import HttpUrlModel, QueryParamsModel


def test_query_params_model():
    empty_params = QueryParamsModel()
    assert empty_params.contents == {}
    assert empty_params.to_data() == str(empty_params) == ''

    params = QueryParamsModel('a=1&b=2&c=3')
    assert params.contents == {'a': '1', 'b': '2', 'c': '3'}
    assert params.to_data() == str(params) == 'a=1&b=2&c=3'

    with pytest.raises(ValidationError):
        QueryParamsModel('a=1=b')


def test_http_model_validation_errors():
    with pytest.raises(ValidationError):
        HttpUrlModel()

    with pytest.raises(ValidationError):
        HttpUrlModel('/abc/def')

    with pytest.raises(ValidationError):
        HttpUrlModel('file:///abc/def')


def test_http_model_parse_only_hostname():
    url = HttpUrlModel('http://abc.net')

    assert url.scheme == 'http'
    assert url.username is None
    assert url.password is None
    assert url.host == 'abc.net'
    assert url.port == 80
    assert url.path == '/'
    assert url.query == QueryParamsModel()
    assert url.fragment is None

    assert url.to_data() == str(url) == 'http://abc.net/'


def test_http_model_parse_all_fields():
    url = HttpUrlModel('https://user:pass@abc.net:8080/def?ghi=jkl#mno')

    assert url.scheme == 'https'
    assert url.username == 'user'
    assert url.password == 'pass'
    assert url.host == 'abc.net'
    assert url.port == 8080
    assert url.path == '/def'
    assert url.query == QueryParamsModel(dict(ghi='jkl'))
    assert url.fragment == 'mno'

    assert url.to_data() == str(url) == 'https://user:pass@abc.net:8080/def?ghi=jkl#mno'


def test_http_model_parse_international_domains():
    for domain in ('https://www.example.珠宝/', 'https://www.example.xn--pbt977c/'):
        url = HttpUrlModel(domain)
        assert url.host == 'www.example.珠宝'
        assert url.to_data() == str(url) == 'https://www.example.xn--pbt977c/'


def test_http_model_url_escape():
    def _assert_fields(url: HttpUrlModel):
        assert url.username == 'bø'
        assert url.password == 'bø'
        assert url.path == '/def æ/jkl'
        assert url.query == QueryParamsModel(dict(mnø='pqr å'))
        assert url.fragment == 'vwx yz'

    url = HttpUrlModel('https://bø:bø@abc.net/def æ/jkl?mnø=pqr å#vwx yz')
    _assert_fields(url)
    assert url.to_data() == str(url) \
        == 'https://b%C3%B8:b%C3%B8@abc.net/def%20%C3%A6/jkl?mn%C3%B8=pqr%20%C3%A5#vwx%20yz'

    url = HttpUrlModel(
        'https://b%C3%B8:b%C3%B8@abc.net/def%20%C3%A6/jkl?mn%C3%B8=pqr%20%C3%A5#vwx%20yz')
    _assert_fields(url)
    assert url.to_data() == str(url) \
        == 'https://b%C3%B8:b%C3%B8@abc.net/def%20%C3%A6/jkl?mn%C3%B8=pqr%20%C3%A5#vwx%20yz'


def test_http_model_modify_direct_fields(runtime: Annotated[IsRuntime, pytest.fixture]):
    url = HttpUrlModel('http://abc.net/def')
    url.scheme = 'https'
    url.username = 'user'
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


def test_http_model_modify_port():
    url = HttpUrlModel('http://abc.net/def')
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


def test_http_model_query_params():
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
