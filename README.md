# Research Internship Deadlines

A deadline-first, HCI-Deadlines-inspired personal tracker for research-oriented Summer 2027 internships in the United States, Canada, Singapore and Hong Kong. The public site is a static Vercel app served from `public/`.

## What the interface shows

- Chronological opportunity cards, with research-topic and location filters. Filters can be shared using URL parameters such as `?sub=HCI,CSCW&loc=US,CA`.
- Official postings verified by inspecting employer pages, labeled separately from unverified search leads and personal entries. The built-in official links are starting points; availability can change.
- A date is shown only if supported by the source. Google 2027 listings give an **anticipated rolling-window end of February 26, 2027**, not a firm deadline: these are explicitly marked rolling and **never receive a precise countdown**. Unknown deadlines appear under a separate TBA section. A countdown is possible only for an explicitly confirmed closing instant with an offset in the data.
- Research teams are listed in a separate directory; appearing there does not mean an internship is open.
- Favorites, notes, application status and manual entries stay in this browser's `localStorage`. They do not sync across devices and are lost when browser site data is cleared.

## Automatic scanning

A GitHub Actions workflow `.github/workflows/scan.yml` uses `SERPAPI_KEY` stored under repository Settings → Secrets and variables → Actions, searches for opportunities, and writes results to `public/data/feed.json`. Without the secret, no automated scan is performed. Search results are candidates, not proof of an open vacancy, eligibility, sponsorship or specific research-team assignment.

Deploy by importing this GitHub repository into Vercel, using the project root and `public` as Output Directory. Commits to `main` should deploy automatically if Git integration is configured. No private keys or personal application notes belong in the public repository. AI analysis, email notifications and multi-device synchronization are not enabled in this edition.

## Research scope

Corporate HCI and visualization research, Human–AI Interaction, creativity support tools, collaborative design/CAD, digital fabrication, and research-oriented UX research. Ordinary product design and pure algorithm internships are filtered out of automated discovery.
