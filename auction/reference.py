"""Plaintext reference implementations used to validate the MPC auction.

Two independent references are provided:

* ``plaintext_auction`` -- the auction rule stated directly on integers
  (max / second max, lowest index wins ties). This is the ground truth.
* ``bitslice_simulate`` -- a bit-level simulation of the *oblivious*
  Kurosawa-Ogata bit-slice circuit exactly as ``mpc/auction.mpc`` computes it:
  only additions, subtractions and multiplications of 0/1 values, with no
  data-dependent branching. Agreement between the two shows that the
  arithmetic formulas are correct independently of MP-SPDZ.
"""

from dataclasses import dataclass, field

MECHANISMS = ("first", "vickrey")


@dataclass
class AuctionResult:
    winner: int  # 0-based index of the winning bidder
    price: int  # amount the winner pays


def check_bids(bids, k):
    if len(bids) == 0:
        raise ValueError("at least one bid is required")
    for b in bids:
        if not isinstance(b, int) or not 0 <= b < 2 ** k:
            raise ValueError(f"bid {b!r} is not an integer in [0, 2^{k})")


def plaintext_auction(bids, mechanism="first"):
    """Ground-truth auction outcome. Ties are broken towards the lowest index."""
    if mechanism not in MECHANISMS:
        raise ValueError(f"unknown mechanism {mechanism!r}")
    top = max(bids)
    winner = bids.index(top)
    if mechanism == "first":
        return AuctionResult(winner, top)
    others = bids[:winner] + bids[winner + 1:]
    return AuctionResult(winner, max(others, default=0))


def to_bits(value, k):
    """Little-endian bit list: to_bits(value, k)[j] is bit j (bit 0 = LSB)."""
    return [(value >> j) & 1 for j in range(k)]


def tree_product(values):
    """Product of a list by pairwise halving, mirroring the MPC's log-depth tree."""
    values = list(values)
    while len(values) > 1:
        half = len(values) // 2
        paired = [values[i] * values[half + i] for i in range(half)]
        values = paired + values[2 * half:]
    return values[0]


def prefix_product(values):
    """Inclusive prefix products (Hillis-Steele), mirroring the MPC."""
    p = list(values)
    d = 1
    while d < len(p):
        p = p[:d] + [p[i] * p[i - d] for i in range(d, len(p))]
        d *= 2
    return p


@dataclass
class ScanTrace:
    """Per-bit record of one scan, for debugging and the report's worked example."""
    rows: list = field(default_factory=list)  # (j, c_j, mask after update)


def bitslice_scan(bits, k, trace=None):
    """One oblivious bit-slice scan.

    ``bits[i][j]`` is bit j of bidder i. Returns (mask, c) where ``mask[i]`` is
    1 iff bidder i holds the maximum and ``c[j]`` is bit j of the maximum.
    """
    n = len(bits)
    S = [1] * n
    c = [0] * k
    for j in reversed(range(k)):
        t = [S[i] * bits[i][j] for i in range(n)]               # survivor has a 1
        c[j] = 1 - tree_product([1 - x for x in t])             # n-input OR
        S = [S[i] - c[j] * (S[i] - t[i]) for i in range(n)]     # = S * (1 - c(1 - b))
        if trace is not None:
            trace.rows.append((j, c[j], list(S)))
    return S, c


def lowest_index_one_hot(mask):
    """w[i] = mask[i] * prod_{l<i} (1 - mask[l]): keep only the first survivor."""
    exclusive = [1] + prefix_product([1 - s for s in mask])[:-1]
    return [m * e for m, e in zip(mask, exclusive)]


def bitslice_simulate(bids, k, mechanism="first", trace=None):
    """Run the same arithmetic as mpc/auction.mpc on plaintext 0/1 values."""
    check_bids(bids, k)
    if mechanism not in MECHANISMS:
        raise ValueError(f"unknown mechanism {mechanism!r}")
    n = len(bids)
    bits = [to_bits(b, k) for b in bids]
    mask, c = bitslice_scan(bits, k, trace)
    w = lowest_index_one_hot(mask)
    winner = sum(i * w[i] for i in range(n))
    if mechanism == "first":
        price = sum(c[j] << j for j in range(k))
    else:
        # Zero the winner's bits and rescan: the new maximum is the second price.
        masked = [[bits[i][j] * (1 - w[i]) for j in range(k)] for i in range(n)]
        _, c2 = bitslice_scan(masked, k)
        price = sum(c2[j] << j for j in range(k))
    return AuctionResult(winner, price)
