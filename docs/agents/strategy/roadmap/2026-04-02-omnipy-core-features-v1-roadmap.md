# Omnipy Core Features & v1.0 Roadmap

This document captures the defining technical features of Omnipy that separate it from standard data validation and orchestration libraries. It also outlines the critical path for the v1.0 release based on current implementation gaps.

## 1. Continuous Validation via Type Mimicking
Unlike standard Pydantic models which only validate at object creation, Omnipy `Model` objects wrap and **mimic** their underlying types.
*   **How it works:** `list_of_ints = Model[list[int]]([1, 2, 3])` ensures the list contains only integers. Any state-changing manipulation triggers re-validation.
*   **Developer Experience:** The model seamlessly supports all underlying list methods and operators. Through Python `Protocol`s, it provides full auto-completion and static type checking in IDEs via advanced type checkers like `basedpyright`.

## 2. Declarative Type Conversions (`.to()`)
Models are designed for fluid transformation between complex formats.
*   **How it works:** Developers can transition from nested JSON to tabular data with a single call: `JsonDictOfListOfScalarsModel(...).to(PandasModel)`. This yields a model wrapping a pandas DataFrame, inheriting all DataFrame methods seamlessly.
*   **v1.0 Blocker:** The specification of these converters is currently not user-friendly. A simplified, intuitive converter registration/definition API must be finalized for v1.0.

## 3. Interactive Snapshots and Rollbacks
Perfect for Jupyter and interactive terminal sessions, Omnipy supports automatic, lazy snapshots.
*   **How it works:** During interactive manipulation, if an operation violates the strict validation schema (e.g., appending a string to `list_of_ints`), the model catches the validation error and cleanly reverts to its previously validated state. This encourages safe interactive data exploration.

## 4. First-Class Batch Processing via `Dataset`
Omnipy eliminates boilerplate `for`-loops when applying tasks across large data collections.
*   **How it works:** `Dataset[Model[list[int]]]` acts as a dictionary of models, enriched with slice and integer indexing. When a task is mapped over a `Dataset`, Omnipy natively handles the batch execution, vastly simplifying data processing code.

## 5. Dataset Blueprints & Hierarchies
Beyond homogeneous collections, `Dataset` objects can map specific distinct models dynamically based on item names (e.g., mapping a dataset to represent a specific file directory structure).
*   **How it works:** Datasets are fundamentally hierarchical and can contain other datasets, allowing them to mirror extremely complex biological or computational data layouts while maintaining strict typing throughout the tree.

## 6. Type-to-Format Serialization Mapping
The final step in a FAIR pipeline is persisting the validated objects cleanly to disk or over a network.
*   **How it works:** The system maps in-memory models to specific serialization formats (e.g., `JsonModel` serializes to JSON, `PandasModel` serializes to CSV).
*   **v1.0 Blocker:** The initial serialization implementation is inadequate and must be completely rewritten. Providing a robust, extensible mapping scheme for formats is a strictly required milestone for v1.0.

## 7. Modular Data Components & Architecture
Omnipy isn't just a generic engine; it ships with specialized components targeting specific data types and operations.
*   **Core Data Components:** Includes `General` (chaining models), `JSON` (flattening to tables), `Nested` (datasets of datasets), `Raw` (bytes/text splitting and joining), `Remote` (robust API calls, URL building), and `Tables` (row/column transformations, schema validation).
*   **External Ecosystem (The Plugin Strategy):** Specifically domain-heavy or heavy-dependency modules like `ISA` (ISA-JSON for ELIXIR), `Pandas`, `Prefect` engines, and `SeqCol` (GA4GH refget standard) are designed to be moved into external repositories via a plugin scheme. For v1.0, `ISA` and `Pandas` remain easy/thin inclusions, but the architectural boundary needs to be established.

---

## Strategic Focus for v1.0 (The Path Forward)

To ensure a successful v1.0 release, the scope needs to be grounded in the structural reality of the library. Because Pydantic v2 fundamentally improves how types and schemas are handled natively, it is the crucial dependency for finalizing converters and serialization.

The roadmap is categorized into immediate critical path items and parallel execution tracks:

### Phase 1: The Core Engine Rewrite (The "Must-Haves")
This phase tackles the deep architectural changes that everything else relies on.
1.  **Migrate to Pydantic v2:** This is the absolute priority, as it unlocks the improved converter and serialization logic.
2.  **Improve Type Mimicking:** Deeply refine how Pydantic models are wrapped and mimic their underlying types within Omnipy models (essential for `ISA` and general robustness).
3.  **Refactor `MultiModelDataset`:** Transition structurally to `Dataset[PydanticModel]`.
4.  **Refactor Converters and Serializers:** Rebuilding these explicitly on top of the new Pydantic v2 foundation.
5.  **Revitalize Core `JSON` & Hierarchical Flattening:** Leverage Pydantic v2.0's native support for recursive models to clean up JSON handling, and explicitly resurrect the "JSON-to-Table" hierarchical flattening engine (the original spark of the library) to serve as the heavy-duty harmonizer for complex standards.
6.  **Finalize Core `Tables` Component:** Complete the matrix of table conversions (row/col-wise × with/without columns × with/without indices).
7.  **Better Table Visualization:** Implement high-quality interactive visualization for tabular data (a strict must-have for the v1.0 user experience).
8.  **Refactor Job Modifiers:** Ensure these are only included if parameters are set.
9.  **Merge all half-finished branches:** Consolidate the codebase before freezing the API for v1.0.
10. **Basic Python 3.14 Support:** Straightforward ecosystem catch-up for standard execution (support for GIL removal / free-threading is deferred to future work).

### Phase 2: Core Execution & Infrastructure (Core Python Skills)
Focus on robust core execution features that require deep Python expertise.
1.  **Full Async/Parallel Support:** Essential for performance on large datasets.
2.  **Automatic Snapshots:** Ensure job runs trigger automatic state snapshots.
3.  **Plugin Architecture Scaffolding:** Establish the boundaries for externalizing `SeqCol`, `ISA`, `Pandas`, and `Prefect` into separate repos securely.

### Phase 3 (Parallel Track): Applied Data Engineering & Scaling (FGA-WG Project - Junior Dev Lead)
This phase runs in parallel to the core rewrite. It acts as the real-world proving ground for the library, driven by the "FAIRification of Genomic Annotations WG" use cases, and perfectly utilizes the junior developer's Kubernetes/Ops background.
1.  **Real-World Model-to-Model Mapping:** Design and implement straightforward mapping routines to convert data from one domain model to another.
    *   *Step 1:* Map ENCODE API metadata to the harmonised FGA-WG model.
    *   *Step 2:* Map Darwin Tree-of-Life (DTOL) tabular data to the FGA-WG model.
2.  **Scaling with Prefect/Kubernetes:** Once unblocked by the Pydantic v2 migration, leverage the junior developer's K8s experience to scale up the FGA-WG metadata pipelines.
    *   Streamline seamless job dispatches onto K8s clusters.
    *   Reliably return remote data and logs from Prefect/K8s runs.
3.  **Docs and Testing:** Comprehensive documentation and tests for all included tasks/flows. This is perfectly suited for the junior developer to own: as they learn how to use Omnipy, they can document the ideal onboarding experience they would have wanted, supplemented by AI generation.

### Phase 4: Ecosystem & Community Integration Track
These features are relatively isolated from the core engine's complexity and are targeted for community efforts, domain experts, or later polishing:
*   **Format Integrations:** Add support for standard structured formats like Excel, XML, YAML, JSON-LD, and **RO-Crate**.
*   **Scientific Integrations (Community/Domain Experts):** Formalize **BioNumpy** integration. Integrate **Ontology Validation** (via Ontology Access Kit / OAK), LinkML, and Whyqd.
*   **Polish Thin Plugins:** Polish the `Pandas` and `ISA` components for the v1.0 launch.

### Phase 5: Data Interoperability & UX (Post-v1.0 or Nice-to-Haves)
If time permits before v1.0, or scheduled immediately for v1.x:
*   **Table and Schema Tools:** Auto-mapping relational tables to single tables/hierarchical JSON, robust JSON-to-table flattening for unpredicted schemas, improved table conversions, and automatic schema detection.
*   **Enhanced UX:** Improved interactive data views (tables, scrolling via external libraries) and uniform indexing across JSON, Pandas, Numpy.
*   **Support for GIL Removal:** Optimizing the engine for Python's free-threading features to radically speed up parallel data transformations.
