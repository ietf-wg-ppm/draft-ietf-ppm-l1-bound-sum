from vdaf_poc.field import Field64, Field96, Field128, NttField
from vdaf_poc.flp_bbcggi19 import FlpBBCGGI19, encode_range_checked_int
from vdaf_poc.test_utils import TestFlpBBCGGI19

from flp_l1_bound_sum import L1BoundSum


class TestL1BoundSum(TestFlpBBCGGI19):
    def run_encode_truncate_decode_with_ntt_fields_test(
        self,
        measurements: list[list[int]],
        length: int,
        max_value: int,
        chunk_length: int,
    ) -> None:
        for field in [Field64, Field96, Field128]:
            l1boundsum = L1BoundSum[NttField](
                field,
                length,
                max_value,
                chunk_length,
            )
            self.assertEqual(l1boundsum.field, field)
            self.assertTrue(isinstance(l1boundsum, L1BoundSum))
            self.run_encode_truncate_decode_test(
                FlpBBCGGI19(l1boundsum),
                measurements,
            )

    def test_with_fields(self) -> None:
        self.run_encode_truncate_decode_with_ntt_fields_test(
            [
                [7, 0, 0, 0],
                [0, 0, 0, 7],
                [1, 2, 2, 1],
                [2, 1, 2, 2],
                [5, 2, 0, 0],
                [0, 0, 0, 0],
            ],
            length=4,
            max_value=7,
            chunk_length=3,
        )

    def test_valid(self) -> None:
        valid = L1BoundSum(Field128, 4, 7, 3)
        flp = FlpBBCGGI19(valid)
        self.run_flp_test(
            flp,
            [
                (flp.encode([7, 0, 0, 0]), True),
                (flp.encode([0, 0, 0, 7]), True),
                (flp.encode([2, 2, 2, 1]), True),
                (flp.encode([0, 0, 0, 0]), True),
                (flp.encode([2, 2, 2, 0]), True),
                (flp.encode([1, 0, 2, 0]), True),
            ],
        )

    def test_invalid(self) -> None:
        field = Field128
        length = 4
        max_value = 7
        valid = L1BoundSum(field, length, max_value, 3)
        flp = FlpBBCGGI19(valid)
        self.run_flp_test(
            flp,
            [
                (
                    encode_range_checked_int(field, 7, max_value)
                    + encode_range_checked_int(field, 0, max_value)
                    + encode_range_checked_int(field, 0, max_value)
                    + encode_range_checked_int(field, 0, max_value)
                    + encode_range_checked_int(field, 6, max_value),
                    False,
                ),
                (
                    [field(2)]
                    + [field(0)] * 11
                    + encode_range_checked_int(field, 2, max_value),
                    False,
                ),
                (
                    [
                        # first vector element: 2
                        field(0),
                        field(1),
                        field(0),
                        # rest of vector elements: 0
                        field(0),
                        field(0),
                        field(0),
                        field(0),
                        field(0),
                        field(0),
                        field(0),
                        field(0),
                        field(0),
                        # improperly encoded weight
                        field(2),
                        field(0),
                        field(0),
                    ],
                    False,
                ),
            ],
        )
