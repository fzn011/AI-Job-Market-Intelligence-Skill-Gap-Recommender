"""Generate README preview images for CareerCompass."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "docs" / "screenshots"

ACCENT = "#FF4433"
DARK = "#120608"
SURFACE = "#1A0A0C"
TEXT = "#FFFFFF"
MUTED = "#B8B8B8"


def _save(fig: plt.Figure, name: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    fig.savefig(path, dpi=160, facecolor=DARK, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print(f"Saved {path.relative_to(PROJECT_ROOT)}")


def landing_page() -> None:
    fig, ax = plt.subplots(figsize=(12, 6.5))
    fig.patch.set_facecolor(DARK)
    ax.set_facecolor(SURFACE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    hero = patches.FancyBboxPatch((0.04, 0.55), 0.92, 0.38, boxstyle="round,pad=0.02", linewidth=1.5, edgecolor=ACCENT, facecolor="#2A1014")
    ax.add_patch(hero)
    ax.text(0.07, 0.82, "CareerCompass", fontsize=24, color=TEXT, fontweight="bold")
    ax.text(0.07, 0.74, "Job Market Intelligence & Skill Gap Analyzer", fontsize=12, color=MUTED)
    ax.text(0.07, 0.64, "Quick Start: choose goal -> add CV/details -> get match score and next action", fontsize=11, color=TEXT)

    for idx, label in enumerate(["Job Market", "CV Skill Gap", "Career Explorer", "Intelligence Hub"]):
        x = 0.07 + idx * 0.23
        card = patches.FancyBboxPatch((x, 0.12), 0.2, 0.34, boxstyle="round,pad=0.015", linewidth=1, edgecolor=ACCENT, facecolor="#241015")
        ax.add_patch(card)
        ax.text(x + 0.02, 0.38, label, fontsize=10, color=TEXT, fontweight="bold")

    _save(fig, "01_landing_page.png")


def skill_gap_dashboard() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1, 1.2]})
    fig.patch.set_facecolor(DARK)
    for ax in axes:
        ax.set_facecolor(SURFACE)

    axes[0].text(0.5, 0.85, "CV Skill Gap", ha="center", transform=axes[0].transAxes, fontsize=16, color=TEXT, fontweight="bold")
    axes[0].text(0.5, 0.62, "72%", ha="center", fontsize=42, color=ACCENT, fontweight="bold", transform=axes[0].transAxes)
    axes[0].text(0.5, 0.48, "Match Score", ha="center", transform=axes[0].transAxes, fontsize=12, color=MUTED)
    axes[0].text(0.5, 0.28, "Missing: Docker, MLflow, Kubernetes", ha="center", transform=axes[0].transAxes, fontsize=10, color=TEXT)
    axes[0].axis("off")

    skills = ["Python", "SQL", "Power BI", "Docker", "MLflow"]
    matched = [1, 1, 1, 0, 0]
    colors = [ACCENT if m else "#5A2A30" for m in matched]
    axes[1].barh(skills, [1] * 5, color=colors)
    axes[1].set_title("Skill Coverage", color=TEXT, fontsize=14)
    axes[1].tick_params(colors=TEXT)
    axes[1].set_xlim(0, 1.2)
    for spine in axes[1].spines.values():
        spine.set_color(ACCENT)

    _save(fig, "02_cv_skill_gap.png")


def market_overview() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor(DARK)

    skills = ["Python", "SQL", "Excel", "Power BI", "Docker"]
    counts = [10, 7, 4, 3, 3]
    axes[0].set_facecolor(SURFACE)
    axes[0].bar(skills, counts, color=ACCENT)
    axes[0].set_title("Top Skills in Dataset", color=TEXT)
    axes[0].tick_params(axis="x", rotation=25, colors=TEXT)
    axes[0].tick_params(axis="y", colors=TEXT)

    matrix = np.array([[1.0, 0.6, 0.3], [0.6, 1.0, 0.4], [0.3, 0.4, 1.0]])
    axes[1].set_facecolor(SURFACE)
    im = axes[1].imshow(matrix, cmap="Reds")
    axes[1].set_xticks(range(3))
    axes[1].set_yticks(range(3))
    axes[1].set_xticklabels(["Python", "SQL", "Docker"], color=TEXT)
    axes[1].set_yticklabels(["Python", "SQL", "Docker"], color=TEXT)
    axes[1].set_title("Skill Co-occurrence", color=TEXT)

    _save(fig, "03_market_analytics.png")


def career_explorer() -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor(DARK)
    ax.set_facecolor(SURFACE)
    categories = ["Data & AI", "Software & IT", "Finance", "Marketing", "Healthcare"]
    roles = [8, 7, 6, 5, 4]
    ax.barh(categories, roles, color=ACCENT)
    ax.set_title("Career Explorer — Roles by Category", color=TEXT, fontsize=14)
    ax.tick_params(colors=TEXT)
    ax.set_xlabel("Role profiles available", color=MUTED)
    for spine in ax.spines.values():
        spine.set_color(ACCENT)

    _save(fig, "04_career_explorer.png")


def main() -> None:
    landing_page()
    skill_gap_dashboard()
    market_overview()
    career_explorer()
    print("README screenshots ready.")


if __name__ == "__main__":
    main()
