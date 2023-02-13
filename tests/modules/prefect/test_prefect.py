import logging
import os


def test_no_root_logger():
    import omnipy.modules.prefect

    assert os.environ['PREFECT_LOGGING_SETTINGS_PATH'].endswith('logging.yml')

    assert logging.root.level == logging.WARN
    print(logging.root.handlers)
    assert len(logging.root.handlers) == 0


def test_only_local_orion():
    import omnipy.modules.prefect

    assert os.environ['PREFECT_API_KEY'] == ''
    assert os.environ['PREFECT_API_URL'] == ''
