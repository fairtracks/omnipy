from typing import Annotated

import pytest

from omnipy.data._display.constraints import Constraints, ConstraintsSatisfaction


def test_constraints_init(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    constraints = Constraints()
    assert constraints.container_width_per_line_limit is None

    constraints = Constraints(container_width_per_line_limit=40)
    assert constraints.container_width_per_line_limit == 40

    with pytest.raises(TypeError):
        Constraints(40)  # type: ignore[misc]

    with pytest.raises(TypeError):
        Constraints(container_width_per_line_limit=40, extra=123)  # type: ignore[call-arg]


def test_fail_constraints_it_invalid_params(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(ValueError):
        Constraints(container_width_per_line_limit=-1)

    with pytest.raises(ValueError):
        Constraints(container_width_per_line_limit='None')  # type: ignore[arg-type]


def test_constraints_hashable(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    constraints_1 = Constraints()
    constraints_2 = Constraints()
    constraints_3 = Constraints(container_width_per_line_limit=40)
    constraints_4 = Constraints(container_width_per_line_limit=40)

    assert hash(constraints_1) == hash(constraints_2)
    assert hash(constraints_1) != hash(constraints_3)
    assert hash(constraints_3) == hash(constraints_4)


# noinspection PyDataclass
def test_fail_constraints_no_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    constraints = Constraints()

    with pytest.raises(AttributeError):
        constraints.container_width_per_line_limit = 50  # type: ignore[misc]


def test_constraints_satisfaction(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    with pytest.raises(TypeError):
        ConstraintsSatisfaction()  # type: ignore[call-arg]

    satisfied = ConstraintsSatisfaction(Constraints())
    assert satisfied.container_width_per_line_limit is None

    constraints = Constraints(container_width_per_line_limit=20)
    satisfied = ConstraintsSatisfaction(constraints)
    assert satisfied.container_width_per_line_limit is False

    satisfied = ConstraintsSatisfaction(constraints, max_container_width_across_lines=10)
    assert satisfied.container_width_per_line_limit is True

    satisfied = ConstraintsSatisfaction(constraints, max_container_width_across_lines=20)
    assert satisfied.container_width_per_line_limit is True

    satisfied = ConstraintsSatisfaction(constraints, max_container_width_across_lines=30)
    assert satisfied.container_width_per_line_limit is False


def test_constraints_satisfaction_immutable_properties(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    satisfied = ConstraintsSatisfaction(Constraints())
    with pytest.raises(AttributeError):
        satisfied.container_width_per_line_limit = True  # type: ignore[misc]
