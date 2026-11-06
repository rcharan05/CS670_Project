"""Figures and tables for the final report, from bench/results/results.csv.

Writes into bench/results/:
  fig_scale_n.png   rounds and data vs number of bidders (k = 32)
  fig_scale_k.png   rounds and data vs bid length (n = 32)
  fig_wan.png       modelled end-to-end time on LAN and WAN links vs n
  fig_security.png  semi-honest vs malicious communication
  summary.md        headline numbers as Markdown tables

Modelled time = measured local time + rounds * RTT + bytes / bandwidth, using
party 0's rounds and bytes. Localhost runs have ~0 latency, so this is what
separates a round-heavy protocol from a data-heavy one on a real network.
"""

import csv
import os
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

# Reference palette, light mode: first two categorical slots (all-pairs safe).
# Colour encodes the algorithm, line style the domain (solid = arithmetic,
# dashed + hollow marker = binary), so the figures also survive grayscale print.
SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"
BLUE, ORANGE = "#2a78d6", "#eb6834"
SERIES = {  # variant: (color, marker, linestyle, label)
    "bitslice-ring": (BLUE, "o", "-", "Bit-slice, arithmetic"),
    "bitslice-bin": (BLUE, "o", "--", "Bit-slice, binary"),
    "tournament-ring": (ORANGE, "^", "-", "Tournament, arithmetic"),
    "tournament-bin": (ORANGE, "^", "--", "Tournament, binary"),
}
# bitslice-ring-int (in-MPC bit decomposition) is an extra: it stays in results.csv
# and summary.md but is left out of the figures.
SECURITY_COLORS = {"semi-honest": BLUE, "malicious": ORANGE}
SECURITY_LABELS = {"semi-honest": "Semi-honest",
                   "malicious": "Malicious with abort"}
NETWORKS = [("LAN: 1 ms RTT, 1 Gbit/s", 0.001, 1000),
            ("WAN: 50 ms RTT, 100 Mbit/s", 0.050, 100)]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": TEXT_2, "axes.titlecolor": TEXT,
    "axes.titlesize": 11, "axes.labelsize": 9.5, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": TEXT_2, "ytick.color": TEXT_2,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
    "legend.frameon": False, "legend.fontsize": 9, "font.size": 9.5,
    "legend.handlelength": 4,
    "lines.linewidth": 2, "lines.markersize": 6,
})


def load():
    with open(os.path.join(RESULTS, "results.csv")) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for key in ("n", "k", "mults", "rand_bits", "opens", "static_rounds", "rounds"):
            r[key] = int(r[key])
        for key in ("time_s", "time_s_min", "data_mb", "global_data_mb"):
            r[key] = float(r[key])
    return rows


def modelled_time(r, rtt, mbit_s):
    return r["time_s"] + r["rounds"] * rtt + r["data_mb"] * 8 / mbit_s


def series(rows, experiment, mechanism, x):
    out = defaultdict(list)
    for r in rows:
        if r["experiment"] == experiment and r["mechanism"] == mechanism:
            out[r["variant"]].append(r)
    return {v: sorted(rs, key=lambda r: r[x]) for v, rs in out.items()}


def plot_series(ax, variant, rs, x, y):
    color, marker, style, label = SERIES[variant]
    binary = style == "--"
    ax.plot([r[x] for r in rs], [y(r) for r in rs], color=color, marker=marker,
            linestyle=style, label=label,
            markerfacecolor=SURFACE if binary else color,
            markeredgecolor=color if binary else SURFACE, markeredgewidth=1.5)


def legend_below(fig, axes, ncol=None):
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=ncol or len(labels),
               bbox_to_anchor=(0.5, 0.0))


def grid_figure(rows, experiment, x, xlabel, fname, title):
    metrics = [("rounds", "Communication rounds"),
               ("data_mb", "Data sent per server (MB)")]
    fig, axes = plt.subplots(len(metrics), 2, figsize=(10, 7), sharex=True)
    for col, mech in enumerate(["first", "vickrey"]):
        data = series(rows, experiment, mech, x)
        for row_i, (metric, ylabel) in enumerate(metrics):
            ax = axes[row_i][col]
            for variant in SERIES:
                plot_series(ax, variant, data.get(variant, []), x,
                            lambda r: r[metric])
            if x == "n":
                ax.set_xscale("log", base=2)
            if metric == "data_mb":
                ax.set_yscale("log")
            if row_i == 0:
                ax.set_title(f"{'First-price' if mech == 'first' else 'Vickrey'}")
            if col == 0:
                ax.set_ylabel(ylabel)
            if row_i == len(metrics) - 1:
                ax.set_xlabel(xlabel)
    for row_i in range(len(metrics)):  # share y within a row for honest comparison
        lo = min(a.get_ylim()[0] for a in axes[row_i])
        hi = max(a.get_ylim()[1] for a in axes[row_i])
        for a in axes[row_i]:
            a.set_ylim(lo, hi)
    fig.suptitle(title, color=TEXT, fontsize=12)
    legend_below(fig, axes[0], ncol=4)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(os.path.join(RESULTS, fname), dpi=200)
    plt.close(fig)


