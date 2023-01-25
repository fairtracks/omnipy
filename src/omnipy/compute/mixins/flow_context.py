from datetime import datetime

from omnipy.api.protocols import IsNestedContext


class FlowContextJobMixin:
    def __init__(self) -> None:
        self._time_of_last_run = None

    @property
    def flow_context(self) -> IsNestedContext:
        class FlowContext:
            @classmethod
            def __enter__(cls):
                self.__class__.job_creator.__enter__()
                self._time_of_last_run = self.time_of_cur_toplevel_flow_run

            @classmethod
            def __exit__(cls, exc_type, exc_val, exc_tb):
                self.__class__.job_creator.__exit__(exc_type, exc_val, exc_tb)

        return FlowContext()

    @property
    def time_of_last_run(self) -> datetime:
        return self._time_of_last_run
