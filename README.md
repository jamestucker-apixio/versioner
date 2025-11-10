# Versioner

A Python package for managing versions across Jupyter notebooks, Databricks delta tables, and Databricks asset bundles.

## Features

- **Notebook Versioning**: Automatically append version numbers to Jupyter notebook filenames
- **Table Name Formatting**: Generate versioned names for Databricks delta tables
- **YAML Updates**: Sync version information to Databricks asset bundle configuration files
  - Updates `version` field in `databricks.yml`
  - Updates `variables.pkg_version.default` field in `resources/variables.yml`
- **CLI & Library**: Use as a command-line tool or import functions into your notebooks

## Installation

```bash
pip install versioner
```

For development:

```bash
git clone https://github.com/JamesMTucker/versioner.git
cd versioner
pip install -e .
```

## Quick Start

### 1. Create a `__version__.py` file in your project

```python
# __version__.py
__version__ = "0.1.0"
```

Place this file in your project root or within your package directory (e.g., `src/mypackage/__version__.py`).

### 2. Version your notebooks

```bash
# Preview changes
versioner notebooks --dry-run

# Apply versioning
versioner notebooks
```

This will rename notebooks like:

- `analysis.ipynb` → `analysis_v0.1.0.ipynb`
- `data_processing_v0.0.1.ipynb` → `data_processing_v0.1.0.ipynb` (updates existing version)

### 3. Update Databricks configuration

```bash
versioner update-yaml
```

This updates:
- The `version` field in your `databricks.yml` file
- The `variables.pkg_version.default` field in your `resources/variables.yml` file

### 4. Use in notebooks for table naming

```python
from versioner import format_table_name

# Create versioned table names
table_name = format_table_name("user_events")
# Returns: "user_events_v0.1.0"

# Use in Databricks SQL
spark.sql(f"CREATE TABLE catalog.schema.{table_name} AS SELECT ...")
```

## CLI Usage

### Version all notebooks

```bash
versioner notebooks
```

Options:

- `--dry-run`: Preview changes without modifying files

### Update databricks.yml

```bash
versioner update-yaml
```

Options:

- `--dry-run`: Preview changes without modifying files
- `--no-backup`: Don't create a `.yml.bak` backup file

### Run all operations

```bash
versioner all
```

This runs both notebook versioning and YAML updates in one command.

### Show version information

```bash
versioner version
```

## Library API

### Import functions

```python
from versioner import (
    format_table_name,
    format_full_table_path,
    get_project_version,
    version_all_notebooks,
)
```

### Table Name Formatting

```python
# Basic usage
table_name = format_table_name("my_table")
# Returns: "my_table_v0.1.0"

# Custom separator
table_name = format_table_name("my_table", separator=".")
# Returns: "my_table.v0.1.0"

# Full path with catalog and schema
full_path = format_full_table_path("my_table", "prod_catalog", "analytics_schema")
# Returns: "prod_catalog.analytics_schema.my_table_v0.1.0"
```

### Get Current Version

```python
version = get_project_version()
print(f"Current version: {version}")
```

### Version Notebooks Programmatically

```python
from pathlib import Path
from versioner import version_all_notebooks, print_version_results

# Version all notebooks
results = version_all_notebooks()
print_version_results(results)

# Dry run from specific directory
results = version_all_notebooks(
    root_dir=Path("/path/to/project"),
    dry_run=True
)
```

## How It Works

### Notebook Versioning

1. Recursively scans for `.ipynb` files
2. Parses existing version suffix (if present) from filename
3. Compares with current version from `__version__.py`
4. Renames files in place if version differs
5. Skips files already at current version

**Filename format**: `{base_name}_v{version}.ipynb`

Examples:

- `analysis.ipynb` → `analysis_v0.1.0.ipynb`
- `model_v0.1.0.ipynb` → `model_v0.2.0.ipynb` (when version changes)

### Version Detection

The package searches for `__version__.py` in:

1. Current directory
2. `src/` directory
3. Package directories within `src/`
4. Parent directory

Supported version formats:

```python
__version__ = "0.1.0"
__version__ = '0.1.0'
__version__: str = "0.1.0"
```

### YAML Updates

Updates version information in Databricks asset bundle configuration files:

#### databricks.yml
Updates the top-level `version` field:

```yaml
# Before
version: 0.1.0

# After running versioner update-yaml (with __version__.py = "0.2.0")
version: 0.2.0
```

#### resources/variables.yml
Updates the `variables.pkg_version.default` field:

```yaml
# Before
variables:
  pkg_version:
    description: "The version of the python package"
    default: "0.1.0"

# After running versioner update-yaml (with __version__.py = "0.2.0")
variables:
  pkg_version:
    description: "The version of the python package"
    default: "0.2.0"
```

Creates backup files (`.yml.bak`) by default for both files that are updated.

## Configuration

No configuration file needed! The package:

- Reads version from `__version__.py` in your project
- Looks for `databricks.yml` in the project root
- Looks for `resources/variables.yml` in the project
- Operates on the current working directory
- Gracefully skips any YAML files that don't exist

## Examples

### Workflow Example

```bash
# 1. Update your version
echo '__version__ = "0.2.0"' > __version__.py

# 2. Preview changes
versioner all --dry-run

# 3. Apply all changes
versioner all
```

### Notebook Example

```python
# In your Databricks notebook
from versioner import format_table_name, get_project_version

# Get current version
version = get_project_version()
print(f"Running analysis version: {version}")

# Create versioned tables
bronze_table = format_table_name("bronze_events")
silver_table = format_table_name("silver_events")

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS catalog.schema.{bronze_table} (
        event_id STRING,
        timestamp TIMESTAMP,
        data STRING
    )
""")
```

### Python Script Example

```python
#!/usr/bin/env python3
from versioner import version_all_notebooks, update_all_yaml_files

# Version everything
print("Versioning notebooks...")
results = version_all_notebooks()

print("Updating YAML files...")
yaml_results = update_all_yaml_files()
for updated, message in yaml_results:
    print(message)

print("Done!")
```

## Requirements

- Python >= 3.12
- PyYAML >= 6.0

## Development

### Setup

```bash
git clone https://github.com/JamesMTucker/versioner.git
cd versioner
pip install -e .
```

### Project Structure

```
versioner/
    src/
        versioner/
            __init__.py           # CLI and public API
            __version__.py        # Package version
            version_reader.py     # Read project version
            notebook_versioner.py # Notebook versioning logic
            table_namer.py        # Table name formatting
            yaml_updater.py       # YAML file updates
        pyproject.toml
        README.md
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Author

James M Tucker, Ph.D. (james.tucker@datavant.com)
