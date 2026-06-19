## Optimus Parse vs. Lord Franken-Format

Create one **small battle panel** in a larger scientific comic poster.

**Scene:** Lord Franken-Format, a chaotic data monster, throws messy bioinformatics payloads at Optimus Parse: tangled **GFF**, **BED**, **CSV**, and **nested JSON**, with broken headers, mixed delimiters, comment lines, and `key=value;key=value` strings flying everywhere.

**What Omnipy does in this battle:**

- **Declarative parsing chains:** Omnipy turns parsing into a visible sequence of small steps. `SplitToLinesModel` cuts raw text into lines. `SplitLinesToColumnsModel` cuts each line into columns. `RowWiseTableFirstRowAsColNamesModel` turns the first row into column headers. `Chain3[...]` means these happen as one pipeline.
- **Model-driven typing:** `PydanticRecordModel` and `IteratingPydanticRecordsModel` force messy values to fit a declared schema. Strings, integers, booleans, and defaults are snapped into the right places. The schema should look like a glowing blueprint.
- **Nested parsing:** `AttributesSplitToItemsModel` and `NestedSplitToItemsModel` split complex strings in layers, for example turning `ID=gene1;Parent=tx1,tx2;Dbxref=GeneID:123` into separate labeled fields.
- **Clean table output:** `PandasModel` and `PandasDataset` are the final clean table result.
- **Parse, don't validate:** Omnipy reshapes data into the right form instead of only checking it at the end.

**What to draw:** Show Optimus Parse performing these stages in order. He catches raw text chaos, slices it into lines, folds the lines into columns, tears apart tangled attribute strings into labeled fields, and presses the pieces against a glowing typed schema so that values snap into place. The final result is clean, orderly tables or dataframe-like panels.

**Concrete examples to depict:**

- **Messy GFF input:**
  `chr1\tsource\tgene\t100\t900\t.\t+\t.\tID=gene1;Name=BRCA1;Parent=tx1,tx2;Dbxref=GeneID:672`
  becoming a clean typed record with fields like:
  `seqid=chr1, type=gene, start=100, end=900, strand=True, ID=gene1, Name=BRCA1, Parent=[tx1, tx2]`
- **Messy BED input:**
  `chr2\t200\t400\tpeakA\t960\t-\t200\t400\t255,0,0`
  becoming:
  `chrom=chr2, chromStart=200, chromEnd=400, name=peakA, score=960, strand='-', itemRgb=(255, 0, 0)`
- **Messy CSV input:**
  `name,age,active` then `Alice,30,true` and `Bob,25,false`
  becoming columns like:
  `name=[Alice, Bob], age=[30, 25], active=[True, False]`
- **Messy nested JSON input:**
  `{"sample":{"id":"S1","reads":[12,15],"passed":"true"}}`
  becoming a structured table row like:
  `id=S1, reads=[12, 15], passed=True`

The main visual message is: **chaotic raw formats in, structured typed tables out**.

Include Optimus Parse's catchphrase:

> **"Parse, don't validate! FAIR data in disguise!"**
