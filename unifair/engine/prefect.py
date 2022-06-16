from prefect import Flow
from prefect import task
from prefect.engine.results import LocalResult


def result_persisting_task_decorator(result_dir, result_type_to_serializer_map):
    def _decorate_task_with_result_persistence(task_func):
        return_type = task_func.__annotations__['return'].__name__
        return task(
            task_func,
            checkpoint=True,
            result=LocalResult(
                dir=result_dir,
                location='{task_name}_{date}.tar.gz',
                serializer=result_type_to_serializer_map[return_type],
            ),
        )

    return _decorate_task_with_result_persistence


def get_executable_task_decorator():
    class ExecutableTaskDecorator:
        def __init__(self, task_func):
            self._flow = Flow(name=task_func.__name__)
            self._flow.add_task(task_func)

        def __call__(self):
            self._flow.run()

    return ExecutableTaskDecorator
