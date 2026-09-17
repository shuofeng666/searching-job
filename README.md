# Research Intern Radar

Research-first tracker for Summer 2027 internships in the United States, Canada, Singapore, and Hong Kong. Prioritizes corporate HCI labs, human–AI interaction, creativity/design tools, collaborative CAD, digital fabrication and research-oriented UX research. Excludes ordinary product-design and pure algorithm roles.

The Vercel site displays public search leads from `public/data/feed.json`, kept distinct from a directory of research labs. Notes, favorites and application status are stored only in the current browser and are not synced. A scheduled GitHub Actions workflow uses a `SERPAPI_KEY` repository secret to search for jobs daily and commit a public feed; without that secret the site intentionally shows no discovered jobs.

**Setup:** Import this repository into Vercel as a static project with output directory `public`. In GitHub Settings → Secrets and variables → Actions, set `SERPAPI_KEY` privately, then trigger Research internship scan under Actions. Never put API keys or personal information in public files. Vercel Git integration should redeploy on commits.

Discovery is not proof of an open posting, Summer 2027 availability, PhD eligibility, visa sponsorship, or publication opportunity. Always confirm on the official employer's site. The dashboard is updated periodically, not in real time; AI analysis and email notifications are not enabled in this edition.
