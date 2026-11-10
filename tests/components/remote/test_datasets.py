"""Tests for remote datasets."""

from typing import Annotated

import pytest

import omnipy as om
from omnipy.components.remote.datasets import HostUrlDataset, HttpUrlDataset
from omnipy.components.remote.models import HostUrlModel
from omnipy.util.pydantic import ValidationError

from ...helpers.protocols import AssertModelOrValFunc


def test_host_url_dataset() -> None:
    urls = HostUrlDataset({'files': 'ftp://example.com/data', 'api': 'https://example.com/api'})
    urls['other'] = HostUrlModel('s3://bucket/path')

    assert om.HostUrlDataset is HostUrlDataset
    assert all(isinstance(url, HostUrlModel) for url in urls.values())
    assert urls['files'].host == 'example.com'
    assert urls.to_data() == {
        'files': 'ftp://example.com/data',
        'api': 'https://example.com/api',
        'other': 's3://bucket/path',
    }


def test_host_url_dataset_rejects_invalid_urls() -> None:
    with pytest.raises(ValidationError):
        HostUrlDataset({'invalid': '/relative/path'})

    urls = HostUrlDataset()
    with pytest.raises(ValidationError):
        urls['invalid'] = '/relative/path'


def test_http_url_dataset_rejects_non_http_schemes() -> None:
    with pytest.raises(ValidationError):
        HttpUrlDataset({'files': 'ftp://example.com/data'})


def test_http_url_dataset(
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    urls = HttpUrlDataset()
    urls['url1'] = 'http://abc.net'
    urls['url2'] = 'https://user:pass@cba.com/def?ghi=jkl#mno'

    # TODO: Support dynamically_convert_elements_to_models also for accessing members of
    #       omnipy-wrapped pydantic models

    assert urls['url1'].host == 'abc.net'
    assert_model_if_dyn_conv_else_val(urls['url2'].query['ghi'], str, 'jkl')
