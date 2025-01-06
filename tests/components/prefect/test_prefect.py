import logging
import os


def test_no_prefect_console_handler_in_root_logger():
    import omnipy.components.prefect  # noqa: F401

    assert os.environ['PREFECT_LOGGING_SETTINGS_PATH'].endswith('logging.yml')

    assert logging.root.level == logging.WARN

    from prefect.logging.handlers import PrefectConsoleHandler
    assert not any(isinstance(handler, PrefectConsoleHandler) for handler in logging.root.handlers)


def test_only_local_orion():
    import omnipy.components.prefect  # noqa: F401

    assert os.environ['PREFECT_API_KEY'] == ''
    assert os.environ['PREFECT_API_URL'] == ''
