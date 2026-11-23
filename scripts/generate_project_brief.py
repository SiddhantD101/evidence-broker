from pathlib import Path
from textwrap import wrap

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "pdf"
REVIEW_DIR = ROOT / "tmp" / "pdf-review"
PDF_PATH = OUTPUT_DIR / "evidence-broker-project-brief.pdf"


COLORS = {
    "ink": "#172026",
    "muted": "#61707A",
    "line": "#D7DEE2",
    "blue": "#326EBD",
    "green": "#2F7D57",
    "red": "#B34545",
    "gold": "#A36B10",
    "panel": "#F7F9F8",
}


def add_text(ax, x, y, text, size=10, weight="normal", color=None, width=86, line_gap=0.042):
    color = color or COLORS["ink"]
    lines = []
    for para in text.split("\n"):
        if para.strip() == "":
            lines.append("")
        else:
            lines.extend(wrap(para, width=width))
    for line in lines:
        ax.text(x, y, line, fontsize=size, fontweight=weight, color=color, va="top", family="DejaVu Sans")
        y -= line_gap
    return y


def header(ax, page, title):
    ax.text(0.07, 0.955, "Evidence Broker", fontsize=10, fontweight="bold", color=COLORS["blue"], va="top")
    ax.text(0.93, 0.955, f"{page}", fontsize=9, color=COLORS["muted"], va="top", ha="right")
    ax.plot([0.07, 0.93], [0.93, 0.93], color=COLORS["line"], lw=1)
    ax.text(0.07, 0.9, title, fontsize=20, fontweight="bold", color=COLORS["ink"], va="top")


def pill(ax, x, y, text, color, w=0.18):
    box = FancyBboxPatch((x, y - 0.032), w, 0.05, boxstyle="round,pad=0.008,rounding_size=0.012", fc=color, ec=color)
    ax.add_patch(box)
    ax.text(x + w / 2, y - 0.008, text, color="white", fontsize=8.5, fontweight="bold", ha="center", va="center")


def panel(ax, x, y, w, h, title, body, accent=None):
    box = FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0.012,rounding_size=0.014", fc="white", ec=COLORS["line"], lw=1)
    ax.add_patch(box)
    if accent:
        ax.add_patch(FancyBboxPatch((x, y - h), 0.012, h, boxstyle="round,pad=0,rounding_size=0.014", fc=accent, ec=accent, lw=0))
    ax.text(x + 0.025, y - 0.03, title, fontsize=11.5, fontweight="bold", color=COLORS["ink"], va="top")
    add_text(ax, x + 0.025, y - 0.072, body, size=8.2, color=COLORS["muted"], width=42, line_gap=0.022)


def setup_ax(fig):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0", fc="#EEF2F0", ec="none"))
    ax.add_patch(FancyBboxPatch((0.045, 0.045), 0.91, 0.91, boxstyle="round,pad=0.012,rounding_size=0.018", fc="white", ec=COLORS["line"], lw=1.0))
    return ax


