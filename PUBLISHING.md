# Publishing akl-ped-counts to PyPI

## Package Status

✅ **Package is ready for publication**

- Build completed successfully
- Wheel created: `akl_ped_counts-0.1.0-py3-none-any.whl` (2.3 MB)
- Source distribution: `akl_ped_counts-0.1.0.tar.gz` (2.2 MB)
- All naming is consistent (`akl_ped_counts`)
- Documentation updated to UK English
- README cleaned and focused on users
- Quarto website created with examples

## Publishing to PyPI

### Step 1: Get Your PyPI API Token

1. Go to https://pypi.org/account/login/
2. Navigate to Account Settings → API tokens
3. Click "Add API token"
4. Give it a name (e.g., "akl-ped-counts upload")
5. Set scope to "Entire account" or specific to this project
6. Copy the token (starts with `pypi-...`)

### Step 2: Publish the Package

**Option A: Using Environment Variable (Recommended)**

```bash
cd /Users/dataandcrowd/Github/akl-ped-counts

# Set your PyPI token
export UV_PUBLISH_TOKEN="pypi-AgEI..."  # Replace with your actual token

# Publish to PyPI
uv publish
```

**Option B: Interactive Login**

```bash
cd /Users/dataandcrowd/Github/akl-ped-counts
uv publish

# When prompted:
# Username: __token__
# Password: (paste your PyPI API token)
```

### Step 3: Verify Publication

After publishing, verify at:
https://pypi.org/project/akl-ped-counts/

Then test installation:

```bash
# Create a test environment
uv venv /tmp/test-install
source /tmp/test-install/bin/activate

# Install from PyPI
pip install akl-ped-counts

# Quick test
python -c "from akl_ped_counts import load_hourly; print(load_hourly().shape)"

# Expected output: (61367, 24)
deactivate
```

## Testing on TestPyPI First (Optional but Recommended)

If you want to test before publishing to the real PyPI:

### 1. Get TestPyPI Token

- Go to https://test.pypi.org/account/register/
- Create account and get API token from Account Settings

### 2. Publish to TestPyPI

```bash
export UV_PUBLISH_TOKEN="pypi-AgEI..."  # Your TestPyPI token
uv publish --publish-url https://test.pypi.org/legacy/
```

### 3. Test Installation from TestPyPI

```bash
uv venv /tmp/test-install
source /tmp/test-install/bin/activate

# Install from TestPyPI (use PyPI for dependencies)
pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  akl-ped-counts

# Test it
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

### 4. If TestPyPI Works, Publish to Real PyPI

```bash
export UV_PUBLISH_TOKEN="pypi-AgEI..."  # Your real PyPI token
uv publish
```

## Post-Publication Checklist

After successful publication:

- [ ] Verify package page: https://pypi.org/project/akl-ped-counts/
- [ ] Test installation: `pip install akl-ped-counts`
- [ ] Update GitHub repository with release tag
- [ ] Build and deploy Quarto documentation website
- [ ] Share the package!

## Troubleshooting

### "Package already exists"

If you get this error, it means version 0.1.0 is already published. You need to:

1. Update version in `pyproject.toml`: `version = "0.1.1"`
2. Update version in `src/akl_ped_counts/__init__.py`: `__version__ = "0.1.1"`
3. Rebuild: `uv build`
4. Publish again: `uv publish`

### "Invalid credentials"

- Make sure you're using `__token__` as username (not your PyPI username)
- Verify your token is correct and hasn't expired
- Check you're using the right token (TestPyPI vs PyPI)

### "Missing dependencies"

If the build fails, ensure all build dependencies are available:

```bash
uv build --index-strategy unsafe-best-match
```

## Deploying Documentation Website

After publishing to PyPI, deploy the Quarto website:

```bash
cd docs

# Update _quarto.yml with your GitHub username
# Then preview locally
quarto preview

# When ready, publish to GitHub Pages
quarto publish gh-pages
```

Your documentation will be available at:
`https://[your-username].github.io/akl-ped-counts/`

## Future Updates

To publish a new version:

1. Make your changes
2. Update version in both:
   - `pyproject.toml`
   - `src/akl_ped_counts/__init__.py`
3. Rebuild: `uv build`
4. Publish: `uv publish`

## Questions?

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed build instructions.
