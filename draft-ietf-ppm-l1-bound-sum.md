---
title: "A Prio Instantiation for Vector Sums with an L1 Norm Bound on Contributions"
abbrev: "Prio L1 Bound Sum"
category: std

docname: draft-ietf-ppm-l1-bound-sum-latest
submissiontype: IETF
number:
date:
consensus: true
v: 3
area: "Security"
workgroup: "Privacy Preserving Measurement"
keyword:
 - vectors
 - manhattan
 - multi-dimensional
venue:
  group: "Privacy Preserving Measurement"
  type: "Working Group"
  mail: "ppm@ietf.org"
  arch: "https://mailarchive.ietf.org/arch/browse/ppm/"
  github: "martinthomson/prio-l1-bound-sum"
  latest: "https://martinthomson.github.io/prio-l1-bound-sum/draft-thomson-ppm-l1-bound-sum.html"

author:
 -
    fullname: "Martin Thomson"
    organization: Mozilla
    email: "mt@lowentropy.net"
 -
    fullname: "David Cook"
    organization: ISRG
    email: "divergentdave@gmail.com"

normative:
  VDAF: I-D.irtf-cfrg-vdaf
  DAP: I-D.ietf-ppm-dap

informative:
  CGB17:
    title: "Prio: Private, Robust, and Scalable Computation of Aggregate Statistics"
    author:
      - name: Dan Boneh
      - name: Henry Corrigan-Gibbs
    date: 2017
    refcontent: "USENIX Symposium on Networked Systems Design and Implementation (NSDI)"
    target: https://dl.acm.org/doi/10.5555/3154630.3154652

--- abstract

A Prio Verifiable Distributed Aggregation Function is defined
that supports vector or histogram addition,
where the sum of the values in the contribution is less than a chosen value.


--- middle

# Introduction

Existing Prio instantiations of a Verifiable Distributed Aggregation Function (VDAF)
{{VDAF}}
all support a simple summation of measurements.
From Prio3Count ({{Section 7.4.1 of VDAF}}),
which adds measurements containing a single one or a zero value,
to Prio3SumVec ({{Section 7.4.3 of VDAF}}),
which adds measurements containing a vector where each dimension is a limited number of bits,
all instantations take the same basic form.

One case that is presently not included in the suite of instantiations
is the addition of vectors or histogram contributions,
where each measurement has an L1 bound.
The L1 norm of a vector is defined as the sum of its components.
An L1 bound limits that sum to some maximum.

This document defines the Prio3L1BoundSum instantiation.
This instantiation limits the L1 norm of a vector or histogram
to a value less than a predetermined maximum.

This instantiation has similarities with other instantiations.
Unlike Prio3Histogram ({{Section 7.4.4 of VDAF}}),
in which measurements need to have an L1 norm of exactly 1,
a valid measurement for Prio3L1BoundSum can have an L1 norm equal to any value
between 0 and the chosen limit.
Unlike Prio3MultiHotCountVec ({{Section 7.4.5 of VDAF}}),
in which each component can only be zero or one,
components in Prio3L1BoundSum can take any value up to the L1 bound
as long as their sum is within that bound.

{{def}} defines the Prio3L1BoundSum VDAF.


# Conventions and Definitions

{::boilerplate bcp14-tagged}

This document uses the terminology, notation conventions, and functions
defined in {{Section 2 of VDAF}}.


# Prio3L1BoundSum Definition {#def}

The Prio3L1BoundSum instantiation of Prio {{CGB17}}
supports the addition of a vector of integers.
It also uses `bit_length()`,
which returns the minimum number of bits
needed to encode an integer value.

The instantiation is summarized in {{table-l1-bound-sum}}.

