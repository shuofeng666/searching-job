# Research Internship Deadlines

A deadline-first internship tracker for a PhD interested in HCI, human-AI interaction, CSCW, design tools, CAD and fabrication research. Coverage: United States, Canada, Singapore and Hong Kong; established company research teams take priority over startups and generic algorithm positions.

- **Current opportunities:** `/` and `public/data/feed.json` display 2027 role leads. A search result does not prove that a position is still open, is a Summer 2027 role, or supports visas. Closing dates remain unknown unless checked against a dated official posting. Personal favorites and application notes stay in the current browser, not the public repository.
- **Historical library:** `/archive.html` and `public/data/archive.json` collect explicit 2025/2026 references from employer-domain search results. History is evidence that a team advertised a role in a particular year, not proof of a recurring opening. Do not infer 2027 opening or deadlines from past dates.
- **Research teams:** the directory is a watchlist, not evidence that each team is hiring. The historical page also shows which companies have actually been searched and any scan errors.

## How searches work

`scanner_v2.py` is run by `.github/workflows/scan.yml` with `SERPAPI_KEY` held privately in GitHub Actions Secrets. The new daily plan uses **12 requests maximum**: Microsoft, Meta, Autodesk and Adobe receive individual searches each run; four other large firms rotate; two queries search specific HCI and research-oriented UX topics; two gradually build the 2025/2026 archive. This rotation does not mean all firms are checked every day. Only URLs on recognized employer domains with explicit years and relevant title/snippet language are automatically admitted. They remain labeled as search leads until their live official pages are checked.

The first scan on September 17, 2026 used the older broad-query scanner: 12 requests, 8 Google Jobs timeouts, 36 raw results and 22 largely unverified leads. Some results were third-party reposts, algorithm positions, or wrong country labels. The v2 scan intentionally drops these old unverified records from the active feed instead of silently treating them as official opportunities. It does not fabricate replacements; the 2027 and archive feeds may remain empty until evidence is found.

To trigger a scan, configure `SERPAPI_KEY` at GitHub repository Settings → Secrets and variables → Actions and run **Research internship scan** under Actions. Run `python -m unittest discover -s tests -v` to test the scanner before consuming API calls. A scheduled run uses up to 12 SerpApi searches per day (approximately 360 in a 30-day month if every run occurs); check your plan and available credits. GitHub updates `feed.json` and `archive.json`; Vercel will update from `main` only when Git integration is active.

To deploy, import this repository into Vercel as a static project with Output Directory `public` and no build command. API credentials and personal notes must never be committed to the public repository. AI analysis, email notifications, confirmed deadline extraction and cross-device synchronization are not yet enabled.
