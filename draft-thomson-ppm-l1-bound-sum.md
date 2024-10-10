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
a valid measurement can have an L1 norm equal to any value
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


# Security Considerations

TODO Security


# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
