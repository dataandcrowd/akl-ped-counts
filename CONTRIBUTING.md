# Contributing to akl-ped-counts

This document contains technical information for package maintainers and contributors.

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
cd akl-ped-counts
uv build
```

This creates two files in `dist/`:

```
dist/
├── akl_ped_counts-0.1.0-py3-none-any.whl
└── akl_ped_counts-0.1.0.tar.gz
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
  akl-ped-counts

# Smoke test
python -c "
from akl_ped_counts import load_hourly, load_locations, list_sensors
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
2. `src/akl_ped_counts/__init__.py` → `__version__ = "0.2.0"`

Then rebuild and publish:

```bash
uv build
uv publish
```

## Package structure

```
akl-ped-counts/
├── pyproject.toml                      # Build config (hatchling backend, compatible with uv)
├── README.md
├── LICENSE
├── CONTRIBUTING.md                     # This file
├── examples/                           # Visualisation scripts and outputs
│   ├── march_trajectories.py
│   ├── march_trajectories.png
│   ├── heatmap_hour_dow.png
│   ├── above_below_average.png
│   └── sensor_map.html
└── src/akl_ped_counts/
    ├── __init__.py                     # Public API and version
    ├── loader.py                       # Pandas data loading functions
    ├── polars_loader.py                # Polars data loading functions
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

## Development setup

```bash
# Clone the repository
git clone https://github.com/yourusername/akl-ped-counts.git
cd akl-ped-counts

# Create a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with all dependencies
uv pip install -e ".[all]"

# Run tests (if available)
pytest
```

## Contributing guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Questions or issues?

Please open an issue on GitHub if you encounter any problems or have suggestions for improvements.
