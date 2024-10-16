from omnipy.modules.tables.datasets import TableListOfDictsOfJsonScalarsDataset
from omnipy.modules.tables.tasks import create_row_index_from_column


def test_create_row_index_from_column():
    in_dataset = TableListOfDictsOfJsonScalarsDataset(
        abc=[{
            'name': 'abc_0', 'x': 33.2, 'y': 14.5
        }, {
            'name': 'abc_1', 'x': 9.2, 'y': 21.3
        }],
        bcd=[{
            'name': 'bcd_0', 'x': 2.34, 'y': 3.3
        }])
    out_dataset = create_row_index_from_column.run(in_dataset, column_key='name')
    assert out_dataset.to_data() == {
        'abc': {
            'abc_0': {
                'x': 33.2, 'y': 14.5
            }, 'abc_1': {
                'x': 9.2, 'y': 21.3
            }
        },
        'bcd': {
            'bcd_0': {
                'x': 2.34, 'y': 3.3
            }
        }
    }