def wan_figure(rows):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    data = series(rows, "scale_n", "vickrey", "n")
    for ax, (net, rtt, bw) in zip(axes, NETWORKS):
        for variant in SERIES:
            plot_series(ax, variant, data.get(variant, []), "n",
                        lambda r: modelled_time(r, rtt, bw))
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_title(net)
        ax.set_xlabel("Number of bidders n")
    axes[0].set_ylabel("Modelled time (s)")
    fig.suptitle("Vickrey auction, k = 32: modelled end-to-end time", color=TEXT, fontsize=12)
    legend_below(fig, axes, ncol=4)
    fig.tight_layout(rect=(0, 0.13, 1, 1))
    fig.savefig(os.path.join(RESULTS, "fig_wan.png"), dpi=200)
    plt.close(fig)


def security_figure(rows):
    rs = [r for r in rows if r["experiment"] == "security"]
    if not rs:
        return
    variants = [v for v in SERIES if any(r["variant"] == v for r in rs)]
    ns = sorted({r["n"] for r in rs})
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharey=True)
    axes = axes.flatten()
    width = 0.38
    for ax, variant in zip(axes, variants):
        for j, security in enumerate(SECURITY_COLORS):
            vals = [next(r["data_mb"] for r in rs if r["variant"] == variant
                         and r["security"] == security and r["n"] == n) for n in ns]
            xs = [i + (j - 0.5) * (width + 0.02) for i in range(len(ns))]
            bars = ax.bar(xs, vals, width, color=SECURITY_COLORS[security],
                          label=SECURITY_LABELS[security])
            ax.bar_label(bars, fmt="%.3g", fontsize=7.5, color=TEXT_2, padding=2)
        ax.set_xticks(range(len(ns)), [f"n = {n}" for n in ns])
        ax.set_yscale("log")
        ax.set_title(SERIES[variant][3])
        ax.grid(axis="x", visible=False)
    for ax in axes[::2]:
        ax.set_ylabel("Data sent per server (MB)")
    fig.suptitle("Cost of malicious security (Vickrey, k = 32)", color=TEXT, fontsize=12)
    legend_below(fig, axes)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(os.path.join(RESULTS, "fig_security.png"), dpi=200)
    plt.close(fig)


def summary_table(rows):
    lines = ["# Benchmark summary", ""]
    lines += ["## Scaling in n (k = 32, semi-honest)", "",
              "| mechanism | n | variant | ANDs | rand bits | opens | rounds | MB/server "
              "| local s | LAN s | WAN s |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["experiment"] != "scale_n":
            continue
        lines.append(
            f"| {r['mechanism']} | {r['n']} | {r['variant']} | {r['mults']} | "
            f"{r['rand_bits']} | {r['opens']} | {r['rounds']} | {r['data_mb']:.4f} | "
            f"{r['time_s']:.4f} | {modelled_time(r, *NETWORKS[0][1:]):.3f} | "
            f"{modelled_time(r, *NETWORKS[1][1:]):.3f} |")
    lines += ["", "## Semi-honest vs malicious (Vickrey, k = 32)", "",
              "| variant | n | security | rounds | MB/server | local s |",
              "|---|---|---|---|---|---|"]
    for r in rows:
        if r["experiment"] == "security":
            lines.append(f"| {r['variant']} | {r['n']} | {r['security']} | {r['rounds']} | "
                         f"{r['data_mb']:.4f} | {r['time_s']:.4f} |")
    with open(os.path.join(RESULTS, "summary.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    rows = load()
    grid_figure(rows, "scale_n", "n", "Number of bidders n", "fig_scale_n.png",
                "Scaling with the number of bidders (k = 32)")
    grid_figure(rows, "scale_k", "k", "Bid length k (bits)", "fig_scale_k.png",
                "Scaling with the bid length (n = 32)")
    wan_figure(rows)
    security_figure(rows)
    summary_table(rows)
    print(f"figures and summary.md written to {RESULTS}")


if __name__ == "__main__":
    main()
