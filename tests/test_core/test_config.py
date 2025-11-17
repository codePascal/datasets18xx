#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from datasets18xx.core import config


class TestGameEnding(unittest.TestCase):

    def test_argparse(self):
        self.assertEqual(
            config.GameEnding.NotFinished,
            config.GameEnding.argparse('NotFinished')
        )
        with self.assertRaises(ValueError) as e:
            config.GameEnding.argparse('UnknownEnding')
        self.assertEqual(
            'Unknown game end: UnknownEnding', e.exception.__str__()
        )


class TestDatasetConfig(unittest.TestCase):

    def test_init_wrong_num_player(self):
        with self.assertRaises(ValueError):
            config.DatasetConfig(num_players={"1"})
        with self.assertRaises(AttributeError):
            # noinspection PyTypeChecker
            config.DatasetConfig(num_players=[1])

    def test_init_wrong_game_ending(self):
        with self.assertRaises(AttributeError):
            # noinspection PyTypeChecker
            config.DatasetConfig(game_ending=[config.GameEnding.BankBroke])
        with self.assertRaises(ValueError):
            config.DatasetConfig(game_ending={1})

    def test_suffix(self):
        conf = config.DatasetConfig(
            num_players={2, 3, 5},
            game_ending={
                config.GameEnding.BankBroke,
                config.GameEnding.PlayerGoesBankrupt
            }
        )
        self.assertEqual('2p3p5p_BankBroke_PlayerGoesBankrupt', conf.suffix())

    def test_suffix_players_only(self):
        conf = config.DatasetConfig(
            num_players={2, 3, 5}
        )
        self.assertEqual('2p3p5p', conf.suffix())

    def test_suffix_end_only(self):
        conf = config.DatasetConfig(
            game_ending={
                config.GameEnding.BankBroke,
                config.GameEnding.PlayerGoesBankrupt
            }
        )
        self.assertEqual('BankBroke_PlayerGoesBankrupt', conf.suffix())

    def test_suffix_default(self):
        self.assertEqual(str(), config.DefaultDatasetConfig().suffix())

    def test_query(self):
        conf = config.DatasetConfig(
            game_ending={
                config.GameEnding.BankBroke,
                config.GameEnding.PlayerGoesBankrupt
            }
        )
        self.assertEqual(
            "game_ending in ['BankBroke', 'PlayerGoesBankrupt']", conf.query()
        )

        conf.num_players = {3}
        conf.game_ending = {config.GameEnding.BankBroke}
        self.assertEqual(
            "num_players in [3] and game_ending in ['BankBroke']", conf.query()
        )

    def test_from_cli(self):
        np = [2, 3]
        conf = config.DatasetConfig.from_cli(np=tuple(np), ge=tuple())
        self.assertEqual({2, 3}, conf.num_players)
        self.assertIsNone(conf.game_ending)

        ge = config.GameEnding.BankBroke
        conf = config.DatasetConfig.from_cli(np=tuple(), ge=tuple([ge]))
        self.assertIsNone(conf.num_players)
        self.assertEqual({ge}, conf.game_ending)

        conf = config.DatasetConfig.from_cli(np=None, ge=None)
        self.assertIsInstance(conf, config.DefaultDatasetConfig)

    def test_from_db(self):
        dataset_name = '1830_3p4p_BankBroke'
        conf = config.DatasetConfig.from_db(dataset_name)
        self.assertEqual({3, 4}, conf.num_players)
        self.assertEqual({config.GameEnding.BankBroke}, conf.game_ending)

        dataset_name = '1830_BankBroke_PlayerGoesBankrupt'
        conf = config.DatasetConfig.from_db(dataset_name)
        self.assertIsNone(conf.num_players)
        self.assertEqual(
            {config.GameEnding.BankBroke, config.GameEnding.PlayerGoesBankrupt},
            conf.game_ending
        )

