"""Models for HTTP URLs, URL parts, query strings, and automatic response decoding."""

from pathlib import PurePosixPath
from typing import Any, cast, TypeGuard
from urllib.parse import quote, unquote

from omnipy.data.model import Model
from omnipy.shared.typing import TYPE_CHECKER, TYPE_CHECKING
from omnipy.util.contexts import hold_and_reset_prev_attrib_value
import omnipy.util.pydantic as pyd

from ..json.models import AnyJsonListOrDictModel, JsonListOrDictModel
from ..raw.models import (NestedJoinItemsModel,
                          NestedSplitToItemsModel,
                          StrictBytesModel,
                          StrictStrModel)

__all__ = [
    'QueryParamsModel',
    'UrlPathModel',
    'UrlDataclassModel',
    'HttpUrlModel',
]

QueryParamsSplitterModel = NestedSplitToItemsModel.adjust(
    'QueryParamsSplitterModel', delimiters=('&', '='))

QueryParamsJoinerModel = NestedJoinItemsModel.adjust(
    'QueryParamsJoinerModel', delimiters=('&', '='))


class QueryParamsModel(Model[dict[str, str] | tuple[tuple[str, str], ...] | tuple[str, ...] | str]):
    """Represent URL query parameters as a decoded key-value mapping.

    Args:
        *args: Positional data forwarded to :class:`~omnipy.data.model.Model`.
        **kwargs: Keyword arguments forwarded to
            :class:`~omnipy.data.model.Model`.

    Returns:
        QueryParamsModel: Model instance containing decoded query parameters.

    Raises:
        AssertionError: If tuple-like input does not contain key-value pairs.

    Example:
        >>> params = QueryParamsModel('name=alice&lang=en')
        >>> str(params)
        'name=alice&lang=en'
    """

    if TYPE_CHECKING and TYPE_CHECKER != 'mypy':

        def __new__(cls, *args: Any, **kwargs: Any) -> 'QueryParamsModel_dict':
            ...

    @classmethod
    def _validate_tuple_of_pairs(
            cls, params_list: list[str | list] | str) -> TypeGuard[list[tuple[str, str]]]:
        """Check that each split query parameter contains exactly two elements.

        Args:
            params_list: Split query representation produced by
                ``QueryParamsSplitterModel``.

        Returns:
            bool: ``True`` when every element is a two-item list ``[key, value]``.
        """
        # The validated type is really a list of lists of two items, but we can't express that with
        # Python type hints, so we use a list of tuple pairs instead.
        return all(isinstance(param, list) and len(param) == 2 for param in params_list)

    @classmethod
    def _parse_data(
        cls, data: dict[str, str] | tuple[tuple[str, str], ...] | tuple[str, ...] | str
    ) -> dict[str, str]:
        """Parse supported query-parameter inputs into a decoded mapping.

        Args:
            data: Query parameters as a mapping, tuple pairs, or URL query string.

        Returns:
            dict[str, str]: Decoded query parameters.

    Raises:
        AssertionError: If non-mapping input does not split into key-value pairs.
        """
        if isinstance(data, dict):
            return data

        params_list = QueryParamsSplitterModel(data).content
        assert cls._validate_tuple_of_pairs(params_list), \
            (f'Each parameter must have 2 elements only: [key, value]. '
             f'Incorrect parameter list: {params_list}')

        return dict((unquote(key), unquote(val)) for key, val in params_list)

    def to_data(self) -> str:
        """Serialize query parameters back to a URL-encoded query string.

        Returns:
            str: URL-encoded query string without a leading ``?``.

        Raises:
            AssertionError: If model content is not a dictionary at serialization time.
        """
        with hold_and_reset_prev_attrib_value(self.config.model,
                                              'dynamically_convert_elements_to_models'):
            self.config.model.dynamically_convert_elements_to_models = False
            assert isinstance(self.content, dict)
            url_encoded_content = tuple(
                (quote(key), quote(val)) for key, val in self.content.items())
            return cast(str, QueryParamsJoinerModel(url_encoded_content).to_data())

    def __str__(self) -> str:
        return self.to_data()


