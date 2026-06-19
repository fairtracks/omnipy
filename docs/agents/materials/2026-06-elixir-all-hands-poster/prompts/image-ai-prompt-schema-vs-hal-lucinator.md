## The Schema vs. "Honest" HAL Lucinator

Create one **small battle panel** in a larger scientific comic poster.

**Scene:** "Honest" HAL Lucinator projects elegant, polished metadata records and tables full of confident-looking but unreliable content: invented keys, made-up labels, extra fields, and plausible values that do not actually match the declared contract. Opposing him stands **The Schema**, a silent hooded entity holding the glowing Pydantic Book of Models. Between them is a luminous threshold of truth.

**What Omnipy does in this battle:**

- **Single-record schema enforcement:** `PydanticRecordModel[...]` defines what one valid record is allowed to contain. If incoming data can be coerced into the declared fields and types, it is accepted. If not, it is rejected.
- **Whole-table schema enforcement:** `IteratingPydanticRecordsModel[...]` applies the same declared schema across an entire table or dataset. Values are coerced into the right types column by column, and defaults can be filled in automatically.
- **Type coercion:** Omnipy can turn acceptable messy values into the right shape, for example strings like `'30'` into integers like `30`, and missing defaulted fields into values like `False`.
- **Strict rejection:** If required fields are missing, if there are too many values in a row, or if extra fields are forbidden by the schema, the data does not pass.
- **Configurable extra-field policy:** A schema can allow unexpected fields or explicitly forbid them. In this battle, The Schema is using the strict form: if a field is not in the Book, it dissolves.
- **Coming soon — ontology validation*:** show a faint future-power glyph or asterisk near the Book suggesting that controlled vocabulary / ontology checks are an upcoming extension, not a current Omnipy power yet.

**What to draw:** HAL should throw beautiful but suspicious records and tables toward the threshold: polished enough to look trustworthy, but with fabricated metadata keys and semantically dubious labels hidden inside. The Schema does not attack physically; instead, the glowing Book and truth-threshold judge the incoming data. Valid parts are reshaped and aligned into the model. Coercible values snap into the correct type. Missing defaulted values are filled in. Extra invented fields, wrong-shape rows, and non-conforming records dissolve into ash, static, or light fragments at the boundary.

**Concrete examples to depict:**

- **Coercion and defaults across a table:**
  incoming data:
  `firstname=John, lastname=Doe, age='30'`
  `firstname=Jane, lastname=Doe, age='25'`
  `firstname=Tarzan, lastname=None, age='19'`
  becoming:
  `firstname=[John, Jane, Tarzan]`
  `lastname=[Doe, Doe, None]`
  `age=[30, 25, 19]`
  `deceased=[False, False, False]`
- **Invented field rejected:**
  HAL throws:
  `firstname=Tarzan, title='King of Apes'`
  but the schema only allows `firstname` and `lastname`
  so `firstname=Tarzan` survives while `title='King of Apes'` dissolves at the threshold.
- **Wrong-shape row rejected:**
  incoming row:
  `John\tDoe\t37\textra`
  expected schema:
  `firstname, lastname, age?`
  so the extra trailing value is blocked and shattered by the truth boundary.
- **Future ontology validation marker*:**
  show a faint ghost-image of a controlled vocabulary seal or ontology sigil near terms like `disease=dragon_flu` or `ontology=TOTALLY_REAL:1234`, marked with an asterisk to suggest “coming soon” semantic checking.

The main visual message is: **plausible-looking lies are not enough — only data that matches the declared model may pass**.

Include The Schema's catchphrase:

> **"If it is not written in the Book, it cannot be."**

Optional tiny footnote marker in the panel:

> `* Ontology validation shown as a future Omnipy power, not yet implemented.`
