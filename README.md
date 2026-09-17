# Research Internship Deadlines

A deadline-first tracker for Summer 2027 HCI, Human–AI interaction, CSCW, creativity support, CAD and digital fabrication research internships in the US, Canada, Singapore and Hong Kong. Established corporate research teams are tracked separately from actual open vacancies.

## Website and data integrity

- `/`: current 2027 research opportunities with deadline/date caveats, topic filters, browser-only favorites, an in-page scan control and coverage indicators for Microsoft, Meta, Adobe and Autodesk.
- `/archive.html`: historical 2025/2026 search evidence. A previous posting does **not** mean the 2027 position is open.
- `public/data/feed.json`: current 2027 search leads, scan records and separately retained `watch_leads` when the year is not verified. A search snippet is **not** proof of an active job or a firm deadline.
- Research-team directory entries are monitoring targets, not open jobs. Company coverage `matched: 0` means zero matches in that particular query, **not** no jobs exist.

## Automatic and manual scanning

The GitHub Actions workflow `.github/workflows/scan.yml` runs `scanner_v3.py` daily and supports manual dispatch. The GitHub Actions secret `SERPAPI_KEY` is required for paid searches. Each run uses 12 queries: one each for Microsoft, Meta, Autodesk and Adobe; four rotating large companies; two HCI-oriented topic searches; two historical queries. It intentionally filters out generic Product Design, Product Management, algorithm and model-training jobs. Employer-domain snippets with no confirmed hiring year go into `watch_leads`, never into 2027 openings. All search leads need human validation against the real role page, including location, eligibility, working authorization and date.

The homepage's **立即搜索新岗位** button calls the password-protected Vercel Function in `api/scan.js`. It is disabled until both production environment variables below are configured. The endpoint checks GitHub run status and enforces a 15-minute cooldown, so public visitors cannot trigger paid searches without the password. The password is sent only to the backend for each click, never saved by the browser or committed.

### One-time configuration by the repo owner (DO NOT send secrets in chat)

1. In GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens, create a token for owner `shuofeng666`, **Only select repositories** → `searching-job`, **Actions: Read and write** and Metadata: Read (implicit). Do not give broad repository or account access. Choose an expiration date you can renew later.
2. Open Vercel → `searching-job` → Settings → Environment Variables. Add **`GH_ACTIONS_TOKEN`** (the fine-grained GitHub token) and **`SCAN_PASSWORD`** (a separate random password of at least 16 characters). Set the variables to **Production** and use Sensitive/Encrypted if offered. They belong in Vercel, not GitHub source files or a browser-visible env variable.
3. Redeploy the latest **main** production deployment from Vercel → Deployments after adding variables. Open the website and check that the button displays `▶ 立即搜索新岗位`. Press it, enter your chosen scanning password and wait for GitHub Actions. The site updates after the feed commit and successful Git integration deployment.
4. If the button reports API unavailable, check Vercel Functions and Git integration. The fallback GitHub Actions entry remains available from the homepage; use `workflow_dispatch` → Run workflow.

A single scan consumes up to 12 SerpApi searches. Daily scans are roughly 360/month if all run. Check SerpApi quota. The GitHub token and password are never placed in `public/`, localStorage, query strings, or logs.

## Deployment and tests

Import the GitHub repo into Vercel using repository root, Framework `Other`, Output Directory `public`, and no custom build command. The `/api/scan` Node.js file runs server-side, not as a public static file. Git integration needs to connect the `main` branch for automatic redeployments. Run `python -m unittest discover -s tests -v` to test scanning without paid API calls. `ui_patch.py` idempotently adds the scan UI loader and archive link to the existing design; `.github/workflows/install-scan-ui.yml` installs it on update.

AI review, email notification, reliable automatic deadline extraction and cross-device synchronization are not yet implemented.
