from dataclasses import dataclass

from omnipy.util.publisher import DataPublisher


class MockFoo:
    ...


@dataclass
class MockDataPublisher(DataPublisher):
    foo: MockFoo | None = None
    text: str = 'bar'
    number: int = 42


class MockSubscriberCls:
    def __init__(self):
        self.foo: MockFoo | None = None
        self.text: str = ''

    def set_foo(self, foo: MockFoo | None) -> None:
        self.foo = foo

    def set_text(self, text: str) -> None:
        self.text = text
