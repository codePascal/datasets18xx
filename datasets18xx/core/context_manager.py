#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Context manager

Module implements a context manager to summarize contexts from transcripts
and inspect and summarize them.
"""
import ast
import logging

from itertools import chain
from pathlib import Path

import pandas as pd
import transcripts18xx as trx

from ..utils import pooling
from ..io import io
from . import config

logger = logging.getLogger(__name__)


def create_context(file_list: list[Path]) -> pd.DataFrame:
    """Create a context from transcripts.

    Args:
        file_list: The transcript filepaths.

    Returns:
        The context of the transcript contexts.
    """
    runner = pooling.PoolRunner(trx.TranscriptContext.from_raw, file_list)
    ctx = runner.run()
    return pd.DataFrame([io.serialize(c.__dict__) for c in ctx])


class ContextManager:
    """ContextManager

    Class implements a manager to handle the context of a dataset. Upon
    initialization, the context will be loaded if available.

    Args:
        context_path: Path to the dataset's context file.
    """

    def __init__(self, context_path: Path):
        self._context_path = context_path
        if self._context_path.exists():
            self._df = pd.read_csv(self._context_path, header=0)
            self._df.unprocessed_lines = self._df.unprocessed_lines.apply(
                ast.literal_eval)
        else:
            self._df = pd.DataFrame()

    def _size(self) -> int:
        # Get the full size of the dataset.
        return len(self._df)

    def _valid_ctx(self) -> pd.DataFrame:
        # Limit the dataset to its valid entries.
        return self._df[self._df.valid]

    def _valid(self) -> int:
        # Get the size of the valid dataset.
        return len(self._valid_ctx())

    def _num_players(self) -> dict:
        # Get the distribution of the number of players of the valid dataset.
        dist = self._valid_ctx().num_players.value_counts().to_dict()
        return {int(k): v for k, v in dist.items()}

    def _game_ending(self) -> dict:
        # Get the game endings of the valid dataset.
        return self._valid_ctx().game_ending.value_counts().to_dict()

    def _unprocessed_lines(self) -> list[str]:
        # Combine the unprocessed lines for debug purposes.
        unprocessed_lines = self._df.unprocessed_lines.tolist()
        return list(chain.from_iterable(unprocessed_lines))

    def _parsing_failed(self) -> dict:
        # Get the parsing errors and their transcripts for debug purposes.
        errors = self._df[self._df.parse_result != 'SUCCESS']
        grouped = errors.groupby('parse_result')['raw'].apply(list).to_dict()
        result = {k: io.serialize(v) for k, v in grouped.items()}
        return result

    def _verification_failed(self) -> list[str]:
        # Get the verification errors and transcripts for debug purposes.
        file_list = self._df[self._df.verification_result == False].raw.tolist()
        result = io.serialize(file_list)
        return result

    def add_context(self, df: pd.DataFrame) -> None:
        """Add a dataset context to the manager.

        Note: The context will be saved immediately.

        Args:
            df: The dataset context.
        """
        self._df = df
        self._df.to_csv(self._context_path, index=False)

    def get_context(self) -> pd.DataFrame:
        """Get the dataset context.

        Returns:
            The dataset context as frame.
        """
        return self._df

    def create_snapshot(self, debug: bool = False) -> dict:
        """Create a snapshot of the dataset.

        The snapshot will include size, valid transcripts, distribution of the
        number of players and game endings. For debug purposes, it will include
        the unprocessed lines, parsing and verification errors with their
        corresponding transcripts.

        Args:
            debug: To include debug outputs, otherwise these will not be added.

        Returns:
            The snapshot of the dataset with the above-mentioned data.
        """
        snapshot = {
            'size': self._size(),
            'valid': self._valid(),
            'num_players': self._num_players(),
            'game_endings': self._game_ending()
        }

        if debug:
            debug = {
                'unprocessed_lines': sorted(set(self._unprocessed_lines())),
                'parse_errors': self._parsing_failed(),
                'verify_errors': self._verification_failed()
            }
            snapshot['debug'] = debug

        return snapshot

    def failed_transcripts(self) -> list[Path]:
        """Retrieves the paths to the transcripts that failed either parsing or
        verification.

        Returns:
            List of transcripts that failed above-mentioned checks.

        # TODO: check for transcripts with no data (.csv, .json)
        """
        parse_err = list(chain.from_iterable(self._parsing_failed().values()))
        verify_err = self._verification_failed()
        file_list = parse_err + verify_err
        return [Path(f) for f in file_list]

    def filter_context(self, conf: config.DatasetConfig) -> list[Path]:
        """Filter the context based on dataset config.

        Args:
            conf: The dataset config, describing desired players and/or game
                endings.

        Returns:
            List of raw transcripts matching the filter.
        """
        subset = self._df.query(conf.query())
        if subset.empty:
            return []
        return [Path(f) for f in subset.raw.tolist()]

    def raw_transcript(self, game_id: int) -> str | None:
        """Load the raw transcript with given game id.

        Args:
            game_id: The game ID to load raw transcript path.

        Returns:
            The raw transcript file path or None if either game id does not
            exist or is not valid.
        """
        if game_id in self._valid_ctx().game_id.values:
            # There is only one unique game id.
            return self._df[self._df.game_id == game_id].iloc[0].raw
        return None
