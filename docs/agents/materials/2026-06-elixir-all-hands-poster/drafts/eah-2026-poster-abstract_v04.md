# ELIXIR All-Hands 2026 Abstract

## Bridging the gap between messy biological metadata and AI-ready pipelines with Omnipy

The AI revolution in bioinformatics holds immense promise, but its success
hinges on an unglamorous reality: data interoperability. Today,
bioinformaticians are trapped in the "Missing Middle" of data tooling.
While powerful workflow engines like Nextflow and Snakemake expertly
orchestrate large files, the complex, nested metadata within them—or
pulled from obscure REST APIs—is typically wrangled using fragile, ad-hoc
Python scripts.

As we integrate Large Language Models (LLMs) and autonomous agents into
our work, this fragility becomes a critical bottleneck. AI agents
hallucinate data formats, and ML training loops demand strict structural
guarantees. Your AI models and pipelines are only as reliable as the data
structures they consume and produce.

Omnipy, developed in ELIXIR Norway, is a Python-based workflow and ETL
framework that solves this by applying the "Parse, Don't Validate"
philosophy to dynamic biological data. By enforcing strict programmatic
typing, Omnipy actively parses unpredictable JSON and complex tabular
metadata into rigorously structured objects. Only structurally flawless
data is allowed to cascade through the pipeline.

Crucially, Omnipy *mimics* its underlying types. A validated list of
annotations behaves exactly like a native Python list, automatically
triggering re-validation upon any state change. Designed for the
interactive researcher, Omnipy acts as a safe sandbox: if a manipulation
violates the schema during a Jupyter or terminal session, Omnipy
automatically rolls back to the last safe state.

Omnipy focuses on standardizing the tools researchers reach for daily:
- Fluid, declarative conversions from nested API JSON directly to Pandas DataFrames.
- First-class `Dataset` batch-processing that eliminates boilerplate for-loops over large collections.
- Rich, interactive panel-based visualization of complex data structures.
- Seamless scaling of interactive workflows to local execution, Prefect, or Kubernetes clusters.

Currently driving real-world metadata harmonization for the ELIXIR
FAIRification of Genomic Annotations WG (mapping ENCODE APIs to Darwin
Tree-of-Life tables), Omnipy is rapidly advancing toward its v1.0 release.
Furthermore, because every Omnipy task possesses an explicit type
signature, these pipelines are perfectly positioned to act as safe,
strongly-typed "tools" for future AI agents to execute.

We warmly invite developers, bioinformaticians, and FAIR experts to
collaborate with us in building the robust, type-safe foundations required
for the next generation of AI-assisted bioinformatics.