if TYPE_CHECKING:

    class QueryParamsModel_dict(QueryParamsModel, dict):  # type: ignore[misc]
        """Type-checking helper refining ``QueryParamsModel`` as ``dict``-like.

        This helper exists only for static typing so query-parameter model
        instances can be treated as decoded string-to-string mappings.
        """

        ...


class UrlPathModel(Model[PurePosixPath | str]):
    """Represent a URL path with path-like joining and mutation helpers.

    Args:
        *args: Positional data forwarded to :class:`~omnipy.data.model.Model`.
        **kwargs: Keyword arguments forwarded to
            :class:`~omnipy.data.model.Model`.

    Returns:
        UrlPathModel: Model instance wrapping a ``PurePosixPath``.

    Raises:
        TypeError: If input cannot be converted to ``PurePosixPath``.

    Example:
        >>> path = UrlPathModel('/api')
        >>> str(path / 'users')
        '/api/users'
    """

    if TYPE_CHECKING and TYPE_CHECKER != 'mypy':

        def __new__(cls, *args: Any, **kwargs: Any) -> 'UrlPathModel_PurePosixPath':
            ...

    @classmethod
    def _parse_data(cls, data: PurePosixPath | str) -> PurePosixPath:
        """Normalize path input to a ``PurePosixPath`` instance.

        Args:
            data: URL path provided as a string or path object.

        Returns:
            PurePosixPath: Normalized path value.

    Raises:
        TypeError: If ``data`` is neither ``str`` nor ``PurePosixPath``.
        """
        return PurePosixPath(data) if isinstance(data, str) else data

    def to_data(self) -> str:
        """Return the normalized URL path as a string.

        Returns:
            str: Path content rendered as a POSIX-style string.
        """

        return str(self.content)

    def __str__(self) -> str:
        return str(self.content)

    def _slash_operator(self, other: PurePosixPath | str | object) -> PurePosixPath:
        content = cast(PurePosixPath, self.content)
        match other:
            case PurePosixPath() | str():
                return content / other
            case _:
                return content / str(other)

    def __truediv__(self, other: PurePosixPath | str | object) -> 'UrlPathModel_PurePosixPath':
        return UrlPathModel(self._slash_operator(other))

    def __floordiv__(self, other: PurePosixPath | str | object) -> 'UrlPathModel_PurePosixPath':
        self.content = self._slash_operator(other)
        return self  # type: ignore[return-value]

    def __add__(self, other: PurePosixPath | str | object) -> 'UrlPathModel_PurePosixPath':
        return UrlPathModel(str(self) + str(other))


if TYPE_CHECKING:

    class UrlPathModel_PurePosixPath(UrlPathModel, PurePosixPath):  # type: ignore[misc]
        """Type-checking helper combining path-model and path-like APIs.

        This helper exists only for static typing to expose both
        ``UrlPathModel`` behavior and ``PurePosixPath`` operations.
        """

        ...


DEFAULT_PORTS = {80, 443}


class UrlDataclassModel(pyd.BaseModel):
    """Store mutable URL components used by :class:`HttpUrlModel`.

    Args:
        scheme: URL scheme, currently expected to be ``http`` or ``https``.
        username: Optional username part of the URL authority.
        password: Optional password part of the URL authority.
        host: Hostname or IP address.
        port: Optional explicit port number.
        path: URL path represented as :class:`UrlPathModel`.
        query: Query parameters represented as :class:`QueryParamsModel`.
        fragment: Optional URL fragment value.

    Returns:
        UrlDataclassModel: Structured URL parts that can be rendered as a URL string.

    Raises:
        pyd.ValidationError: If any URL part violates model field constraints.

    Example:
        >>> parts = UrlDataclassModel(scheme='https', host='example.com')
        >>> str(parts)
        'https://example.com/'
    """
    # Mutable fields
    scheme: str
    username: str | None = None
    password: str | None = None
    host: str = 'localhost'
    port: int | None = None

    if TYPE_CHECKING:
        path: UrlPathModel_PurePosixPath = pyd.Field(default_factory=UrlPathModel)
        query: QueryParamsModel_dict = pyd.Field(default_factory=QueryParamsModel)

    else:
        path: UrlPathModel = pyd.Field(default_factory=UrlPathModel)
        query: QueryParamsModel = pyd.Field(default_factory=QueryParamsModel)

    fragment: str | None = None

    def __str__(self) -> str:
        kwargs: dict[str, str | int] = {}
        for key, val in self.dict().items():
            if val is None:
                continue
            match key:
                case 'port':
                    if val in DEFAULT_PORTS:
                        continue
                    kwargs[key] = val
                case 'path':
                    # Fix for second problem described in
                    # https://github.com/pydantic/pydantic/issues/7186#issuecomment-1912791497
                    if val != '.':
                        kwargs[key] = val.lstrip('/')
                case 'query':
                    if val:
                        kwargs[key] = str(val)
                case _:
                    kwargs[key] = val

        return str(pyd.Url.build(**kwargs))  # type: ignore[arg-type]


