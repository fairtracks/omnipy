"""Tests for job keyword arguments that no loaded mixin declares, and for optional job mixins."""

import logging
from types import MappingProxyType
from typing import Annotated

import pytest

from omnipy import TaskTemplate
from omnipy.compute._job import JobBase
from omnipy.compute._mixins.unclaimed_kwargs import SILENCE_UNCLAIMED_KWARGS_WARNING_ENV_VAR
from omnipy.shared.protocols.hub.runtime import IsRuntime

WARNING_TEXT = 'ignores keyword arguments not used by any loaded job mixin'


class PluginOptionsJobMixin:
    """Job mixin standing in for a plugin's per-job options."""

    def __init__(self, *, plugin_image: str | None = None, plugin_split: str = 'none'):
        self._plugin_image = plugin_image
        self._plugin_split = plugin_split

    @property
    def plugin_image(self) -> str | None:
        return self._plugin_image

    @property
    def plugin_split(self) -> str:
        return self._plugin_split


def _accept_plugin_mixin() -> None:
    JobBase.accept_mixin(PluginOptionsJobMixin, optional=True)


def test_unknown_keywords_are_kept_on_templates(
    runtime: Annotated[IsRuntime, pytest.fixture],
) -> None:
    @TaskTemplate(plugin_image='image:1')
    def task(a: int) -> int:
        return a

    assert dict(task.unclaimed_kwargs) == {'plugin_image': 'image:1'}
    assert dict(task.refine(name='other').unclaimed_kwargs) == {'plugin_image': 'image:1'}
    assert task.refine(plugin_image='image:2') != task
    assert task.refine(name='task') == task


def test_unknown_keyword_values_are_frozen_and_merged_by_refine(
    runtime: Annotated[IsRuntime, pytest.fixture],
) -> None:
    @TaskTemplate(plugin_resources={'cpu_cores': 1, 'ram_gb': 2}, plugin_tags=['a', 'b'])
    def task(a: int) -> int:
        return a

    assert isinstance(task.unclaimed_kwargs['plugin_resources'], MappingProxyType)
    assert task.unclaimed_kwargs['plugin_tags'] == ('a', 'b')

    refined = task.refine(plugin_resources={'ram_gb': 4})
    assert dict(refined.unclaimed_kwargs['plugin_resources']) == {'cpu_cores': 1, 'ram_gb': 4}


def test_warning_for_unclaimed_keywords_at_apply_only(
    runtime: Annotated[IsRuntime, pytest.fixture],
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING):

        @TaskTemplate(plugin_imgae='typo')
        def task(a: int) -> int:
            return a

        assert WARNING_TEXT not in caplog.text

        assert task.run(1) == 1

    assert WARNING_TEXT in caplog.text
    assert '"plugin_imgae"' in caplog.text


def test_warning_can_be_silenced(
    runtime: Annotated[IsRuntime, pytest.fixture],
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(SILENCE_UNCLAIMED_KWARGS_WARNING_ENV_VAR, '1')

    @TaskTemplate(plugin_imgae='typo')
    def task(a: int) -> int:
        return a

    with caplog.at_level(logging.WARNING):
        assert task.run(1) == 1

    assert WARNING_TEXT not in caplog.text


def test_mixin_loaded_after_template_claims_keywords_at_apply(
    runtime: Annotated[IsRuntime, pytest.fixture],
    restore_job_base_mixins: Annotated[None, pytest.fixture],
    caplog: pytest.LogCaptureFixture,
) -> None:
    @TaskTemplate(plugin_image='image:1')
    def task(a: int) -> int:
        return a

    assert not hasattr(task, 'plugin_image')

    _accept_plugin_mixin()

    with caplog.at_level(logging.WARNING):
        job = task.apply()

    assert job.plugin_image == 'image:1'  # type: ignore[attr-defined]
    assert dict(job.unclaimed_kwargs) == {}
    assert WARNING_TEXT not in caplog.text
    assert job(2) == 2


def test_optional_mixin_only_added_when_keyword_differs_from_default(
    runtime: Annotated[IsRuntime, pytest.fixture],
    restore_job_base_mixins: Annotated[None, pytest.fixture],
) -> None:
    _accept_plugin_mixin()

    @TaskTemplate()
    def plain(a: int) -> int:
        return a

    @TaskTemplate(plugin_split='none')
    def at_default(a: int) -> int:
        return a

    @TaskTemplate(plugin_split='steps')
    def with_option(a: int) -> int:
        return a

    assert not hasattr(plain, 'plugin_split')
    assert not hasattr(plain.apply(), 'plugin_split')
    assert not hasattr(at_default, 'plugin_split')
    assert dict(at_default.unclaimed_kwargs) == {}

    assert with_option.plugin_split == 'steps'  # type: ignore[attr-defined]
    assert with_option.plugin_image is None  # type: ignore[attr-defined]
    assert with_option.apply().plugin_split == 'steps'  # type: ignore[attr-defined]

    refined_plain = plain.refine(name='refined')
    assert not hasattr(refined_plain, 'plugin_split')
    assert 'plugin_split' not in refined_plain._get_init_kwargs()


def test_optional_mixin_with_activation_function(
    runtime: Annotated[IsRuntime, pytest.fixture],
    restore_job_base_mixins: Annotated[None, pytest.fixture],
) -> None:
    active = False
    JobBase.accept_mixin(PluginOptionsJobMixin, optional=True, activate_if=lambda: active)

    @TaskTemplate()
    def task(a: int) -> int:
        return a

    assert not hasattr(task.apply(), 'plugin_split')

    active = True
    job = task.apply()
    assert job.plugin_split == 'none'  # type: ignore[attr-defined]
    assert job(3) == 3
