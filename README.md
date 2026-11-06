# Privacy-Preserving Sealed-Bid Auction

CS670 course project (IIT Kanpur). A sealed-bid auction, first-price or second-price (Vickrey), computed by three servers using secure multiparty computation (MPC). No server ever sees an individual bid. The servers learn the winner and the price they pay, and nothing else.

- **Protocol:** 3-party replicated secret sharing over Z<sub>2^64</sub> (MP-SPDZ `replicated-ring`), semi-honest, honest majority.
- **Circuit:** the Kurosawa–Ogata (2002) bit-slice maximum, plus an oblivious second scan for the Vickrey price.
- **Baseline:** a knockout tournament built on MP-SPDZ's built-in secure comparison.
- **Two domains:** each program exists in an *arithmetic* version, where every secret is an additive share over Z<sub>2^64</sub>, and a *binary* version, where every secret is an XOR-shared bit (MP-SPDZ `replicated-bin`). The circuit is identical in both. An AND costs 64 bits of communication in the first and 1 bit in the second.

Team: Aarav Oswal (230012), Ch. Rishitha (230311), R. Charan (230819), Poorvie Sadagopan (230759).

**Documents:** [Final report](report/report.pdf) · [Slides](presentation/slides.pdf) · [Mid-term report](Mid_Term_Project_Report.pdf) · [Literature review](CS670_Literature_Review.pdf)

## Requirements

- **OS:** Linux on x86-64, or Windows 10/11 through WSL2. macOS (including Apple Silicon) is not supported, because the MP-SPDZ release binaries are built for x86-64 Linux only. On a Mac, use an x86-64 Linux VM or a remote Linux machine.
- **Python** 3.10 or newer, with `venv`.
- **System tools:** `git`, `curl`, `tar`, `xz`, `openssl` (the setup script checks for them).
- An internet connection for the first setup (it downloads MP-SPDZ).

## Setup

Runs on **Linux** (x86-64) and on **Windows through WSL2**. The MPC engine, MP-SPDZ, has no native Windows build.

### Linux

```bash
git clone https://github.com/rcharan05/CS670_Project.git && cd CS670_Project
bash setup/setup.sh
```

`setup.sh` checks prerequisites, downloads MP-SPDZ 0.4.3 into `third_party/`, creates `.venv`, installs the Python packages, and runs a 3-server smoke test. It takes about a minute. If a system package is missing, it prints the exact `apt` command to install it.

### Windows (WSL2)

1. **Install WSL with Ubuntu.** In PowerShell *as Administrator*, run the following, then reboot:
   ```powershell
   wsl --install -d Ubuntu
   ```
   Open **Ubuntu** from the Start menu and create a Linux username and password when asked.
2. **Install the prerequisites** in the Ubuntu terminal:
   ```bash
   sudo apt update && sudo apt install -y git curl xz-utils openssl python3 python3-venv
   ```
3. **Clone and set up inside your WSL home folder**, not under `/mnt/c/...`:
   ```bash
   cd ~
   git clone https://github.com/rcharan05/CS670_Project.git && cd CS670_Project
   bash setup/setup.sh
   ```
4. **Edit in VS Code** (optional): install the *WSL* extension, then run `code .` from the Ubuntu terminal. VS Code opens the folder through WSL, so its terminal, Python interpreter (`.venv/bin/python`) and test runner all run in Linux.

Troubleshooting:

| Symptom | Fix |
|---|---|
| `$'\r': command not found` or `bash\r: No such file` | The repository was cloned with Windows Git, which converted line endings. Clone it again *inside WSL* (step 3). The repo's `.gitattributes` prevents this for new clones. |
| Setup is very slow | The project is under `/mnt/c/`. Move it to `~` inside WSL. |
| `Timed out waiting for peer` | A port was briefly busy. The runner retries automatically; just re-run if it ever surfaces. |

## Run an auction

```bash
.venv/bin/python -m auction --bids 11 13 9 --names Alice Bob Carol -k 4 --mech vickrey --show-shares --check
```

```
Server 0 receives:
  from      Alice: -8760345893813108272, 5303196773236420981, 4155692657406917683, ... (4 shares)
  ...
Winner: Bob pays 11
Cost (party 0): 0.0020 s, 0.0008 MB sent, ~38 rounds; all parties: 0.0023 MB
Plaintext check: OK
```

Useful flags:

