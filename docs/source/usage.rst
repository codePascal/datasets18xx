Usage
=====

Getting started
---------------

With the package installation, a CLI tool is available: ``dsx``.

Run the following to inspect command line arguments::

    $ dsx --help

By default, it is assumed that the database is available at ``~/.database18xx``.
The default path can be adjusted by exporting the environment variable
``DATABASE``::

    $ export DATABASE=<path/to/the/database>

.. admonition:: Note

    The environment variable is only valid for the current shell and all
    processes started from it. To set is permanently for all future sessions
    add the export to your ``.bashrc`` file (see this
    `gist <https://gist.github.com/magland/518945134209c0c13789c963efda482f>`_)

Within the database, datasets for each 18xx game variant exist.

Downloading the database
------------------------

The script can be used to download and extract the database from
`records18xx <https://github.com/codePascal/records18xx>`_ to the local disk.

Running the following command will install the database either the default
database path or the exported one::

    $ dsx download-db

Thanks to the extraction principle, downloading the database again will not
override existing files but only updates changes and adds new files.
Hence, the database can be updated without losing any processed data.

Generating a dataset
--------------------

Upon the first download of the database, the transcripts are not processed yet.

To invoke the parsing of these, run the following command with the 18xx game
variant specified, e.g., 1830::

    $ dsx make --game G1830

This will created the parsed transcripts as well their metadata.
Additionally, the metadata over the whole dataset will be created as well as a
context depicting key elements of the transcripts.

Output artifacts
^^^^^^^^^^^^^^^^

The metadata file will be saved in the dataset root, named ``metadata.json``.

It depicts the following data:

+------------------+---------------------------------------------------------------------------+
| Field            | Description                                                               |
+==================+===========================================================================+
| ``size``         | Total number of transcripts in dataset                                    |
+------------------+---------------------------------------------------------------------------+
| ``valid``        | Total number of valid transcripts in dataset                              |
+------------------+---------------------------------------------------------------------------+
| ``num_players``  | Number of transcripts mapped to number of players                         |
+------------------+---------------------------------------------------------------------------+
| ``game_endings`` | Number of transcripts mapped to game endings                              |
+------------------+---------------------------------------------------------------------------+
| ``debug``        | Unprocessed lines, paths to transcripts that failed / could not be parsed |
+------------------+---------------------------------------------------------------------------+

.. admonition:: Note

    Valid means that the transcript could be parsed and the final game
    state verification was successful.

The context is saved in the dataset root as well, named ``context.csv``.
It is primarily used to filter the dataset based on key elements, such as
number of players or game endings.
Each row depicts the context of one transcript
(see `TranscriptContext <https://transcripts18xx.readthedocs.io/en/latest/reference.html#transcripts18xx.TranscriptContext>`_).

Re-generating a dataset
^^^^^^^^^^^^^^^^^^^^^^^

Running the above command again, will only parse transcripts again that
either failed or could not be parsed during the last generation (see ``debug``
in the metadata).

Since the parser is under active development, updating the database with
the latest parser is required.
The full dataset of a given 18xx game variant can be generated using the flag
``--force``::

    $ dsx make --game G1830 --force

Inspecting a dataset
--------------------

Datasets can be inspected, i.e., the following command will print the contents
of the metadata to the console::

    $ dsx inspect --game G1830

Inspecting a transcript
-----------------------

Similar to the inspection of the dataset, individual processed transcripts can
be inspected.

The following command will load the transcript data by its game id and print
its context as well as the head of the parsed result to the console::

    $ dsx load --game G1830 --game_id 201210

Creating subsets
----------------

The default dataset contains all available transcripts for the specific game
variant, irrespective of validity, number of players or game endings.

To create more meaningful datasets, a subset from the default dataset can be
created.
In this subset the number of players as well as the game endings can be
selected.

The example below will create a subset of the default 1830 dataset, including
only 4 players and games that ended in bankruptcy or with the bank broken::

    $ dsx subset -g G1830 -n 4 -e BankBroke -e PlayerGoesBankrupt

Running the above command will select all transcripts matching the number of
players as well as either of the two game endings.
The new dataset will be saved in the database, named
``1830_4p_BankBroke_PlayerGoesBankrupt``.

.. admonition:: Note

    Re-generating the default dataset does not automatically update the subset.
    The subset is seen as a new dataset. However, creating a subset from a
    subset is not possible.

.. admonition:: Note

    The above mentioned functionality for generation and inspection can be
    run on the subset as well by defining the number of players and game
    endings from the commandline as depicted above in the example.


