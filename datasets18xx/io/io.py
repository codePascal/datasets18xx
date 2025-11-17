#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""I/O module

Module implements general usage input/output functionalities.
"""
import json
import os.path
import logging
import shutil

from pathlib import Path

logger = logging.getLogger(__name__)


def home() -> Path:
    """Expand the `~` to the user home.

    Returns:
        Path to the user.
    """
    return Path(os.path.expanduser('~'))


def unix_path(file: Path) -> str:
    """Make Unix path from Windows path.

    Args:
        file: Filepath in windows format.

    Returns:
        Path in Unix format.
    """
    return str(file).replace('\\', '/')


def write_json(file: Path, content: dict) -> None:
    """Write dict to JSON, with indentation of 2.

    Args:
        file: The JSON filepath to write to.
        content: The data to write.
    """
    with open(file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(content, indent=2))


def read_json(file: Path) -> dict:
    """Read a JSON to dict.

    Args:
        file: The JSON filepath to read from.

    Returns:
        The data of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not file.exists():
        raise FileNotFoundError(file)
    with open(file, 'r', encoding='utf-8') as f:
        content = json.load(f)
    return content


def copy_record(file: Path, dest: Path) -> None:
    """Copy a full record to a new directory.

    Args:
        file: The raw transcript filepath.
        dest: The root folder of the new dataset.
    """
    shutil.copytree(file.parent, dest.joinpath(file.parent.name))


def serialize(obj):
    """Serialize an object for JSON.

    Renders WindowsPaths to unix-filepaths.

    Args:
        obj: The object to serialize paths.

    Returns:
        The object with rendered paths.
    """
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(x) for x in obj]
    if isinstance(obj, Path):
        return unix_path(obj)
    if isinstance(obj, str):
        return unix_path(Path(obj))
    return obj
