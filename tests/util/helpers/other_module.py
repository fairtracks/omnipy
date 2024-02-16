from omnipy.util.helpers import get_calling_module_name


# For test_helpers::test_get_calling_module_name
def other_module_call_get_calling_module_name() -> str:
    return get_calling_module_name()


calling_module_name_when_importing_other_module = get_calling_module_name()
