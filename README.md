# Pedestrian Counts in Auckland CBD

[![PyPI version](https://img.shields.io/pypi/v/auckland-ped-counts)](https://pypi.org/project/auckland-ped-counts/)
[![Python](https://img.shields.io/pypi/pyversions/auckland-ped-counts)](https://pypi.org/project/auckland-ped-counts/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Hourly pedestrian count data from [Heart of the City Auckland](https://www.hotcity.co.nz/pedestrian-counts)'s pedestrian monitoring system, covering **21 sensor locations** across Auckland CBD from **2019 to 2025**.

---

## Building and publishing with uv

### Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you haven't already:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

You will also need accounts on both [TestPyPI](https://test.pypi.org/account/register/) and [PyPI](https://pypi.org/account/register/), each with an API token generated from **Account Settings → API tokens**.

### Step 1: Build the package

```bash
cd auckland-ped-counts
uv build
```

This creates two files in `dist/`:

```
dist/
├── auckland-ped-counts-0.1.0-py3-none-any.whl
└── auckland-ped-counts-0.1.0.tar.gz
```

### Step 2: Publish to TestPyPI

Always test on [TestPyPI](https://test.pypi.org/) first:

```bash
uv publish --publish-url https://test.pypi.org/legacy/
```

uv will prompt for your credentials. Use `__token__` as the username and paste your TestPyPI API token as the password. Alternatively, set the token via an environment variable:

```bash
export UV_PUBLISH_TOKEN=pypi-AgEI...   # your TestPyPI token
uv publish --publish-url https://test.pypi.org/legacy/
```

### Step 3: Verify the TestPyPI install

```bash
# Create a throwaway venv and install from TestPyPI
uv venv /tmp/test-install
source /tmp/test-install/bin/activate

# --extra-index-url ensures pandas is pulled from real PyPI
uv pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  auckland-ped-counts

# Smoke test
python -c "
from auckland-ped-counts import load_hourly, load_locations, list_sensors
print('Sensors:', len(list_sensors()))
print('Hourly shape:', load_hourly().shape)
print('Locations shape:', load_locations().shape)
"

deactivate
```

Expected output:

```
Sensors: 21
Hourly shape: (61367, 24)
Locations shape: (21, 3)
```

### Step 4: Publish to PyPI

Once the TestPyPI install looks good:

```bash
export UV_PUBLISH_TOKEN=pypi-AgEI...   # your real PyPI token
uv publish
```

### Version bumps

To release a new version, update the version string in **two places**:

1. `pyproject.toml` → `version = "0.2.0"`
2. `src/auckland-ped-counts/__init__.py` → `__version__ = "0.2.0"`

Then rebuild and publish:

```bash
uv build
uv publish
```

---

## Installation (for users)

```bash
# uv
uv add auckland-ped-counts

# pip
pip install auckland-ped-counts
```

## Quick start

```python
from auckland-ped-counts import load_hourly, load_locations, list_sensors

# Load all hourly counts (61,000+ rows × 21 sensors)
counts = load_hourly()

# Load sensor coordinates (WGS 84)
locations = load_locations()

# See all 21 sensor names
print(list_sensors())
```

## API reference

### `load_hourly(years=None, sensors=None, dropna=False)`

Load hourly pedestrian counts. Returns a DataFrame with columns `date`, `hour`, `year`, plus one column per sensor location.

```python
# Filter by year
df_2024 = load_hourly(years=[2024])

# Filter by sensor
df = load_hourly(sensors=["45 Queen Street", "210 Queen Street"])

# Drop rows with any missing values
df_clean = load_hourly(dropna=True)
```

### `load_daily(years=None, sensors=None, dropna=False)`

Daily totals aggregated from hourly data. Same filtering parameters.

```python
daily = load_daily(years=[2023, 2024])
```

### `load_monthly(years=None, sensors=None, dropna=False)`

Monthly totals. Returns columns `year_month` (Period), `year`, `month`, plus sensor totals.

```python
monthly = load_monthly()
```

### `load_locations()`

Sensor metadata: `Address`, `Latitude`, `Longitude` (WGS 84).

```python
locs = load_locations()
```

### `list_sensors()`

Returns the list of all 21 sensor location names.

### `describe_missing()`

Returns a DataFrame summarising missing data by year and sensor, with columns `year`, `sensor`, `total_hours`, `missing_hours`, `pct_missing`.

```python
from auckland-ped-counts import describe_missing

report = describe_missing()
print(report.query("pct_missing > 1"))
```

## Data coverage

| Year | Rows  | Sensors | Missing (%) | Notes                                    |
|------|-------|---------|-------------|------------------------------------------|
| 2019 | 8,760 | 19      | 0.0         | Complete                                 |
| 2020 | 8,784 | 19      | 0.0         | Complete (leap year)                     |
| 2021 | 8,760 | 19      | 0.0         | Complete                                 |
| 2022 | 8,760 | 21      | 8.2         | Two new sensors added; startup gaps      |
| 2023 | 8,760 | 21      | 0.1         | Near-complete                            |
| 2024 | 8,783 | 21      | 0.0         | Complete (leap year + DST adjustments)   |
| 2025 | 8,760 | 21      | 0.0         | Camera upgrades on 5 Mar for 5 sensors   |

## Handling missing data

Missing values appear as `NaN` in the count columns. They arise from three sources: sensors not yet installed, sensor downtime/maintenance, and data transmission failures.

### Structural missingness

The two **188 Quay Street Lower Albert** sensors (EW and NS) were installed in 2022 and are therefore `NaN` for 2019–2021. To work with a uniform panel across all years, filter to the 19 original sensors:

```python
from auckland-ped-counts import load_hourly, SENSORS_ADDED_2022

df = load_hourly()
original = [c for c in df.columns
            if c not in ("date", "hour", "year")
            and c not in SENSORS_ADDED_2022]
df_uniform = df[["date", "hour", "year"] + original]
```

### Sensor-level gaps

**107 Quay Street** has the highest non-structural missingness (~5.6% overall), concentrated in 2022 during extended sensor maintenance. **150 K Road** has a minor gap (~1.6%) in 2023.

### Recommended approaches to fill missing data

**1. Drop missing rows** — simplest approach, recommended when completeness matters:

```python
df = load_hourly(dropna=True)
# or equivalently
df = load_hourly().dropna()
```

**2. Forward/backward fill** — suitable for short gaps of a few hours:

```python
df = load_hourly()
sensor_cols = [c for c in df.columns if c not in ("date", "hour", "year")]
df[sensor_cols] = df[sensor_cols].ffill(limit=3)  # fill up to 3 consecutive hours
```

**3. Linear interpolation** — smooth estimation across moderate gaps:

```python
df = load_hourly()
sensor_cols = [c for c in df.columns if c not in ("date", "hour", "year")]
df[sensor_cols] = df[sensor_cols].interpolate(method="linear", limit=6)
```

**4. Seasonal median fill** — use the median for the same hour and day-of-week:

```python
df = load_hourly()
sensor_cols = [c for c in df.columns if c not in ("date", "hour", "year")]
df["dow"] = df["date"].dt.dayofweek

for sensor in sensor_cols:
    mask = df[sensor].isna()
    if mask.any():
        medians = df.groupby(["dow", "hour"])[sensor].transform("median")
        df.loc[mask, sensor] = medians[mask]
```

### 2025 camera upgrades

On 5 March 2025, five sensors were upgraded to wider recording zones: 30 Queen Street, 205 Queen Street, 210 Queen Street, 261 Queen Street, and 297 Queen Street. Counts from these sensors may show a step-change from this date. Heart of the City captures the additional area separately — contact them for disaggregated data.

## Sensor locations

The 21 sensors span Auckland CBD from the Viaduct Harbour in the north to Karangahape Road in the south:

- **Waterfront**: 107 Quay Street, 188 Quay Street Lower Albert (EW/NS), Te Ara Tahuhu Walkway
- **Lower Queen Street**: Commerce Street West, 7 Custom Street East, 45 Queen Street, 30 Queen Street
- **Mid-city**: 19 Shortland Street, 2 High Street, 1 Courthouse Lane, 61 Federal Street, 59 High Street
- **Upper Queen Street**: 210 Queen Street, 205 Queen Street, 8 Darby Street (EW/NS), 261 Queen Street, 297 Queen Street
- **Karangahape Road**: 150 K Road, 183 K Road

## Data source and licence

Data collected by [Heart of the City Auckland](https://www.hotcity.co.nz/) using automated pedestrian counting cameras. The system records movements (not images), so no individual information is collected.

Licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

## Package structure

```
auckland-ped-counts/
├── pyproject.toml                      # Build config (hatchling backend, compatible with uv)
├── README.md
├── LICENSE
└── src/auckland-ped-counts/
    ├── __init__.py                     # Public API and version
    ├── loader.py                       # All data loading functions
    ├── py.typed                        # PEP 561 marker
    └── data/
        ├── hourly_counts.csv           # 61,367 rows × 24 columns (~8 MB)
        ├── locations.csv               # 21 sensors with lat/lon
        └── missing_data_report.json    # Per-year/sensor missing data summary
```

## Data cleaning applied

The raw Excel files from Heart of the City required several cleaning steps before bundling:

- **Date corrections**: Feb 4 and Feb 15 were mislabelled as 2017 in the 2019–2021 files; corrected to their respective years.
- **Spelling fix**: "59 High Stret" → "59 High Street".
- **2025 header skip**: Three metadata rows about camera upgrades were removed.
- **Non-data rows dropped**: Monthly summary rows embedded in some Excel files were excluded.
- **Numeric standardisation**: All sensor counts stored as float64 to preserve `NaN` for missing values.

## Citation

If you use this data in research, please cite:

```
Heart of the City Auckland. Pedestrian Monitoring System Data (2019–2025).
https://www.hotcity.co.nz/pedestrian-counts
```
