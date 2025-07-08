# Reference implementation

This directory contains a reference implementation of the Prio3L1BoundSum VDAF.
It is based on the [VDAF reference implementation][vdaf-poc].

[vdaf-poc]: https://github.com/cfrg/draft-irtf-cfrg-vdaf/tree/main/poc

## Installation

This code requires Python 3.12 to run. To install dependencies:

```
pip install -r requirements.txt
```

## Development

To run unit tests:

```
python -m unittest
```

## Generating test vectors

To generate test vectors:

```
./gen_test_vec.py
```
