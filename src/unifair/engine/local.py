from typing import Callable

from unifair.engine.base import Engine


class LocalRunner(Engine):
    @staticmethod
    def task_decorator() -> Callable:
        pass

    @staticmethod
    def result_persisting_task_decorator(result_dir: str) -> Callable:
        pass

    @staticmethod
    def flow_decorator() -> Callable:
        pass

    @staticmethod
    def executable_task_decorator() -> Callable:
        pass