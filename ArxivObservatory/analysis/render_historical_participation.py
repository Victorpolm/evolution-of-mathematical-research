"""Render the aggregate historical comparison; no network or raw records."""
import argparse
import json
from pathlib import Path


def render(source, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter

    data = json.loads(source.read_text())
    rows = data["annual"]
    years = [int(r["period"]) for r in rows]
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":10,
                         "axes.spines.top":False, "axes.spines.right":False,
                         "svg.fonttype":"none"})
    fig = plt.figure(figsize=(10.5, 9), facecolor="white")
    fig.suptitle("Papers per observed contributor, 2010–2025", x=.09, y=.97,
                 ha="left", fontsize=18, fontweight="bold", color="#111e35")
    fig.text(.09,.932,"OpenAlex arXiv-linked Mathematics · frozen metadata, 16 September 2026",
             color="#526077", fontsize=10)
    a = fig.add_axes([.09,.64,.87,.225])
    b = fig.add_axes([.09,.245,.87,.225])
    for method, label, color, style in (("ids","OpenAlex resolved author IDs","#365bc9","-"),
                                        ("names","Distinct raw names","#a76519","--")):
        a.plot(years, [r[method]["papers_per_author"] for r in rows], label=label,
               color=color, linestyle=style, linewidth=2.2, marker="o", markersize=3.5)
    a.set_title("1. Retained papers divided by distinct contributor keys (P/A)",loc="left",pad=12,fontweight="bold")
    a.set_ylabel("Papers / contributor key")
    a.set_ylim(bottom=0)
    a.legend(frameon=False,loc="lower left",fontsize=9)
    fig.text(.09,.535,"Both definitions use the same complete paired bylines. Each key is counted once per calendar year.\n"
             "P/A is mean fractional paper credit; it is not mean full-count coauthored papers or validated person productivity.",
             fontsize=9,color="#526077",linespacing=1.5)
    b.plot(years,[100*r["coverage"]["retention"] for r in rows],color="#a76519",linewidth=2.2,marker="o",markersize=3.5,label="Paired / unambiguously linked papers")
    b.plot(years,[100*r["coverage"]["overall_retention"] for r in rows],color="#365bc9",linestyle="--",linewidth=2.2,label="Paired / mapped arXiv paper IDs")
    b.legend(frameon=False,loc="lower left",fontsize=9)
    b.set_title("2. Retention through linkage and byline checks",loc="left",pad=12,fontweight="bold")
    b.set_ylabel("Retained share")
    b.set_ylim(0,100)
    b.yaxis.set_major_formatter(PercentFormatter())
    fig.text(.09,.14,"Brown: P / unambiguously linked papers. Blue also counts IDs with ambiguous version links in its denominator.\n"
             "This is byline completeness within the queried OpenAlex frame, not coverage of all arXiv mathematics.",
             fontsize=9,color="#526077",linespacing=1.5)
    for ax in (a,b):
        ax.set_xlim(years[0]-.2,years[-1]+.2)
        ax.set_xticks([2010,2013,2016,2019,2022,2025])
        ax.set_xlabel("arXiv ID year (submission-year proxy)")
        ax.grid(axis="y",alpha=.2)
        ax.set_axisbelow(True)
    fig.text(.09,.052,"Scope: primary OpenAlex field Mathematics; indexed in arXiv; queried publication years 2010–2026.\n"
             "Unique arXiv ID dates 2010–2025; ambiguous links and unusable paired bylines excluded.\n"
             "Name keys and resolved IDs can both split or combine people. No causal effect of AI is established.",
             fontsize=8.5,color="#526077",linespacing=1.45)
    output.mkdir(parents=True,exist_ok=True)
    for suffix in ("svg","png"):
        fig.savefig(output / ("historical_participation."+suffix), dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    render(args.input,args.output)
