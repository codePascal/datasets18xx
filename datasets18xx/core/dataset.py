#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataset module

Module implements the handling of a 18xx dataset with raw transcript and
processed result paths.
"""
import logging
import os

from pathlib import Path
from tqdm import tqdm

import pandas as pd
import transcripts18xx as trx

from ..io import io, local
from ..utils import pooling
from . import config, context_manager

logger = logging.getLogger(__name__)


class Dataset18xx:
    """Dataset18xx

    Class to maintain a dataset for a given 18xx game. The class is used to
    access the raw transcript and processed result files.

    Args:
        db: Path to the database.
        game: The game to load the dataset.
        conf: The dataset config.

    Attributes:
        game: The game to load the dataset.
        conf: The dataset config.
        root: The root folder of the dataset.
    """

    def __init__(self, db: Path, game: trx.Games, conf: config.DatasetConfig):
        self.db = db
        self.game = game
        self.conf = conf

        self.root = self._create_root()

        self._raw = local.find_raw_transcripts(self.root)

        self._metadata_path = self.root.joinpath('metadata.json')
        self._context_path = self.root.joinpath('context.csv')
        self._ctx_manager = context_manager.ContextManager(self._context_path)

    @staticmethod
    def from_db(root: Path) -> "Dataset18xx":
        """Build dataset from dataset root.

        Args:
            root: The root of the dataset.

        Returns:
            The corresponding dataset.
        """
        db = root.parent
        game = trx.Games.argparse(f'G{root.stem[:4]}')
        conf = config.DatasetConfig.from_db(root.stem)
        return Dataset18xx(db, game, conf)

    def _create_root(self) -> Path:
        # Create the root of the dataset.
        root = local.create_root(self.db, self.game.game(), self.conf.suffix())
        if not root.exists():
            raise IOError(f'Dataset does not exist: {root}')
        return root

    def _invoke_parser(self, file: Path) -> None:
        # Invoke the parser in a thread-safe manner.
        trx.TranscriptParser(file, self.game.select()).parse()

    def _create_context(self) -> None:
        # Create the context if it does not exist.
        if not self._context_path.exists():
            context = context_manager.create_context(self._raw)
            self._ctx_manager.add_context(context)

    def prune(self):
        """Delete processed data from the dataset.
        """
        file_list = []
        for root, _, file in os.walk(self.root):
            for f in file:
                p = Path(root).joinpath(f)
                if p.suffix in ['.json', '.csv', '.h5']:
                    file_list.append(p)
        for file in file_list:
            os.remove(file)

    def make(self, force: bool = False) -> pd.DataFrame:
        """Invokes the transcript parser on the raw transcripts.

        Args:
            force: Enforce parsing of valid transcripts without errors such as
                failed verification, missing game finish. Otherwise, only
                transcripts with noted failures will be parsed.

        Returns:
            The parsed dataset context.
        """
        if not force and self._context_path.exists():
            file_list = self._ctx_manager.failed_transcripts()
        else:
            file_list = self._raw
        runner = pooling.PoolRunner(self._invoke_parser, file_list)
        runner.run()
        self._create_context()
        return self._ctx_manager.get_context()

    def context(self, valid_only: bool = False) -> pd.DataFrame:
        """Get the transcript context.

        Args:
            valid_only: To only include valid transcripts.

        Returns:
            The dataframe containing individual transcript contexts.
        """
        df = self._ctx_manager.get_context()
        if valid_only:
            return df[df.valid]
        return df

    def inspect(self) -> dict:
        """Create and write a snapshot of the dataset.

        Returns:
            The snapshot including sizes, distributions, debug data.
        """
        self._create_context()
        snapshot = self._ctx_manager.create_snapshot(debug=True)
        io.write_json(self._metadata_path, snapshot)
        return snapshot

    def subset(self, conf: config.DatasetConfig) -> "Dataset18xx":
        """Create a subset of the current dataset.

        The subset can be created based on the full dataset, not on a subset.
        Can filter number of players and/or game endings.

        Args:
            conf: The dataset config, i.e. number of players, game endings to
                keep.

        Returns:
            The new dataset instance.
        """
        if not isinstance(self.conf, config.DefaultDatasetConfig):
            raise AttributeError('Can only filter default dataset')
        self._create_context()
        raw_transcripts = self._ctx_manager.filter_context(conf)
        target = local.create_root(self.db, self.game.game(), conf.suffix())
        if target.exists():
            raise FileExistsError('Dataset already exists, delete it first.')
        target.mkdir(parents=True, exist_ok=True)
        for file in tqdm(raw_transcripts):
            io.copy_record(file, target)
        new_ds = Dataset18xx(self.db, self.game, conf)
        new_ds.inspect()
        return new_ds

    def load(self, game_id: int) -> trx.TranscriptContext:
        """Load a transcript context.

        Args:
            game_id: The game id to load context from.

        Returns:
            The transcript context to analyse result or metadata.

        Raises:
            ValueError: If game id does not exist of transcript is invalid.
        """
        transcript = self._ctx_manager.raw_transcript(game_id)
        if transcript is None:
            raise ValueError(f'Game ID {game_id} does not exist or is invalid.')
        return trx.TranscriptContext.from_raw(Path(transcript))
