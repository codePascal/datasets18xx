#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataset config

Module implements a dataset configuration to create subsets of processed
datasets, e.g. limit number of players, specific game endings only.
"""
import logging
import enum
import re

from dataclasses import dataclass

logger = logging.getLogger(__name__)


class GameEnding(enum.IntEnum):
    """GameEnding

    Enum class implements the available game endings.
    """
    NotFinished = 1
    BankBroke = 2
    PlayerGoesBankrupt = 3
    GameEndedManually = 4

    @staticmethod
    def argparse(game_end: str):
        """Maps the game ending to its enum member.

        Args:
            game_end: The enum member name as string.

        Returns:
            The enum member matching to the string.

        Raises:
            ValueError: If ending is not found in the enum.
        """
        try:
            return GameEnding[game_end]
        except KeyError as exc:
            raise ValueError(f'Unknown game end: {game_end}') from exc


@dataclass
class DatasetConfig:
    """DatasetConfig

    Data class implements available filters for the full dataset.

    Attributes:
        num_players: Set of number of players in a game to include as int.
        game_ending: Set of game endings to include, see GameEnding.
    """
    num_players: set = None
    game_ending: set = None

    def __post_init__(self):
        if not self.num_players:
            pass
        else:
            if not isinstance(self.num_players, set):
                raise AttributeError('Number of players must be set of ints')
            if not any(isinstance(p, int) for p in self.num_players):
                raise ValueError('Player number must be of type integer')

        if not self.game_ending:
            pass
        else:
            if not isinstance(self.game_ending, set):
                raise AttributeError('Game endings must be a set of GameEnding')
            if not any(isinstance(e, GameEnding) for e in self.game_ending):
                raise ValueError('Game ending must be of type GameEnding')

    @staticmethod
    def from_db(dir_name: str) -> "DatasetConfig":
        """Build config from dataset directory name.

        Args:
            dir_name: Name of the dataset directory.

        Returns:
            Corresponding dataset config.
        """
        np = [i for i in range(2, 7) if re.search(rf'{i}p', dir_name)]
        ge = [e for e in GameEnding if re.search(rf'{e.name}', dir_name)]
        return DatasetConfig.from_cli(tuple(np), tuple(ge))

    @staticmethod
    def from_cli(np: tuple[int] = None,
                 ge: tuple[GameEnding] = None) -> "DatasetConfig":
        """Create dataset configuration from CLI inputs.

        Args:
            np: Number of players definition, default is None.
            ge: Game endings for configuration, default is None.

        Returns:
            The dataset config based on number of players and game ending.
        """
        if np is not None and len(np) > 0:
            num_players = set(np)
        else:
            num_players = None
        if ge is not None and len(ge) > 0:
            game_ending = set(ge)
        else:
            game_ending = None
        if num_players is None and game_ending is None:
            return DefaultDatasetConfig()
        return DatasetConfig(num_players=num_players, game_ending=game_ending)

    def suffix(self) -> str:
        """Create the suffix for the dataset name based on the config.

        Returns:
            The suffix, i.e. number of players and game endings. E.g,
            `4p_BankBroke` or `3p4p_BankBroke_PlayerGoesBankrupt`.
        """
        # Create the suffix of the dataset name based on config.
        path = str()
        if self.num_players:
            player_str = ''.join(f'{i}p' for i in sorted(self.num_players))
            path = player_str
        if self.game_ending:
            end_str = '_'.join(mem.name for mem in self.game_ending)
            if path:
                path += '_' + end_str
            else:
                path = end_str
        return path

    def query(self) -> str:
        """Construct a query for a dataframe based on config.

        Returns:
            The query to search for num_players and game_ending in context.
        """
        queries = []
        if self.num_players is not None:
            player_search = list(self.num_players)
            player_query = f'num_players in {player_search}'
            queries.append(player_query)
        if self.game_ending is not None:
            ending_search = [ending.name for ending in self.game_ending]
            ending_query = f'game_ending in {ending_search}'
            queries.append(ending_query)
        return ' and '.join(queries)


@dataclass
class DefaultDatasetConfig(DatasetConfig):
    """DefaultDatasetConfig

    Dataclass implements the default config for the full dataset.
    """
    num_players = None
    game_ending = None
