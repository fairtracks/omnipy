class Void:
    """
    Empty sync/async iterable for signature-only generator flow bodies.

    Use this when a flow template body exists only to define a generator or
    async-generator callable signature, while the child jobs perform the
    actual work.

    Examples:
        @LinearFlowTemplate(task_one, generator_task_two)
        def my_sync_generator_flow(number: int) -> Generator[int, None, None]:
            yield from Void()  # For generator signature only; never run.

        @DagFlowTemplate(task_one, generator_task_two)
        async def my_async_generator_flow(number: int) -> AsyncGenerator[int, None]:
            async for _ in Void():  # For generator signature only; never run.
                yield _
    """

    def __iter__(self):
        return iter(())

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration
