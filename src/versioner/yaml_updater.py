"""Module for updating Databricks asset bundle YAML files with version information."""

import shutil
from pathlib import Path
from typing import Optional, Tuple
import yaml

from .version_reader import get_project_version


class YAMLUpdateError(Exception):
    """Raised when YAML file cannot be updated."""
    pass


def find_databricks_yaml(root_dir: Optional[Path] = None) -> Path:
    """
    Locate the databricks.yml file in the project.

    Args:
        root_dir: Directory to search. Defaults to current working directory.

    Returns:
        Path to databricks.yml file

    Raises:
        YAMLUpdateError: If databricks.yml cannot be found
    """
    if root_dir is None:
        root_dir = Path.cwd()

    yaml_path = root_dir / "databricks.yml"

    if not yaml_path.exists():
        raise YAMLUpdateError(
            f"Could not find databricks.yml in {root_dir}\n"
            "Expected location: databricks.yml"
        )

    return yaml_path


def create_backup(yaml_path: Path) -> Path:
    """
    Create a backup of the YAML file.

    Args:
        yaml_path: Path to the YAML file to backup

    Returns:
        Path to the backup file

    Examples:
        >>> backup = create_backup(Path("databricks.yml"))
        >>> print(backup)
        PosixPath('databricks.yml.bak')
    """
    backup_path = yaml_path.with_suffix('.yml.bak')
    shutil.copy2(yaml_path, backup_path)
    return backup_path


def update_databricks_yaml(
    yaml_path: Optional[Path] = None,
    target_version: Optional[str] = None,
    create_backup_file: bool = True,
    dry_run: bool = False
) -> Tuple[bool, str]:
    """
    Update the version field in a Databricks asset bundle YAML file.

    Args:
        yaml_path: Path to databricks.yml. If None, searches for it automatically.
        target_version: Version to set. If None, reads from __version__.py
        create_backup_file: Whether to create a .bak backup before modifying
        dry_run: If True, don't actually modify the file

    Returns:
        Tuple of (updated, message)
        - updated: Whether the file was/would be updated
        - message: Description of action taken

    Raises:
        YAMLUpdateError: If YAML file cannot be found or updated

    Examples:
        >>> updated, msg = update_databricks_yaml(target_version="0.1.0")
        >>> print(msg)
        'Updated version in databricks.yml: 0.0.1 -> 0.1.0'
    """
    if yaml_path is None:
        yaml_path = find_databricks_yaml()

    if target_version is None:
        target_version = get_project_version(yaml_path.parent)

    # Read the current YAML file
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise YAMLUpdateError(f"Failed to parse YAML file {yaml_path}: {e}")

    if data is None:
        data = {}

    # Get current version if it exists
    current_version = data.get('version')

    if current_version == target_version:
        return False, f"Already at version {target_version}: {yaml_path.name}"

    # Update the version
    data['version'] = target_version

    action = "Would update" if dry_run else "Updated"
    if current_version:
        message = f"{action} version in {yaml_path.name}: {current_version} -> {target_version}"
    else:
        message = f"{action} version in {yaml_path.name}: (no version) -> {target_version}"

    if not dry_run:
        # Create backup if requested
        if create_backup_file:
            backup_path = create_backup(yaml_path)
            message += f" (backup: {backup_path.name})"

        # Write updated YAML
        try:
            with open(yaml_path, 'w') as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise YAMLUpdateError(f"Failed to write YAML file {yaml_path}: {e}")

    return True, message


def get_databricks_version(yaml_path: Optional[Path] = None) -> Optional[str]:
    """
    Get the current version from a Databricks asset bundle YAML file.

    Args:
        yaml_path: Path to databricks.yml. If None, searches for it automatically.

    Returns:
        Current version string, or None if not set

    Raises:
        YAMLUpdateError: If YAML file cannot be found or read
    """
    if yaml_path is None:
        yaml_path = find_databricks_yaml()

    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise YAMLUpdateError(f"Failed to parse YAML file {yaml_path}: {e}")

    if data is None:
        return None

    return data.get('version')


def find_variables_yaml(root_dir: Optional[Path] = None) -> Path:
    """
    Locate the resources/variables.yml file in the project.

    Args:
        root_dir: Directory to search. Defaults to current working directory.

    Returns:
        Path to resources/variables.yml file

    Raises:
        YAMLUpdateError: If resources/variables.yml cannot be found
    """
    if root_dir is None:
        root_dir = Path.cwd()

    yaml_path = root_dir / "resources" / "variables.yml"

    if not yaml_path.exists():
        raise YAMLUpdateError(
            f"Could not find resources/variables.yml in {root_dir}\n"
            "Expected location: resources/variables.yml"
        )

    return yaml_path


