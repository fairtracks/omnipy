# ELIXIR All-Hands 2026 Abstract

## Omnipy v1.0: Defending FAIR Bioinformatics Against Bad Data and AI Hallucinations

Bioinformaticians are currently fighting a two-front war. On one side, messy REST APIs serve up unstructured "junk food" data that poisons machine learning models before training even begins. On the other side, cutting-edge AI agents risk unleashing unpredictable "hallucinations" back into scientific workflows. Together, these bad inputs and fabricated outputs cause silent data corruption. While heavy-duty engines like Snakemake expertly orchestrate large compute tasks, the community needs a dedicated metadata wrangling framework to safely pipeline the complex data flowing in between.

Enter Omnipy v1.0, developed by ELIXIR Norway. Omnipy is an interactive Python framework that brings strict typing and "Code Zen" to FAIR data processing. By leveraging Pydantic v2, Omnipy goes beyond standard validation: its models seamlessly mimic standard Python types (like `list` and `dict`), allowing researchers to safely manipulate deeply nested data natively in Jupyter with automatic state rollbacks the microsecond a silent corruption is attempted. Omnipy further strips away boilerplate through fluid declarative type conversions, robust REST API retry-shields, and first-class `Dataset` batch-processing that replaces impenetrable iteration with single declarative operations.

To conceptualize these technical architecture choices, our poster presents an epic, comic-book-style showdown: the "UnFAIR Alliance" of data corruption versus the "Omni-Squad" of data integrity. Attendees will discover how Omnipy's strict type enforcement (*The Endless Schema*) acts as an inevitable cosmic law to banish AI-fabricated keys (*"Honest" HAL Lucinator*), and how elegant declarative dataset mapping (*Master Zen-Batch*) effortlessly slices through the tangled, boilerplate-heavy code of ad-hoc scripts (*The Spaghetti Monster*).

By actively combatting boilerplate, silent type coercion, and schema decay, Omnipy v1.0 guarantees structurally flawless data at every step, providing the hallucination-proof foundation necessary to safely build the next generation of AI-assisted bioinformatics.


