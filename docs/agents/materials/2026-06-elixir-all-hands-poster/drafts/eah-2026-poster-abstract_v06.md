# ELIXIR All-Hands 2026 Abstract

## Connecting the pieces in the data sandbox:
### Type-safe, boilerplate-free metadata pipelines with Omnipy
You trained as a scientist, yet you likely spend 80% of your time
wrestling with complex metadata. While powerful engines like Snakemake
expertly orchestrate massive compute tasks, the metadata glued in between
is often handled with fragile, ad-hoc Python scripts. This leaves the door
wide open to silent data corruption. As we increasingly rely on AI models
and agents—which are prone to hallucinating formats—feeding them
unstructured "junk food" data is a guaranteed recipe for analytical
disaster.

Enter Omnipy: a type-safe, boilerplate-free Python framework designed to
harmonize biological data into rigorously typed, FAIR-compliant data
models. By applying the "Parse, Don't Validate" philosophy, Omnipy ensures
that dynamic biological metadata is continuously parsed into flawless
structures.

For the interactive researcher, Omnipy acts as a fearless data sandbox. By
closely mimicking underlying Python types and utilizing automatic
rollbacks, it catches slip-ups in real-time, letting you aggressively
experiment with datasets without permanently breaking state. Because "you
can't fix data you can't see," Omnipy includes a visually rich toolkit to
beautifully present underlying raw data and nested structures directly in
Jupyter or your terminal—without the need for complex plotting.

At its core, Omnipy treats data orchestration like a puzzle. Pre-built
tasks and dataset objects act as the puzzle pieces, seamlessly snapping
together with Omnipy’s strict models providing the glue. This design acts
as a Zen-master for your codebase: stripping away messy `for`-loops, API
retry logic, and repetitive boilerplate, so your pipelines remain clean,
readable, and highly powerful. Whether you are shapeshifting deeply nested
JSON into tabular Pandas frames or making resilient remote REST calls,
Omnipy handles the heavy lifting.

Join us as we gear up for our v1.0 release. Stop fighting your data, and
discover the type-safe, modular foundation you need to build the next
generation of AI-ready bioinformatics pipelines.
