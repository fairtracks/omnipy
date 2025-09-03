from typing import Annotated

import pytest

from omnipy.config import ConfigBase
from omnipy.data._display.integrations.jupyter.helpers import ReactiveConfigCopy


class MyChildConfig(ConfigBase):
    param2: int = 0


class MyConfig(ConfigBase):
    param1: str = 'default'
    child: MyChildConfig = MyChildConfig()


class MyParentConfig(ConfigBase):
    config: MyConfig = MyConfig()


@pytest.fixture
def parent() -> MyParentConfig:
    parent = MyParentConfig(config=MyConfig(
        param1='test',
        child=MyChildConfig(param2=10),
    ))
    return parent


def test_reactive_config_copy_init(parent: Annotated[MyParentConfig, pytest.fixture]) -> None:
    reactive_config_copy = ReactiveConfigCopy(parent.config)

    assert reactive_config_copy.value.param1 == 'test'
    assert reactive_config_copy.value.child.param2 == 10

    parent.config.param1 = 'updated'
    parent.config.child.param2 = 15

    assert reactive_config_copy.value.param1 == 'test'
    assert reactive_config_copy.value.child.param2 == 10


def test_reactive_config_copy_set(parent: Annotated[MyParentConfig, pytest.fixture]) -> None:
    reactive_config_copy = ReactiveConfigCopy(parent.config)

    assert reactive_config_copy.value.param1 == 'test'
    assert reactive_config_copy.value.child.param2 == 10

    parent.config.param1 = 'updated'
    parent.config.child.param2 = 15

    reactive_config_copy.set(parent.config)

    assert reactive_config_copy.value.param1 == 'updated'
    assert reactive_config_copy.value.child.param2 == 15


def test_reactive_config_copy_subscribe_with_set(
        parent: Annotated[MyParentConfig, pytest.fixture]) -> None:
    reactive_config_copy = ReactiveConfigCopy(parent.config)

    assert reactive_config_copy.value.param1 == 'test'
    assert reactive_config_copy.value.child.param2 == 10

    parent.subscribe_attr(
        'config',
        reactive_config_copy.set,
    )

    parent.config.param1 = 'new value'

    assert reactive_config_copy.value.param1 == 'new value'
    assert reactive_config_copy.value.child.param2 == 10

    parent.config.child.param2 = 5

    assert reactive_config_copy.value.param1 == 'new value'
    assert reactive_config_copy.value.child.param2 == 5