def page_one(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    ax = setup_ax(fig)
    header(ax, 1, "Project Brief")
    ax.text(0.07, 0.84, "Credential brokering", fontsize=23, fontweight="bold", color=COLORS["ink"], va="top")
    ax.text(0.07, 0.795, "for agent workflows", fontsize=23, fontweight="bold", color=COLORS["ink"], va="top")
    add_text(
        ax,
        0.07,
        0.72,
        "Evidence Broker is a standalone MCP server that lets an agent use a named credential without seeing the secret. The broker validates host and method scope, asks the operator when needed, performs the request, redacts the result, and seals the decision into a hash-chained ledger.",
        size=10.5,
        width=82,
        line_gap=0.028,
    )

    pill(ax, 0.07, 0.535, "MCP server", COLORS["blue"])
    pill(ax, 0.27, 0.535, "Default deny", COLORS["red"])
    pill(ax, 0.47, 0.535, "Hash chained", COLORS["green"])
    pill(ax, 0.67, 0.535, "119 tests", COLORS["gold"])

    panel(
        ax,
        0.07,
        0.455,
        0.4,
        0.14,
        "Problem",
        "Putting tokens in an agent context exposes them to transcripts, logs, and accidental echoing. Operators need a durable record of attempts and approvals.",
        COLORS["red"],
    )
    panel(
        ax,
        0.53,
        0.455,
        0.4,
        0.14,
        "Approach",
        "The agent names a credential and target. The broker parses the host, enforces scope, asks a human, and injects the secret only inside the broker.",
        COLORS["blue"],
    )
    panel(
        ax,
        0.07,
        0.265,
        0.4,
        0.14,
        "Evidence",
        "Allows and denials are sealed. Each row links to the previous hash, and a separate head helps detect tail truncation.",
        COLORS["green"],
    )
    panel(
        ax,
        0.53,
        0.265,
        0.4,
        0.14,
        "Operator Channel",
        "Approvals are file based, avoiding a new local control port. The decision stays outside the agent-owned stdio path.",
        COLORS["gold"],
    )
    pdf.savefig(fig)
    fig.savefig(REVIEW_DIR / "page-1.png", dpi=160)
    plt.close(fig)


def page_two(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    ax = setup_ax(fig)
    header(ax, 2, "Runtime Flow")

    nodes = [
        ("Agent", 0.13, 0.67, COLORS["blue"], "Lists credential scope\nRequests one action\nReceives redacted result"),
        ("Broker", 0.38, 0.67, COLORS["green"], "Validates target\nHolds the secret\nSeals evidence"),
        ("Operator", 0.63, 0.67, COLORS["gold"], "Reviews pending file\nApproves or denies\nVerifies ledger"),
        ("Target API", 0.84, 0.67, COLORS["red"], "Receives one request\nMay echo credential\nNever talks to agent"),
    ]

    for i, (name, x, y, color, body) in enumerate(nodes):
        ax.add_patch(Circle((x, y), 0.055, fc=color, ec="white", lw=2))
        ax.text(x, y + 0.002, name.split()[0][0], color="white", fontsize=18, fontweight="bold", ha="center", va="center")
        ax.text(x, y - 0.09, name, fontsize=11.5, fontweight="bold", color=COLORS["ink"], ha="center", va="top")
        add_text(ax, x - 0.085, y - 0.13, body, size=8.5, color=COLORS["muted"], width=22, line_gap=0.029)
        if i < len(nodes) - 1:
            ax.add_patch(FancyArrowPatch((x + 0.065, y), (nodes[i + 1][1] - 0.065, y), arrowstyle="-|>", mutation_scale=14, lw=1.5, color=COLORS["line"]))

    ax.text(0.07, 0.43, "Key security properties", fontsize=15, fontweight="bold", color=COLORS["ink"], va="top")
    bullets = [
        "Secrets never cross the agent boundary and are never returned through MCP.",
        "Host allowlists are parsed, so substring tricks and userinfo targets are refused.",
        "Approvals bind to an action digest and cannot be replayed for a different request.",
        "Redaction covers raw, URL-encoded, base64, base64url, and JSON-escaped forms.",
        "Denials are evidence too, so failed attempts remain visible after the fact.",
    ]
    y = 0.385
    for bullet in bullets:
        ax.text(0.085, y, ">", fontsize=10, color=COLORS["blue"], va="top", fontweight="bold")
        y = add_text(ax, 0.11, y, bullet, size=9.3, color=COLORS["ink"], width=76, line_gap=0.029) - 0.002

    pdf.savefig(fig)
    fig.savefig(REVIEW_DIR / "page-2.png", dpi=160)
    plt.close(fig)


def page_three(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    ax = setup_ax(fig)
    header(ax, 3, "How To Run And Demo")
    panel(
        ax,
        0.07,
        0.82,
        0.86,
        0.17,
        "Local commands",
        "npm install\nnpm test\nnpm run build\nnpm run demo\nnpm run visual",
        COLORS["blue"],
    )
    panel(
        ax,
        0.07,
        0.58,
        0.4,
        0.21,
        "Agent tool surface",
        "list_credentials\nrequest_credential_use\nsend\nverify_evidence\nrecent_evidence\n\nThere is deliberately no approve tool.",
        COLORS["green"],
    )
    panel(
        ax,
        0.53,
        0.58,
        0.4,
        0.21,
        "Project layout",
        "src/target.ts parses targets\nsrc/redact.ts scrubs secrets\nsrc/chain.ts verifies hashes\nsrc/broker.ts orchestrates calls\nsrc/server.ts exposes MCP tools\ntest/ covers the full trust boundary",
        COLORS["gold"],
    )

    ax.text(0.07, 0.29, "Current limitations", fontsize=15, fontweight="bold", color=COLORS["ink"], va="top")
    limitations = [
        "The chain is tamper-evident, not tamper-proof; an external anchor or signing key is future work.",
        "Secrets come from environment variables today, not a host vault integration.",
        "Grants live in memory, so a restart drops outstanding approvals in the safe direction.",
    ]
    y = 0.245
    for item in limitations:
        ax.text(0.085, y, ">", fontsize=10, color=COLORS["red"], va="top", fontweight="bold")
        y = add_text(ax, 0.11, y, item, size=9.2, color=COLORS["ink"], width=76, line_gap=0.028) - 0.002

    pdf.savefig(fig)
    fig.savefig(REVIEW_DIR / "page-3.png", dpi=160)
    plt.close(fig)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    with PdfPages(PDF_PATH) as pdf:
        page_one(pdf)
        page_two(pdf)
        page_three(pdf)
    print(PDF_PATH)


if __name__ == "__main__":
    main()
