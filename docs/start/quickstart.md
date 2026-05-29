# 10-minute Quickstart

This quickstart walks through install → model parsing → safe editing → dataset conversion.

## 1) Install

Follow [Install](install.md).

## 2) Parse messy input into a typed model

```pycon exec="1" session="quickstart" source="console"
>>> from omnipy import Model, runtime
>>> runtime.config.root_log.log_to_stdout = False
>>> runtime.config.root_log.log_to_stderr = False
>>> runtime.config.root_log.log_to_file = False
>>> runtime.config.job.output_storage.persist_outputs = 'disabled'
>>> runtime.config.data.model.interactive = True
>>> readings = Model[list[int]]((101, '102', 103.0))
>>> readings
```

```pycon exec="1" session="quickstart" result="console" html="true"
>>> print(readings._docs())
```

## 3) Safe interactive manipulation

```pycon exec="1" session="quickstart" source="console"
>>> try:
...     readings.append('invalid')
... except Exception as err:
...     print(type(err).__name__)
>>> readings
```

```pycon exec="1" session="quickstart" result="console" html="true"
>>> print(readings._docs())
```

## 4) Build a Dataset and batch-parse values

```pycon exec="1" session="quickstart" source="console"
>>> from omnipy import Dataset
>>> batch = Dataset[Model[int]]({'sample_a': '1', 'sample_b': 2.0, 'sample_c': 3})
>>> batch
```

```pycon exec="1" session="quickstart" result="console" html="true"
>>> print(batch._docs())
```

## 5) Convert nested records to pandas-ready tables

```pycon exec="1" session="quickstart" source="console"
>>> from omnipy import JsonListOfDictsDataset, PandasDataset
>>> records = JsonListOfDictsDataset({'rows': [{'id': 'a', 'value': '1'}, {'id': 'b', 'value': 2}]})
>>> records
>>> records_pd = records.to(PandasDataset)
>>> records_pd
```

```pycon exec="1" session="quickstart" result="console" html="true"
>>> print(records_pd._docs())
```

## Next steps

- [Tutorial 1: Interactive safety](../tutorials/01-interactive-safety.md)
- [Tutorial 2: Nested JSON to tables](../tutorials/02-json-to-tables.md)
- [Tutorial 3: Dataset batch](../tutorials/03-dataset-batch.md)
