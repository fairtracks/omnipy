## Master Zen-Batch vs. The Spaghetti Monster

Create one **small battle panel** in a larger scientific comic poster.

**Scene:** The Spaghetti Monster attacks with tangled scripts, nested `for` loops, brittle notebook cells, and chaotic pipeline arrows twisting around batches of data files. Master Zen-Batch stands calm in the middle, guiding many data files through the same clean sequence of steps at once.

**What Omnipy does in this battle:**

- **Batch datasets:** An Omnipy `Dataset[...]` holds many named data files at once, such as `a`, `b`, and `c`, instead of making the user handle each file separately.
- **Hierarchical datasets:** Omnipy can also represent nested, hierarchical data with `NestedDataset`, so batches do not have to be flat. A dataset can contain sub-datasets, records, and nested lists/dicts that are still inspectable and manageable as structure instead of chaos.
- **Map over the batch without writing the outer loop:** `TaskTemplate(iterate_over_data_files=True)` applies one small task to every data file in a dataset automatically. The user writes the transformation once; Omnipy repeats it across the whole batch.
- **Simple flow composition:** `FuncFlowTemplate` and `DagFlowTemplate` compose small tasks into clean reusable pipelines, so the work is organized as a few clear stages instead of a giant tangled script.
- **Interactive inspection:** `peek()` shows a preview of dataset contents, `list()` shows file names, types, lengths, and sizes, and `json()` shows plain data. These should feel like calm inspection windows in Jupyter, a terminal, or an IDE.
- **Conversion when needed:** `convert_dataset(...)` changes one dataset type into another cleanly, instead of manual boilerplate conversion code.
- **Coming soon — file structure mapped to dataset schema*:** show a future-power asterisk for organizing whole directory trees into loose or strict dataset schemas, so folders and files themselves can be brought under the same calm structural discipline.

**What to draw:** Show The Spaghetti Monster flinging loops like `for file in dataset:` and tangled arrows between notebook cells. Some of his chaos should be flat batches, while some should be folder-trees and nested structures. Show Master Zen-Batch countering with one clean task symbol that is mirrored across multiple data files at once, then passing those files through a small orderly pipeline of stages. Around him, floating inspection panels should show previews and summaries of both flat and hierarchical datasets, as if he can calmly inspect the whole structure without losing control. Add a faint future-power symbol showing directory trees aligning into a schema-shaped frame. The main visual idea is: **many files, one calm workflow**.

**Concrete examples to depict:**

- **Batch input dataset:**
  `a=3, b=5, c=-2`
  processed by one task with `iterate_over_data_files=True`
  becoming:
  `a='5', b='7', c='0'`
  This comes from the tested pattern of applying one small transformation to each file in `Dataset[Model[int]]({'a': 3, 'b': 5, 'c': -2})`.
- **Simple three-step flow:**
  input batch of messy phenotype / health-genomics metadata records:
  `patient_A -> {'patient id': 'P001', 'age_at_diagnosis': '34', 'sex': 'female', 'phenotype': 'HP:0001250', 'candidate_variant_count': '2'}`
  `patient_B -> {'patient_id': 'P002', 'age': 29, 'biological_sex': 'male', 'hpo_terms': ['HP:0004322'], 'candidate_variant_count': 1}`
  `patient_C -> {'subject': 'P003', 'age_at_dx': '41', 'sex': 'F', 'phenotype': 'seizures', 'candidate_variants': '3'}`
  stages:
  `parse raw records -> flatten nested structures -> rename fields to a shared schema -> coerce types -> combine into one clean table`
  final harmonized output like:
  `patient_id=[P001, P002, P003]`
  `age_at_diagnosis=[34, 29, 41]`
  `sex=[female, male, female]`
  `phenotype_terms=[[HP:0001250], [HP:0004322], ['seizures']]`
  `candidate_variant_count=[2, 1, 3]`
  This should feel like real phenotype / clinical metadata harmonization across inconsistent sources.
- **Dataset inspection panels:**
  show a small summary table like:
  `# | Data file name | Type | Length`
  `0 | a | Model[int] | 1`
  `1 | b | Model[int] | 1`
  `2 | c | Model[int] | 1`
  and nearby preview panels showing the transformed values.
- **Hierarchical dataset example:**
  show nested data like:
  `project -> sample_1 -> reads, metadata`
  `project -> sample_2 -> reads, metadata`
  or concrete nested content like:
  `id_0 -> kids -> 0, 1, 2`
  to suggest that Omnipy can keep tree-shaped data organized, not just flat file batches.
- **Notebook / terminal / IDE integration:**
  show the same calm dataset previews appearing as floating windows or panels beside the battle, suggesting that Master Zen-Batch can inspect the same workflow in multiple work environments.
- **Future file-structure schema marker*: **
  show a faint directory tree such as:
  `project/`
  `  sample_A/reads.fastq`
  `  sample_A/meta.json`
  `  sample_B/reads.fastq`
  `  sample_B/meta.json`
  being gently pulled toward a glowing dataset schema outline, marked with an asterisk to show this as a coming-soon Omnipy power.

The main visual message is: **replace tangled loops and messy pipelines with calm batch processing, clear reusable steps, and fast interactive inspection**.

Include Master Zen-Batch's catchphrase:

> **"One task, many files. Breathe in, batch out."**

Optional tiny footnote marker in the panel:

> `* File-structure-to-dataset-schema mapping shown as a future Omnipy power, not yet implemented.`
