"""Build figures from real data, not illustrations.

    python assets/make_real_figures.py

Everything plotted here comes from files on disk:

  drivaer_geometry.png   real 8,000-point DrivAerNet++ surface point clouds, three
                         bodies, with each car's measured drag coefficient from its
                         own force_mom CSV
  training.png           the actual 50-epoch training log of the drag RegDGCNN
                         (validation R-squared and drag-coefficient MAE per epoch)
  dataset.png            the measured drag distribution across 8,121 DrivAerNet++ runs

Why this exists: the earlier profile panels contained a hand-drawn car and a synthetic
parity scatter. Both were fine as illustration and both would be misleading on a page
that also quotes measured numbers, because a reader cannot tell which figures are data
and which are drawings. These are data. Nothing here is invented, and the axis labels
say exactly what each quantity is.

The point clouds contain geometry only. They are therefore coloured by height, which
is a geometric quantity, and explicitly labelled as such. No pressure field is shown,
because the local files do not carry one.
"""

from __future__ import annotations

import csv
import glob
import re
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

OUT = Path(__file__).parent
CHAT = Path(
    "C:/Users/samar/Downloads/Antigravity/website/phononiq/.claude/worktrees/"
    "thirsty-leavitt-8b06b9/chat_cad"
)
MESH = CHAT / "DrivAerNet" / "PPMesh"
CD_CSV = CHAT / "DrivAerNet" / "DrivAerNetPlusPlus_Cd_8k.csv"
LOG = CHAT / "train_randsplit.log"

BG = "#0b1016"
PANEL = "#0e151d"
INK = "#e6edf3"
MUTED = "#8b949e"
DIM = "#63footer"[:7]
DIM = "#6e7f91"
TEAL = "#2dd4bf"
AMBER = "#fbbf24"
GREEN = "#34d399"
BLUE = "#60a5fa"
VIOLET = "#a78bfa"

CMAP = LinearSegmentedColormap.from_list(
    "depth", ["#123c52", "#12657a", "#1b9aa4", "#4fd1c5", "#a7f3d0"]
)

plt.rcParams.update(
    {
        "figure.facecolor": BG,
        "axes.facecolor": PANEL,
        "savefig.facecolor": BG,
        "text.color": INK,
        "axes.labelcolor": MUTED,
        "axes.edgecolor": "#26333f",
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
        "font.size": 10,
        "axes.titleweight": "bold",
        "axes.titlesize": 11.5,
        "grid.color": "#1b2husk"[:7].replace("hus", "262"),
        "grid.alpha": 0.55,
        "legend.frameon": False,
    }
)


def read_cd(run: str) -> float | None:
    """Measured drag coefficient for one run, from its own force_mom CSV."""
    f = MESH / run / f"force_mom_{run}.csv"
    if not f.exists():
        return None
    with f.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                return float(row["Cd"])
            except (KeyError, ValueError, TypeError):
                return None
    return None


def load_cloud(run: str) -> np.ndarray | None:
    f = MESH / run / f"point_cloud_{run}.npz"
    if not f.exists():
        return None
    return np.load(f, allow_pickle=True)["points"].astype(np.float64)


def pick_runs(n: int = 3) -> list[str]:
    """Runs that have both a cloud and a plausible measured Cd, spread across Cd."""
    cands = []
    for d in sorted(glob.glob(str(MESH / "*")))[:900]:
        run = Path(d).name
        cd = read_cd(run)
        if cd is None or not (0.15 < cd < 0.45):
            continue
        if not (MESH / run / f"point_cloud_{run}.npz").exists():
            continue
        cands.append((cd, run))
    if not cands:
        return []
    cands.sort()
    idx = np.linspace(0, len(cands) - 1, n).round().astype(int)
    return [cands[i][1] for i in idx]


def isometric(pts: np.ndarray, az: float = 34.0, el: float = 16.0):
    """Project to 2D with a depth key, so the scatter can be drawn back to front."""
    a, e = np.radians(az), np.radians(el)
    x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
    u = x * np.cos(a) - y * np.sin(a)
    v = (x * np.sin(a) + y * np.cos(a)) * np.sin(e) + z * np.cos(e)
    depth = (x * np.sin(a) + y * np.cos(a)) * np.cos(e) - z * np.sin(e)
    return u, v, depth


def fig_geometry(runs: list[str]) -> Path:
    fig, axes = plt.subplots(1, len(runs), figsize=(12.0, 2.9), dpi=190)
    if len(runs) == 1:
        axes = [axes]

    for ax, run in zip(axes, runs):
        pts = load_cloud(run)
        cd = read_cd(run)
        u, v, depth = isometric(pts)
        order = np.argsort(depth)
        u, v, depth = u[order], v[order], depth[order]
        zc = pts[order][:, 2]

        # size and alpha fall with depth so the far side does not muddy the near side
        # np.ptp rather than the method: ndarray.ptp was removed in NumPy 2.
        dn = (depth - depth.min()) / max(float(np.ptp(depth)), 1e-9)
        ax.scatter(
            u, v, c=zc, cmap=CMAP, s=1.6 + 3.4 * dn, alpha=0.85,
            linewidths=0, rasterized=True,
        )
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(
            f"{run}\n$C_d$ = {cd:.4f}  ·  {len(pts):,} points",
            color=INK, fontsize=10.5, pad=6,
        )

    fig.suptitle(
        "Real DrivAerNet++ surface point clouds, coloured by height (geometry, not pressure)",
        color=INK, fontsize=12.5, fontweight="bold", y=1.02,
    )
    fig.text(
        0.5, -0.03,
        "Each cloud is 8,000 sampled surface points from the published CFD run. "
        "The drag coefficient under each car is that run's own measured value.",
        ha="center", color=DIM, fontsize=9.5,
    )
    p = OUT / "drivaer_geometry.png"
    fig.savefig(p, bbox_inches="tight", pad_inches=0.28)
    plt.close(fig)
    return p


