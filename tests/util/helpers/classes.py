class SomeObject:
    def __init__(self, name: str) -> None:
        self.name = name

    def __eq__(self, other):
        if isinstance(other, SomeObject):
            return self.name == other.name
        return False
