"""Matplotlib charts used in the PDF report (the web UI uses Chart.js)."""
import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402,F401

BLUE, GREEN, AMBER, GREY = "#2563EB", "#10B981", "#F59E0B", "#9CA3AF"


def _png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def site_scores(recs):
    fig, ax = plt.subplots(figsize=(7, 3.6))
    r = recs[:8][::-1]
    ax.barh([x["area"] for x in r], [x["score"] for x in r], color=[GREEN if x["rank"] == 1 else BLUE for x in r])
    for i, x in enumerate(r):
        ax.text(x["score"] + 0.5, i, f"{x['score']:.0f}", va="center", fontsize=8)
    ax.set_xlabel("Expansion score (0-100)")
    ax.spines[["top", "right"]].set_visible(False)
    return _png(fig)


def revenue_forecast(fc):
    fig, ax = plt.subplots(figsize=(7, 3.2))
    h, f = fc["hist_labels"], fc["f_labels"]
    ax.plot(h, fc["hist"], color=BLUE, lw=2, label="Actual")
    ax.plot([h[-1]] + f, [fc["hist"][-1]] + fc["forecast"], color=AMBER, lw=2, ls="--", label="Forecast")
    ax.fill_between(f, fc["lower"], fc["upper"], color=AMBER, alpha=0.2)
    ax.set_xticks(list(range(0, len(h) + len(f), 3)))
    ax.set_xticklabels((h + f)[::3], rotation=45, fontsize=7)
    ax.legend(frameon=False)
    ax.set_ylabel("Monthly revenue (₹ lakh)")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1e5:.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    return _png(fig)


def area_bars(areas):
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.bar(areas["labels"], [v / 1e5 for v in areas["revenue"]], color=BLUE)
    ax.set_ylabel("Revenue (₹ lakh)")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    return _png(fig)


def map_png(customers, stores, recs):
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    ax.scatter(customers["longitude"], customers["latitude"], s=4, c=BLUE, alpha=0.18, label="Customers")
    if len(stores):
        ax.scatter(stores["longitude"], stores["latitude"], s=90, marker="s", c="#111827", label="Existing stores")
    for x in recs[:3]:
        ax.scatter(x["longitude"], x["latitude"], s=160, marker="*", c=GREEN if x["rank"] == 1 else AMBER, edgecolor="k", zorder=5)
        ax.annotate(f"#{x['rank']} {x['area']}", (x["longitude"], x["latitude"]), xytext=(6, 6), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    return _png(fig)
