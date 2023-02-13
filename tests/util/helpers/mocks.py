from dataclasses import dataclass
from typing import Optional

from omnipy.util.publisher import DataPublisher


class MockFoo:
    ...


@dataclass
class MockDataPublisher(DataPublisher):
    foo: Optional[MockFoo] = None
    text: str = 'bar'
    number: int = 42


class MockSubscriberCls:
    def __init__(self):
        self.foo: Optional[MockFoo] = None
        self.text: str = ''

    def set_foo(self, foo: Optional[MockFoo]) -> None:
        self.foo = foo

    def set_text(self, text: str) -> None:
        self.text = text
