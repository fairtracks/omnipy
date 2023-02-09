# @pytest.mark.skipif(os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1', reason='To be implemented later')
import logging


def test_no_root_logger():
    import omnipy.modules.prefect

    assert logging.root.level == logging.WARN
    print(logging.root.handlers)
    assert len(logging.root.handlers) == 0