def update_variables_yaml(
    yaml_path: Optional[Path] = None,
    target_version: Optional[str] = None,
    create_backup_file: bool = True,
    dry_run: bool = False
) -> Tuple[bool, str]:
    """
    Update the pkg_version.default field in a Databricks variables YAML file.

    Args:
        yaml_path: Path to resources/variables.yml. If None, searches for it automatically.
        target_version: Version to set. If None, reads from __version__.py
        create_backup_file: Whether to create a .bak backup before modifying
        dry_run: If True, don't actually modify the file

    Returns:
        Tuple of (updated, message)
        - updated: Whether the file was/would be updated
        - message: Description of action taken

    Raises:
        YAMLUpdateError: If YAML file cannot be found or updated

    Examples:
        >>> updated, msg = update_variables_yaml(target_version="0.1.0")
        >>> print(msg)
        'Updated pkg_version.default in resources/variables.yml: 0.0.1 -> 0.1.0'
    """
    if yaml_path is None:
        yaml_path = find_variables_yaml()

    if target_version is None:
        target_version = get_project_version(yaml_path.parent.parent)

    # Read the current YAML file
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise YAMLUpdateError(f"Failed to parse YAML file {yaml_path}: {e}")

    if data is None:
        data = {}

    # Ensure variables key exists
    if 'variables' not in data:
        data['variables'] = {}

    # Ensure pkg_version key exists
    if 'pkg_version' not in data['variables']:
        data['variables']['pkg_version'] = {}

    # Get current version if it exists
    current_version = data['variables']['pkg_version'].get('default')

    if current_version == target_version:
        return False, f"Already at version {target_version}: {yaml_path}"

    # Update the version
    data['variables']['pkg_version']['default'] = target_version

    action = "Would update" if dry_run else "Updated"
    if current_version:
        message = f"{action} pkg_version.default in {yaml_path}: {current_version} -> {target_version}"
    else:
        message = f"{action} pkg_version.default in {yaml_path}: (no version) -> {target_version}"

    if not dry_run:
        # Create backup if requested
        if create_backup_file:
            backup_path = create_backup(yaml_path)
            message += f" (backup: {backup_path.name})"

        # Write updated YAML
        try:
            with open(yaml_path, 'w') as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise YAMLUpdateError(f"Failed to write YAML file {yaml_path}: {e}")

    return True, message


def get_variables_version(yaml_path: Optional[Path] = None) -> Optional[str]:
    """
    Get the current pkg_version.default from a Databricks variables YAML file.

    Args:
        yaml_path: Path to resources/variables.yml. If None, searches for it automatically.

    Returns:
        Current version string, or None if not set

    Raises:
        YAMLUpdateError: If YAML file cannot be found or read
    """
    if yaml_path is None:
        yaml_path = find_variables_yaml()

    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise YAMLUpdateError(f"Failed to parse YAML file {yaml_path}: {e}")

    if data is None:
        return None

    if 'variables' not in data:
        return None

    if 'pkg_version' not in data['variables']:
        return None

    return data['variables']['pkg_version'].get('default')


def update_all_yaml_files(
    root_dir: Optional[Path] = None,
    target_version: Optional[str] = None,
    create_backup_file: bool = True,
    dry_run: bool = False
) -> list[Tuple[bool, str]]:
    """
    Update both databricks.yml and resources/variables.yml files.

    Args:
        root_dir: Directory to search. Defaults to current working directory.
        target_version: Version to set. If None, reads from __version__.py
        create_backup_file: Whether to create .bak backups before modifying
        dry_run: If True, don't actually modify files

    Returns:
        List of tuples (updated, message) for each file updated

    Examples:
        >>> results = update_all_yaml_files(target_version="0.1.0")
        >>> for updated, msg in results:
        ...     print(msg)
        'Updated version in databricks.yml: 0.0.1 -> 0.1.0'
        'Updated pkg_version.default in resources/variables.yml: 0.0.1 -> 0.1.0'
    """
    if root_dir is None:
        root_dir = Path.cwd()

    results = []

    # Try to update databricks.yml
    try:
        databricks_path = find_databricks_yaml(root_dir)
        result = update_databricks_yaml(
            databricks_path, target_version, create_backup_file, dry_run
        )
        results.append(result)
    except YAMLUpdateError as e:
        results.append((False, f"Skipped databricks.yml: {e}"))

    # Try to update resources/variables.yml
    try:
        variables_path = find_variables_yaml(root_dir)
        result = update_variables_yaml(
            variables_path, target_version, create_backup_file, dry_run
        )
        results.append(result)
    except YAMLUpdateError as e:
        results.append((False, f"Skipped resources/variables.yml: {e}"))

    return results
