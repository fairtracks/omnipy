# Components catalog

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Now**

This page lists the bundled Omnipy component families and what practical problem each one solves.

## General

General components provide foundational typed utilities used across workflows, including chain-style
model composition and generic helper tasks. Use this family when you want reusable type-safe
building blocks without committing to a domain-specific format.

**Problem it solves:** Shared typed primitives for cross-cutting workflow logic.

## JSON

JSON components provide models, datasets, tasks, and flows for structured and semi-structured JSON,
including nested variants. They are useful when incoming API payloads are irregular and you still
want repeatable parsing, coercion, and transformation behavior.

**Problem it solves:** Turning messy JSON payloads into predictable typed structures.

## Nested

Nested components focus on hierarchical content where nested dictionaries/lists are the native
representation. They keep deep structures explicit so you can validate and transform without losing
shape information too early.

**Problem it solves:** Working safely with hierarchical data before flattening/table conversion.

## Raw

Raw components handle plain bytes/text and line/item/column splitting and joining operations. They
are a good fit for pre-parse cleanup steps, lightweight parsing, and conversion between raw and
structured representations.

**Problem it solves:** Deterministic text/byte normalization before typed parsing.

## Remote

Remote components provide typed URL/query models and dataset/task patterns for loading data from
HTTP endpoints. This family is aimed at API ingestion where you need typed request inputs and
structured response handling.

**Problem it solves:** Reliable API boundary handling with typed request/response shapes.

## Tables

Tables components provide row-wise and column-wise tabular models plus CSV/TSV parsing and
conversion utilities. They are useful when moving between analysis-friendly records and broader
pipeline data structures.

**Problem it solves:** Typed table parsing and conversion between record-style and column-style data.

## Quick sanity check examples

```pycon exec="1" source="console"
>>> import omnipy as om
>>> NotIterableExceptStrOrBytesModel = om.NotIterableExceptStrOrBytesModel
>>> JsonListOfDictsModel = om.JsonListOfDictsModel
>>> NestedDataset = om.NestedDataset
>>> SplitToLinesModel = om.SplitToLinesModel
>>> HttpUrlModel = om.HttpUrlModel
>>> TsvTableModel = om.TsvTableModel
>>> NotIterableExceptStrOrBytesModel('abc').content
'abc'
>>> JsonListOfDictsModel([{'id': 's1'}]).content
[{'id': 's1'}]
>>> NestedDataset({'group': {'value': 1}}).json()
{'group': {'value': 1}}
>>> SplitToLinesModel('a\nb').content
['a', 'b']
>>> HttpUrlModel('https://example.org/api').content
'https://example.org/api'
>>> TsvTableModel('a\tb\n1\t2\n').content
[{'a': '1', 'b': '2'}]
```
