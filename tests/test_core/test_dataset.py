#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

from collections import Counter
from pathlib import Path

import transcripts18xx as trx

from datasets18xx.core import dataset, config

from tests import context


class TestDataset(unittest.TestCase):

    @staticmethod
    def count_files_in_dataset(ds: dataset.Dataset18xx) -> dict:
        suffixes = []
        for root, dirs, file in os.walk(ds.root):
            for f in file:
                suffixes.append(Path(root).joinpath(f).suffix)
        return Counter(suffixes)

    def setUp(self) -> None:
        self.ds = context.mocked_dataset()

    def test_make(self):
        self.ds.prune()
        n_files_prune = self.count_files_in_dataset(self.ds)
        self.assertEqual(20, n_files_prune['.txt'])

        self.ds.make(force=True)
        n_files_make = self.count_files_in_dataset(self.ds)
        self.assertEqual(20, n_files_make['.txt'])
        self.assertEqual(20, n_files_make['.json'])
        self.assertEqual(18, n_files_make['.csv'])

    def test_context(self):
        self.ds.make()
        df = self.ds.context(valid_only=False)
        cols = trx.TranscriptContext.__dict__['__annotations__'].keys()
        self.assertListEqual(list(cols), list(df.columns))
        self.assertEqual(20, df.shape[0])

        df2 = self.ds.context(valid_only=True)
        self.assertEqual(14, df2.shape[0])

    def test_inspect(self):
        self.ds.make()
        snapshot = self.ds.inspect()
        self.assertEqual(20, snapshot['size'])
        self.assertEqual(14, snapshot['valid'])
        self.assertEqual({4: 6, 3: 3, 6: 2, 5: 2, 2: 1},
                         snapshot['num_players'])
        self.assertEqual(7, snapshot['game_endings']['BankBroke'])
        self.assertEqual(5, snapshot['game_endings']['PlayerGoesBankrupt'])
        self.assertEqual(2, snapshot['game_endings']['GameEndedManually'])
        self.assertTrue('unprocessed_lines' in snapshot['debug'])
        self.assertTrue('parse_errors' in snapshot['debug'])
        self.assertTrue('verify_errors' in snapshot['debug'])

    def test_subset(self):
        self.ds.make()
        new_conf = config.DatasetConfig(
            num_players={3, 4},
            game_ending={config.GameEnding.BankBroke}
        )
        new_ds = self.ds.subset(new_conf)

        n_files_subset = self.count_files_in_dataset(new_ds)
        self.assertEqual(6, n_files_subset['.txt'])
        self.assertEqual(7, n_files_subset['.json'])
        self.assertEqual(7, n_files_subset['.csv'])

        snapshot = new_ds.inspect()
        self.assertEqual(6, snapshot['size'])
        self.assertEqual(5, snapshot['valid'])
        self.assertEqual({4: 3, 3: 2}, snapshot['num_players'])
        self.assertEqual(5, snapshot['game_endings']['BankBroke'])

        shutil.rmtree(new_ds.root)

    def test_from_db(self):
        dataset_root = context.mocked_database().joinpath('1830')
        ds = dataset.Dataset18xx.from_db(dataset_root)
        self.assertEqual(self.ds.game, ds.game)
        self.assertEqual(self.ds.root, ds.root)
        self.assertEqual(self.ds.conf, ds.conf)
