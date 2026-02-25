from abc import ABC, abstractmethod

from omnipy.components.remote.models import HttpUrlModel
from omnipy.components.seqcol.models import SeqColLevel0DigestModel, SeqColLevel2Model
from omnipy.data.model import Model


class UrlProvider(ABC):
    @abstractmethod
    def get_url(self, data: object, return_type: type[Model]) -> HttpUrlModel:
        ...


class SeqColServiceUrlProvider(UrlProvider):
    def __init__(self, server_url: str) -> None:
        self._server_url = server_url

    def get_url(self, data: object, return_type: type[Model]) -> HttpUrlModel:
        if isinstance(data, SeqColLevel0DigestModel) and return_type is SeqColLevel2Model:
            url = HttpUrlModel(self._server_url)
            url.path = url.path / 'collection' / data
            url.query['level'] = 2
            return url
        else:
            raise ValueError(f'Unsupported data and return type combination: '
                             f'{type(data)} and {return_type}')
