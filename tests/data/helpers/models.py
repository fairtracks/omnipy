from unifair.data.model import Model


class StringToLength(Model[str]):
    @classmethod
    def _parse_data(cls, data: str) -> int:
        return len(data)
