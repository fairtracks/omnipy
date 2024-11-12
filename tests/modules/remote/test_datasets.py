from typing import Annotated

import pytest

from omnipy.modules.remote.datasets import HttpUrlDataset

from ...helpers.protocols import AssertModelOrValFunc


def test_http_url_dataset(
        assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture]) -> None:
    urls = HttpUrlDataset()
    urls['url1'] = 'http://abc.net'  # type: ignore[assignment]
    urls['url2'] = 'https://user:pass@cba.com/def?ghi=jkl#mno'  # type: ignore[assignment]

    # TODO: Support dynamically_convert_elements_to_models also for accessing members of
    #       omnipy-wrapped pydantic models

    assert urls['url1'].host == 'abc.net'
    assert_model_if_dyn_conv_else_val(urls['url2'].query['ghi'], str, 'jkl')
