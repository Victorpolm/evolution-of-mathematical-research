"""Render the aggregate-only contributor comparison as a standalone SVG."""
import argparse
import json
from pathlib import Path


def render(source, output, preview=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter, MaxNLocator

    data = json.loads(source.read_text())
    rows, study = data["annual"], data["study"]
    years = [int(r["period"]) for r in rows]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                        "svg.fonttype": "none", "axes.spines.top": False,
                        "axes.spines.right": False})
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.subplots_adjust(left=.08, right=.97, top=.85, bottom=.24, hspace=.9, wspace=.27)
    configs = [
        ("1. Papers per active contributor", "papers_per_active_contributor", None,
         "Papers / active key", "Papers in each year ÷ distinct keys on those same papers.\nThe denominator is recomputed within every year."),
        ("2. Papers per full-study contributor", "papers_per_study_contributor", None,
         "Papers / full-study key", "The same annual papers ÷ all keys observed in 2010–2025.\nInactive keys contribute zero; this follows paper-count growth."),
        ("3. Top 10% share of fractional credit", "fractional", "share",
         "Share of paper credit", "Give each byline slot 1/k of a paper; rank keys each year.\nTop-decile credit ÷ all credit (equal to paper count P)."),
        ("4. Top 10% share of coauthored counts", "coauthored", "share",
         "Share of key–paper participations", "Count each key once per paper; rank keys each year.\nTop-decile counts ÷ all key–paper participations J, not P."),
    ]
    for ax, (title, field, sub, ylabel, caption) in zip(axes.flat, configs):
        for method, label, color, style in (("ids", "OpenAlex IDs", "#365bc9", "-"),
                                            ("names", "Distinct names", "#a76519", "--")):
            y = [r[method][field][sub] if sub else r[method][field] for r in rows]
            ax.plot(years, y, color=color, linestyle=style, linewidth=2, label=label)
        if sub:
            ax.axhline(.1, color="#8792a6", linewidth=1, linestyle=":", label="Equal-output benchmark")
            ax.set_ylim(0, .4)
            ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
            ax.set_yticks([0, .1, .2, .3, .4])
        else:
            ax.set_ylim(bottom=0)
            ax.yaxis.set_major_locator(MaxNLocator(5))
        ax.set_xlim(2010, 2025)
        ax.set_xticks([2010, 2015, 2020, 2025])
        ax.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=13)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xlabel("arXiv ID year", fontsize=9)
        ax.grid(axis="y", alpha=.2)
        ax.legend(loc="lower left" if sub or field == "papers_per_active_contributor" else "upper left",
                  frameon=False, fontsize=8)
        ax.text(0, -.32, caption, transform=ax.transAxes, ha="left", va="top", fontsize=9, linespacing=1.5)
    fig.suptitle("Papers, contributor populations and the most prolific decile", x=.08, y=.97,
                 ha="left", fontsize=19, fontweight="bold")
    fig.text(.08, .92, f"2010–2025 · {study['papers']:,} retained papers · two identity definitions on identical papers", fontsize=12)
    fig.text(.08, .89, f"Full-study pool: {study['ids']['authors']:,} OpenAlex IDs or {study['names']['authors']:,} distinct names", fontsize=10)
    fig.text(.08, .065, "Source: frozen OpenAlex metadata, 16 Sep 2026; selected arXiv-linked Mathematics works.\n"
             "Top 10% uses exact population weight with proportional boundary ties. Names/IDs are observed keys, not validated people.\n"
             "Whole-study P/A: " + f"{study['ids']['papers_per_active_contributor']:.3f} per ID; "
             f"{study['names']['papers_per_active_contributor']:.3f} per name (16-year totals, not annual rates).",
             fontsize=9, linespacing=1.5, color="#39475b")
    fig.savefig(output, format="svg", metadata={"Date": "2026-09-16"})
    if preview:
        fig.savefig(preview, dpi=110)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args()
    render(args.source, args.out, args.preview)


if __name__ == "__main__":
    main()