class HttpUrlModel(Model[UrlDataclassModel | str]):
    """Represent a validated HTTP or HTTPS URL as a structured model.

    Args:
        *args: Positional data forwarded to :class:`~omnipy.data.model.Model`.
        **kwargs: Keyword arguments forwarded to
            :class:`~omnipy.data.model.Model`.

    Returns:
        HttpUrlModel: Model instance containing validated URL components.

    Raises:
        AssertionError: If the URL scheme is not ``http`` or ``https``.
        pyd.ValidationError: If URL parsing fails.

    Example:
        >>> url = HttpUrlModel('https://example.com/path?q=1')
        >>> str(url)
        'https://example.com/path?q=1'
    """

    if TYPE_CHECKING:

        def __new__(cls, *args: Any, **kwargs: Any) -> 'HttpUrlModel_UrlDataclassModel':
            ...

    @classmethod
    def _parse_data(cls, data: UrlDataclassModel | str) -> UrlDataclassModel:
        """Parse and validate URL data into :class:`UrlDataclassModel`.

        Args:
            data: URL string or prebuilt URL dataclass model.

        Returns:
            UrlDataclassModel: Parsed URL parts with normalized decoded fields.

    Raises:
        AssertionError: If the URL scheme is unsupported.
        pyd.ValidationError: If the URL cannot be parsed.
        """
        if data == '':
            data = 'http://localhost/'
        if data == 'https://':
            data = 'https://localhost/'
        # For validation only
        url_obj = pyd.Url(str(data) if isinstance(data, UrlDataclassModel) else data)

        parts: dict[str, str | int | None] = {}
        for key in UrlDataclassModel.__fields__.keys():
            match key:
                case 'scheme':
                    val = url_obj.scheme
                    assert val in {'http', 'https'}, f'Unsupported scheme: {val}'
                    parts[key] = val
                case 'host':
                    parts[key] = url_obj.unicode_host()
                case 'username' | 'password' | 'path' | 'fragment':
                    val = getattr(url_obj, key)
                    parts[key] = unquote(val) if val is not None else None
                case _:
                    parts[key] = getattr(url_obj, key)

        return UrlDataclassModel(**{
            key: val  # type: ignore[arg-type]
            for key, val in parts.items()
            if val is not None
        })

    def __add__(self, other: str) -> 'HttpUrlModel':
        return HttpUrlModel(str(self) + other)

    def to_data(self) -> str:
        """Return the normalized URL as a string.

        Returns:
            str: Fully rendered HTTP(S) URL string.
        """

        return str(self.content)

    def __str__(self) -> str:
        return str(self.content)


if TYPE_CHECKING:

    class HttpUrlModel_UrlDataclassModel(HttpUrlModel, UrlDataclassModel):  # type: ignore[misc]
        """Type-checking helper combining URL model and URL-part attributes.

        This helper exists only for static typing so parsed URL fields can be
        accessed directly on ``HttpUrlModel`` values.
        """

        ...


