"""Module for reading version information from target projects."""

import ast
import re
from pathlib import Path
from typing import Optional


class VersionNotFoundError(Exception):
    """Raised when version information cannot be found."""
    pass


def find_version_file(start_path: Optional[Path] = None) -> Path:
    """
    Locate the __version__.py file in the project.

    Searches in the following order:
    1. Current directory (__version__.py)
    2. src/ directory (src/__version__.py)
    3. Any package directory in src/ (src/<package>/__version__.py)
    4. Parent directory (../__version__.py)

    Args:
        start_path: Directory to start searching from. Defaults to current working directory.

    Returns:
        Path to the __version__.py file

    Raises:
        VersionNotFoundError: If __version__.py cannot be found
    """
    if start_path is None:
        start_path = Path.cwd()

    search_locations = [
        start_path / "__version__.py",
        start_path / "src" / "__version__.py",
    ]

    # Check for package directories in src/
    src_dir = start_path / "src"
    if src_dir.exists():
        for item in src_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                version_file = item / "__version__.py"
                search_locations.append(version_file)

    # Check parent directory
    search_locations.append(start_path.parent / "__version__.py")

    for location in search_locations:
        if location.exists():
            return location

    raise VersionNotFoundError(
        f"Could not find __version__.py file. Searched locations:\n"
        + "\n".join(f"  - {loc}" for loc in search_locations)
    )


def parse_version_from_file(version_file: Path) -> str:
    """
    Parse the version string from a __version__.py file.

    Supports the following formats:
    - __version__ = "x.y.z"
    - __version__ = 'x.y.z'
    - __version__: str = "x.y.z"

    Args:
        version_file: Path to the __version__.py file

    Returns:
        Version string (e.g., "0.1.0")

    Raises:
        VersionNotFoundError: If version cannot be parsed from file
    """
    content = version_file.read_text()

    # Try using AST parsing (most robust)
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__version__':
                        if isinstance(node.value, ast.Constant):
                            return str(node.value.value)
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == '__version__':
                    if isinstance(node.value, ast.Constant):
                        return str(node.value.value)
    except SyntaxError:
        pass

    # Fallback to regex parsing
    patterns = [
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        r'__version__\s*:\s*str\s*=\s*["\']([^"\']+)["\']',
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1)

    raise VersionNotFoundError(
        f"Could not parse version from {version_file}. "
        "Expected format: __version__ = \"x.y.z\""
    )


def get_project_version(start_path: Optional[Path] = None) -> str:
    """
    Get the current project version from __version__.py.

    This is the main function to use for retrieving version information.

    Args:
        start_path: Directory to start searching from. Defaults to current working directory.

    Returns:
        Version string (e.g., "0.1.0")

    Raises:
        VersionNotFoundError: If version file cannot be found or parsed

    Example:
        >>> version = get_project_version()
        >>> print(f"Current version: {version}")
        Current version: 0.1.0
    """
    version_file = find_version_file(start_path)
    return parse_version_from_file(version_file)
