datasets18xx
============

![docs](https://img.shields.io/readthedocs/datasets18xx)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/codePascal/datasets18xx/test_pytest.yml)
![GitHub Tag](https://img.shields.io/github/v/tag/codePascal/datasets18xx)

A Python package to create, maintain datasets consisting of game transcripts
from [18xx.games](https://18xx.games/).

The datasets can be used to visualize, and analyze a specific game or a specific
game configuration.
On top, the datasets help create meaningful machine learning models.

For a more enriched documentation, visit the project documentation on
readthedocs
[datasets18xx documentation](https://datasets18xx.readthedocs.io/).

Installation
------------

Python library can be installed with `poetry`. Run the following command:

```shell
poetry add git+ssh://git@github.com:codePascal/datasets18xx.git
```

Or use https instead of ssh:

```shell
poetry add git+https://git@github.com:codePascal/datasets18xx.git
```

See the [poetry documentation](https://python-poetry.org/docs/cli/#add) for more
information.

Database and datasets usage
---------------------------

After installation, the database and datasets can be maintained, inspected
and processed using the poetry script `dsx` from the command line.

Run the following command to see command line options:

```bash
dsx --help
```

Database is available from [records18xx](https://github.com/codePascal/records18xx)
and can be installed on the local disk using `dsx download-db`.

Quick references
----------------

### The dataset class

The core of the library is the `Dataset18xx` class.
It creates a shell of a 18xx game variant with a given configuration.
The class can be used to `process`, `inspect` a dataset, create a `subset`
of the base dataset or access parsed records.

```pycon
>>> import transcripts18xx as trx
>>> import datasets18xx as dsx
>>> game_type = trx.Games.G1830
>>> conf = dsx.DefaultDatasetConfig()
>>> ds = dsx.Dataset18xx(game_type, conf)
```

The configuration allows to fine tune the dataset into number of players or
how the game ended.
The above used `DefaultDatasetConfig()` is used as the default with no filter on
the number of players or game endings.

The example below shows how to create such a configuration with only 4 players
and with the bank broken as game ending:

```pycon
>>> my_config = dsx.DatasetConfig(
        num_players={4},
        game_ending={dsx.GameEnding.BankBroke}
    )
```

### Creating datasets

The database mentioned above will only contain raw transcripts of the different
game variants of 18xx.

When using a fresh installation of the database, these transcripts must be
parsed first.
Note that the fine-tuning with a special configuration can only be done after
the original dataset was processed.

```pycon
>>> ds.make()
```

After parsing the original dataset, fine-tuning as mentioned above is possible.

```pycon
>>> new_ds = ds.subset(my_config)
```

**Note**: The dataset instance must be invoked with the default configuration!
As a second argument to the filter, the desired configuration is given.
The filter will not invoke the parsing again but copies the transcript records
that match the filter to a new dataset.

### Inspecting datasets

For debugging purposes or just for information, datasets can be inspected.

```pycon
>>> ds.inspect()
```

During inspection, relevant data of the transcripts are merged.

Below an example of such a metadata file content is shown:

```json
{
  "size": 20,
  "valid": 14,
  "num_players": {
    "4": 6,
    "3": 3,
    "6": 2,
    "5": 2,
    "2": 1
  },
  "game_endings": {
    "BankBroke": 7,
    "PlayerGoesBankrupt": 5,
    "GameEndedManually": 2
  },
  "debug": {
    "unprocessed_lines": [
      "* Buy Multiple Brown Shares From IPO: Multiple brown shares may be bought from IPO as well as from pool",
      "* Optional extra 6-Train: Adds a 3rd 6-train",
      "Optional rules used in this game:",
      "PRR buys Camden & Amboy from this is not a train for $320",
      "PRR buys Mohawk & Hudson from this is not a train for $220",
      "this is not a train wins the auction for Camden & Amboy with a bid of $175",
      "this is not a train wins the auction for Mohawk & Hudson with a bid of $150"
    ],
    "parse_errors": {
      "No players found": [
        "~/.datasets18xx/1830/1830_179295/1830_179295.txt",
        "~/.datasets18xx/1830/1830_179462/1830_179462.txt"
      ],
      "Player not found: player5": [
        "~/.datasets18xx/1830/1830_179489/1830_179489.txt"
      ]
    },
    "verify_errors": [
      "~/.datasets18xx/1830/1830_179190/1830_179190.txt",
      "~/.datasets18xx/1830/1830_179212/1830_179212.txt",
      "~/.datasets18xx/1830/1830_179455/1830_179455.txt"
    ]
  }
}
```

The metadata depicts the following:

* size of the dataset: `size`
* size of the valid dataset: `valid`
* the number of players: `num_players`
* the type of game endings: `game_endings`

For debugging purposes, the unprocessed lines are written.
Further, the occurred parsing errors and corresponding transcripts are given.
The transcripts that failed verification are given as well.

### Accessing datasets

Up to now it was all about creating or filtering datasets.
This section deals with how to access these datasets.

Individual transcript contexts can be loaded with their game id.

```pycon
>>> ctx = ds.load(game_id=123456)
```

Contributing
------------

Here are some ways you can contribute to this project:

* You can [open an issue](https://github.com/codePascal/datasets18xx/issues)
  if you would like to request a feature or report a bug/error.
* If you found a bug, please illustrate it with a minimal [reprex](https://tidyverse.org/help/#reprex)
* If you want to contribute on a deeper level, it is a good idea to file an
  issue first. I will be happy to discuss other ways of contribution!