# Column-based tabular validation

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Preview**

    Column-oriented patterns are usable today, but this area is still maturing.

This guide shows how to work with columnar and record-style tables in Omnipy while keeping typed
validation in the flow.

## Columnar input to row-wise records

```pycon exec="1" source="console"
>>> import omnipy as om
>>> columnar = om.ColumnWiseTableWithColNamesModel({
...     'sample': ['s1', 's2'],
...     'count': [10, 20],
... })
>>> columnar.content
{'sample': ['s1', 's2'], 'count': [10, 20]}
>>> columnar.to(om.RowWiseTableWithColNamesModel).content
[{"sample": "s1", "count": 10}, {"sample": "s2", "count": 20}]
```

## Add typed validation on top of records

```pycon exec="1" source="console"
>>> import omnipy as om
>>> import pydantic as pyd
>>> class Row(pyd.v1.BaseModel):
...     sample: str
...     count: int
>>> om.runtime.config.data.model.interactive = True
>>> columnar = om.ColumnWiseTableWithColNamesModel({'sample': ['s1', 's2'], 'count': ['10', '20']})
>>> typed_rows = om.Model[list[Row]](columnar.to(om.RowWiseTableWithColNamesModel).content)
>>> typed_rows.content
[{"sample": "s1", "count": 10}, {"sample": "s2", "count": 20}]
>>> typed_rows[0] = {'sample': 's1', 'count': '11'}
>>> typed_rows.content
[{"sample": "s1", "count": 11}, {"sample": "s2", "count": 20}]
>>> try:
...     typed_rows[0] = {'sample': 's1', 'count': 'bad'}
... except Exception as exc:
...     type(exc).__name__
'ValidationError'
>>> typed_rows.content
[{"sample": "s1", "count": 11}, {"sample": "s2", "count": 20}]
>>> om.runtime.config.data.model.interactive = False
```

With interactive mode enabled (`runtime.config.data.model.interactive = True`), failed assignments
do not leave partial invalid state in the container.

## Omnipy vs Pandera (honest comparison)

### Where Omnipy has advantages

- End-to-end typed flow from nested/JSON/remote ingestion to table-style records.
- Continuous validation behavior integrated with model/dataset operations.
- Practical handling of nested structures before or alongside table conversion.

### Where Pandera wins today

- More mature dedicated dataframe validation ecosystem.
- Richer dataframe-native schema checks and integrations.
- Generally better raw speed for pure dataframe-only validation workloads.

## When to choose which

- Choose Omnipy when tabular validation is one part of a broader typed transformation pipeline.
- Choose Pandera when your core problem is dataframe-first validation at scale.
- Use both when needed: Omnipy for ingestion/transforms, Pandera for dataframe policy gates.
