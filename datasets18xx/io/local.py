#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Local module

Module implements functionality regarding the local database.
"""
import logging

from pathlib import Path

logger = logging.getLogger(__name__)


def find_raw_transcripts(dataset_dir: Path) -> list[Path]:
    """Loads the raw transcripts from dataset.

    Args:
        dataset_dir: The directory of the dataset.

    Returns:
        List of raw transcript filepaths which are part of the dataset.
    """
    # TODO: check if dir is <game>_<id> structure
    return sorted(
        [
            d.joinpath(d.name + '.txt') for d in dataset_dir.iterdir()
            if d.is_dir()
        ]
    )


def create_root(root: Path, game: str, conf_suffix: str) -> Path:
    """Create the installation path for the dataset.

    Args:
        root: The root of the database.
        game: The game variant of the dataset.
        conf_suffix: The dataset configuration suffix, added to the root name.

    Returns:
        The installation path of the dataset.
    """
    base = root.joinpath(game)
    if not conf_suffix:
        return base
    return base.parent.joinpath(base.name + '_' + conf_suffix)
