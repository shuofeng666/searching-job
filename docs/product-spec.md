# Research Internship Radar — product specification

Updated: 2026-09-17. Owner: the single PhD user of this personal dashboard.

## Job to be done

> When a research-focused Summer 2027 internship is announced in the US, Canada, Singapore or Hong Kong, tell me what changed, show the employer's source and uncertainties, and let me decide whether to pursue it **without repeating the same searches manually**.

This is **not** a generic job board. The owner primarily wants a collaboration with a substantial corporate research group that can develop an HCI research agenda, system prototype, user study or publication. UX Research at a large company is acceptable. Do not automatically include small startup Product Design, SWE, ranking/recommendation, foundation-model or ML algorithm roles. A PhD-only requirement or publication possibility must be verified from a posting, never guessed from a company name.

## Comparable systems and what to adopt

1. [HCI Deadlines](https://hci-deadlines.github.io/) and its [conference database](https://github.com/hci-deadlines/conf-database): concise timeline, multi-topic filtering and source-based, structured deadline records. Adopt the compact date-first cards and filtering. Unlike fixed conference dates, internships may be rolling or have **no published deadline**, so do not invent countdowns. Its Google Calendar/ICS export suggests a future enhancement **only for confirmed deadlines**.
2. [2027 internship tracker](https://github.com/SuryaHarikrishnan/2027-internship-tracker): automated multi-source refresh, deduplication and personal application tracking. Adopt dedup and 'new since reviewed'; do not adopt its unrelated mass SWE/AI jobs or take counts as correctness.
3. [FAANG 2027 tracker](https://github.com/Emjumaev/FAANG-2027-Internships-Tracker): company-first monitoring and a visible last-updated timestamp. Adopt source coverage, freshness, and separate labels for a new listing vs an open verified listing. Its roles target software engineering, so its job list cannot be copied into a research-only feed.
4. [Adobe Research internships](https://research.adobe.com/careers/internships/) and [Autodesk Research careers](https://www.research.autodesk.com/careers/): organization-level evidence and prior programs often exist before a specific 2027 posting. Keep such evidence in a *research-team watchlist* instead of labeling the company 'hiring now'.

## Essential views

- **Current 2027 list**: original-source role URL, exact title, actual country only when supported, topic tags, date status (`firm`, `rolling`, `unknown`), discovery date, application state and notes. `year=2027` based on title is STILL a search lead, not an independently verified live opening.
- **Unknown-year review queue**: research internship title with an employer-domain link but no verified cycle. Never silently merge into current jobs. User can check directly when interesting.
- **Group watchlist**: Microsoft, Meta, Adobe, Autodesk always visible. Distinguish no search / search error / no matching result / year-unconfirmed evidence / researched official group. Other large firms rotate; one search query is not a full inventory.
- **History**: 2025/2026 records, historical team publications and program pages clearly marked retrospective. Never project previous-cycle deadlines into 2027.
- **My queue**: current browser favorites, applied, dismissed, notes and 'new since I last reviewed' without exposing application data in the public repository. Cross-device sync is NOT implemented.
- **Run diagnostics**: last scan age, HTTP failures and individual-company query coverage. Show 'no evidence found' not 'no position exists'.

## Data pipeline and trust levels

`source discovered → official employer-domain result → role/title screening → year/title screening → independent page verification (future enhancement) → 2027 open state verified (future enhancement)`.

The current scanner stops at source-domain/title evidence, and clearly flags that limit. It cannot verify start dates, visa eligibility, active opening or application deadlines from a snippet. Do not let any optional LLM override those facts: AI may summarize tradeoffs or describe conceptual research fit **only after** explicit source extraction, and every substantive claim must map to a source passage or be marked unknown. No AI key is necessary for deterministic discovery.

Scanner v4: 12 search requests per run. Four fixed companies, six rotating and two topical searches most days; on Sundays four rotating, two topical and two historical searches. The same four fixed companies receive separate queries every day; this is *not* full coverage of their job boards. The job feed is cleaned of known non-research false positives. Workday employer-specific URLs are allowlisted narrowly, not all Workday hosts. Unknown year stays in the review queue.

## Acceptance checklist

- [x] Company-first daily workflow exists and has mock-based regression tests.
- [x] Product Design, Product Management and algorithm roles are blocked from the research feed.
- [x] Unknown-year leads cannot be automatically called 2027 jobs.
- [x] Source-linked evidence for the four main research groups exists independently of job records.
- [x] Frontend has 'new since reviewed' and a distinct evidence queue.
- [x] Source code, parsing, API authorization and UI-script syntax pass GitHub CI.
- [ ] Verify latest production deployment and browser behavior after Vercel permissions are restored.
- [ ] Verify the manual scan button end-to-end using user-configured Production secrets.
- [ ] Independently check live job pages and published deadlines; audit first 20 accepted leads.
- [ ] Add optional email alerts and source-grounded AI analysis only after reliable discovery.
- [ ] Add calendar export only for *officially verified* deadline timestamps.

## Operational restrictions

GitHub Actions carries `SERPAPI_KEY` in a repository secret. Vercel holds `GH_ACTIONS_TOKEN` (fine-grained access to this repository's Actions only) and a separate `SCAN_PASSWORD` for the manual button. Nothing secret belongs in `public/`, Git commits, personal notes or chat. Each paid scan is at most 12 SerpApi requests; daily execution consumes roughly 360/month, so inspect quota. User may need to redeploy the latest `main` version after changing Production variables. A GitHub CI success does NOT verify a Vercel production URL. GitHub-to-Vercel linkage and app access must be checked separately.
