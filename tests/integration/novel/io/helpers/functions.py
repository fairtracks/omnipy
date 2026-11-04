"""Helper functions for public I/O integration tests."""

from omnipy.data.dataset import is_dataset_instance
from omnipy.data.model import is_model_instance


def expected_for(result: object, expected_model: object, expected_dataset: object) -> object:
    """Return the expected data for a Dataset, a Model wrapping one, or another Model."""
    content = result
    while is_model_instance(content):
        content = content.content
    return expected_dataset if is_dataset_instance(content) else expected_model
