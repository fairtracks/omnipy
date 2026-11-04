"""Scalar and collection inputs to the public HTTP loading API."""

import pytest_cases as pc

from omnipy.components.remote.datasets import HttpUrlDataset
from omnipy.components.remote.models import HttpUrlModel
from omnipy.data.model import Model


@pc.parametrize('wrapper', [str, HttpUrlModel])
def case_single_url(load_content_server, wrapper):
    url = str(load_content_server.make_url('/json'))
    return {'paths_or_urls': wrapper(url)}, [1, 2], {url: [1, 2]}


@pc.parametrize('wrapper', [dict, HttpUrlDataset, Model[Model[HttpUrlDataset]]])
@pc.parametrize('count', [0, 1, 2])
def case_keyed_urls(load_content_server, wrapper, count):
    urls = {
        key: str(load_content_server.make_url(f'/json?item={key}'))
        for key in ('first', 'second')[:count]
    }
    expected = {key: [1, 2] for key in urls}
    return {'paths_or_urls': wrapper(urls)}, expected, expected


@pc.parametrize('wrapper', [list, tuple, iter])
@pc.parametrize('count', [0, 1, 2])
def case_url_iterables(load_content_server, wrapper, count):
    urls = [str(load_content_server.make_url(f'/json?item={index}')) for index in range(count)]
    expected = {url: [1, 2] for url in urls}
    return {'paths_or_urls': wrapper(urls)}, expected, expected


@pc.parametrize('count', [1, 2])
def case_keyword_urls(load_content_server, count):
    urls = {
        key: HttpUrlModel(str(load_content_server.make_url(f'/json?item={key}')))
        for key in ('first', 'second')[:count]
    }
    expected = {key: [1, 2] for key in urls}
    return urls, expected, expected