| Flag | Meaning |
|---|---|
| `--mech first\|vickrey` | First-price (the default) or second-price auction |
| `-k` | Bid bit length (default 16; bids must lie in [0, 2^k)) |
| `--encoding bits\|int` | Bidders share each bit (the default), or the whole integer (an extra; see [below](#extra-integer-encoding-with-secure-bit-decomposition)) |
| `--baseline` | Use the comparison tournament instead of the bit-slice circuit |
| `--binary` | Run in the binary domain (XOR-shared bits) |
| `--security malicious` | Malicious security with abort for the servers |
| `--show-shares` | Print what each server receives |
| `--check` | Compare with a plaintext computation. Demo only: it computes the outcome in the clear. |

## Tests

```bash
.venv/bin/pytest -q
```

| File | What it checks |
|---|---|
| `tests/test_reference.py` | The plaintext auction rule and edge cases; the corrected worked example from the lit review (Table 1) |
| `tests/test_bitslice_sim.py` | The oblivious bit-slice arithmetic against the auction rule: exhaustive for n ≤ 3, k = 3, plus 6,000 random cases |
| `tests/test_sharing.py` | Shares reconstruct correctly, the server input layout is right, and a single share is uniform (χ² test) |
| `tests/test_mpc_e2e.py` | Real 3-server runs of all four programs against the reference, covering ties, a single bidder, all-equal bids, zeros and maximum values, plus random cases. Also a malicious-security run, and a reveal audit confirming that the compiled bit-slice programs open only the winner and the price. |

## Benchmarks

```bash
.venv/bin/python bench/run_bench.py --reps 5        # → bench/results/results.csv (~2 min)
.venv/bin/python bench/plot.py                      # → bench/results/fig_*.png, summary.md
```

`plot.py` also produces a modelled LAN/WAN time: measured time + rounds × RTT + bytes / bandwidth. All runs execute on localhost, where latency is close to zero.

## Building the report and slides

The PDFs are committed, so this is only needed after editing the LaTeX sources. It requires a TeX distribution with TikZ and Beamer (for example `sudo apt install texlive-full`, or TeX Live / MiKTeX).

```bash
cd report && latexmk -pdf report.tex                 # → report/report.pdf
cd ../presentation && latexmk -pdf slides.tex        # → presentation/slides.pdf
```

The report includes the figures from `bench/results/`, so regenerate them first (see [Benchmarks](#benchmarks)) if the benchmark data changes.

## How it works

1. **Input** (`auction/sharing.py`). Each bidder splits each bit of its bid into three additive shares mod 2^64 and sends one share to each server. Any two shares are uniformly random, so a single server learns nothing.
2. **Computation** (`mpc/auction.mpc`). The servers add the shares inside the MPC. They then scan from the most significant bit down, keeping a secret mask `S` of the bidders still in the running:
   ```
   t   = S · b[j]                 # survivor has a 1 at bit j
   c_j = 1 − Π (1 − t_i)          # does any survivor have a 1? (log-depth tree)
   S   = S − c_j · (S − t)        # if so, drop survivors with a 0
   ```
   The bits `c_j` form the maximum bid. Ties go to the lowest index, computed obliviously with a prefix product, so it is never revealed who else tied. For Vickrey, the winner's bits are zeroed obliviously and the scan is repeated; the new maximum is the price.
3. **Output.** Only `winner` and `price` are opened (`auction/audit.py` checks this against the compiler's count of opened values).

Cost per scan: 3nk − k secure multiplications (ANDs) and k·(⌈log₂ n⌉ + 2) rounds. Vickrey roughly doubles both.

**Binary version** (`mpc/auction_bin.mpc`). Bidders XOR-share their bids, and the servers pack bit j of all n bidders into one n-bit word. Each scan step is then a single word-wide AND, and the update becomes `S ⊕ (c_j ∧ (S ⊕ t))`. The AND count is identical to the arithmetic version, but each AND costs 1 bit instead of 64. XOR and NOT are free.

## Extra: integer encoding with secure bit decomposition

This mode is not part of the report or the presentation. By default a bidder converts its bid to bits and shares each bit, because that conversion is trivial for whoever knows the bid. With `--encoding int` the bidder instead shares the whole number, and the servers extract its bits inside the MPC (`bids.bit_decompose(k)` in `mpc/auction.mpc`, which uses MP-SPDZ's `BitDecRingRaw`):

1. **Mask.** Preprocessing gives the servers shares of a random k-bit number `r` and of each of its bits. Nobody knows `r`.
2. **Open.** The servers compute and open `c = (bid − r) mod 2^k`. Because `r` is uniformly random, `c` is too, so it reveals nothing about the bid.
3. **Add back.** The bid equals `c + r mod 2^k`. The servers run a binary adder on the public bits of `c` and the secret bits of `r`. XOR gives each sum bit and a secret AND gives each carry, so they end up with shares of the bid's bits.

```bash
.venv/bin/python -m auction --bids 5 3 6 --mech vickrey -k 3 --encoding int --check
```

Trade-offs compared with the default:

- **Cost.** At n = 128, k = 32 (Vickrey) it needs 46,017 ANDs instead of 29,505, plus 4,096 random bits. Data per server rises from 0.27 MB to 0.40 MB.
- **Extra opens.** The program opens the `n` masked values `c` as well as the winner and price. `auction/audit.py` expects 2 + n opens for this mode.
- **Valid bits.** The adder always produces valid 0/1 bits, so a cheating bidder can't submit a "bit" equal to 2. With the default encoding, bidders are trusted on this.

The benchmark sweep still measures this mode as the `bitslice-ring-int` variant. It appears in `bench/results/results.csv` and `summary.md`, but not in the figures.

## Layout

```
auction/      reference.py (plaintext + bit-level simulation), sharing.py, runner.py, audit.py, cli.py
mpc/          auction.mpc, baseline_tournament.mpc            (arithmetic, Z_2^64)
              auction_bin.mpc, baseline_tournament_bin.mpc    (binary, XOR-shared bits)
tests/        pytest suite
bench/        run_bench.py, plot.py, results/
report/       report.tex, report.pdf, diagrams/   (final report)
presentation/ slides.tex, slides.pdf, speaker_notes.md, diagrams/
setup/        setup.sh, install_mpspdz.sh
third_party/  MP-SPDZ (installed by the setup script, not committed)
```
