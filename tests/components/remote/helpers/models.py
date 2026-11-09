"""Typed page generation and merge declarations for remote-loading examples."""

from omnipy.components.general.models import ConverterModel
from omnipy.components.remote.models import HttpUrlModel, PagesInfo
import omnipy.util.pydantic as pyd


class ObservationPagesInfo(PagesInfo):
    base_url: pyd.HttpUrl
    endpoint: str = 'observations'


class ObservationPageUrl(ConverterModel[ObservationPagesInfo, HttpUrlModel]):
    @classmethod
    def _convert(cls, data: ObservationPagesInfo) -> HttpUrlModel:
        url = HttpUrlModel(data.base_url)
        url.path // 'api' // data.endpoint
        url.query['page'] = data.page
        if data.items_per_page is not None:
            url.query['limit'] = data.items_per_page
        return url
