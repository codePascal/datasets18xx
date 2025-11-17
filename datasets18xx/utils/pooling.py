#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Multiprocessing pool executor

Module implements functionality to run a pool executor.
"""
import logging
import multiprocessing as mp

from tqdm import tqdm

logger = logging.getLogger(__name__)


class PoolRunner:
    """PoolRunner

    Class implements a pool executor to run a function on a given list of items.

    Note that this is not race-condition proof. Hence, calling a function that
    writes to a common object, this method will fail.

    Args:
        target: The function to be executed.
        items: The arguments to invoke the function.
    """

    def __init__(self, target, items):
        self.target = target
        self.items = items

    def run(self):
        """Run the pool executor.

        Returns:
            The results gathered from the processes.
        """
        pool = mp.Pool(processes=mp.cpu_count() - 1)
        results = []
        with tqdm(total=len(self.items)) as pbar:
            for res in pool.imap(self.target, self.items):
                pbar.update()
                results.append(res)
                pbar.refresh()
        pool.close()
        pool.join()
        return results
