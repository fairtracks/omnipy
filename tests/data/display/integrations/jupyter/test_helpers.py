from solara import Reactive

from omnipy.data._display.integrations.jupyter.helpers import AvailableDisplayDimsRegistry


def test_available_display_dims_registry() -> None:
    registry = AvailableDisplayDimsRegistry()
    assert len(registry) == 0

    available_display_dims = registry.new_reactive_obj()
    assert len(registry) == 1
    assert isinstance(available_display_dims, Reactive)
    assert available_display_dims.value['width'] == 80
    assert available_display_dims.value['height'] == 24

    available_display_dims.set({'width': 100, 'height': 48})
    assert available_display_dims.value['width'] == 100
    assert available_display_dims.value['height'] == 48

    available_display_dims_2 = registry.new_reactive_obj()
    assert len(registry) == 2
    assert isinstance(available_display_dims_2, Reactive)
    assert available_display_dims_2.value['width'] == 80
    assert available_display_dims_2.value['height'] == 24

    assert available_display_dims is not available_display_dims_2

    keys = [_ for _ in registry.keys()]
    assert len(keys) == 2
    assert keys[0] != keys[1]

    values = [_ for _ in registry.values()]
    assert len(values) == 2
    assert values[0] is available_display_dims
    assert values[1] is available_display_dims_2

    registry.remove_reactive_obj(available_display_dims)
    assert len(registry) == 1
    assert available_display_dims not in registry.values()
    assert available_display_dims_2 in registry.values()

    registry.remove_reactive_obj(available_display_dims_2)
    assert len(registry) == 0
    assert available_display_dims_2 not in registry.values()
