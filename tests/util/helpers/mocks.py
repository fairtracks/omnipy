from omnipy.util.publisher import DataPublisher
import omnipy.util.pydantic as pyd


class MockFoo:
    ...


class MockDataPublisher(DataPublisher):
    foo: MockFoo | None = None
    text: str = 'bar'
    number: int = 42


class MockDataPublisherParent(DataPublisher):
    config: MockDataPublisher = pyd.Field(default_factory=MockDataPublisher)


class MockDataPublisherGrandParent(DataPublisher):
    parent_config: MockDataPublisherParent = pyd.Field(default_factory=MockDataPublisherParent)


class MockAttrSubscriberCls:
    def __init__(self) -> None:
        self.foo: MockFoo | None = None
        self.text: str = ''
        self.number: int = 10

    def set_foo(self, foo: MockFoo | None) -> None:
        self.foo = foo

    def set_text(self, text: str) -> None:
        self.text = text


class MockConfigSubscriberCls:
    def __init__(self) -> None:
        self.config: MockDataPublisher | MockAttrSubscriberCls = MockAttrSubscriberCls()

    def set_config(self, config: MockDataPublisher) -> None:
        self.config = config


class MockParentConfigSubscriberCls:
    def __init__(self) -> None:
        self.parent_config: MockDataPublisherParent | MockConfigSubscriberCls = \
            MockConfigSubscriberCls()

    def set_parent_config(self, parent_config: MockDataPublisherParent) -> None:
        self.parent_config = parent_config
