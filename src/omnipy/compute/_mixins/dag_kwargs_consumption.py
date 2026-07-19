"""Mixin for controlling DAG keyword-argument consumption behavior."""


class DagKwargsConsumptionJobMixin:
    """Store whether DAG child matching should consume keys from accumulated results."""
    def __init__(self, *, consume_kwargs_from_results: bool = True) -> None:
        if not isinstance(consume_kwargs_from_results, bool):
            raise TypeError('consume_kwargs_from_results must be a bool')

        self._consume_kwargs_from_results = consume_kwargs_from_results

    @property
    def consume_kwargs_from_results(self) -> bool:
        return self._consume_kwargs_from_results
