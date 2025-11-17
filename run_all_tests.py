#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import math
import subprocess

from pytest import ExitCode


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run tests')
    parser.add_argument('--coverage', action='store_true', help='Coverage')
    return parser.parse_args()


def run_tests() -> None:
    ret = subprocess.run(['pytest', 'tests/', '--disable-warnings'])
    print(delimiter('test session result'))
    print(ExitCode(ret.returncode).name)


def run_tests_with_coverage() -> None:
    ret = subprocess.run(['coverage', 'run', '-m', 'pytest', 'tests/'])
    if ret.returncode == ExitCode.NO_TESTS_COLLECTED:
        pass
    else:
        print(delimiter('generating coverage report'))
        subprocess.run(['coverage', 'report', '-m'], check=True)
        print(delimiter('writing coverage report'))
        subprocess.run(['coverage', 'html'], check=True)
    print(delimiter('test session result'))
    print(ExitCode(ret.returncode).name)


def delimiter(text: str) -> str:
    length = 79
    text_length = len(text) + 2  # whitespaces
    padding = 0.5 * (length - text_length)
    return '{} {} {}'.format(
        math.floor(padding) * '=',
        text,
        math.ceil(padding) * '='
    )


if __name__ == '__main__':
    args = parse_arguments()
    if args.coverage:
        run_tests_with_coverage()
    else:
        run_tests()