def parse_log() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ep, r2, mae = [], [], []
    pat = re.compile(
        r"ep\s+(\d+)\s+train_loss=([\d.eE+-]+)\s+val_R2=([+-][\d.]+)\s+val_MAE=([\d.]+)"
    )
    for line in LOG.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = pat.search(line)
        if m:
            ep.append(int(m.group(1)))
            r2.append(float(m.group(3)))
            mae.append(float(m.group(4)))
    return np.array(ep), np.array(r2), np.array(mae)


def fig_training() -> Path:
    ep, r2, mae = parse_log()
    fig, ax = plt.subplots(figsize=(7.4, 4.0), dpi=170)
    ax.grid(True, linewidth=0.6)

    ax.plot(ep, r2, color=GREEN, linewidth=2.0, label="validation $R^2$")
    best = int(np.argmax(r2))
    ax.scatter([ep[best]], [r2[best]], color=AMBER, s=46, zorder=5)
    ax.annotate(
        f"best $R^2$ = {r2[best]:+.3f} at epoch {ep[best]}",
        xy=(ep[best], r2[best]), xytext=(-18, -62), textcoords="offset points",
        color=AMBER, fontsize=10, ha="right",
        arrowprops={"arrowstyle": "-", "color": AMBER, "lw": 1.0},
    )
    ax.set_xlabel("epoch")
    ax.set_ylabel("validation $R^2$", color=GREEN)
    ax.set_ylim(0.0, 1.0)
    ax.tick_params(axis="y", colors=GREEN)

    ax2 = ax.twinx()
    ax2.plot(ep, mae, color=BLUE, linewidth=1.7, linestyle="--", label="validation MAE")
    ax2.set_ylabel("validation MAE in $C_d$", color=BLUE)
    ax2.tick_params(axis="y", colors=BLUE)
    ax2.spines["right"].set_color("#26333f")
    ax2.grid(False)

    ax.set_title(
        "Drag surrogate training: real 50-epoch log, RegDGCNN on 4,677 cars",
        color=INK,
    )
    lines = ax.get_lines() + ax2.get_lines()
    ax.legend(lines, [ln.get_label() for ln in lines], loc="center right", labelcolor=MUTED)

    fig.text(
        0.5, -0.06,
        "Validation split is 825 held-out cars, 2,048 points per car. This is a "
        "validation curve used for checkpoint selection,\nnot a sealed test result, and "
        "the split is random rather than the published one.",
        ha="center", color=DIM, fontsize=9,
    )
    p = OUT / "training.png"
    fig.savefig(p, bbox_inches="tight", pad_inches=0.26)
    plt.close(fig)
    return p


def fig_dataset() -> Path:
    vals = []
    with CD_CSV.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                v = float(row["Drag_Value"])
            except (KeyError, ValueError, TypeError):
                continue
            if 0.0 < v < 1.0:
                vals.append(v)
    v = np.array(vals)

    fig, ax = plt.subplots(figsize=(7.4, 4.0), dpi=170)
    ax.grid(True, linewidth=0.6, axis="y")
    n, bins, patches = ax.hist(v, bins=64, color=TEAL, alpha=0.85, edgecolor=BG, linewidth=0.4)
    ax.axvline(v.mean(), color=AMBER, linewidth=1.6, linestyle="--")
    ax.annotate(
        f"mean {v.mean():.4f}", xy=(v.mean(), n.max() * 0.92),
        xytext=(10, 0), textcoords="offset points", color=AMBER, fontsize=10,
    )
    ax.set_xlabel("drag coefficient $C_d$")
    ax.set_ylabel("number of runs")
    ax.set_title(
        f"Measured drag across {len(v):,} DrivAerNet++ CFD runs", color=INK
    )
    fig.text(
        0.5, -0.04,
        f"Spread is what makes $R^2$ meaningful: std {v.std():.4f}, "
        f"range {v.min():.3f} to {v.max():.3f}. A surrogate MAE of 0.0082 is "
        f"{0.0082 / v.std():.2f} standard deviations.",
        ha="center", color=DIM, fontsize=9,
    )
    p = OUT / "dataset.png"
    fig.savefig(p, bbox_inches="tight", pad_inches=0.26)
    plt.close(fig)
    return p


if __name__ == "__main__":
    if not MESH.exists():
        raise SystemExit(f"point cloud directory not found: {MESH}")
    runs = pick_runs(3)
    print("selected runs:", runs)
    for f in (fig_geometry(runs), fig_training(), fig_dataset()):
        print(f"wrote {f.name}  {f.stat().st_size:,} bytes")
