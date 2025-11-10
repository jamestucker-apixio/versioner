"""Module for versioning Jupyter notebooks."""

import re
from pathlib import Path
from typing import List, Optional, Tuple

from .version_reader import get_project_version

VERSION_PATTERN = re.compile(r"_v(\d+\.\d+\.\d+)\.ipynb$")


def parse_notebook_name(notebook_path: Path) -> Tuple[str, Optional[str]]:
    """
    Parse a notebook filename to extract the base name and version.

    Args:
        notebook_path: Path to the notebook file

    Returns:
        Tuple of (base_name, version) where version is None if not present

    Examples:
        >>> parse_notebook_name(Path("analysis.ipynb"))
        ('analysis', None)

        >>> parse_notebook_name(Path("analysis_v0.1.0.ipynb"))
        ('analysis', '0.1.0')

        >>> parse_notebook_name(Path("my_notebook_v1.2.3.ipynb"))
        ('my_notebook', '1.2.3')
    """
    filename = notebook_path.name

    match = VERSION_PATTERN.search(filename)
    if match:
        version = match.group(1)
        base_name = filename[: match.start()]
        return base_name, version

    # No version found - remove .ipynb extension for base name
    if filename.endswith(".ipynb"):
        base_name = filename[:-6]
        return base_name, None

    return filename, None


def create_versioned_name(base_name: str, version: str) -> str:
    """
    Create a versioned notebook filename.

    Args:
        base_name: Base name without extension or version
        version: Version string (e.g., "0.1.0")

    Returns:
        Versioned filename (e.g., "notebook_v0.1.0.ipynb")

    Examples:
        >>> create_versioned_name("my_notebook", "0.1.0")
        'my_notebook_v0.1.0.ipynb'
    """
    return f"{base_name}_v{version}.ipynb"


def find_notebooks(root_dir: Optional[Path] = None) -> List[Path]:
    """
    Recursively find all Jupyter notebooks in a directory.

    Args:
        root_dir: Directory to search. Defaults to current working directory.

    Returns:
        List of paths to .ipynb files

    Examples:
        >>> notebooks = find_notebooks()
        >>> print(f"Found {len(notebooks)} notebooks")
    """
    if root_dir is None:
        root_dir = Path.cwd()

    return list(root_dir.rglob("*.ipynb"))


def version_notebook(
    notebook_path: Path, target_version: str, dry_run: bool = False
) -> Tuple[bool, Optional[Path], str]:
    """
    Version a single notebook file.

    Args:
        notebook_path: Path to the notebook to version
        target_version: Version to apply
        dry_run: If True, don't actually rename files

    Returns:
        Tuple of (renamed, new_path, message)
        - renamed: Whether the file was/would be renamed
        - new_path: New path if renamed, None otherwise
        - message: Description of action taken

    Examples:
        >>> renamed, new_path, msg = version_notebook(
        ...     Path("analysis.ipynb"), "0.1.0"
        ... )
        >>> print(msg)
        'Versioned: analysis.ipynb -> analysis_v0.1.0.ipynb'
    """
    base_name, current_version = parse_notebook_name(notebook_path)

    if current_version == target_version:
        return False, None, f"Already at version {target_version}: {notebook_path.name}"

    new_name = create_versioned_name(base_name, target_version)
    new_path = notebook_path.parent / new_name

    if new_path.exists() and new_path != notebook_path:
        return False, None, f"Error: Target file already exists: {new_name}"

    action = "Would rename" if dry_run else "Renamed"
    if current_version:
        message = (
            f"{action}: {notebook_path.name} -> {new_name} (from v{current_version})"
        )
    else:
        message = f"{action}: {notebook_path.name} -> {new_name} (added version)"

    if not dry_run and new_path != notebook_path:
        notebook_path.rename(new_path)

    return True, new_path, message


def version_all_notebooks(
    root_dir: Optional[Path] = None,
    target_version: Optional[str] = None,
    dry_run: bool = False,
) -> List[Tuple[bool, Optional[Path], str]]:
    """
    Version all notebooks in a directory tree.

    Args:
        root_dir: Directory to search. Defaults to current working directory.
        target_version: Version to apply. If None, reads from __version__.py
        dry_run: If True, don't actually rename files

    Returns:
        List of results from version_notebook for each notebook found

    Examples:
        >>> # Dry run to see what would change
        >>> results = version_all_notebooks(dry_run=True)
        >>> for renamed, new_path, msg in results:
        ...     print(msg)

        >>> # Actually version all notebooks
        >>> results = version_all_notebooks()
    """
    if root_dir is None:
        root_dir = Path.cwd()

    if target_version is None:
        target_version = get_project_version(root_dir)

    notebooks = find_notebooks(root_dir)
    results = []

    for notebook in notebooks:
        result = version_notebook(notebook, target_version, dry_run)
        results.append(result)

    return results


def print_version_results(results: List[Tuple[bool, Optional[Path], str]]) -> None:
    """
    Print formatted results from versioning operation.

    Args:
        results: List of results from version_notebook or version_all_notebooks
    """
    renamed_count = sum(1 for renamed, _, _ in results if renamed)
    skipped_count = len(results) - renamed_count

    print("\nVersioning complete:")
    print(f"  Files processed: {len(results)}")
    print(f"  Files renamed: {renamed_count}")
    print(f"  Files skipped: {skipped_count}")
    print()

    for renamed, new_path, message in results:
        prefix = "✓" if renamed else "○"
        print(f"{prefix} {message}")
