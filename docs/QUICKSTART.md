# CVE.ICU Quick Start Guide 🚀

> **Quick reference for commands, data locations, and GitHub Actions setup**

## 📋 Table of Contents
- [GitHub Actions Setup](#github-actions-setup)
- [Local Development Commands](#local-development-commands)
- [Data File Locations](#data-file-locations)
- [Growth Table Format](#growth-table-format)
- [Monthly Status Format](#monthly-status-format)
- [NVD Status Analysis](#nvd-status-analysis)

---

## ⚙️ GitHub Actions Setup

### Enabling GitHub Actions

GitHub Actions are **automatically enabled** when you push the repository to GitHub. The workflows are defined in `.github/workflows/`:

| Workflow | File | Purpose |
|----------|------|---------|
| **Build & Deploy** | `deploy.yml` | Full build + GitHub Pages deployment |
| **CI Tests** | `ci.yml` | Run tests on PRs and feature branches |

### How It Works

1. **Push to GitHub** - Just push your code to the `main` branch:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

2. **Automatic Scheduling** - The workflow runs automatically:
   - **Every 6 hours** (0:00, 6:00, 12:00, 18:00 UTC)
   - On every push to `main`
   - Manually via "Actions" tab → "Run workflow"

3. **Enable GitHub Pages** (one-time setup):
   - Go to **Settings** → **Pages**
   - Under "Build and deployment", select:
     - Source: **Deploy from a branch**
     - Branch: **gh-pages** / **(root)**
   - Click **Save**

4. **View Action Runs**:
   - Go to the **Actions** tab in your GitHub repository
   - Click on any workflow run to see logs and status

### Manual Trigger

To manually run the workflow:
```bash
# Via GitHub CLI
gh workflow run deploy.yml

# Or via GitHub UI: Actions → "Build and Deploy CVE.ICU" → "Run workflow"
```

---

## 🖥️ Local Development Commands

### Quick Reference

```bash
# Install dependencies
make install
# OR: pip install -r requirements.txt

# Full build (downloads data + generates all files)
make build
# OR: python build.py

# Quick build (templates only, no data regeneration)
make quick
# OR: python data/scripts/quick_build.py

# Start local server
make serve
# OR: cd web && python -m http.server 8000
# Then open: http://localhost:8000

# Run tests
make test
# OR: python -m pytest tests/ -v

# Clean build artifacts
make clean
```

### Individual Data Rebuilds

Rebuild specific analysis without full build:

```bash
# Rebuild NVD Status Analysis (monthly status + growth table)
make rebuild-nvd-status

# Other rebuild targets
make rebuild-cna       # CNA analysis
make rebuild-cpe       # CPE/product analysis
make rebuild-cvss      # CVSS score analysis
make rebuild-cwe       # CWE weakness analysis
make rebuild-growth    # Growth trends
make rebuild-quality   # Data quality metrics

# Rebuild ALL analysis files
make rebuild-all
```

### Build Options

```bash
# Verbose build (default)
python build.py

# Quiet mode (for CI)
python build.py --quiet

# With validation
python build.py --validate

# Using environment variable
CVE_BUILD_QUIET=1 python build.py
```

---

## 📁 Data File Locations

### Where to Find Data

After running `make build` or `python build.py`, all generated data is in `web/data/`:

| File | Description | View At |
|------|-------------|---------|
| **`cve_YYYY.json`** | CVE data for specific year (e.g., `cve_2024.json`) | `years.html` |
| **`cve_all.json`** | Aggregated summary of all CVEs | `index.html` |
| **`yearly_summary.json`** | Year-over-year statistics | `years.html` |
| **`growth_table.json`** | **Quarterly breakdown + YoY deltas** | `nvd-status.html` |
| **`nvd_status_analysis.json`** | **Monthly status aggregation** | `nvd-status.html` |
| **`cna_analysis.json`** | CNA assignment statistics | `cna.html` |
| **`cvss_analysis.json`** | CVSS score distributions | `cvss.html` |
| **`cwe_analysis.json`** | CWE classification data | `cwe.html` |
| **`cpe_analysis.json`** | Vendor/product analysis | `cpe.html` |
| **`calendar_analysis.json`** | Publication timing patterns | `calendar.html` |
| **`growth_analysis.json`** | CVE growth trends | `growth.html` |
| **`epss_analysis.json`** | EPSS scoring data | `epss.html` |
| **`kev_analysis.json`** | Known Exploited Vulnerabilities | `kev.html` |

### Yearly Data Quick Access

Each year has its own JSON file with detailed CVE data:

```
web/data/
├── cve_1999.json
├── cve_2000.json
├── ...
├── cve_2024.json
├── cve_2025.json
└── cve_2026.json
```

**View yearly data directly:**
- Local: `http://localhost:8000/data/cve_2024.json`
- Live: `https://cve.icu/data/cve_2024.json`

### Cache Files (Raw Data)

Downloaded source data is cached in `data/cache/`:

| File | Description |
|------|-------------|
| `nvd.json` | Raw NVD vulnerability data |
| `epss_scores-current.json` | EPSS scoring data |
| `known_exploited_vulnerabilities.json` | CISA KEV catalog |
| `cna_list.json` | CNA registry data |
| `cvelistV5/` | Cloned CVE V5 Git repository |

---

## 📊 Growth Table Format

The **growth_table.json** contains quarterly CVE breakdowns with year-over-year analysis.

### Location
- **File:** `web/data/growth_table.json`
- **Page:** `nvd-status.html`

### Schema

```json
[
  {
    "year": 2024,
    "q1": 10234,
    "q2": 11456,
    "q3": 12789,
    "q4": 8234,
    "total_actual": 42713,
    "projection": 48000,
    "cumulative": 298000,
    "yoy_difference": 5678,
    "delta_percent": 15.3,
    "is_ytd": false
  }
]
```

### Field Descriptions

| Field | Description | Example |
|-------|-------------|---------|
| `year` | Calendar year | `2024` |
| `q1` | CVEs published in Jan-Mar | `10234` |
| `q2` | CVEs published in Apr-Jun | `11456` |
| `q3` | CVEs published in Jul-Sep | `12789` |
| `q4` | CVEs published in Oct-Dec | `8234` |
| `total_actual` | Sum of all quarters | `42713` |
| `projection` | Projected full-year total (for current year) | `48000` |
| `cumulative` | Running total of all CVEs up to this year | `298000` |
| `yoy_difference` | Absolute change from previous year | `5678` |
| `delta_percent` | Percentage change from previous year | `15.3` |
| `is_ytd` | Whether this is a year-to-date (current year) | `false` |

### Example Table Rendering

| Year | Q1 | Q2 | Q3 | Q4 | TOTAL | Projection | Cumulative | YoY Diff | Delta % |
|------|-----|-----|-----|-----|-------|------------|------------|----------|---------|
| 2023 | 9.5K | 10.2K | 11.1K | 9.8K | 40.6K | - | 255K | +4.2K | +11.5% |
| 2024 | 10.2K | 11.5K | 12.8K | 8.2K* | 42.7K | 48K | 298K | +2.1K | +5.2% |

*Q4 in progress for current year

---

## 📈 Monthly Status Format

The **nvd_status_analysis.json** contains monthly aggregation of NVD vulnerability statuses.

### Location
- **File:** `web/data/nvd_status_analysis.json`
- **Page:** `nvd-status.html`

### Schema

```json
{
  "generated_at": "2024-01-15T00:00:00Z",
  "total_cves_processed": 303456,
  "monthly_status_aggregation": {
    "2024-01": {
      "Analyzed": 1523,
      "Awaiting Analysis": 2971,
      "Modified": 2485,
      "Rejected": 672,
      "Received": 180,
      "Undergoing Analysis": 31
    },
    "2024-02": { ... }
  },
  "monthly_status_deltas": {
    "2024-02": {
      "Analyzed": 234,
      "Awaiting Analysis": -150,
      ...
    }
  },
  "recent_activity": {
    "last_7_days": {
      "Analyzed": 89,
      "Modified": 156,
      ...
    },
    "last_30_days": { ... }
  },
  "cna_vulnerability_mapping": {
    "Microsoft": { "2024": 1234, "2023": 987 },
    "Google": { "2024": 567, "2023": 432 },
    ...
  }
}
```

### Status Definitions

| Status | Description |
|--------|-------------|
| **Analyzed** | CVE has been fully analyzed by NVD |
| **Awaiting Analysis** | In the NVD queue, waiting to be analyzed |
| **Modified** | CVE record has been updated since initial analysis |
| **Rejected** | CVE has been rejected or withdrawn |
| **Received** | Received by NVD but not yet processed |
| **Undergoing Analysis** | Currently being analyzed by NVD |

### Example Monthly Status Table

| Month | Analyzed | Awaiting Analysis | Modified | Rejected | Received | Undergoing |
|-------|----------|-------------------|----------|----------|----------|------------|
| 2024-01 | 1,523 | 2,971 | 2,485 | 672 | 180 | 31 |
| 2024-02 | 1,757 | 2,821 | 2,641 | 698 | 145 | 28 |
| 2024-03 | 1,892 | 3,102 | 2,298 | 721 | 203 | 42 |

---

## 🔍 NVD Status Analysis

### What's Included

The NVD Status page (`nvd-status.html`) provides:

1. **Current Status Snapshot** - Real-time counts of CVEs in each status
2. **Recent Activity** - CVE changes in the last 7 and 30 days
3. **Monthly Status Distribution Chart** - Stacked bar chart of statuses over time
4. **Quarterly CVE Breakdown Chart** - Stacked bar chart by quarter
5. **Growth Table** - Full historical quarterly breakdown with deltas
6. **Top CNAs Chart** - Horizontal bar chart of most active CNAs

### Generating NVD Status Data

```bash
# Generate only NVD status analysis
make rebuild-nvd-status

# OR directly
python data/scripts/rebuild_nvd_status.py

# Full build (includes all analysis)
make build
```

### Output Files Generated

| File | Contents |
|------|----------|
| `web/data/nvd_status_analysis.json` | Monthly status, deltas, recent activity, CNA mapping |
| `web/data/growth_table.json` | Quarterly breakdown with YoY analysis |

---

## 🔗 Quick Links

### Web Pages (after build + serve)

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | http://localhost:8000/ | Main overview |
| **NVD Status** | http://localhost:8000/nvd-status.html | **Monthly status + growth table** |
| Yearly Analysis | http://localhost:8000/years.html | Per-year CVE data |
| Growth Trends | http://localhost:8000/growth.html | Growth analysis |
| CNA Stats | http://localhost:8000/cna.html | CNA activity |
| CVSS Analysis | http://localhost:8000/cvss.html | CVSS scoring |
| CWE Analysis | http://localhost:8000/cwe.html | Weakness types |
| CPE Analysis | http://localhost:8000/cpe.html | Products/vendors |

### JSON Data (direct access)

| Data | URL |
|------|-----|
| Growth Table | http://localhost:8000/data/growth_table.json |
| NVD Status | http://localhost:8000/data/nvd_status_analysis.json |
| CVE 2024 | http://localhost:8000/data/cve_2024.json |
| CNA Analysis | http://localhost:8000/data/cna_analysis.json |
| All Years Summary | http://localhost:8000/data/yearly_summary.json |

---

## 🆘 Troubleshooting

### Common Issues

**Build fails with "No NVD data":**
```bash
# Force download fresh data
cd data && python -c "
from download_cve_data import CVEDataDownloader
d = CVEDataDownloader()
d.ensure_data_available(force=True)
"
```

**GitHub Actions not running:**
- Check **Settings** → **Actions** → **General** → Enable "Allow all actions"
- Ensure workflows exist in `.github/workflows/`

**Empty data files:**
```bash
# Clean and rebuild
make clean
make build
```

**Port 8000 already in use:**
```bash
# Use a different port
cd web && python -m http.server 8080
```

---

## 📚 Further Reading

- [Architecture Guide](ARCHITECTURE.md) - System design and data flow
- [JSON Schemas](SCHEMAS.md) - Complete output file specifications
- [Counting Methodology](COUNTING.md) - How CVEs are counted
- [Development Roadmap](ROADMAP.md) - Project history and future plans

---

*Last updated: January 2026*

