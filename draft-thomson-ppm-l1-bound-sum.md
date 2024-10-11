---
title: "A Prio Instantiation for Vector Sums with an L1 Norm Bound on Contributions"
abbrev: "Prio L1 Bound Sum"
category: std

docname: draft-thomson-ppm-l1-bound-sum-latest
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

normative:

informative:


--- abstract

A Prio Verifiable Distributed Aggregation Function is defined that supports vector or histogram addition,
where the sum of the values in the contribution is less than a chosen value.


--- middle

# Introduction

Existing Prio instantiations of a Verifiable Distributed Aggregation Function (VDAF)
{{!VDAF=I-D.irtf-cfrg-vdaf}}
all support a simple summation of measurements.
From Prio3Count ({{Section 7.4.1 of VDAF}}),
which adds measurements containing a single one or a zero value,
to Prio3SumVec ({{Section 7.4.3 of VDAF}}),
which adds measurements containing an vector where each dimension is a limited number of bits,
all instantations take the same basic form.

One case that is presently not included in the suite of instantiations
is the addition of vectors or histogram contributions,
where each measurement has an L1 bound.
The L1 norm of a vector is defined as the sum of its components.
An L1 bound limits that sum to some maximum.

This document defines the Prio3L1BoundSum instantiation.
Unlike Prio3Histogram ({{Section 7.4.4 of VDAF}}),
in which measurements need to have an L1 norm of exactly 1,
a valid measurement for Prio3L1BoundSum can have an L1 norm equal to any value
between 0 and the chosen limit.

This instantiation limits the L1 norm of a vector or histogram
to a value that is one less than a chosen power of 2,
or 2<sup>n</sup>-1.
This choice significantly reduces the size of the encoding
relative to a more flexible limit.

{{def}} defines the encoding of measurements for this instantiation
and how the validation function is evaluated.


# Conventions and Definitions

{::boilerplate bcp14-tagged}

This document uses the terminology and functions defined in {{Section 2 of VDAF}}.


# Prio3L1BoundSum Definition {#def}

The Prio3L1BoundSum instantiation of Prio {{?PRIO=DOI.10.5555/3154630.3154652}}
supports the addition of a vector of integers.
The instantiation is summarized in {{table-l1-bound-sum}}.

| Parameter | Value |
|:-|:-|
| Valid | L1BoundSum(Field128, length, bits, chunk_length) |
| Field | Field128 ({{Section 6.1.2 of VDAF}}) |
| PROOFS | 1 |
| XOF | XofTurboShake128 ({{Section 6.2.1 of VDAF}}) |
{: #table-l1-bound-sum title="Prio3L1BoundSum Parameters"}

The function takes three parameters:
length, bits, and chunk_length.
The vector contains "length" components,
each of which is a non-negative integer less than 2<sup>bits</sup>.

## Chunk Length Choice

The chunk_length parameter can be chosen
in approximately the same way as for Prio3SumVec,
as detailed in {{Section 7.4.3.1 of VDAF}}.
The difference is that Prio3L1BoundSum involves validation of
`bits * (length + 1)` values,
which might increase the most efficient value for chunk_length.


## Encoding and Decoding

The encode, truncate, and decode functions for Prio3L1BoundSum is identical to that of Prio3SumVec;
see {{Section 7.4.3 of VDAF}} for those definitions.


## Validity Circuit

The validity circuit for Prio3L1BoundSum uses a modified version of the Prio3SumVec validity circuit.
The values from the measurement are extended to include their sum,
so that the sum is checked in the same way as each vector component.

~~~ python
def eval(
        self,
        meas: list[F],
        joint_rand: list[F],
        num_shares: int) -> list[F]:
    weight = 0
    for i in range(self.length):
        weight += self.field.decode_from_bit_vector(
            meas[i * self.bits : (i + 1) * self.bits]
        )
    weight_bits = self.field.encode_into_bit_vector(weight)

    sum_vec = SumVec(self.field, self.length + 1,
                     self.bits, chunk_length)
    return sum_vec.eval(meas + weight_bits, joint_rand, num_shares)
~~~

Key characteristics of the validity circuit
are summarized in {{table-prio3l1boundsum-validity}}.

| Parameter | Value |
|:-|:-|
| GADGETS | \[ParallelSum(Mul(), chunk_length)] |
| GADGET_CALLS | \[ceil((length + 1) * bits / chunk_length)] |
| MEAS_LEN | length * bits |
| OUTPUT_LEN | length |
| JOINT_RAND_LEN | GADGET_CALLS\[0] |
| EVAL_OUTPUT_LEN | 1 |
| Measurement | list\[int], each element in range(2**bits) |
| AggResult | list\[int] |
{: #table-prio3l1boundsum-validity title="Prio3L1BoundSum Validity Circuit Characteristics"}


# Security Considerations

The Prio3L1BoundSum VDAF is subject to the same considerations as other Prio-based VDAFs.
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
: 0xTBD
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

TODO acknowledge.
