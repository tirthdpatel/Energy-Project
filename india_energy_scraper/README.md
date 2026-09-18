# 🇮🇳 India Energy Atlas Data Scrapers

A production-ready suite of Python web scrapers designed to automatically crawl, validate, and aggregate India's state-level energy capacity and generation data from official sources (NPP, MNRE, Grid-India, ICED).

## 📊 Features
- Discovers and downloads published datasets (PDFs, XLSX, CSV, JSON APIs, dynamic dashboards).
- Implements comprehensive cross-validation and reconciliation (flagging discrepancies >5%).
- Normalizes units natively `(Capacity=MW, Generation=GWh)`.
- Fully typed data schemas using `Pydantic`.
- Configurable rate-limiting, respects `robots.txt`, and uses `httpx` with exponential backoff for transient failures.

## 🛠 Prerequisites & Installation

```bash
# 1. Clone the repository and setup your virtual environment
python -m venv venv
# Windows: venv\\Scripts\\activate | Mac/Linux: source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup browsers for Javascript rendering
playwright install chromium

# 4. Optional: Create an environment file
cp .env.example .env
```

## 🚀 Running the Scraper

To run the full suite:
```bash
python main.py
```

### Outputs
Data will be stored in your `STORAGE_ROOT` (default `data/`) in the following structure:
```
/data/npp.gov.in/2026-02-27/pages/
/data/npp.gov.in/2026-02-27/assets/
```

The final reconciled outputs are generated in the `output/` directory:
1. `india_energy_atlas_combined_YYYYMMDD.jsonl`
2. `india_energy_atlas_time_series_YYYYMMDD.csv`
3. `cross_validation_report.md`
4. `verification_dashboard.html`

## 🔄 Refreshing the CEA datasets

The Simple view's sector dashboards (`/api/sectors`) are served from the CEA
snapshot in `web/frontend/api/data/scraped/cea/<date>/`. Refresh it with:

```bash
python -m scrapers.cea_extractor            # fetch a new dated snapshot
python -m scrapers.cea_extractor --check    # validate the newest snapshot
```

The extractor pulls all twelve `cea.nic.in/api` feeds (installed capacity,
renewables split, generation by mode, peak demand, transmission and more),
validates each response, and only writes once every endpoint checks out — a
partial outage leaves the previous snapshot in place. The web API always reads
the most recent dated folder, so a successful run is picked up with no code
change.

Runs are automated by `.github/workflows/refresh-cea-data.yml` (daily, plus
manual dispatch). The extractor only writes when the data actually differs from
the snapshot on disk, so an unchanged day commits nothing, and `--keep` prunes
older snapshots so the repo does not grow by ~10 MB per run.

> `cea.nic.in` is unreliable — it often answers `Connection failed` under an
> HTTP 200, or times out entirely. Those responses are rejected rather than
> written, so a failed run simply leaves the previous snapshot in place.

## 🧪 Testing
Run the provided smoke tests using `pytest`:
```bash
pytest tests/
```

## 📅 Scheduling Recommendations
- **Full Run**: Once per month (e.g. on the 5th) to capture updated monthly consolidated generation data.
- **Daily Check**: Set up a CRON job to run specifically the `GridIndiaExtractor` to append daily generation status files to your dataset.
