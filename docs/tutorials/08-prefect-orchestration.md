# Tutorial 8: Prefect orchestration

--8<-- "_includes/maturity_labels.md"

> [!NOTE]
> **Status: Preview**
>
> Prefect execution works today, but Omnipy's orchestration integration is still evolving.

This tutorial shows a practical path for running Omnipy flows with the Prefect engine, including
engine configuration, CLI usage with `--engine prefect`, and opening the Prefect UI.

## Step 1: Install dependencies

Install Omnipy:

```bash
pip install omnipy
```

Prefect is already included in Omnipy's base dependencies.

If you want to run the example CLI workflows, also install `omnipy-examples`:

```bash
pip install omnipy-examples
```

## Step 2: Switch engine configuration to Prefect

```pycon exec="1" source="console"
>>> from omnipy import runtime
>>> runtime.config.engine.choice
'local'
>>> runtime.config.engine.choice = 'prefect'
>>> runtime.config.engine.choice
'prefect'
```

## Step 3: Run a flow with the Prefect engine

```pycon exec="1" source="console"
>>> from omnipy import TaskTemplate, LinearFlowTemplate, runtime
>>> runtime.config.engine.choice = 'prefect'
>>> @TaskTemplate()
... def plus_one(number: int) -> int:
...     return number + 1
>>> @LinearFlowTemplate(plus_one, plus_one)
... def plus_two(number: int) -> int:
...     ...
>>> plus_two.run(10)
12
>>> runtime.config.engine.choice = 'local'
```

## Step 4: Run an example from CLI with `--engine prefect`

```bash
omnipy-examples --engine prefect isajson
```

This is useful when you want to test the same flow behavior through the CLI entrypoint.

## Step 5: View flow runs in Prefect UI

Start a local Prefect server:

```bash
prefect server start
```

Then open the URL printed by Prefect (commonly `http://127.0.0.1:4200`) and inspect flow runs,
task states, and logs.

## Practical limits in Preview

- Local engine remains the best default for quick inner-loop docs/examples.
- Prefect adds orchestration visibility and control, but operational conventions are still maturing.
- Prefer testing your own retry/scheduling behavior explicitly before production rollout.
