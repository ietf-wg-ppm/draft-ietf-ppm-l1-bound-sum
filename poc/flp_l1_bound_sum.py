from typing import Any, Optional, TypeVar, cast

from vdaf_poc.field import NttField
from vdaf_poc.flp_bbcggi19 import (
    Mul,
    ParallelSum,
    Valid,
    decode_range_checked_int,
    encode_range_checked_int,
)

F = TypeVar("F", bound=NttField)


class L1BoundSum(Valid[list[int], list[int], F]):
    EVAL_OUTPUT_LEN = 2
    length: int
    max_value: int
    chunk_length: int
    field: type[F]

    def __init__(self, field: type[F], length: int, max_value: int, chunk_length: int):
        """
        Instantiate the `L1BoundSum` circuit for measurements with
        `length` elements, each in the range `[0, max_value)`, and with
        a maximum L1 norm in the same range.
        """
        self.field = field
        self.length = length
        self.max_value = max_value
        self.chunk_length = chunk_length
        bits = max_value.bit_length()
        self.GADGETS = [ParallelSum(Mul(), chunk_length)]
        self.GADGET_CALLS = [((length + 1) * bits + chunk_length - 1) // chunk_length]
        self.MEAS_LEN = (length + 1) * bits
        self.OUTPUT_LEN = length
        self.JOINT_RAND_LEN = self.GADGET_CALLS[0]

    def eval(self, meas: list[F], joint_rand: list[F], num_shares: int) -> list[F]:
        bits = self.max_value.bit_length()
        shares_inv = self.field(num_shares).inv()
        range_check = self.field(0)
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
            observed_weight += decode_range_checked_int(
                self.field, meas[i * bits : (i + 1) * bits], self.max_value
            )
        weight_position = self.length * bits
        claimed_weight = decode_range_checked_int(
            self.field,
            meas[weight_position : weight_position + bits],
            self.max_value,
        )
        weight_check = observed_weight - claimed_weight

        return [range_check, weight_check]

    def encode(self, measurement: list[int]) -> list[F]:
        encoded = []
        for val in measurement:
            encoded += encode_range_checked_int(
                self.field,
                val,
                self.max_value,
            )
        encoded += encode_range_checked_int(
            self.field,
            sum(measurement),
            self.max_value,
        )
        return encoded

    def truncate(self, meas: list[F]) -> list[F]:
        truncated = []
        bits = self.max_value.bit_length()
        for i in range(self.length):
            truncated.append(
                decode_range_checked_int(
                    self.field,
                    meas[i * bits : (i + 1) * bits],
                    self.max_value,
                )
            )
        return truncated

    def decode(self, output: list[F], _num_measurements) -> list[int]:
        return [x.int() for x in output]

    def test_vec_set_type_param(self, test_vec: dict[str, Any]) -> list[str]:
        test_vec["length"] = self.length
        test_vec["max_value"] = self.max_value
        test_vec["chunk_length"] = self.chunk_length
        return ["length", "max_value", "chunk_length"]
