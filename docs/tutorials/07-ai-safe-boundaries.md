# Tutorial 7: AI-safe boundaries

--8<-- "_includes/maturity_labels.md"

!!! note
    **Status: Preview**

    This tutorial presents practical patterns for validating and cleaning LLM output with Omnipy
    models. It is intentionally not a native LLM orchestration feature.

Omnipy can act as a schema firewall between probabilistic LLM output and deterministic downstream
dataflows.

## Ecosystem fit

These patterns work well alongside tooling such as Instructor, Marvin, and PydanticAI.

## Pattern 1: model as schema firewall

Use a typed model at the boundary where untrusted model output enters your system.

```pycon exec="1" source="console"
>>> import omnipy as om
>>> import pydantic as pyd
>>> class LlmAnswer(pyd.v1.BaseModel):
...     title: str
...     score: int
>>> om.Model[LlmAnswer]({'title': 'Candidate A', 'score': '7'})
{'title': 'Candidate A', 'score': 7}
```

This gives explicit, typed data before any business logic continues.

### Reject hallucinated extra keys explicitly

When your downstream contract is strict, reject unknown fields instead of silently accepting them.

```python
import omnipy as om
import pydantic as pyd


class StrictLlmAnswer(pyd.v1.BaseModel):
    title: str
    score: int

    class Config:
        extra = 'forbid'


# Hallucinated key: "confidence_bucket"
payload = {
    'title': 'Candidate A',
    'score': 7,
    'confidence_bucket': 'high',
}

# Raises ValidationError (extra fields not permitted)
om.Model[StrictLlmAnswer](payload)
```

Use this in safety-critical paths where unknown keys should be treated as schema drift.

## Pattern 2: parse + coerce for pragmatic cleanup

When input quality varies, start permissive and normalize first.

```pycon exec="1" source="console"
>>> import omnipy as om
>>> import pydantic as pyd
>>> class ParsedAnswer(pyd.v1.BaseModel):
...     score: int
...     approved: bool
>>> om.Model[ParsedAnswer]({'score': '7', 'approved': 'true'})
{'score': 7, 'approved': True}
```

This pattern is useful for inbound parsing layers where downstream tasks require normalized types.

## Pattern 2b: batch-cleaning many LLM outputs into a table

For realistic pipelines, parse a batch of responses and then convert to a table-oriented model.

```python
import omnipy as om

raw_answers = [
    {'id': 'a1', 'score': '7', 'approved': 'true'},
    {'id': 'a2', 'score': '9', 'approved': 'false'},
    {'id': 'a3', 'score': '5', 'approved': 'true'},
]

cleaned_answers = [om.Model[ParsedAnswer](answer) for answer in raw_answers]

table = om.JsonListOfDictsModel(cleaned_answers).to(om.RowWiseTableWithColNamesModel).to(om.PandasModel)
table
```

This pattern keeps AI output handling composable: parse at the boundary, then use familiar
table tooling for downstream analysis.

## Pattern 3: strictness knobs when you need hard failure

Switch specific fields to strict types to reject coercion and force explicit repair logic.

```pycon exec="1" source="console"
>>> import omnipy as om
>>> import pydantic as pyd
>>> class StrictAnswer(pyd.v1.BaseModel):
...     score: pyd.StrictInt
>>> try:
...     om.Model[StrictAnswer]({'score': '7'})
... except Exception as exc:
...     type(exc).__name__
'ValidationError'
```

Use this where silent coercion could hide quality issues.

## Pattern 4: explicit repair flow task (beyond coercion)

Coercion alone is often not enough. Add a repair task that normalizes known LLM failure shapes
before strict model parsing.

```python
import omnipy as om


@om.TaskTemplate()
def repair_and_parse_llm_answer(payload: dict[str, object]) -> dict[str, object]:
    normalized_payload = {
        'title': str(payload.get('title', '')).strip(),
        'score': int(payload.get('score', 0)),
    }
    return om.Model[StrictLlmAnswer](normalized_payload)
```

Typical repair actions:

- Rename common synonym keys (for example `rating` -> `score`).
- Strip markdown/code fences from text values.
- Convert obvious string numerics before strict parsing.
- Route unrecoverable payloads to a review queue.

## Suggested template in production pipelines

1. Generate/collect LLM output with your preferred LLM library.
2. Parse through an Omnipy model at ingestion boundary.
3. Decide field-by-field strictness according to downstream risk.
4. Route failures to retry, repair, or human-review paths.

This keeps LLM integration modular while preserving typed contracts in your core pipeline.

## Template-style guide (reusable pattern)

Use this as a copy/paste starter for new AI-boundary pipelines.

1. **Boundary model**: define strict typed schema (`extra='forbid'` when needed).
2. **Repair task**: normalize known messy patterns.
3. **Strict parse**: parse repaired payload via `Model[YourSchema]`.
4. **Batch convert**: convert cleaned records to table model.
5. **Escalate failures**: retries/human review for irreparable inputs.

```python
# 1) schema
class YourSchema(pyd.v1.BaseModel):
    ...
    class Config:
        extra = 'forbid'


# 2) repair task
@TaskTemplate()
def repair_payload(payload: dict[str, object]) -> dict[str, object]:
    ...


# 3) strict parse
cleaned = om.Model[YourSchema](repair_payload.run(raw_payload))


# 4) batch -> table
records = [om.Model[YourSchema](repair_payload.run(item)) for item in raw_items]
table = om.JsonListOfDictsModel(records).to(om.RowWiseTableWithColNamesModel).to(om.PandasModel)


# 5) escalate failures (retry queue / human review)
```
