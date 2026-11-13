"""Tests for the portable config export: secrets and machine-local fields are left out."""

import json
from typing import Annotated

import pytest

from omnipy.config import ConfigBase, MACHINE_LOCAL
from omnipy.config.job import S3OutputStorageConfig
from omnipy.shared.protocols.hub.runtime import IsRuntime
import omnipy.util.pydantic as pyd


class _InnerConfig(ConfigBase):
    level: int = 1
    scratch_dir: str = pyd.Field(default='/tmp/scratch', **MACHINE_LOCAL)


class _OuterConfig(ConfigBase):
    name: str = 'outer'
    token: pyd.SecretStr = pyd.SecretStr('')
    inner: _InnerConfig = pyd.Field(default_factory=_InnerConfig)
    machine_section: _InnerConfig = pyd.Field(default_factory=_InnerConfig, **MACHINE_LOCAL)
    sizes: tuple[int, ...] = (1, 2)


def test_portable_dict_leaves_out_secrets_and_machine_local_fields() -> None:
    config = _OuterConfig(token='s3cr3t')

    assert config.to_portable_dict() == {
        'name': 'outer',
        'inner': {'level': 1},
        'sizes': [1, 2],
    }


def test_update_from_portable_dict_updates_in_place() -> None:
    config = _OuterConfig()
    inner = config.inner

    config.update_from_portable_dict({'name': 'changed', 'inner': {'level': 5}, 'sizes': [3]})

    assert config.name == 'changed'
    assert config.inner is inner
    assert config.inner.level == 5
    assert config.sizes == (3,)
    assert config.inner.scratch_dir == '/tmp/scratch'


def test_update_from_portable_dict_rejects_unknown_keys() -> None:
    with pytest.raises(AttributeError, match='nonexistent'):
        _OuterConfig().update_from_portable_dict({'nonexistent': 1})


def test_s3_keys_are_secrets() -> None:
    s3_config = S3OutputStorageConfig(access_key='AKIA', secret_key='very-secret')

    assert s3_config.access_key.get_secret_value() == 'AKIA'
    assert s3_config.secret_key.get_secret_value() == 'very-secret'
    assert 'very-secret' not in repr(s3_config)
    assert 'very-secret' not in str(s3_config.as_model())
    assert 'access_key' not in s3_config.to_portable_dict()
    assert 'secret_key' not in s3_config.to_portable_dict()


def test_runtime_config_round_trip(
    runtime: Annotated[IsRuntime, pytest.fixture],
    runtime_cls: Annotated[type[IsRuntime], pytest.fixture],
) -> None:
    runtime.config.data.model.dynamically_convert_elements_to_models = True
    runtime.config.data.http.for_host['example.org'].retry_attempts = 2
    runtime.config.job.output_storage.s3.secret_key = 'very-secret'  # type: ignore[assignment]

    portable = runtime.config.to_portable_dict()
    portable_json = json.dumps(portable)

    assert 'very-secret' not in portable_json
    assert 'ui' not in portable['data']
    assert 'file_log_path' not in portable['root_log']
    assert 'stdout' not in portable['root_log']
    assert 'persist_data_dir_path' not in portable['job']['output_storage']['local']

    # The data and job configs are shared through the job and data class creators, so the second
    # runtime needs fresh config objects to show that the values come from the export
    other = runtime_cls()
    other.config.reset_to_defaults()
    assert other.config.data is not runtime.config.data
    assert other.config.data.model.dynamically_convert_elements_to_models is False

    other.config.update_from_portable_dict(json.loads(portable_json))

    assert other.config.to_portable_dict() == portable
    assert other.config.data.model.dynamically_convert_elements_to_models is True
    assert other.config.data.http.for_host['example.org'].retry_attempts == 2
    assert other.config.job.output_storage.s3.secret_key.get_secret_value() == ''

    # Reading a host without its own settings still gives a copy of the defaults
    assert other.config.data.http.for_host['other.org'].retry_attempts == 5
