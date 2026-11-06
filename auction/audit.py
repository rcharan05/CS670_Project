"""Output-boundary audit: what does a compiled program open?

The privacy target is that the protocol opens the winner and the price and
nothing else. MP-SPDZ's compiler reports how many values the program opens in
total; this module recompiles a program and checks that count.

Expected opens for the bit-slice programs:

* ``auction`` with ``bits`` encoding: exactly 2 integer opens (winner, price).
* ``auction`` with ``int`` encoding: 2 + n. Each extra open is one masked
  value ``(bid - r) mod 2^k`` opened inside MP-SPDZ's ring bit-decomposition
  (Compiler/floatingpoint.py, BitDecRingRaw); ``r`` is a fresh uniformly random
  k-bit mask from preprocessing, so the opened value is uniform and
  independent of the bid. These are protocol-internal and not part of the
  output.
* ``auction_bin``: no integer opens, and exactly two revealed bit words (the
  winner index and the price). MP-SPDZ's "bit opens" counter is in bytes,
  8 per revealed register of up to 64 bits, so two words count as 16.
"""

import math
import re

from .runner import program_args, run_compiler


def compile_summary(source, args):
    """Compile mpc/<source>.mpc and return the compiler's cost summary.

    Returns a dict such as ``{"integer opens": 2, "integer triples": 277,
    "virtual machine rounds": 87, ...}``.
    """
    summary = {}
    out = run_compiler(source, args)
    for m in re.finditer(r"^\s+(\d+) ([a-z][a-z0-9 ]+?)\s*$", out, re.M):
        summary[m.group(2)] = summary.get(m.group(2), 0) + int(m.group(1))
    return summary


def expected_opens(program, n, k, encoding="bits"):
    """{counter name: expected count} for the values a program may open."""
    if program == "auction":
        return {"integer opens": 2 if encoding == "bits" else 2 + n}
    if program == "auction_bin":
        idx_bits = max(1, (n - 1).bit_length())
        words = [idx_bits + 1, k + 1]  # each with one constant top bit
        return {"integer opens": 0,
                "bit opens": sum(8 * math.ceil(w / 64) for w in words)}
    raise ValueError(f"no open budget defined for {program}")


def audit(program, n, k, mechanism, encoding="bits"):
    """Return (ok, summary) for a bit-slice program with the given parameters."""
    summary = compile_summary(program, program_args(program, n, k, mechanism, encoding))
    expected = expected_opens(program, n, k, encoding)
    return all(summary.get(key, 0) == v for key, v in expected.items()), summary
