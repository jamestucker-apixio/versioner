"""Module for formatting Databricks delta table names with version information."""

from pathlib import Path
from typing import Optional

from .version_reader import get_project_version, VersionNotFoundError


def format_table_name(base_name: str, separator: str = '_', version: Optional[str] = None) -> str:
    """
    Format a table name with version information.

    Automatically reads the project version from __version__.py and appends it
    to the base table name. This is useful for versioning Databricks delta tables.

    Args:
        base_name: The base name for the table (e.g., "my_table")
        separator: The separator to use between name and version. Defaults to '_'
        version: Optional version string to use instead of auto-detecting from __version__.py

    Returns:
        Formatted table name with version (e.g., "my_table_v0_1_0")

    Raises:
        VersionNotFoundError: If version cannot be determined and not provided

    Examples:
        >>> # In a project with __version__.py containing __version__ = "0.1.0"
        >>> format_table_name("my_table")
        'my_table_v0_1_0'

        >>> format_table_name("my_table", separator='.')
        'my_table.v0_1_0'

        >>> # Manually specify version
        >>> format_table_name("my_table", version="1.2.3")
        'my_table_v1_2_3'

        >>> # For use in Databricks notebooks with catalog and schema:
        >>> table = format_table_name("user_events")
        >>> full_path = f"catalog.schema.{table}"
        >>> print(full_path)
        'catalog.schema.user_events_v0_1_0'
    """
    if version is None:
        version = get_project_version()

    # Replace periods with underscores to avoid Unity Catalog parsing issues
    version = version.replace('.', '_')

    return f"{base_name}{separator}v{version}"


def format_full_table_path(
    base_name: str,
    catalog: str,
    schema: str,
    separator: str = '_',
    version: Optional[str] = None
) -> str:
    """
    Format a complete table path including catalog and schema.

    Args:
        base_name: The base name for the table (e.g., "my_table")
        catalog: Databricks catalog name
        schema: Databricks schema name
        separator: The separator to use between name and version. Defaults to '_'
        version: Optional version string to use instead of auto-detecting

    Returns:
        Full table path (e.g., "catalog.schema.my_table_v0_1_0")

    Examples:
        >>> format_full_table_path("user_events", "prod", "analytics")
        'prod.analytics.user_events_v0_1_0'
    """
    table_name = format_table_name(base_name, separator, version)
    return f"{catalog}.{schema}.{table_name}"
