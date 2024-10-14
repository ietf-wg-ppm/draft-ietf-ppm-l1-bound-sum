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


## Validity Circuit

The validity circuit for Prio3L1BoundSum uses a modified version of the
Prio3SumVec validity circuit, see {{Section 7.4.3 of VDAF}}.

The values from the measurement are extended to include their sum, so that the
sum is checked in the same way as each vector component. The encoded measurement
has a total length of `(length + 1) * bits`. The field elements in the encoded
vector represent all the bits of the measurement vector's elements, followed by
the bits of the L1 norm of the vector.

The validity circuit checks that the encoded measurement consists of ones and
zeros, and that the encoded L1 norm is consistent with the encoded vector
elements. The first checks, that all field elements are ones and zeros, are done
in the same manner as in the `SumVec` circuit. The L1 norm is checked by
decoding the reported L1 norm, decoding the measurement vector, recomputing the
L1 norm, and subtracting to confirm they are identical.

The complete circuit is specified below.

~~~ python
class L1BoundSum(Valid[list[int], list[int], F]):
    EVAL_OUTPUT_LEN = 2
    length: int
    bits: int
    chunk_length: int
    field: type[F]

    def __init__(self,
                 field: type[F],
                 length: int,
                 bits: int,
                 chunk_length: int):
        """
        Instantiate the `L1BoundSum` circuit for measurements with
        `length` elements, each in the range `[0, 2^bits)`, and with
        a maximum L1 norm of `2^bits - 1`.
        """
        self.field = field
        self.length = length
        self.bits = bits
        self.chunk_length = chunk_length
        self.GADGETS = [ParallelSum(Mul(), chunk_length)]
        self.GADGET_CALLS = [
            ((length + 1) * bits + chunk_length - 1) // chunk_length
        ]
        self.MEAS_LEN = (length + 1) * bits
        self.OUTPUT_LEN = length
        self.JOINT_RAND_LEN = self.GADGET_CALLS[0]

    def eval(
            self,
            meas: list[F],
            joint_rand: list[F],
            num_shares: int) -> list[F]:
        range_check = self.field(0)
        shares_inv = self.field(num_shares).inv()
        for i in range(self.GADGET_CALLS[0]):
            r = joint_rand[i]
            r_power = r
            inputs: list[Optional[F]]
            inputs = [None] * (2 * self.chunk_length)
            for j in range(self.chunk_length):
                index = i * self.chunk_length + j
                if index < len(meas):
                    meas_elem = meas[index]
                else:
                    meas_elem = self.field(0)

                inputs[j * 2] = r_power * meas_elem
                inputs[j * 2 + 1] = meas_elem - shares_inv

                r_power *= r

            range_check += self.GADGETS[0].eval(
                self.field,
                cast(list[F], inputs),
            )

        observed_weight = self.field(0)
        for i in range(self.length):
            observed_weight += self.field.decode_from_bit_vector(
                meas[i * self.bits:(i + 1) * self.bits]
            )
        weight_position = self.length * self.bits
        claimed_weight = self.field.decode_from_bit_vector(
            meas[weight_position:weight_position + self.bits]
        )
        weight_check = observed_weight - claimed_weight

        return [range_check, weight_check]

    def encode(self, measurement: list[int]) -> list[F]:
        encoded = []
        for val in measurement:
            encoded += self.field.encode_into_bit_vector(
                val,
                self.bits,
            )
        encoded += self.field.encode_into_bit_vector(
            sum(measurement),
            self.bits,
        )
        return encoded

    def truncate(self, meas: list[F]) -> list[F]:
        truncated = []
        for i in range(self.length):
            truncated.append(self.field.decode_from_bit_vector(
                meas[i * self.bits: (i + 1) * self.bits]
            ))
        return truncated

    def decode(
            self,
            output: list[F],
            _num_measurements) -> list[int]:
        return [x.as_unsigned() for x in output]
~~~


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
