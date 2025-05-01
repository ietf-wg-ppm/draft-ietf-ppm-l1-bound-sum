# Reference implementation

This directory contains a reference implementation of the Prio3L1BoundSum VDAF.
It is based on the [VDAF reference implementation][vdaf-poc].

[vdaf-poc]: https://github.com/cfrg/draft-irtf-cfrg-vdaf/tree/main/poc

## Installation

This code requires [Sage](https://www.sagemath.org/) to run. To install
dependencies:

```
sage -pip install -r requirements.txt
```

## Development

To run unit tests:

```
sage -python -m unittest
```

## Generating test vectors

To generate test vectors:

```
sage -python gen_test_vec.py
```
