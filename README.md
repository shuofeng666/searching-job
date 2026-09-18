# Research Internship Deadlines — personal research radar

A research-first Summer 2027 tracker for an HCI PhD who wants to **advance a research agenda** through an internship, not just find a generic internship. Geography: United States, Canada, Singapore and Hong Kong. Primary targets: established corporate research labs doing HCI, Human–AI, CSCW, creativity support, CAD, computational design, digital fabrication, interaction and visualization. Research-oriented UX roles at large companies are included; ordinary product design, PM, ML algorithms and generic SWE are excluded.

**[Product requirements and comparable trackers](docs/product-spec.md)** describes user workflows, sources, design rationale, acceptance criteria and remaining limitations.

## Product views

- `/` — 2027 **search leads**, date-first HCI Deadlines-style list, topic and location filters, original role URL, browser-only favorites, notes and applied/dismissed status. An employer-domain URL and a year in the title **do not mean the position is independently verified open**. Dates are unknown unless supported by the employer.
- Personal radar panel — fresh leads since the user last pressed `我已查看本轮线索`, with an **unknown-year review queue** that is NOT added to the current job list. All review state lives only in this browser; there is no cross-device sync.
- Research group watchlist — Autodesk, Adobe, Microsoft and Meta have separately cited research-group and past-program evidence in `public/data/research-evidence.json`; research-team existence is not a 2027 job announcement. Each firm displays its last search, matches, unresolved items and errors. `0` means **zero matching results from that one query**, not zero open roles across the company.
- `/archive.html` — separate historical 2025/2026 job evidence in `public/data/archive.json`. It can be empty while research-history links exist in the team watchlist. Previous-year application dates are never extrapolated into 2027.
- Manual scan — in-page `立即搜索新岗位` button posts only to `api/scan.js` using a separately entered password. This button is unusable until Vercel Production secrets are configured. GitHub Actions manual dispatch remains a fallback.

## Reliable data before AI

`.github/workflows/scan.yml` runs `scanner_v4.py` daily at `13:23 UTC` or by authenticated manual dispatch; the workflow tests code before any paid requests and commits updated `public/data/feed.json` and `archive.json` to `main` when changed.

**Budget: at most 12 SerpApi queries per run**, roughly 360/month at daily cadence. Four individual searches always target Autodesk, Adobe, Microsoft and Meta; six more companies rotate and two topic queries run on most days. Sunday rotates four other companies, adds two topic queries and two historical searches. A query is **not** a full audit of a company's official board. More frequent searches can hit provider quota and do not establish the truth of an opening.

Ingestion requires a recognized company/official domain or a narrowly allowlisted company ATS host, an internship **research** title and HCI/related topic language; generic product design, PM and algorithm roles are blocked. The cycle year must appear explicitly in the title to enter the 2027 lead list. Employer results without a confirmed year remain in `watch_leads`. We cannot accurately infer the year from a snippet, and do not mark live opening, application cutoff, eligibility, visa support, mentor or publication as verified from search snippets. `sanitize_feed.py` and `.github/workflows/clean-legacy.yml` purge known bad legacy records offline without consuming search credits. Historical scan counts remain in the run log even after bad roles are removed.

**Current limitations:** automatic verification of individual job descriptions and hiring status is not implemented, so do not call this a comprehensive list or claim all 2027 positions are open. AI scoring/summarization, verified deadline extraction, email/push alerts, calendar export and cross-device sync remain planned enhancements. Personal notes should never be committed to the public repository. Full architecture and sources: [product specification](docs/product-spec.md).

## One-time setup (never send credentials into chat)

1. In GitHub repository `shuofeng666/searching-job`, configure Actions secret `SERPAPI_KEY` with the SerpApi key. GitHub Actions alone is sufficient for daily scanning; no OpenAI API key is required.
2. For the **optional website manual scan button**, issue a fine-grained GitHub PAT scoped to **only this repository** with **Actions: Read and write**, Metadata: Read. In Vercel `searching-job` → Settings → Environment Variables, add Production Secret `GH_ACTIONS_TOKEN` (PAT) and Production Secret `SCAN_PASSWORD` (a distinct random password at least 16 characters). Never use an `NEXT_PUBLIC_`/client-exposed key or commit tokens to source. Renew the PAT before expiration.
3. Ensure the Vercel project imports the repository `main` branch with project root at repository root, framework `Other`, output directory `public`, and serverless `api/scan.js` available. After saving Production secrets, redeploy the **latest main commit** and verify site and `/api/scan` with Vercel deployment logs. GitHub tests passing **do not** prove Vercel is deployed or the manual button works.
4. Visit the site, run a manual scan with your password if configured, observe GitHub Actions completion and the feed commit, and confirm that Vercel automatically builds updated `main`. If the server endpoint fails, use [manual GitHub Actions scanning](https://github.com/shuofeng666/searching-job/actions/workflows/scan.yml). Each manual run can consume up to 12 paid searches.

Run tests locally with `python -m pip install -r requirements.txt && python -m unittest discover -s tests -v`. Node tests and JavaScript syntax are run automatically by `.github/workflows/tests.yml`. A green CI validates logic/syntax but not job-market comprehensiveness, live API billing, actual Vercel permissions or user-specific work authorization.