| Parameter | Value |
|:-|:-|
| field | Field128 ({{Section 6.1.2 of VDAF}}) |
| Valid | L1BoundSum(field, length, max, chunk_length) |
| PROOFS | 1 |
| XOF | XofTurboShake128 ({{Section 6.2.1 of VDAF}}) |
{: #table-l1-bound-sum title="Prio3L1BoundSum Parameters"}

The function takes three parameters:
`length`, `max_value`, and `chunk_length`.
The vector contains "`length`" components,
each of which is a non-negative integer less than `max_value`.

The value of `max_value` can be any non-negative integer
greater than 1.
A value of 2 causes Prio3L1BoundSum
to be nearly identical to Prio3Histogram,
except that Prio3Histogram cannot encode an all-zero report.


## Chunk Length Selection

The `chunk_length` parameter can be chosen
in approximately the same way as for Prio3SumVec,
as detailed in {{Section 7.4.3.1 of VDAF}}.
The difference is that Prio3L1BoundSum involves validation of
`bits * (length + 1)` values,
where `bits = max_value.bit_length()`.
This might increase the most efficient value for `chunk_length`
relative to a similar encoding of Prio3SumVec.


## Encoding and Decoding

The encoded form of each measurement appends a bitwise decomposition
of the L1 norm (the sum of the vector components) to the encoding:

~~~ python
def encode(self, measurement: list[int]) -> list[F]:
    encoded = []
    erci = encode_range_checked_int
    for v in measurement:
        encoded += erci(self.field, v, self.max_value)
    weight = erci(self.field, sum(measurement), self.max_value)
    return encoded + weight
~~~

The encoded measurement has a total length of `(length + 1) * bits`.

The encoding function `encode_range_checked_int`
is described in {{Section 7.4.2 of VDAF}}.

The encoded information is not included in the output share
that is submitted for aggregation.
That is, the `truncate()` function emits only the core measurements.

~~~ python
def truncate(self, meas: list[F]) -> list[F]:
    return [
       decode_range_checked_int(self.field, m, self.max_value)
       for m in chunks(meas, self.max_value.bit_length())
    ]
~~~

This uses a `chunks(v, c)` function that takes a list of values, `v`,
and a chunk length, `c`,
to split `v` into multiple lists from `v`,
where each chunk has a length `c`.

The `decode()` function is therefore identical to that in Prio3SumVec.

~~~ python
def decode(self, output: list[F], _count) -> list[int]:
    return [x.int() for x in output]
~~~


## Validity Circuit

The validity circuit for Prio3L1BoundSum uses an extended version
of the validity circuit used by Prio3SumVec,
see {{Section 7.4.3 of VDAF}}.

The encoded measurement is checked
to ensure that every component of the vector –
plus the added L1 norm –
is encoded in the specified number of bits.
That is, the circuit checks that each component has a value between
0 (inclusive) and `max_value` (exclusive)
by first checking the value is correctly composed from bits,
where each bit is either zero or one.
This process is identical to the Prio3SumVec check,
except that one additional value is checked.

The validity circuit then checks whether the added L1 norm value
is consistent with the encoded vector elements.
The L1 norm is checked by decoding the measurement values,
including the L1 norm.
The decoded values are used to recompute the L1 norm
as the sum of the individual components.
The difference between reported and computed values
is checked to confirm that the values are identical.

The complete circuit is specified in {{fig-eval}}.

~~~ python
def eval(self, meas: list[F],
         joint_rand: list[F], num_shares: int) -> list[F]:
    bits = self.max_value.bit_length()
    assert len(meas) == (self.length + 1) * bits
    shares_inv = self.field(num_shares).inv()
    parallel_sum = ParallelSum(Mul(), chunk_length)

    num_chunks = ceil(len(meas) / self.chunk_length)
    pad_len = self.chunk_length * num_chunks - len(meas)
    meas += [self.field(0)] * pad_len

    range_check = self.field(0)
    for (r, m) in zip(joint_rand, chunks(meas, self.chunk_length)):
        inputs = []
        for i in range(self.chunk_length):
            inputs += [
                r**(i + 1) * m[i],
                m[i] - shares_inv,
            ]
        range_check += parallel_sum.eval(self.field, inputs)

    c = chunks(meas, bits)
    components = [
        decode_range_checked_int(self,field, m, self.max_value)
        for m in c[:self.length]
    ]
    observed_weight = sum(components)
    claimed_weight = decode_range_checked_int(
        self.field, c[self.length], self.max_value
    )
    weight_check = observed_weight - claimed_weight

    return [range_check, weight_check]
~~~
{: #fig-eval title="Evaluation function for Prio3L1BoundSum"}

This evaluation uses the `decode_range_checked_int()` function
defined in {{Section 7.4.2 of VDAF}}.


# DAP Integration

The integration of Prio3L1BoundSum in DAP {{DAP}}
requires the definition of an encoding
for the configuration of the VDAF.
{{fig-config}} defines the encoding of `Prio3L1BoundSumConfig`,
using the syntax definitions from {{Section 3 of !RFC8446}}.

~~~ tls-presentation
struct {
  uint32 length;
  uint32 max_value;
  uint32 chunk_length;
} Prio3L1BoundSumConfig;
~~~
{: #fig-config title="VDAF Configuration Encoding for Prio3L1BoundSum"}

This configuration is three 32-bit integers,
each in network byte order,
with semantics described in {{def}},
as follows:

length:

: The total number of values in each measurement.

max_value:

: The maximum value, inclusive,
  for the sum of all measurement values.

chunk_length:

: The size of each chunk used in the evaluation circuit;
  see {{fig-eval}}.


# Security Considerations

The Prio3L1BoundSum VDAF is subject to the same considerations
as other Prio-based VDAFs.
These considerations are detailed in {{Section 9 of VDAF}}.

In particular, this instantiation uses Field128 to ensure robustness
despite the use of joint randomness in proofs.
Joint randomness increases the risk of an attacker finding
a combination of invalid inputs that passes validation.
A larger field increases the computational cost
of finding such a combination.


# IANA Considerations

This document registers a codepoint for Prio3L1BoundSum
in the "Verifiable Distributed Aggregation Functions (VDAF)" registry
as defined by {{Section 10 of VDAF}}.
This entry contains the following fields:

Value:
: 0x00000007

Scheme:
: Prio3L1BoundSum

Type:
: VDAF

Reference:
: RFCXXXX (this document)
{: spacing="compact"}


--- back

# Acknowledgments
{:numbered="false"}

Chris Patton provided extensive input into the construction of this VDAF.
