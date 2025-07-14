import pytest

from omnipy.data._display.constraints import Constraints, ConstraintsSatisfaction


def test_constraints_init() -> None:
    constraints = Constraints()
    assert constraints.max_inline_container_width_incl is None

    constraints = Constraints(
        max_inline_container_width_incl=40,
        max_inline_list_or_dict_width_excl=36,
    )
    assert constraints.max_inline_container_width_incl == 40
    assert constraints.max_inline_list_or_dict_width_excl == 36

    with pytest.raises(TypeError):
        Constraints(40)  # type: ignore[misc]

    with pytest.raises(TypeError):
        Constraints(max_inline_container_width_incl=40, extra=123)  # type: ignore[call-arg]


def test_fail_constraints_it_invalid_params() -> None:
    with pytest.raises(ValueError):
        Constraints(max_inline_container_width_incl=-1)

    with pytest.raises(ValueError):
        Constraints(max_inline_list_or_dict_width_excl=-1)

    with pytest.raises(ValueError):
        Constraints(max_inline_container_width_incl='None')  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        Constraints(max_inline_list_or_dict_width_excl='None')  # type: ignore[arg-type]


def test_constraints_hashable() -> None:
    constraints_1 = Constraints()
    constraints_2 = Constraints()
    constraints_3 = Constraints(max_inline_container_width_incl=40)
    constraints_4 = Constraints(max_inline_container_width_incl=40)
    constraints_5 = Constraints(max_inline_list_or_dict_width_excl=30)
    constraints_6 = Constraints(max_inline_list_or_dict_width_excl=30)

    assert hash(constraints_1) == hash(constraints_2)
    assert hash(constraints_1) != hash(constraints_3)
    assert hash(constraints_1) != hash(constraints_4)
    assert hash(constraints_3) == hash(constraints_4)
    assert hash(constraints_4) != hash(constraints_5)
    assert hash(constraints_5) == hash(constraints_6)


# noinspection PyDataclass
def test_fail_constraints_no_assignments() -> None:
    constraints = Constraints()

    with pytest.raises(AttributeError):
        constraints.max_inline_container_width_incl = 50  # type: ignore[misc]

    with pytest.raises(AttributeError):
        constraints.max_inline_list_or_dict_width_excl = 50  # type: ignore[misc]


def test_constraints_satisfaction() -> None:
    with pytest.raises(TypeError):
        ConstraintsSatisfaction()  # type: ignore[call-arg]

    satisfied = ConstraintsSatisfaction(Constraints())
    assert satisfied.max_inline_container_width_incl is None
    assert satisfied.max_inline_list_or_dict_width_excl is None

    constraints = Constraints(
        max_inline_container_width_incl=25,
        max_inline_list_or_dict_width_excl=15,
    )
    satisfied = ConstraintsSatisfaction(constraints)
    assert satisfied.max_inline_container_width_incl is False
    assert satisfied.max_inline_list_or_dict_width_excl is False

    satisfied = ConstraintsSatisfaction(constraints, max_inline_container_width_incl=10)
    assert satisfied.max_inline_container_width_incl is True
    assert satisfied.max_inline_list_or_dict_width_excl is False

    satisfied = ConstraintsSatisfaction(constraints, max_inline_list_or_dict_width_excl=15)
    assert satisfied.max_inline_container_width_incl is False
    assert satisfied.max_inline_list_or_dict_width_excl is True

    satisfied = ConstraintsSatisfaction(constraints, max_inline_container_width_incl=20)
    assert satisfied.max_inline_container_width_incl is True
    assert satisfied.max_inline_list_or_dict_width_excl is False

    satisfied = ConstraintsSatisfaction(constraints, max_inline_list_or_dict_width_excl=20)
    assert satisfied.max_inline_container_width_incl is False
    assert satisfied.max_inline_list_or_dict_width_excl is False

    satisfied = ConstraintsSatisfaction(constraints, max_inline_container_width_incl=30)
    assert satisfied.max_inline_container_width_incl is False
    assert satisfied.max_inline_list_or_dict_width_excl is False

    satisfied = ConstraintsSatisfaction(constraints, max_inline_list_or_dict_width_excl=30)
    assert satisfied.max_inline_container_width_incl is False
    assert satisfied.max_inline_list_or_dict_width_excl is False


def test_constraints_satisfaction_immutable_properties() -> None:
    satisfied = ConstraintsSatisfaction(Constraints())
    with pytest.raises(AttributeError):
        satisfied.max_inline_container_width_incl = True  # type: ignore[misc]
        satisfied.max_inline_list_or_dict_width_excl = True  # type: ignore[misc]


def test_constraints_satisfaction_repr() -> None:
    # Test case with no constraint limit (None)
    satisfied = ConstraintsSatisfaction(Constraints())
    expected = ('ConstraintsSatisfaction(max_inline_container_width_incl=None, '
                'max_inline_list_or_dict_width_excl=None)')
    assert repr(satisfied) == expected

    # Test case with constraint limit but no max_inline_container_width_incl (False)
    constraints = Constraints(
        max_inline_container_width_incl=20,
        max_inline_list_or_dict_width_excl=10,
    )
    satisfied = ConstraintsSatisfaction(constraints)
    expected = ('ConstraintsSatisfaction(max_inline_container_width_incl=False, '
                'max_inline_list_or_dict_width_excl=False)')
    assert repr(satisfied) == expected

    # Test case where max width is within limit (True)
    satisfied = ConstraintsSatisfaction(
        constraints,
        max_inline_container_width_incl=10,
        max_inline_list_or_dict_width_excl=10,
    )
    expected = ('ConstraintsSatisfaction(max_inline_container_width_incl=True, '
                'max_inline_list_or_dict_width_excl=True)')
    assert repr(satisfied) == expected

    # Test case where max width exceeds limit (False)
    satisfied = ConstraintsSatisfaction(
        constraints,
        max_inline_container_width_incl=30,
        max_inline_list_or_dict_width_excl=20,
    )
    expected = ('ConstraintsSatisfaction(max_inline_container_width_incl=False, '
                'max_inline_list_or_dict_width_excl=False)')
    assert repr(satisfied) == expected

    # Test edge case with zero constraint limit
    constraints_zero = Constraints(
        max_inline_container_width_incl=0,
        max_inline_list_or_dict_width_excl=0,
    )
    satisfied = ConstraintsSatisfaction(
        constraints_zero,
        max_inline_container_width_incl=0,
        max_inline_list_or_dict_width_excl=0,
    )
    expected = ('ConstraintsSatisfaction(max_inline_container_width_incl=True, '
                'max_inline_list_or_dict_width_excl=True)')
    assert repr(satisfied) == expected

    # Test edge case where max width is 0 but limit is positive
    satisfied = ConstraintsSatisfaction(
        constraints,
        max_inline_container_width_incl=0,
        max_inline_list_or_dict_width_excl=0,
    )
    expected = ('ConstraintsSatisfaction(max_inline_container_width_incl=True, '
                'max_inline_list_or_dict_width_excl=True)')
    assert repr(satisfied) == expected
