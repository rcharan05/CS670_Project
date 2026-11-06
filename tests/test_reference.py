import pytest

from auction.reference import (AuctionResult, ScanTrace, bitslice_simulate,
                               check_bids, lowest_index_one_hot, plaintext_auction,
                               prefix_product, to_bits, tree_product)


@pytest.mark.parametrize("bids, first, vickrey", [
    ([11, 13, 9], (1, 13), (1, 11)),        # lit review worked example
    ([5], (0, 5), (0, 0)),                  # single bidder pays 0 under Vickrey
    ([7, 7, 7], (0, 7), (0, 7)),            # all equal: lowest index, pays the tie
    ([1, 9, 9, 3], (1, 9), (1, 9)),         # tie at the top
    ([2, 9, 4, 4], (1, 9), (1, 4)),         # tie for second place
    ([0, 0], (0, 0), (0, 0)),               # all zeros
    ([15, 0], (0, 15), (0, 0)),             # max value
])
def test_plaintext_auction(bids, first, vickrey):
    assert plaintext_auction(bids, "first") == AuctionResult(*first)
    assert plaintext_auction(bids, "vickrey") == AuctionResult(*vickrey)


def test_check_bids_rejects_bad_input():
    with pytest.raises(ValueError):
        check_bids([], 4)
    with pytest.raises(ValueError):
        check_bids([16], 4)
    with pytest.raises(ValueError):
        check_bids([-1], 4)


def test_to_bits_is_little_endian():
    assert to_bits(11, 4) == [1, 1, 0, 1]


def test_tree_and_prefix_products():
    v = [2, 3, 5, 7, 11]
    assert tree_product(v) == 2310
    assert prefix_product(v) == [2, 6, 30, 210, 2310]


def test_lowest_index_one_hot():
    assert lowest_index_one_hot([0, 1, 0, 1, 1]) == [0, 1, 0, 0, 0]
    assert lowest_index_one_hot([1]) == [1]


def test_worked_example_trace():
    """Corrected Table 1 of the lit review: A=11, B=13, C=9.

    The lit review printed the mask after bits 1 and 0 as {}; the correct
    mask is {B} -- when the check fails the mask is carried forward.
    """
    trace = ScanTrace()
    bitslice_simulate([11, 13, 9], 4, "first", trace)
    assert trace.rows == [
        (3, 1, [1, 1, 1]),
        (2, 1, [0, 1, 0]),
        (1, 0, [0, 1, 0]),
        (0, 1, [0, 1, 0]),
    ]
