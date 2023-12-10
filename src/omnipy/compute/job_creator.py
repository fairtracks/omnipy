from abc import ABCMeta
from datetime import datetime

from omnipy.api.protocols.private.compute.job_creator import IsJobCreator
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.public.config import IsJobConfig


class JobCreator:
    def __init__(self) -> None:
        self._engine: IsEngine | None = None
        self._config: IsJobConfig | None = None
        self._nested_context_level: int = 0
        self._time_of_cur_toplevel_nested_context_run: datetime | None = None

    def set_engine(self, engine: IsEngine) -> None:
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
    def engine(self) -> IsEngine | None:
        return self._engine

    @property
    def config(self) -> IsJobConfig | None:
        return self._config

    @property
    def nested_context_level(self) -> int:
        return self._nested_context_level

    @property
    def time_of_cur_toplevel_nested_context_run(self) -> datetime | None:
        return self._time_of_cur_toplevel_nested_context_run


class JobBaseMeta(ABCMeta):
    """"""
    _job_creator_obj = JobCreator()

    @property
    def job_creator(self) -> IsJobCreator:
        return self._job_creator_obj

    @property
    def nested_context_level(self) -> int:
        return self.job_creator.nested_context_level
