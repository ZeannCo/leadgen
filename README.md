# Leadgen

Reusable Python pipeline code for normalizing, qualifying, scoring, and routing lead records. This public edition is extracted from my lead-generation automation work and includes an offline demo with fictional data.

**[Zeann Co](https://zeann.dev)** · [Project context](https://github.com/ZeannCo/cybersecurity-portfolio/blob/main/projects/leadgen.md)

## Try it

Python 3.11+:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python demo.py
python -m pytest -q
```

No API keys, browser, database, or customer records are needed. The demo processes four fictional records, removes a duplicate, flags an organization name for review, and shows the resulting score and route. It makes no network calls and sends no outreach.

## Included code

| Module | Responsibility |
| --- | --- |
| `models/filing.py` | Typed input record with validation |
| `services/name_utils.py` | Name normalization and parsing |
| `pipeline/gates.py` | Name, address, date, and query-deduplication gates |
| `pipeline/qualification.py` | Record classification and ZIP extraction |
| `pipeline/lead_score.py` | Bounded, explainable scoring profiles |
| `pipeline/router.py` | Routing decisions without external side effects |
| `demo.py` | A runnable end-to-end example using the included modules |

```text
Input records
     |
Identity and address checks
     |
Query deduplication
     |
Qualification + scoring
     |
Routing result for review
```

## Scope of this edition

This repository contains the reusable decision layer, not the full client deployment. Live court collectors, paid enrichment providers, CRM connectors, calling services, client campaigns, and production dashboards are excluded. The original project combines those integrations with this pipeline; its architecture is described in the linked project overview.

Routing labels and scoring profiles are illustrative. A routing result is not permission to contact someone, and a score is not a legal or eligibility determination. Real integrations need consent, suppression checks, provider-specific validation, and human review.

The public history starts from this sanitized edition. Original Git history, exported records, account identifiers, and credentials are excluded. See [SECURITY.md](SECURITY.md).
