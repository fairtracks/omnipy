from omnipy.components.seqcol.models import SeqColLevel0DigestModel, SeqColLevel2Model
from omnipy.data.model import Model


class SeqColServiceUrlProvider:
    def __init__(self, server_url: str) -> None:
        self._server_url = server_url

    def get_url(self, data, return_type: type[Model]) -> str:
        if isinstance(data, SeqColLevel0DigestModel) and return_type is SeqColLevel2Model:
            return f'{self._server_url}/collection/{data.to_data()}?level=2'
        else:
            raise ValueError(f'Unsupported data and return type combination: '
                             f'{type(data)} and {return_type}')
