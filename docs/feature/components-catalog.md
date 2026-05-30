# Components catalog

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Now**

## 1) What it solves

You need a quick map of bundled component families to choose the right starting abstraction.

## 2) The idea

Omnipy ships component groups for common data/interoperability patterns:

- **General**
- **JSON**
- **Nested**
- **Raw**
- **Remote**
- **Tables**

## 3) Example

```pycon exec="1" source="console"
>>> from omnipy import JsonListOfDictsDataset
>>> ds = JsonListOfDictsDataset({'rows': [{'id': 'a', 'x': 1}, {'id': 'b', 'x': 2}]})
>>> ds.to_data()
```

## 4) Output / display

```pycon exec="1" source="console"
>>> from omnipy import JsonListOfDictsDataset
>>> ds = JsonListOfDictsDataset({'rows': [{'id': 'a', 'x': 1}, {'id': 'b', 'x': 2}]})
>>> print(ds._docs())
```

## 5) When to use / when not

Use these components when standard Python containers plus one-off glue stop scaling for your
pipeline.

If plain `Model[T]`/`Dataset[...]` already solves your case, stay simple.

## 6) Gotchas

- Depth differs by area; some families are richer than others.
- Prefer examples and APIs that exist today (Now/Preview/Planned labels matter).

## 7) Links

- Feature: [Declarative conversions](declarative-conversions.md)
- How-to: [Domain formats](../howto/components/domain-formats.md)
