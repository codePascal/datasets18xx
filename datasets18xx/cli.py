#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Command-line interface

Module implements a command-line interface for dataset access, manipulation and
handling.
"""
import json

from pathlib import Path

import click
import transcripts18xx as trx

from .io import io, database
from . import pipeline


@click.group()
def app():
    """CLI for 18xx datasets."""


@app.command()
@click.option(
    '-g', '--game',
    type=click.Choice(trx.Games),
    default=trx.Games.G1830,
    help='Game variant (e.g., -g G1830)'
)
@click.option(
    '-n', '--num_players',
    multiple=True,
    type=int,
    default=None,
    help='Number(s) of players (e.g., -n 3 -4), defaults to None'
)
@click.option(
    '-e', '--game_ending',
    multiple=True,
    type=click.Choice(pipeline.GameEnding),
    default=None,
    help='Type(s) of game endings (e.g., -e BankBroke), defaults to None'
)
@click.option(
    '-f', '--force',
    is_flag=True,
    default=False,
    help='Force re-processing of valid transcripts, default to False'
)
def make(game, num_players, game_ending, force):
    """Process a dataset."""
    try:
        conf = pipeline.make_config(num_players, game_ending)
        ds = pipeline.make_dataset(game, conf)
        ctx = ds.make(force=force)
        click.echo(ctx.head())
    except IOError as exc:
        print(exc)
    except KeyboardInterrupt:
        print('Interrupted by user')


@app.command()
@click.option(
    '-g', '--game',
    type=click.Choice(trx.Games),
    default=trx.Games.G1830,
    help='Game variant (e.g., -g G1830)'
)
@click.option(
    '-n', '--num_players',
    multiple=True,
    type=int,
    default=None,
    help='Number(s) of players (e.g., -n 3 -4), defaults to None'
)
@click.option(
    '-e', '--game_ending',
    multiple=True,
    type=click.Choice(pipeline.GameEnding),
    default=None,
    help='Type(s) of game endings (e.g., -e BankBroke), defaults to None'
)
def inspect(game, num_players, game_ending):
    """Inspect a dataset."""
    try:
        conf = pipeline.make_config(num_players, game_ending)
        ds = pipeline.make_dataset(game, conf)
        snapshot = ds.inspect()
        click.echo(json.dumps(snapshot, indent=2))
    except IOError as exc:
        print(exc)
    except KeyboardInterrupt:
        print('Interrupted by user')


@app.command()
@click.option(
    '-g', '--game',
    type=click.Choice(trx.Games),
    default=trx.Games.G1830,
    help='Game variant (e.g., -g G1830)'
)
@click.option(
    '-n', '--num_players',
    multiple=True,
    type=int,
    default=None,
    help='Number(s) of players (e.g., -n 3 -4), defaults to None'
)
@click.option(
    '-e', '--game_ending',
    multiple=True,
    type=click.Choice(pipeline.GameEnding),
    default=None,
    help='Type(s) of game endings (e.g., -e BankBroke), defaults to None'
)
def subset(game, num_players, game_ending):
    """Create subset of default dataset."""
    try:
        ds = pipeline.make_dataset(game, pipeline.DefaultDatasetConfig())
        conf = pipeline.make_config(num_players, game_ending)
        new_ds = ds.subset(conf)
        click.echo(json.dumps(new_ds.inspect(), indent=2))
    except IOError as exc:
        print(exc)
    except KeyboardInterrupt:
        print('Interrupted by user')


@app.command()
@click.option(
    '-g', '--game',
    type=click.Choice(trx.Games),
    default=trx.Games.G1830,
    help='Game variant (e.g., -g G1830)'
)
@click.option(
    '-n', '--num_players',
    multiple=True,
    type=int,
    default=None,
    help='Number(s) of players (e.g., -n 3 -4), defaults to None'
)
@click.option(
    '-e', '--game_ending',
    multiple=True,
    type=click.Choice(pipeline.GameEnding),
    default=None,
    help='Type(s) of game endings (e.g., -e BankBroke), defaults to None'
)
@click.option(
    '-i', '--game_id',
    type=int,
    default=None,
    help='Game ID to load processed data (e.g., 123456)'
)
def load(game, num_players, game_ending, game_id):
    """Load a processed data snippet of the dataset."""
    try:
        conf = pipeline.make_config(num_players, game_ending)
        ds = pipeline.make_dataset(game, conf)
        ctx = ds.load(game_id)
        ctx_d = io.serialize(ctx.__dict__)
        click.echo(json.dumps(ctx_d, indent=2))
        click.echo(ctx.result().head())
    except (IOError, ValueError) as exc:
        print(exc)
    except KeyboardInterrupt:
        print('Interrupted by user')


@app.command()
def download_db(out_dir: Path):
    """Download the database to the local disk."""
    url = database.create_url()
    print(f'Downloading {url}')
    request = database.download(url)
    print(f'Extracting database to {io.unix_path(out_dir)}')
    database.extract(request, database.database())
    print('All done, Captain!')


if __name__ == '__main__':
    app()
