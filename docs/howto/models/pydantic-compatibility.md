# Pydantic compatibility

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

## What carries over

- Type-driven record definitions
- Parsing/coercion at model boundaries

## What Omnipy adds

- Continuous validation after parsing
- Type-mimicking non-record containers
- Native integration with datasets and compute abstractions

## Example: Pydantic row spec inside Omnipy

```pycon exec="1" source="console"
>>> import omnipy as om
>>> import pydantic as pyd
>>> class BedRow(pyd.v1.BaseModel):
...     chrom: str
...     start: int
...     end: int
...     name: str | None = None
>>> om.Model[BedRow]({'chrom': 'chr1', 'start': '10', 'end': 20})
```

## Trust-builder note

If you are already productive with Pydantic, start with your familiar schema style and add Omnipy
features incrementally.
