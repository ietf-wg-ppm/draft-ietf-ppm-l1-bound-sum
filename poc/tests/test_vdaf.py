from vdaf_poc.test_utils import TestVdaf

from vdaf_prio3_l1_bound_sum import Prio3L1BoundSum


class TestPrio3SumVec(TestVdaf):
    def test(self) -> None:
        prio3 = Prio3L1BoundSum(shares=2, length=4, bits=3, chunk_length=3)
        measurements = [
            [7, 0, 0, 0],
            [0, 0, 0, 7],
            [0, 0, 0, 0],
            [1, 2, 2, 2],
            [0, 1, 0, 0],
        ]
        expected_agg_result = [8, 3, 2, 9]
        self.run_vdaf_test(
            prio3,
            None,
            measurements,
            expected_agg_result,
        )
