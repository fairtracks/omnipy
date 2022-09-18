from typing import Callable, Dict, Type

from prefect import Flow, task
from prefect.engine.results import LocalResult

from unifair.data.serializer import Serializer
from unifair.engine.engine import Engine
from unifair.modules.json.serializers import JsonDatasetToTarFileSerializer
from unifair.modules.pandas.serializers import PandasDatasetToTarFileSerializer

DEFAULT_DATASET_TYPE_TO_SERIALIZER_MAP = {
    'JsonDataset': JsonDatasetToTarFileSerializer,
    'PandasDataset': PandasDatasetToTarFileSerializer
}


class PrefectEngine(Engine):
    def __init__(
            self,
            dataset_type_to_serializer: Dict[str, Type[Serializer]] =
                DEFAULT_DATASET_TYPE_TO_SERIALIZER_MAP):  # yapf: disable
        self._dataset_type_to_serializer_map = dataset_type_to_serializer

    def result_persisting_task_decorator(self, result_dir):
        def _decorate_task_with_result_persistence(task_func):
            return_type = task_func.__annotations__['return'].__name__
            return task(
                task_func,
                checkpoint=True,
                result=LocalResult(
                    dir=result_dir,
                    location='{task_name}_{date}.tar.gz',
                    serializer=self._dataset_type_to_serializer_map[return_type],
                ),
            )

        return _decorate_task_with_result_persistence

    @staticmethod
    def task_decorator():
        def _decorate_task(task_func):
            return task(task_func)

        return _decorate_task

    @staticmethod
    def flow_decorator():
        class FlowDecorator:
            def __init__(self, flow_func: Callable):
                flow_tasks = flow_func()

                with Flow(name=flow_func.__name__) as flow:
                    for i, _task in enumerate(flow_tasks):
                        if i == 0:
                            output = _task()
                        else:
                            output = _task(output)

                self._flow = flow

            def __call__(self):
                return list(self._flow.run().result.values())[-1].result

        return FlowDecorator

    @staticmethod
    def executable_task_decorator():
        class ExecutableTaskDecorator:
            def __init__(self, task_func: Callable):
                self._flow = Flow(name=task_func.__name__)
                self._flow.add_task(task_func)

            def __call__(self):
                return list(self._flow.run().result.values())[-1].result

        return ExecutableTaskDecorator
