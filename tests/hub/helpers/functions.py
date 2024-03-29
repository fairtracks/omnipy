import logging

import omnipy.hub


def assert_logger(logger: logging.Logger) -> None:
    assert logger.name == 'omnipy'
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert logger.handlers[0].stream is omnipy.hub.runtime.stdout
