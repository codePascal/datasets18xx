#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess


def main():
    build()


def build():
    subprocess.run(
        ['sphinx-multiversion', './docs/source', './docs/build'], check=True
    )


if __name__ == '__main__':
    main()
