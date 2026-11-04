from omnipy.data.dataset import Dataset
from omnipy.data.model import Model


def test_docs_renders_dataset_list_by_default_and_peek_on_request() -> None:
    dataset = Dataset[Model[list[int]]](first=[1, 2], second=[3])

    default_output = dataset._docs()
    peek_output = dataset._docs(method='peek')

    assert 'Data file name' in default_output
    assert 'Data file name' not in peek_output
    assert 'first' in peek_output
    assert 'second' in peek_output
