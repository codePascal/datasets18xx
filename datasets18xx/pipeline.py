#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataset pipeline

Module implements entry points for the dataset package.
"""
from pathlib import Path

import transcripts18xx as trx

from .core.config import GameEnding, DatasetConfig, DefaultDatasetConfig
from .core.dataset import Dataset18xx
from .io.database import database


def make_config(num_players: tuple[int] = None,
                game_ending: tuple[GameEnding] = None) -> DatasetConfig:
    """Create dataset configuration.

    Args:
        num_players: Number of players definition.
        game_ending: Game endings for configuration.

    Returns:
        The dataset config based on number of players and game ending.
    """
    if game_ending is None and num_players is None:
        return DefaultDatasetConfig()
    return DatasetConfig.from_cli(num_players, game_ending)


def make_dataset(game: trx.Games = trx.Games.G1830,
                 conf: DatasetConfig = DefaultDatasetConfig) -> Dataset18xx:
    """Create a dataset object.

    Args:
        game: The game to load the dataset.
        conf: The dataset config.

    Returns:
        Dataset instance for game with given database and config.
    """
    return Dataset18xx(database(), game, conf)
