# Documentation Website

This directory contains the Quarto website for **akl-ped-counts** documentation.

## Building the Website

### Prerequisites

Install [Quarto](https://quarto.org/docs/get-started/):

```bash
# macOS
brew install quarto

# Or download from https://quarto.org/docs/get-started/
```

### Preview Locally

```bash
cd docs
quarto preview
```

This will start a local server (usually at http://localhost:4200) with live reload.

### Build the Website

```bash
cd docs
quarto render
```

The rendered site will be in `_site/`.

## Publishing to GitHub Pages

1. Enable GitHub Pages in your repository settings
2. Set source to GitHub Actions
3. Push the docs to your repository
4. GitHub will automatically build and deploy using Quarto

### Manual Deployment

```bash
cd docs
quarto publish gh-pages
```

## Structure

- `_quarto.yml` - Site configuration
- `index.qmd` - Home page
- `getting-started.qmd` - Installation and quick start
- `api-reference.qmd` - Function documentation
- `examples.qmd` - Code examples
- `data-coverage.qmd` - Dataset overview
- `missing-data.qmd` - Handling missing values
- `visualizations.qmd` - Visualization gallery
- `styles.css` - Custom styling

## Customization

Edit `_quarto.yml` to:
- Update site URL
- Change GitHub repository links
- Modify navigation structure
- Adjust theme colors

## Adding New Pages

1. Create a new `.qmd` file
2. Add it to the `_quarto.yml` sidebar or navbar
3. Rebuild with `quarto render`
