import logging

import unifair.config


def assert_logger(logger: logging.Logger) -> None:
    assert logger.name == 'uniFAIR'
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert logger.handlers[0].stream is unifair.config.runtime.stdout
