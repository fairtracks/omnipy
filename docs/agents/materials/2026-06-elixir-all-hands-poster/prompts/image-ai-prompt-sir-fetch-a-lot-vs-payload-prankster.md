## Sir Fetch-a-Lot vs. The Payload Prankster

Create one **small battle panel** in a larger scientific comic poster.

**Scene:** The Payload Prankster, a mischievous ghost of broken APIs, hurls a storm of remote metadata endpoints at Sir Fetch-a-Lot: some return JSON, some return plain text, some return binary blobs, some flash `429 Too Many Requests`, and some drop out just as the response is about to land. Sir Fetch-a-Lot, a noble winged cyber-hound, splits into multiple synchronized flight paths and retrieves many endpoints at once without losing pace or discipline.

**What Omnipy does in this battle:**

- **Parallel retrieval across many URLs:** an Omnipy `HttpUrlDataset` can hold many named endpoints at once. Tasks like `get_json_from_api_endpoint`, `get_str_from_api_endpoint`, `get_bytes_from_api_endpoint`, and `get_auto_from_api_endpoint` can fetch the whole batch.
- **Async fetching with shared sessions:** Omnipy supports asynchronous fetching and can reuse the same `aiohttp` client session across multiple retrieval jobs, so many endpoints can be fetched in parallel without chaos.
- **Disciplined pacing:** `RateLimitingClientSession` controls request speed so fetching stays fast but does not become reckless. It allows an initial burst, then slows into controlled pacing.
- **Retry and backoff:** Omnipy retries on statuses like `429`, `500`, `502`, `503`, and `504`, with configurable retry strategies such as exponential, jitter, Fibonacci, or random backoff.
- **Automatic payload typing:** `get_auto_from_api_endpoint` and `AutoResponseContentModel` inspect the response content type and sort it into JSON, plain text, or bytes automatically.
- **Remote file discovery:** `get_github_repo_urls(...)` and `async_get_github_repo_urls(...)` can discover remote files and build download URLs, turning remote directories into fetchable URL datasets.

**What to draw:** Show Sir Fetch-a-Lot flying along several parallel luminous paths at once, each path ending at a different endpoint orb. Some endpoint orbs should show JSON braces, some plain text scrolls, some binary cubes, and some flashing `429` warning sigils. Around Sir Fetch-a-Lot, show calm pacing rings or clockwork rate-limit halos controlling his speed. Behind him, retries should look deliberate and intelligent, not frantic: failed requests curve back in controlled arcs and are sent again with measured spacing. The Payload Prankster should be changing response shapes, dropping connections, and renaming fields in the middle of flight, but Sir Fetch-a-Lot still sorts each payload into the correct form.

**Concrete examples to depict:**

- **Batch of remote metadata endpoints:**
  `patient_001 -> https://api.example.org/patients/001`
  `patient_002 -> https://api.example.org/patients/002`
  `patient_003 -> https://api.example.org/patients/003`
  all fetched in parallel from one `HttpUrlDataset`.
- **Mixed payload trickery:**
  one endpoint returns JSON like:
  `{"patient_id":"P001","phenotype":["HP:0001250"],"diagnosis":"epilepsy"}`
  another returns plain text like:
  `patient_id=P002; diagnosis=rare_disease; status=reviewed`
  another returns bytes/binary content.
  Sir Fetch-a-Lot should visibly sort these into the right output forms: JSON, text, and bytes.
- **Rate limit and retry pressure:**
  one endpoint flashes:
  `429 Too Many Requests`
  another flickers with `503 Service Unavailable`
  show Sir Fetch-a-Lot circling back with controlled spacing rather than crashing into the endpoint repeatedly.
- **Remote discovery example:**
  show a remote source like:
  `repo/metadata/`
  `  patient_001.json`
  `  patient_002.json`
  `  patient_003.json`
  turning into a clean set of fetchable URL targets before retrieval begins.

The main visual message is: **many remote endpoints, one disciplined retrieval system — fast, parallel, careful, and hard to fool**.

Include Sir Fetch-a-Lot's catchphrase:

> **"Every endpoint gets sniffed."**
