"""Bidder-side secret sharing and server input files.

Each bidder splits every value it submits into additive shares over Z_{2^64}:

    v = s_0 + s_1 + s_2  (mod 2^64)

and sends share s_p to server p only. Any two of the three shares are
uniformly random and independent of v, so a single server learns nothing.
The servers feed their shares into MP-SPDZ, which adds them back together
*inside* the secure computation (see mpc/auction.mpc).

Input file layout (what server p writes to Player-Data/Input-P{p}-0):

* encoding ``bits``: k rows of n shares; row j holds the shares of bit j
  (bit 0 = LSB) of bidders 0..n-1. This bit-major order lets the MPC read
  each bit position as one contiguous vector.
* encoding ``int``: one row of n shares, the shares of each whole bid.
* encoding ``xor`` (binary-domain programs): one XOR share per bidder,
  ``bid = x_0 ^ x_1 ^ x_2`` with each share a k-bit value. XOR-sharing a k-bit
  word is the same as XOR-sharing each of its bits independently.
"""

import os
import secrets

from .reference import check_bids, to_bits

RING_BITS = 64
MODULUS = 1 << RING_BITS
ENCODINGS = ("bits", "int")  # for the arithmetic program; binary ones use "xor"


def share(value, n_servers=3):
    """Split ``value`` into ``n_servers`` additive shares mod 2^64."""
    shares = [secrets.randbelow(MODULUS) for _ in range(n_servers - 1)]
    shares.append((value - sum(shares)) % MODULUS)
    return shares


def reconstruct(shares):
    return sum(shares) % MODULUS


def xor_share(value, k, n_servers=3):
    """Split a k-bit ``value`` into ``n_servers`` XOR shares of k bits each."""
    shares = [secrets.randbits(k) for _ in range(n_servers - 1)]
    last = value
    for s in shares:
        last ^= s
    return shares + [last]


def xor_reconstruct(shares):
    out = 0
    for s in shares:
        out ^= s
    return out


def as_signed(x):
    """MP-SPDZ parses inputs as signed 64-bit; same residue mod 2^64."""
    return x - MODULUS if x >= MODULUS // 2 else x


class Bidder:
    """One bidder: holds a private bid and produces one message per server."""

    def __init__(self, bid, k):
        check_bids([bid], k)
        self.bid = bid
        self.k = k

    def shares_for_servers(self, encoding="bits", n_servers=3):
        """Return ``msgs`` with ``msgs[p]`` = list of values sent to server p.

        For ``bits`` the list has k entries (bit 0 first); for ``int`` and
        ``xor`` one.
        """
        if encoding == "xor":
            return [[s] for s in xor_share(self.bid, self.k, n_servers)]
        values = to_bits(self.bid, self.k) if encoding == "bits" else [self.bid]
        per_value = [share(v, n_servers) for v in values]
        return [[s[p] for s in per_value] for p in range(n_servers)]


def server_inputs(bids, k, encoding="bits", n_servers=3):
    """Collect every bidder's messages into one input list per server.

    Returns ``inputs[p]``: the flat list of shares server p feeds to MP-SPDZ,
    in the layout documented at the top of this module.
    """
    if encoding not in ENCODINGS + ("xor",):
        raise ValueError(f"unknown encoding {encoding!r}")
    check_bids(bids, k)
    msgs = [Bidder(b, k).shares_for_servers(encoding, n_servers) for b in bids]
    width = k if encoding == "bits" else 1
    inputs = []
    for p in range(n_servers):
        # msgs[i][p][j] -> bit-major order: all bidders' bit 0, then bit 1, ...
        inputs.append([msgs[i][p][j] for j in range(width) for i in range(len(bids))])
    return inputs


def write_server_inputs(inputs, player_data_dir):
    """Write ``inputs[p]`` to ``Input-P{p}-0`` (one file per server)."""
    os.makedirs(player_data_dir, exist_ok=True)
    for p, values in enumerate(inputs):
        path = os.path.join(player_data_dir, f"Input-P{p}-0")
        with open(path, "w") as f:
            f.write(" ".join(str(as_signed(v)) for v in values) + "\n")
