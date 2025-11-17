#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

from datasets18xx.core import dataset, config


def mocked_database():
    return Path(__file__).parent.joinpath('resources')


def mocked_dataset():
    return dataset.Dataset18xx(
        mocked_database(),
        dataset.trx.Games.G1830,
        config.DefaultDatasetConfig()
    )
