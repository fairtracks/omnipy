from omnipy.config import ConfigBase
from omnipy.config.data import HttpConfig
from omnipy.data.model import is_model_instance


def test_config_as_model() -> None:
    from omnipy.components.json.models import JsonDictModel

    class MyConfig(ConfigBase):
        param1: int = 10
        param2: str = 'default'

    config = MyConfig(param1=20, param2='custom')
    model = config.as_model()
    assert is_model_instance(model)
    assert isinstance(model, JsonDictModel)
    assert model['param1'] == 20
    assert model['param2'] == 'custom'


def test_http_config_schema_generation_for_defaultdict() -> None:
    schema = HttpConfig.model_json_schema()

    assert 'for_host' in schema['properties']
