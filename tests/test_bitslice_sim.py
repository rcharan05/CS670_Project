"""The oblivious bit-slice arithmetic agrees with the plaintext auction rule."""

import itertools
import random

import pytest

from auction.reference import MECHANISMS, bitslice_simulate, plaintext_auction


@pytest.mark.parametrize("mechanism", MECHANISMS)
@pytest.mark.parametrize("n", [1, 2, 3])
def test_exhaustive_small(mechanism, n):
    k = 3
    for bids in itertools.product(range(2 ** k), repeat=n):
        bids = list(bids)
        assert bitslice_simulate(bids, k, mechanism) == plaintext_auction(bids, mechanism), bids


@pytest.mark.parametrize("mechanism", MECHANISMS)
def test_random(mechanism):
    rng = random.Random(670)
    for _ in range(3000):
        n = rng.randint(1, 20)
        k = rng.randint(1, 16)
        # Draw from a small range half the time to force many ties.
        hi = 2 ** k - 1 if rng.random() < 0.5 else min(3, 2 ** k - 1)
        bids = [rng.randint(0, hi) for _ in range(n)]
        assert bitslice_simulate(bids, k, mechanism) == plaintext_auction(bids, mechanism), (bids, k)
