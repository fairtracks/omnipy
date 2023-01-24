from __future__ import annotations

from abc import ABCMeta
from datetime import datetime
from typing import Optional

from omnipy.api.protocols import IsJobConfig, IsJobConfigHolder, IsTaskRunnerEngine


class JobCreator:
    def __init__(self) -> None:
        self._engine: Optional[IsTaskRunnerEngine] = None
        self._config: Optional[IsJobConfig] = None
        self._nested_context_level: int = 0
        self._time_of_cur_toplevel_nested_context_run: Optional[datetime] = None

    def set_engine(self, engine: IsTaskRunnerEngine) -> None:
        self._engine = engine

    def set_config(self, config: IsJobConfig) -> None:
        self._config = config

    def __enter__(self):
        if self._nested_context_level == 0:
            self._time_of_cur_toplevel_nested_context_run = datetime.now()

        self._nested_context_level += 1

    def __exit__(self, exc_type, exc_value, traceback):
        self._nested_context_level -= 1

        if self._nested_context_level == 0:
            self._time_of_cur_toplevel_nested_context_run = None

    @property
    def engine(self) -> Optional[IsTaskRunnerEngine]:
        return self._engine

    @property
    def config(self) -> Optional[IsJobConfig]:
        return self._config

    @property
    def nested_context_level(self) -> int:
        return self._nested_context_level

    @property
    def time_of_cur_toplevel_nested_context_run(self) -> datetime:
        return self._time_of_cur_toplevel_nested_context_run


class JobBaseMeta(ABCMeta):
    _job_creator: IsJobConfigHolder = JobCreator()

    @property
    def job_creator(self) -> IsJobConfigHolder:
        return self._job_creator

    @property
    def config(self) -> Optional[IsJobConfig]:
        return self.job_creator.config

    @property
    def engine(self) -> Optional[IsTaskRunnerEngine]:
        return self.job_creator.engine

    @property
    def nested_context_level(self) -> int:
        return self.job_creator.nested_context_level
