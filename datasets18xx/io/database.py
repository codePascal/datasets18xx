#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Database module

Module implements functions to download the database and provides a default
entry point to it.
"""
import tarfile
import os.path
import io

from pathlib import Path

import requests


def database() -> Path:
    """Read database exported as environment variable `DATABASE`.

    Returns:
        The exported database, or default is env variable is not set.
    """
    return os.environ.get('DATABASE', default_database())


def default_database() -> Path:
    """The default location of the database.

    Returns:
        The default location of the database.
    """
    return Path(os.path.expanduser('~')).joinpath('.database18xx')


def create_url() -> str:
    """Creates the URL to download database.

    Returns:
        The url to the database located in records18xx package.
    """
    domain = 'github.com'
    user = 'codePascal'
    repo = 'records18xx'
    file = 'database.tar.gz'
    return f'https://{domain}/{user}/{repo}/raw/main/{file}'


def download(url: str) -> requests.Response:
    """Download the database tarball.

    Args:
        url: The URL from which to download the file.

    Returns:
        The response from the get request.
    """
    req = requests.get(url, stream=True)
    req.raise_for_status()
    return req


def extract(request: requests.Response, out: Path) -> None:
    """Extract the content from the get request to the target path.

    Extracting the database will overwrite existing files with the same name,
    processed data however will remain untouched.

    Args:
        request: The downloaded database as tarball.
        out: The folder to extract database to.
    """
    out.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(request.content), mode='r:gz') as tf:
        tf.extractall(out)