class ModelFriendlyMimeType(pyd.BaseModel):
    """Store MIME type parts in a model-friendly immutable representation.

    Args:
        type: MIME top-level type such as ``application`` or ``text``.
        subtype: MIME subtype such as ``json`` or ``plain``.
        suffix: Optional structured syntax suffix.
        parameters: MIME parameters as key-value pairs.

    Returns:
        ModelFriendlyMimeType: MIME parts represented as simple model fields.

    Raises:
        pyd.ValidationError: If supplied fields do not match expected types.
    """
    type: str
    subtype: str
    suffix: str
    parameters: tuple[tuple[str, str], ...]


class ResponseContentPydModel(pyd.BaseModel):
    """Pair response payload data with the content type used for decoding.

    Args:
        content_type: MIME type string or pre-parsed ``ModelFriendlyMimeType``.
        response: Raw decoded payload from HTTP response handling.

    Returns:
        ResponseContentPydModel: Validated wrapper for content type and payload.

    Raises:
        pyd.ValidationError: If the MIME type cannot be parsed.
    """
    content_type: ModelFriendlyMimeType | str
    response: object

    class Config:
        """Configure pydantic behavior for response-wrapper validation.

        Arbitrary payload object types are allowed so decoded response content
        can be preserved without additional wrapping.
        """

        arbitrary_types_allowed = True

    @pyd.validator('content_type', allow_reuse=True)
    def parse_content_type(cls, content_type: ModelFriendlyMimeType | str) -> ModelFriendlyMimeType:
        """Parse MIME content type strings into ``ModelFriendlyMimeType``.

        Args:
            content_type: MIME type value to normalize.

        Returns:
            ModelFriendlyMimeType: Parsed MIME type model.

    Raises:
        ValueError: If MIME parsing fails for a string input.
        """
        from .lazy_import import MimeType, parse_mimetype

        if isinstance(content_type, ModelFriendlyMimeType):
            return content_type

        mime_type: MimeType = parse_mimetype(content_type)
        return ModelFriendlyMimeType(
            type=mime_type.type,
            subtype=mime_type.subtype,
            suffix=mime_type.suffix,
            parameters=tuple(mime_type.parameters.items()),
        )


class AutoResponseContentModel(Model[ResponseContentPydModel | StrictBytesModel | StrictStrModel
                                     | JsonListOrDictModel]):
    """Decode HTTP response content to bytes, text, or JSON from MIME metadata.

    Args:
        *args: Positional data forwarded to :class:`~omnipy.data.model.Model`.
        **kwargs: Keyword arguments forwarded to
            :class:`~omnipy.data.model.Model`.

    Returns:
        AutoResponseContentModel: Model containing auto-decoded response content.

    Raises:
        AssertionError: If wrapped response metadata is missing parsed MIME type data.
    """
    class Config(Model.Config):
        """Configure union parsing for automatic response-content decoding.

        Smart-union matching is disabled so MIME-driven model selection for
        bytes, text, and JSON remains explicit.
        """

        smart_union = False

    @classmethod
    def _parse_data(  # type: ignore[override]
        cls,
        data: ResponseContentPydModel | StrictBytesModel | StrictStrModel | AnyJsonListOrDictModel
    ) -> StrictBytesModel | StrictStrModel | AnyJsonListOrDictModel:
        """Choose response model type from MIME type and payload.

        Args:
            data: Wrapped response metadata or pre-decoded response model.

        Returns:
            StrictBytesModel | StrictStrModel | AnyJsonListOrDictModel: Response model selected
            from MIME metadata.

        Raises:
            AssertionError: If wrapped input is missing parsed MIME type data.
        """
        if isinstance(data, ResponseContentPydModel):
            assert isinstance(data.content_type, ModelFriendlyMimeType)

            mimetype_tuple = (data.content_type.type, data.content_type.subtype)
            match mimetype_tuple:
                case ('application', 'json'):
                    return JsonListOrDictModel(data.response)
                case ('text', 'plain'):
                    return StrictStrModel(data.response)
                case ('application', 'octet-stream') | _:
                    return StrictBytesModel(data.response)
        else:
            return data
