"""Benchmark sweep -> bench/results/results.csv

Experiments:
  scale_n   vary the number of bidders n (k = 32)
  scale_k   vary the bid length k (n = 32)
  security  semi-honest vs malicious replicated secret sharing

Each configuration records the compiler's static counts (multiplications,
random bits, rounds, opens) and, over several repetitions, party 0's measured
time, data sent and rounds.

Variants: the bit-slice circuit and the comparison tournament, each in the
arithmetic domain (Z_2^64, an AND is a ring multiplication) and the binary
domain (XOR-shared bits, an AND costs one bit), plus the arithmetic bit-slice
with integer inputs (in-MPC bit decomposition) as an encoding ablation.

Usage: python bench/run_bench.py [--reps 5] [--only scale_n ...]
"""

import argparse
import csv
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auction.audit import compile_summary  # noqa: E402
from auction.reference import plaintext_auction  # noqa: E402
from auction.runner import (PROGRAMS, input_encoding, program_args,  # noqa: E402
                            program_name, run_program)
from auction.sharing import server_inputs  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# (label, program, encoding for the arithmetic bit-slice)
VARIANTS = [
    ("bitslice-ring", "auction", "bits"),
    ("bitslice-ring-int", "auction", "int"),
    ("tournament-ring", "baseline_tournament", None),
    ("bitslice-bin", "auction_bin", None),
    ("tournament-bin", "baseline_tournament_bin", None),
]
MAIN = [v for v in VARIANTS if v[0] != "bitslice-ring-int"]
MECHS = ["first", "vickrey"]


def configs(only):
    if "scale_n" in only:
        for n in [2, 4, 8, 16, 32, 64, 128, 256]:
            for label, prog, enc in VARIANTS:
                for mech in MECHS:
                    yield "scale_n", label, prog, enc, mech, "semi-honest", n, 32
    if "scale_k" in only:
        for k in [8, 16, 24, 32, 48, 60]:
            for label, prog, enc in VARIANTS:
                for mech in MECHS:
                    yield "scale_k", label, prog, enc, mech, "semi-honest", 32, k
    if "security" in only:
        for n in [4, 16, 64]:
            for label, prog, enc in MAIN:
                for security in ["semi-honest", "malicious"]:
                    yield "security", label, prog, enc, "vickrey", security, n, 32


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--only", nargs="+", default=["scale_n", "scale_k", "security"])
    ap.add_argument("--out", default=os.path.join(RESULTS, "results.csv"))
    args = ap.parse_args()

    os.makedirs(RESULTS, exist_ok=True)
    rng = random.Random(670)
    fields = ["experiment", "variant", "domain", "mechanism", "security", "n", "k",
              "mults", "rand_bits", "opens", "static_rounds",
              "time_s", "time_s_min", "data_mb", "global_data_mb", "rounds"]
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for exp, label, prog, enc, mech, security, n, k in configs(args.only):
            prog_args = program_args(prog, n, k, mech, enc)
            summary = compile_summary(prog, prog_args)
            name = program_name(prog, prog_args)
            domain = PROGRAMS[prog]
            share_enc = input_encoding(prog, enc)
            times, last = [], None
            for _ in range(args.reps):
                bids = [rng.randrange(2 ** k) for _ in range(n)]
                last = run_program(name, server_inputs(bids, k, share_enc), domain, security)
                expected = plaintext_auction(bids, mech)
                if f"winner={expected.winner} price={expected.price}" not in last.stdout:
                    raise SystemExit(f"wrong result for {name} on {bids}")
                times.append(last.stats.time_s)
            row = {
                "experiment": exp, "variant": label, "domain": domain,
                "mechanism": mech, "security": security, "n": n, "k": k,
                # ANDs: ring multiplications or bit triples, per domain
                "mults": summary.get("integer triples", 0) + summary.get("bit triples", 0),
                "rand_bits": summary.get("integer bits", 0),
                "opens": summary.get("integer opens", 0),
                "static_rounds": summary.get("virtual machine rounds", 0),
                "time_s": statistics.median(times), "time_s_min": min(times),
                "data_mb": last.stats.data_mb,
                "global_data_mb": last.stats.global_data_mb,
                "rounds": last.stats.rounds,
            }
            writer.writerow(row)
            f.flush()
            print(f"{exp:9} {label:17} {mech:8} {security:11} n={n:<4} k={k:<3} "
                  f"time={row['time_s']:.4f}s data={row['data_mb']:.4f}MB "
                  f"rounds={row['rounds']} mults={row['mults']}")


if __name__ == "__main__":
    main()
