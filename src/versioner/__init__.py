"""
Versioner: A version management tool for notebooks, Databricks tables, and configuration files.

This package provides tools to:
- Version Jupyter notebooks with semantic versioning
- Format Databricks delta table names with version information
- Update Databricks asset bundle YAML files with current version
  - databricks.yml: Updates top-level 'version' field
  - resources/variables.yml: Updates 'variables.pkg_version.default' field

Example usage in notebooks:
    >>> from versioner import format_table_name
    >>> table = format_table_name("user_events")
    >>> spark.sql(f"CREATE TABLE catalog.schema.{table} ...")

Command-line usage:
    $ versioner notebooks          # Version all notebooks
    $ versioner update-yaml        # Update databricks.yml and resources/variables.yml
    $ versioner all                # Do both operations
"""

import argparse
import sys
from pathlib import Path

# Public API exports
from .table_namer import format_table_name, format_full_table_path
from .version_reader import get_project_version, VersionNotFoundError
from .notebook_versioner import (
    version_all_notebooks,
    version_notebook,
    print_version_results,
)
from .yaml_updater import (
    update_databricks_yaml,
    update_variables_yaml,
    update_all_yaml_files,
    YAMLUpdateError,
)

__all__ = [
    'format_table_name',
    'format_full_table_path',
    'get_project_version',
    'VersionNotFoundError',
    'version_all_notebooks',
    'version_notebook',
    'update_databricks_yaml',
    'update_variables_yaml',
    'update_all_yaml_files',
    'YAMLUpdateError',
]


def cmd_notebooks(args) -> int:
    """Command handler for versioning notebooks."""
    try:
        print(f"Searching for notebooks in: {Path.cwd()}")
        results = version_all_notebooks(dry_run=args.dry_run)

        if not results:
            print("No notebooks found.")
            return 0

        print_version_results(results)
        return 0

    except VersionNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nMake sure your project has a __version__.py file.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_update_yaml(args) -> int:
    """Command handler for updating Databricks YAML files."""
    try:
        results = update_all_yaml_files(
            create_backup_file=not args.no_backup,
            dry_run=args.dry_run
        )

        if not results:
            print("No YAML files found to update.", file=sys.stderr)
            return 1

        # Print all results
        for updated, message in results:
            print(message)

        # Return success if at least one file was updated or would be updated
        any_updated = any(updated for updated, _ in results)
        return 0 if any_updated else 0  # Return 0 even if no updates needed

    except VersionNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_all(args) -> int:
    """Command handler for running all versioning operations."""
    print("=== Versioning Notebooks ===")
    result1 = cmd_notebooks(args)

    print("\n=== Updating Databricks YAML ===")
    result2 = cmd_update_yaml(args)

    return max(result1, result2)


def cmd_version(args) -> int:
    """Command handler for showing version information."""
    from .__version__ import __version__
    print(f"versioner version {__version__}")

    try:
        project_version = get_project_version()
        print(f"Project version: {project_version}")
    except VersionNotFoundError:
        print("Project version: (not found)")

    return 0


def main() -> None:
    """Main entry point for the versioner CLI."""
    parser = argparse.ArgumentParser(
        prog='versioner',
        description='Version management tool for notebooks and Databricks assets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  versioner notebooks              Version all Jupyter notebooks
  versioner notebooks --dry-run    Preview notebook versioning changes
  versioner update-yaml            Update version in databricks.yml and resources/variables.yml
  versioner all                    Version notebooks and update YAML files
  versioner version                Show version information
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Notebooks command
    notebooks_parser = subparsers.add_parser(
        'notebooks',
        help='Version all Jupyter notebooks in the project'
    )
    notebooks_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    notebooks_parser.set_defaults(func=cmd_notebooks)

    # Update YAML command
    yaml_parser = subparsers.add_parser(
        'update-yaml',
        help='Update version in databricks.yml and resources/variables.yml'
    )
    yaml_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    yaml_parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )
    yaml_parser.set_defaults(func=cmd_update_yaml)

    # All command
    all_parser = subparsers.add_parser(
        'all',
        help='Run all versioning operations (notebooks + YAML)'
    )
    all_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    all_parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create a backup of databricks.yml'
    )
    all_parser.set_defaults(func=cmd_all)

    # Version command
    version_parser = subparsers.add_parser(
        'version',
        help='Show version information'
    )
    version_parser.set_defaults(func=cmd_version)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    sys.exit(args.func(args))
