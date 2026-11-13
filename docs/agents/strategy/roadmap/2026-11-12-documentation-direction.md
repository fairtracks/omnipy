# Documentation direction after the 2026-11 release

Recorded 2026-11-12, from the discussion around the readme rework for the release of that week.
This note gives the direction for the documentation work that follows; the detailed plans go under
`docs/agents/documentation/plans/` when the work starts.

## The pitch: a readable contract between researcher and AI agent

Omnipy is to be presented as the structure that makes AI-assisted research data work reviewable:
the agent turns exploratory code into data models, conversions and dataflows declared in Python,
the data is validated at every step, and the researcher reviews the declarations and the data
rather than the agent's code paths. The declarations are the contract between researcher and
agent. The workshop
[Structure your AI-powered research data pipelines with Omnipy](https://www.ub.uio.no/english/courses-events/courses/dsdays/2027/structure-your-ai-powered-research-data-pipelines-wi.html)
at Digital Scholarship Days 2027 (University of Oslo, 2027-01-07) takes this direction further.
The readme of the 2026-11 release introduces the pitch in its first paragraph and its last section
only; a readme built around it is future work.

## What the next release focuses on

- **Rewrite the tutorials.** The existing tutorials are considered poor and are the main target
  of the next release. The sequence data brokering integration test
  (`tests/integration/novel/full/sequence_data_brokering/`) is to become a tutorial, as the
  water-sample harmonization test already is the basis of the readme walkthrough.
- **Skills as documentation for agents.** The omnipy-dataflows skill is the first of several
  Omnipy skills. They ship with the package (`.agents/skills/`, copied into the wheel) and are
  installed into a project with `python -m omnipy skills install`; see `AGENTS.md`.
- **Readme.** `docs/readme.md` is the source, run by MkDocs; the root `README.md` and the SVG
  images are generated from it with `uv run python docs/gen_readme.py`, and `hatch_build.py`
  rewrites the image links for PyPI. No hook enforces regeneration yet. Readme changes stay
  limited until the documentation rewrite.
- **omnipy-examples** on PyPI is updated separately and may lag behind the Omnipy release; the
  readme says so.
