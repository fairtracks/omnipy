class MyPath():
    def __init__(self, *args, **kwargs):
        self._path = args[0] if len(args) > 0 else '.'

    def __eq__(self, other):
        return self._path == other._path

    def __str__(self):
        return self._path

    def __truediv__(self, append_path: str) -> 'MyPath':
        return MyPath(f'{self._path}/{append_path}')