"""Compile MP-SPDZ programs and run them across 3 local server processes."""

import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass

from .reference import AuctionResult
from .sharing import server_inputs, write_server_inputs

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MPSPDZ_ROOT = os.environ.get(
    "MPSPDZ_ROOT", os.path.join(PROJECT_ROOT, "third_party", "mp-spdz"))
MPC_DIR = os.path.join(PROJECT_ROOT, "mpc")
RING_BITS = 64
N_SERVERS = 3

# program -> domain. "arith": additive shares over Z_2^64 (an AND is a ring
# multiplication); "bin": XOR shares of single bits (an AND costs one bit).
PROGRAMS = {
    "auction": "arith",
    "baseline_tournament": "arith",
    "auction_bin": "bin",
    "baseline_tournament_bin": "bin",
}
COMPILE_FLAGS = {"arith": ["-R", str(RING_BITS)], "bin": []}

SECURITY = ("semi-honest", "malicious")
# 3-party replicated secret sharing, honest majority (Araki et al.); the
# malicious variants give security with abort against one corrupt server.
PARTY_BINARIES = {
    ("arith", "semi-honest"): "replicated-ring-party.x",
    ("arith", "malicious"): "malicious-rep-ring-party.x",
    ("bin", "semi-honest"): "replicated-bin-party.x",
    ("bin", "malicious"): "malicious-rep-bin-party.x",
}


def program_args(program, n, k, mechanism, encoding="bits"):
    """Compile-time arguments: only the arithmetic bit-slice takes an encoding."""
    return [n, k, mechanism, encoding] if program == "auction" else [n, k, mechanism]


def input_encoding(program, encoding="bits"):
    """How bidders share their bids for ``program`` (see auction/sharing.py)."""
    if PROGRAMS[program] == "bin":
        return "xor"
    return encoding if program == "auction" else "int"


class MPCError(RuntimeError):
    pass


@dataclass
class RunStats:
    time_s: float = None  # wall time reported by party 0 (incl. preprocessing)
    data_mb: float = None  # data sent by party 0
    rounds: int = None  # communication rounds reported by party 0
    global_data_mb: float = None  # data sent by all parties together


@dataclass
class RunOutput:
    stdout: str
    stats: RunStats


def program_name(source, args):
    return "-".join([source] + [str(a) for a in args])


def run_compiler(source, args):
    """Compile mpc/<source>.mpc with ``args``; return the compiler's stdout."""
    src = os.path.join(MPC_DIR, source + ".mpc")
    proc = subprocess.run(
        ["./compile.py"] + COMPILE_FLAGS[PROGRAMS[source]] + [src]
        + [str(a) for a in args],
        cwd=MPSPDZ_ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise MPCError(f"compilation of {program_name(source, args)} failed:\n"
                       f"{proc.stdout}\n{proc.stderr}")
    return proc.stdout


def compile_program(source, args):
    """Compile mpc/<source>.mpc with ``args``; reuse the bytecode if up to date."""
    name = program_name(source, args)
    src = os.path.join(MPC_DIR, source + ".mpc")
    sch = os.path.join(MPSPDZ_ROOT, "Programs", "Schedules", name + ".sch")
    if not (os.path.exists(sch) and os.path.getmtime(sch) >= os.path.getmtime(src)):
        run_compiler(source, args)
    return name


def _free_port_base(count=N_SERVERS):
    """Find a base port such that base..base+count-1 are currently free."""
    for _ in range(50):
        with socket.socket() as s:
            s.bind(("localhost", 0))
            base = s.getsockname()[1]
        if base + count >= 65536:
            continue
        try:
            for p in range(base, base + count):
                with socket.socket() as s:
                    s.bind(("localhost", p))
            return base
        except OSError:
            continue
    raise MPCError("no free port range found")


def _parse_stats(text):
    stats = RunStats()
    m = re.search(r"^Time = ([\d.e+-]+) seconds", text, re.M)
    if m:
        stats.time_s = float(m.group(1))
    m = re.search(r"^Data sent = ([\d.e+-]+) MB in ~(\d+) rounds", text, re.M)
    if m:
        stats.data_mb = float(m.group(1))
        stats.rounds = int(m.group(2))
    m = re.search(r"^Global data sent = ([\d.e+-]+) MB", text, re.M)
    if m:
        stats.global_data_mb = float(m.group(1))
    return stats


class MPCTimeout(MPCError):
    pass


def _run_once(binary, name, input_prefix, timeout):
    port = _free_port_base()
    procs = []
    for p in range(N_SERVERS):
        cmd = [binary, "-p", str(p), "-pn", str(port),
               "-h", "localhost", "-IF", input_prefix, name]
        procs.append(subprocess.Popen(
            cmd, cwd=MPSPDZ_ROOT, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True))
    # Wait for all parties, but give up as soon as one fails: the others would
    # otherwise block until their own peer timeout.
    deadline = time.monotonic() + timeout
    while any(proc.poll() is None for proc in procs):
        failed = any(proc.returncode not in (None, 0) for proc in procs)
        if failed or time.monotonic() > deadline:
            for proc in procs:
                proc.kill()
            break
        time.sleep(0.005)
    outputs = [proc.communicate()[0] for proc in procs]
    for p, proc in enumerate(procs):
        if proc.returncode != 0:
            details = "\n".join(f"--- party {q}:\n{out}" for q, out in enumerate(outputs))
            if "Timed out waiting for peer" in details or proc.returncode < 0:
                raise MPCTimeout(f"{name}: parties did not connect on port {port}\n{details}")
            raise MPCError(f"party {p} failed on {name}:\n{outputs[p]}")
    return outputs[0]


def run_program(name, inputs, domain="arith", security="semi-honest", timeout=120,
                retries=1):
    """Run compiled program ``name`` on 3 local parties.

    ``inputs[p]`` is the list of values server p reads. Returns party 0's
    output (the only party that prints) together with its cost statistics.
    A run that hangs (e.g. a port grabbed between probing and binding) is
    retried on a fresh port up to ``retries`` times.
    """
    binary = os.path.join(MPSPDZ_ROOT, PARTY_BINARIES[domain, security])
    with tempfile.TemporaryDirectory(prefix="auction-run-") as tmp:
        write_server_inputs(inputs, tmp)
        for attempt in range(retries + 1):
            try:
                out = _run_once(binary, name, os.path.join(tmp, "Input"), timeout)
                break
            except MPCTimeout as e:
                if attempt == retries:
                    raise
                print(f"warning: {e}", file=sys.stderr)
    return RunOutput(out, _parse_stats(out))


def run_auction(bids, k, mechanism="first", encoding="bits", security="semi-honest",
                program="auction"):
    """Secret-share ``bids``, run the MPC auction, return (result, stats).

    ``encoding`` only matters for the arithmetic bit-slice program; the
    others fix their own input encoding (see ``input_encoding``).
    """
    name = compile_program(program, program_args(program, len(bids), k, mechanism, encoding))
    inputs = server_inputs(bids, k, input_encoding(program, encoding))
    out = run_program(name, inputs, PROGRAMS[program], security)
    m = re.search(r"^RESULT winner=(\d+) price=(\d+)", out.stdout, re.M)
    if not m:
        raise MPCError(f"no RESULT line in output of {name}:\n{out.stdout}")
    return AuctionResult(int(m.group(1)), int(m.group(2))), out.stats
