"""End-to-end demo: python -m auction --mech vickrey --bids 11 13 9"""

import argparse

from .reference import MECHANISMS, plaintext_auction
from .runner import SECURITY, input_encoding, run_auction
from .sharing import ENCODINGS, as_signed, server_inputs


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        prog="python -m auction",
        description="Run a privacy-preserving sealed-bid auction across 3 MPC servers.")
    ap.add_argument("--bids", type=int, nargs="+", required=True,
                    help="one bid per bidder (bidder 0, 1, ...)")
    ap.add_argument("--names", nargs="+", help="optional bidder names")
    ap.add_argument("--mech", choices=MECHANISMS, default="first",
                    help="first-price or second-price (Vickrey)")
    ap.add_argument("-k", "--bits", type=int, default=16, help="bid bit length")
    ap.add_argument("--encoding", choices=ENCODINGS, default="bits",
                    help="bidders share individual bits, or whole integers")
    ap.add_argument("--binary", action="store_true",
                    help="run in the binary domain (XOR shares of bits, 1 bit per AND)")
    ap.add_argument("--security", choices=SECURITY, default="semi-honest",
                    help="server adversary model (3-party replicated sharing)")
    ap.add_argument("--baseline", action="store_true",
                    help="use the pairwise-comparison tournament instead of bit-slice")
    ap.add_argument("--show-shares", action="store_true",
                    help="print what each server receives (random-looking shares)")
    ap.add_argument("--check", action="store_true",
                    help="compare against the plaintext reference (demo only: "
                         "this computes the outcome in the clear)")
    args = ap.parse_args(argv)
    if args.names and len(args.names) != len(args.bids):
        ap.error("--names must have one entry per bid")
    return args


def main(argv=None):
    args = parse_args(argv)
    names = args.names or [f"bidder {i}" for i in range(len(args.bids))]
    program = ("baseline_tournament" if args.baseline else "auction") + \
        ("_bin" if args.binary else "")
    encoding = input_encoding(program, args.encoding)

    print(f"{len(args.bids)} bidders, {args.bits}-bit bids, {args.mech}-price, "
          f"{program} program, {encoding} shares, {args.security} servers")

    if args.show_shares:
        # Fresh shares, for display only; run_auction draws its own.
        inputs = server_inputs(args.bids, args.bits, encoding)
        width = len(inputs[0]) // len(args.bids)
        for p, values in enumerate(inputs):
            print(f"\nServer {p} receives:")
            for i, name in enumerate(names):
                mine = [as_signed(values[j * len(args.bids) + i]) for j in range(width)]
                shown = ", ".join(str(v) for v in mine[:3])
                more = f", ... ({width} shares)" if width > 3 else ""
                print(f"  from {name:>10}: {shown}{more}")

    result, stats = run_auction(args.bids, args.bits, args.mech, args.encoding,
                                args.security, program)
    print(f"\nWinner: {names[result.winner]} pays {result.price}")
    print(f"Cost (party 0): {stats.time_s:.4f} s, {stats.data_mb:.4f} MB sent, "
          f"~{stats.rounds} rounds; all parties: {stats.global_data_mb:.4f} MB")

    if args.check:
        expected = plaintext_auction(args.bids, args.mech)
        status = "OK" if expected == result else f"MISMATCH (expected {expected})"
        print(f"Plaintext check: {status}")
        return 0 if expected == result else 1
    return 0
