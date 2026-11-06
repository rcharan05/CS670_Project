"""Real 3-server MP-SPDZ runs checked against the plaintext reference."""

import random

import pytest

from auction.audit import audit
from auction.reference import MECHANISMS, plaintext_auction
from auction.runner import run_auction

EDGE_CASES = [
    ([11, 13, 9], 4),             # lit review worked example
    ([5], 4),                     # single bidder
    ([42, 42], 8),                # n = 2, tie
    ([7, 7, 7, 7], 4),            # all equal
    ([0, 0, 0], 4),               # all zeros
    ([255, 3, 255], 8),           # max value, tied
    ([1, 9, 9, 3, 2], 4),         # tie at the top
    ([2, 9, 4, 4], 4),            # tie for second place
    ([1, 2, 3, 4, 5, 6, 7, 8], 4) # winner is the last bidder
]

OTHER_PROGRAMS = ["baseline_tournament", "auction_bin", "baseline_tournament_bin"]


@pytest.mark.parametrize("encoding", ["bits", "int"])
@pytest.mark.parametrize("mechanism", MECHANISMS)
@pytest.mark.parametrize("bids, k", EDGE_CASES)
def test_bitslice_edge_cases(bids, k, mechanism, encoding):
    result, _ = run_auction(bids, k, mechanism, encoding)
    assert result == plaintext_auction(bids, mechanism)


@pytest.mark.parametrize("program", OTHER_PROGRAMS)
@pytest.mark.parametrize("mechanism", MECHANISMS)
@pytest.mark.parametrize("bids, k", EDGE_CASES)
def test_other_programs_edge_cases(bids, k, mechanism, program):
    result, _ = run_auction(bids, k, mechanism, program=program)
    assert result == plaintext_auction(bids, mechanism)


@pytest.mark.parametrize("program", ["auction"] + OTHER_PROGRAMS)
@pytest.mark.parametrize("mechanism", MECHANISMS)
def test_random(mechanism, program):
    rng = random.Random(2026)
    for _ in range(8):
        n, k = rng.randint(2, 70), rng.choice([8, 16, 32])
        bids = [rng.randrange(2 ** k) for _ in range(n)]
        if rng.random() < 0.5:  # force a tie at the top
            bids[rng.randrange(n)] = max(bids)
        result, _ = run_auction(bids, k, mechanism, program=program)
        assert result == plaintext_auction(bids, mechanism), (n, k, bids)


@pytest.mark.parametrize("program", ["auction", "auction_bin"])
def test_malicious_security_same_result(program):
    bids, k = [11, 13, 9, 13], 4
    for mechanism in MECHANISMS:
        result, _ = run_auction(bids, k, mechanism, security="malicious", program=program)
        assert result == plaintext_auction(bids, mechanism)


@pytest.mark.parametrize("program, encoding",
                         [("auction", "bits"), ("auction", "int"), ("auction_bin", "bits")])
@pytest.mark.parametrize("mechanism", MECHANISMS)
@pytest.mark.parametrize("n", [1, 6, 100])
def test_only_winner_and_price_opened(program, encoding, mechanism, n):
    ok, summary = audit(program, n, 8, mechanism, encoding)
    assert ok, summary
