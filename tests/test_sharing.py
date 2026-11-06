import collections
import random

import pytest

from auction.sharing import (MODULUS, Bidder, as_signed, reconstruct, server_inputs,
                             share, xor_reconstruct, xor_share)


def test_share_reconstructs():
    for v in [0, 1, 12345, MODULUS - 1]:
        assert reconstruct(share(v)) == v


def test_signed_encoding_preserves_residue():
    for x in [0, 1, MODULUS // 2 - 1, MODULUS // 2, MODULUS - 1]:
        assert as_signed(x) % MODULUS == x
        assert -(2 ** 63) <= as_signed(x) < 2 ** 63


def test_bidder_messages_reconstruct_bits():
    msgs = Bidder(11, 4).shares_for_servers("bits")
    assert len(msgs) == 3 and all(len(m) == 4 for m in msgs)
    assert [reconstruct([msgs[p][j] for p in range(3)]) for j in range(4)] == [1, 1, 0, 1]


@pytest.mark.parametrize("encoding", ["bits", "int"])
def test_server_input_layout(encoding):
    bids, k = [11, 13, 9], 4
    inputs = server_inputs(bids, k, encoding)
    values = [reconstruct(col) for col in zip(*inputs)]
    if encoding == "bits":
        # bit-major: all bidders' bit 0, then bit 1, ...
        assert values == [(b >> j) & 1 for j in range(k) for b in bids]
    else:
        assert values == bids


@pytest.mark.parametrize("server", [0, 1, 2])
def test_single_share_looks_uniform(server):
    """A single server's share of a fixed bid is uniform: compare the
    distribution of its low 4 bits for bid 0 and bid 15 (chi-square)."""
    trials, buckets = 4000, 16
    for bid in (0, 15):
        counts = collections.Counter(
            share(bid)[server] % buckets for _ in range(trials))
        expected = trials / buckets
        chi2 = sum((counts[b] - expected) ** 2 / expected for b in range(buckets))
        assert chi2 < 37.7  # p = 0.001 critical value, 15 degrees of freedom


def test_xor_shares():
    for v, k in [(0, 4), (11, 4), (2 ** 32 - 1, 32)]:
        s = xor_share(v, k)
        assert xor_reconstruct(s) == v and all(0 <= x < 2 ** k for x in s)
    inputs = server_inputs([11, 13, 9], 4, "xor")
    assert [xor_reconstruct(col) for col in zip(*inputs)] == [11, 13, 9]
