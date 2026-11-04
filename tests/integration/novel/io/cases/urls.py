"""Scalar and collection inputs to the public HTTP loading API."""

from collections.abc import Callable, Iterable
from typing import NamedTuple

from aiohttp.test_utils import TestServer
import pytest_cases as pc

from omnipy.components.remote.datasets import HttpUrlDataset
from omnipy.components.remote.models import HttpUrlModel
from omnipy.data.model import Model
from omnipy.shared.protocols.data import IsPathsOrUrlsOneOrMore


class UrlCase(NamedTuple):
    urls: IsPathsOrUrlsOneOrMore
    expected_model: object
    """Expected data when loaded into a Model"""
    expected_dataset: dict[str, object]
    """Expected data when loaded into a Dataset, or a Model wrapping one"""


@pc.parametrize('wrapper', [str, HttpUrlModel])
def case_single_url(
    load_content_server: TestServer, wrapper: Callable[[str], str | HttpUrlModel]
) -> UrlCase:
    url = str(load_content_server.make_url('/json'))
    return UrlCase(urls=wrapper(url), expected_model=[1, 2], expected_dataset={url: [1, 2]})


@pc.parametrize('wrapper', [dict, HttpUrlDataset, Model[HttpUrlDataset]])
@pc.parametrize('count', [0, 1, 2])
def case_keyed_urls(
    load_content_server: TestServer,
    wrapper: Callable[[dict[str, str]], IsPathsOrUrlsOneOrMore],
    count: int,
) -> UrlCase:
    urls = {
        key: str(load_content_server.make_url(f'/json?item={key}'))
        for key in ('first', 'second')[:count]
    }
    expected: dict[str, object] = {key: [1, 2] for key in urls}
    return UrlCase(urls=wrapper(urls), expected_model=expected, expected_dataset=expected)


@pc.parametrize('wrapper', [list, tuple, iter])
@pc.parametrize('count', [0, 1, 2])
def case_url_iterables(
    load_content_server: TestServer, wrapper: Callable[[list[str]], Iterable[str]], count: int
) -> UrlCase:
    urls = [str(load_content_server.make_url(f'/json?item={index}')) for index in range(count)]
    expected: dict[str, object] = {url: [1, 2] for url in urls}
    return UrlCase(urls=wrapper(urls), expected_model=expected, expected_dataset=expected)
