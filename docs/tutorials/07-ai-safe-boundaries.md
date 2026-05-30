# Tutorial 7: AI-safe boundaries

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Preview**
>
> This tutorial presents practical patterns for validating and cleaning LLM output with Omnipy
> models. It is intentionally not a native LLM orchestration feature.

Omnipy can act as a schema firewall between probabilistic LLM output and deterministic downstream
dataflows.

## Ecosystem fit

These patterns work well alongside tooling such as Instructor, Marvin, and PydanticAI.

## Pattern 1: model as schema firewall

Use a typed model at the boundary where untrusted model output enters your system.

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> from omnipy.util import pydantic as pyd
>>> class LlmAnswer(pyd.BaseModel):
...     title: str
...     score: int
>>> Model[LlmAnswer]({'title': 'Candidate A', 'score': '7'}).to_data()
{'title': 'Candidate A', 'score': 7}
```

This gives explicit, typed data before any business logic continues.

## Pattern 2: parse + coerce for pragmatic cleanup

When input quality varies, start permissive and normalize first.

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> from omnipy.util import pydantic as pyd
>>> class ParsedAnswer(pyd.BaseModel):
...     score: int
...     approved: bool
>>> Model[ParsedAnswer]({'score': '7', 'approved': 'true'}).to_data()
{'score': 7, 'approved': True}
```

This pattern is useful for inbound parsing layers where downstream tasks require normalized types.

## Pattern 3: strictness knobs when you need hard failure

Switch specific fields to strict types to reject coercion and force explicit repair logic.

```pycon exec="1" source="console"
>>> from omnipy import Model
>>> from omnipy.util import pydantic as pyd
>>> class StrictAnswer(pyd.BaseModel):
...     score: pyd.StrictInt
>>> try:
...     Model[StrictAnswer]({'score': '7'})
... except Exception as exc:
...     type(exc).__name__
'ValidationError'
```

Use this where silent coercion could hide quality issues.

## Suggested template in production pipelines

1. Generate/collect LLM output with your preferred LLM library.
2. Parse through an Omnipy model at ingestion boundary.
3. Decide field-by-field strictness according to downstream risk.
4. Route failures to retry, repair, or human-review paths.

This keeps LLM integration modular while preserving typed contracts in your core pipeline.
