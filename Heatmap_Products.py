# -*- coding: utf-8 -*-
"""
heatmap_adoption_barriers_READABLE_SIMPLE.py

Outputs (exactly four files):
 1) 01_category_heatmap_(timestamp).png
 2) 01_category_heatmap_(timestamp).pdf
 3) 02_coverage_heatmap_(timestamp).png
 4) 02_coverage_heatmap_(timestamp).pdf

Notes:
 - First plot (category heatmap) is PORTRAIT: Products on X-axis, Categories on Y-axis.
 - Clean code: robust save; consistent styling; clear legends.
 - Model: binary presence per simplified trend; category cells count distinct present trends.
"""

import os
from datetime import datetime
import unicodedata
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# ----------------------------------------------------------------------
# Output folder & robust saving
# ----------------------------------------------------------------------
OUT_DIR = r"C:\Users\tputze\Pictures\Heatmaps"  # >>> CHANGE THIS PATH IF NEEDED <<<
os.makedirs(OUT_DIR, exist_ok=True)

def make_names(base_name: str):
    """Return (png_path, pdf_path) with a time-stamped suffix."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    png = os.path.join(OUT_DIR, f"{base_name}_{stamp}.png")
    pdf = os.path.join(OUT_DIR, f"{base_name}_{stamp}.pdf")
    return png, pdf

def safe_save(fig, png_path: str, pdf_path: str):
    """Save PNG and PDF; remain silent if PDF is locked (PNG still saved)."""
    fig.savefig(png_path, bbox_inches="tight")
    try:
        fig.savefig(pdf_path, bbox_inches="tight")
    except PermissionError:
        pass
    finally:
        plt.close(fig)

# ----------------------------------------------------------------------
# Font & style
# ----------------------------------------------------------------------
mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["font.size"] = 11
mpl.rcParams["axes.titlesize"] = 16
mpl.rcParams["axes.labelsize"] = 11
mpl.rcParams["xtick.labelsize"] = 11
mpl.rcParams["ytick.labelsize"] = 11
mpl.rcParams["axes.titleweight"] = "bold"

def sanitize_text(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    s = unicodedata.normalize("NFKC", s)
    s = (
        s.replace("\u2011", "-")
         .replace("\u2013", "-")
         .replace("\u2014", "-")
         .replace("\u2019", "'").replace("\u2018", "'")
         .replace("\u201c", '"').replace("\u201d", '"')
         .replace("\u2192", "->")
    )
    return s

# ----------------------------------------------------------------------
# Data: products, technical trend labels, presence (0/1)
# ----------------------------------------------------------------------
products = [
    "SAP WEB IDE PERSONAL EDITION",
    "SAPUI5",
    "CERBERUS",
    "SAP SIGNUP",
    "BUILD CONFIG REPO",
    "SCS SAT OCP",
    "PORTAL APP STUDIO EXTENSION OP",
    "CLOUD SECURITY CENTRAL",
    "CP PROCESS VISIBILITY",
    "MONITOR OF MONITORS SUITE",
    "SAP FIORI FOR SAP CARAB",
    "SAP ENC EXTERNAL WORKERS",
    "MESSAGE QUEUING SERVICE",
    "SAP DIGITAL PROCESS DNA",
    "SAP CALEIDOSCOPE",
    "SAP CP EF FAAS LIB",
    "SAP PROVISIONING SERVICE",
    "ANALYTICS DATA PRODUCT",
    "SCP CO WORKFLOW OD",
    "CP BUS RULES PRIVATE CLOUD",
    "CREDENTIAL STORE",
    "THINKTANK",
    "PCRM",
]

# Normalize product display names (Title Case) but keep original keys for data mapping
prod_display_map = {p: p.title() for p in products}
products_display = [prod_display_map[p] for p in products]

# Original (technical) trend labels
trends_orig = [
    "Cumulus integration/visibility gaps",
    "Azure DevOps primary / ADO->GHA migration",
    "Documentation/onboarding/self-service needs",
    "Decouple security scans from CI to improve velocity",
    "GitHub org consolidation / repo strategy dependency",
    "PR bot helpfulness / automated review value",
    "Branching model constraints (main vs release/hotfix)",
    "Vault secret rotation automation needed",
    "Teams notifications integration (Slack phase-out)",
    "Multi-cloud deployments (AWS/SAP sovereign/Azure)",
    "Sonar integration delays/ambiguity",
    "Concourse/Converged Cloud integration path unclear",
    "Long-running HDI updates / ADO timeout limits",
    "Jenkins legacy limitations vs GHA",
    "Trend Micro integration desire (artifact/runtime)",
    "Monorepo vs Hyperspace support gap",
    "Nightly builds/distribution build constraints (UI5/Fiori)",
    "Helm-based multi-cluster deployments",
    "Error logs not actionable; single support entry preferred",
    "Hyperspace IaC provisioning desire",
]

# Presence (0/1) keyed by original labels
presence_orig = {p: {t: 0 for t in trends_orig} for p in products}

# ----------------------------------------------------------------------
# Presence toggles per product (existing synthesis; names aligned)
# ----------------------------------------------------------------------
presence_orig["ANALYTICS DATA PRODUCT"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["ANALYTICS DATA PRODUCT"]["GitHub org consolidation / repo strategy dependency"] = 1
presence_orig["ANALYTICS DATA PRODUCT"]["Cumulus integration/visibility gaps"] = 1
presence_orig["ANALYTICS DATA PRODUCT"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["ANALYTICS DATA PRODUCT"]["Error logs not actionable; single support entry preferred"] = 1

presence_orig["SCP CO WORKFLOW OD"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["SCP CO WORKFLOW OD"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["SCP CO WORKFLOW OD"]["Cumulus integration/visibility gaps"] = 1
presence_orig["SCP CO WORKFLOW OD"]["Error logs not actionable; single support entry preferred"] = 1
presence_orig["SCP CO WORKFLOW OD"]["Decouple security scans from CI to improve velocity"] = 1

presence_orig["SAPUI5"]["Jenkins legacy limitations vs GHA"] = 1
presence_orig["SAPUI5"]["Nightly builds/distribution build constraints (UI5/Fiori)"] = 1
presence_orig["SAPUI5"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["SAPUI5"]["Monorepo vs Hyperspace support gap"] = 1
presence_orig["SAPUI5"]["Cumulus integration/visibility gaps"] = 1

presence_orig["CERBERUS"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["CERBERUS"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["CERBERUS"]["Monorepo vs Hyperspace support gap"] = 1
presence_orig["CERBERUS"]["Sonar integration delays/ambiguity"] = 1
presence_orig["CERBERUS"]["Branching model constraints (main vs release/hotfix)"] = 1

presence_orig["SAP SIGNUP"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["SAP SIGNUP"]["Sonar integration delays/ambiguity"] = 1
presence_orig["SAP SIGNUP"]["Branching model constraints (main vs release/hotfix)"] = 1
presence_orig["SAP SIGNUP"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["SAP SIGNUP"]["Cumulus integration/visibility gaps"] = 1

presence_orig["BUILD CONFIG REPO"]["Error logs not actionable; single support entry preferred"] = 1
presence_orig["BUILD CONFIG REPO"]["Branching model constraints (main vs release/hotfix)"] = 1
presence_orig["BUILD CONFIG REPO"]["Decouple security scans from CI to improve velocity"] = 1
presence_orig["BUILD CONFIG REPO"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["BUILD CONFIG REPO"]["Documentation/onboarding/self-service needs"] = 1

presence_orig["SCS SAT OCP"]["Vault secret rotation automation needed"] = 1
presence_orig["SCS SAT OCP"]["Teams notifications integration (Slack phase-out)"] = 1
presence_orig["SCS SAT OCP"]["Multi-cloud deployments (AWS/SAP sovereign/Azure)"] = 1
presence_orig["SCS SAT OCP"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["SCS SAT OCP"]["Hyperspace IaC provisioning desire"] = 1

presence_orig["PORTAL APP STUDIO EXTENSION OP"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["PORTAL APP STUDIO EXTENSION OP"]["Decouple security scans from CI to improve velocity"] = 1
presence_orig["PORTAL APP STUDIO EXTENSION OP"]["Long-running HDI updates / ADO timeout limits"] = 1
presence_orig["PORTAL APP STUDIO EXTENSION OP"]["Cumulus integration/visibility gaps"] = 1
presence_orig["PORTAL APP STUDIO EXTENSION OP"]["Documentation/onboarding/self-service needs"] = 1

presence_orig["CLOUD SECURITY CENTRAL"]["Concourse/Converged Cloud integration path unclear"] = 1
presence_orig["CLOUD SECURITY CENTRAL"]["Trend Micro integration desire (artifact/runtime)"] = 1
presence_orig["CLOUD SECURITY CENTRAL"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["CLOUD SECURITY CENTRAL"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["CLOUD SECURITY CENTRAL"]["Cumulus integration/visibility gaps"] = 1

presence_orig["CP PROCESS VISIBILITY"]["PR bot helpfulness / automated review value"] = 1
presence_orig["CP PROCESS VISIBILITY"]["Jenkins legacy limitations vs GHA"] = 1
presence_orig["CP PROCESS VISIBILITY"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["CP PROCESS VISIBILITY"]["Decouple security scans from CI to improve velocity"] = 1
presence_orig["CP PROCESS VISIBILITY"]["Documentation/onboarding/self-service needs"] = 1

presence_orig["MONITOR OF MONITORS SUITE"]["Monorepo vs Hyperspace support gap"] = 1
presence_orig["MONITOR OF MONITORS SUITE"]["Cumulus integration/visibility gaps"] = 1
presence_orig["MONITOR OF MONITORS SUITE"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["MONITOR OF MONITORS SUITE"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["MONITOR OF MONITORS SUITE"]["Error logs not actionable; single support entry preferred"] = 1

presence_orig["SAP FIORI FOR SAP CARAB"]["Nightly builds/distribution build constraints (UI5/Fiori)"] = 1
presence_orig["SAP FIORI FOR SAP CARAB"]["Jenkins legacy limitations vs GHA"] = 1
presence_orig["SAP FIORI FOR SAP CARAB"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["SAP FIORI FOR SAP CARAB"]["Cumulus integration/visibility gaps"] = 1
presence_orig["SAP FIORI FOR SAP CARAB"]["Azure DevOps primary / ADO->GHA migration"] = 1

presence_orig["SAP ENC EXTERNAL WORKERS"]["Helm-based multi-cluster deployments"] = 1
presence_orig["SAP ENC EXTERNAL WORKERS"]["Decouple security scans from CI to improve velocity"] = 1
presence_orig["SAP ENC EXTERNAL WORKERS"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["SAP ENC EXTERNAL WORKERS"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["SAP ENC EXTERNAL WORKERS"]["Branching model constraints (main vs release/hotfix)"] = 1

presence_orig["MESSAGE QUEUING SERVICE"]["Helm-based multi-cluster deployments"] = 1
presence_orig["MESSAGE QUEUING SERVICE"]["Teams notifications integration (Slack phase-out)"] = 1
presence_orig["MESSAGE QUEUING SERVICE"]["Decouple security scans from CI to improve velocity"] = 1
presence_orig["MESSAGE QUEUING SERVICE"]["Cumulus integration/visibility gaps"] = 1
presence_orig["MESSAGE QUEUING SERVICE"]["Azure DevOps primary / ADO->GHA migration"] = 1

presence_orig["SAP DIGITAL PROCESS DNA"]["Long-running HDI updates / ADO timeout limits"] = 1
presence_orig["SAP DIGITAL PROCESS DNA"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["SAP DIGITAL PROCESS DNA"]["Decouple security scans from CI to improve velocity"] = 1
presence_orig["SAP DIGITAL PROCESS DNA"]["Cumulus integration/visibility gaps"] = 1
presence_orig["SAP DIGITAL PROCESS DNA"]["Documentation/onboarding/self-service needs"] = 1

presence_orig["SAP CALEIDOSCOPE"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["SAP CALEIDOSCOPE"]["GitHub org consolidation / repo strategy dependency"] = 1
presence_orig["SAP CALEIDOSCOPE"]["Cumulus integration/visibility gaps"] = 1
presence_orig["SAP CALEIDOSCOPE"]["Documentation/onboarding/self-service needs"] = 1

presence_orig["SAP CP EF FAAS LIB"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["SAP CP EF FAAS LIB"]["Trend Micro integration desire (artifact/runtime)"] = 1
presence_orig["SAP CP EF FAAS LIB"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["SAP CP EF FAAS LIB"]["Cumulus integration/visibility gaps"] = 1

presence_orig["CP BUS RULES PRIVATE CLOUD"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["CP BUS RULES PRIVATE CLOUD"]["Decouple security scans from CI to improve velocity"] = 1
presence_orig["CP BUS RULES PRIVATE CLOUD"]["Teams notifications integration (Slack phase-out)"] = 1
presence_orig["CP BUS RULES PRIVATE CLOUD"]["Cumulus integration/visibility gaps"] = 1
presence_orig["CP BUS RULES PRIVATE CLOUD"]["Documentation/onboarding/self-service needs"] = 1

# NEW: SAP WEB IDE PERSONAL EDITION (from 2025-12-08 interview)
presence_orig["SAP WEB IDE PERSONAL EDITION"]["Jenkins legacy limitations vs GHA"] = 1
presence_orig["SAP WEB IDE PERSONAL EDITION"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["SAP WEB IDE PERSONAL EDITION"]["Decouple security scans from CI to improve velocity"] = 1

# NEW: CREDENTIAL STORE (from 2025-12-10 interview)
presence_orig["CREDENTIAL STORE"]["Vault secret rotation automation needed"] = 1
presence_orig["CREDENTIAL STORE"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["CREDENTIAL STORE"]["Error logs not actionable; single support entry preferred"] = 1
presence_orig["CREDENTIAL STORE"]["Sonar integration delays/ambiguity"] = 1
presence_orig["CREDENTIAL STORE"]["Jenkins legacy limitations vs GHA"] = 1
presence_orig["CREDENTIAL STORE"]["Cumulus integration/visibility gaps"] = 1

# NEW: SAP PROVISIONING SERVICE (from 2025-11-26 interview)
presence_orig["SAP PROVISIONING SERVICE"]["Jenkins legacy limitations vs GHA"] = 1
presence_orig["SAP PROVISIONING SERVICE"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["SAP PROVISIONING SERVICE"]["Decouple security scans from CI to improve velocity"] = 1
presence_orig["SAP PROVISIONING SERVICE"]["Cumulus integration/visibility gaps"] = 1

# --- NEW PRODUCTS FLAGS FROM LATEST TRANSCRIPTS ---
# THINKTANK
presence_orig["THINKTANK"]["Jenkins legacy limitations vs GHA"] = 1
presence_orig["THINKTANK"]["Azure DevOps primary / ADO->GHA migration"] = 1
presence_orig["THINKTANK"]["Trend Micro integration desire (artifact/runtime)"] = 1
presence_orig["THINKTANK"]["Teams notifications integration (Slack phase-out)"] = 1
presence_orig["THINKTANK"]["Decouple security scans from CI to improve velocity"] = 1
# (Thinktank already pushes evidence to Cumulus/Sirius via its library; no visibility-gap flag here)

# PCRM
presence_orig["PCRM"]["Jenkins legacy limitations vs GHA"] = 1
presence_orig["PCRM"]["Documentation/onboarding/self-service needs"] = 1
presence_orig["PCRM"]["Cumulus integration/visibility gaps"] = 1
presence_orig["PCRM"]["Error logs not actionable; single support entry preferred"] = 1
# (PCRM uses portal + Jenkins; no immediate GHA migration)

# ----------------------------------------------------------------------
# Simplified (plain-English) labels — unique values
# ----------------------------------------------------------------------
label_map = {
    "Cumulus integration/visibility gaps": "Compliance results are difficult to locate",
    "Azure DevOps primary / ADO->GHA migration": "Switch pipelines from Azure DevOps to GitHub Actions",
    "Documentation/onboarding/self-service needs": "Documentation and onboarding are incomplete",
    "Decouple security scans from CI to improve velocity": "Security scans slow builds; need separate process",
    "GitHub org consolidation / repo strategy dependency": "GitHub organization changes disrupt CI setup",
    "PR bot helpfulness / automated review value": "Automated pull-request checks should improve quality",
    "Branching model constraints (main vs release/hotfix)": "Branching rules need support for releases and hotfixes",
    "Vault secret rotation automation needed": "Secrets expire; need automated renewal",
    "Teams notifications integration (Slack phase-out)": "Pipeline alerts should integrate with Microsoft Teams",
    "Multi-cloud deployments (AWS/SAP sovereign/Azure)": "Need deployment patterns for multiple clouds",
    "Sonar integration delays/ambiguity": "Static code analysis setup is confusing",
    "Concourse/Converged Cloud integration path unclear": "Unclear integration for Concourse and Converged Cloud",
    "Long-running HDI updates / ADO timeout limits": "Database updates fail due to pipeline time limits",
    "Jenkins legacy limitations vs GHA": "Legacy Jenkins pipelines hinder migration",
    "Trend Micro integration desire (artifact/runtime)": "Trend Micro security scanning should be available",
    "Monorepo vs Hyperspace support gap": "Monorepo projects are not supported",
    "Nightly builds/distribution build constraints (UI5/Fiori)": "Front-end builds require nightly distribution runs",
    "Helm-based multi-cluster deployments": "Need ability to deploy one release to multiple clusters",
    "Error logs not actionable; single support entry preferred": "Error messages lack clarity; need single support channel",
    "Hyperspace IaC provisioning desire": "Infrastructure-as-code should automate project setup",
}
# Validate uniqueness
if len(set(label_map.values())) != len(label_map.values()):
    raise ValueError("Simplified labels must be unique. Please adjust 'label_map'.")

# Build presence under simplified labels
simplified_trends = [label_map[t] for t in trends_orig]
presence_simple = {p: {label_map[t]: v for t, v in presence_orig[p].items()} for p in products}

# ----------------------------------------------------------------------
# 4 display categories (STRICT ORDER) using simplified labels
# ----------------------------------------------------------------------
display_category_order = [
    "Migration Complexity",
    "Documentation and Self-Service Gaps",
    "Feature and Performance Needs",
    "Miscellaneous",
]

trend_to_display_category = {
    # Migration Complexity
    label_map["Azure DevOps primary / ADO->GHA migration"]: "Migration Complexity",
    label_map["Branching model constraints (main vs release/hotfix)"]: "Migration Complexity",
    label_map["Concourse/Converged Cloud integration path unclear"]: "Migration Complexity",
    label_map["GitHub org consolidation / repo strategy dependency"]: "Migration Complexity",
    label_map["Monorepo vs Hyperspace support gap"]: "Migration Complexity",
    # Documentation and Self-Service Gaps
    label_map["Documentation/onboarding/self-service needs"]: "Documentation and Self-Service Gaps",
    label_map["Error logs not actionable; single support entry preferred"]: "Documentation and Self-Service Gaps",
    # Feature and Performance Needs
    label_map["Decouple security scans from CI to improve velocity"]: "Feature and Performance Needs",
    label_map["Helm-based multi-cluster deployments"]: "Feature and Performance Needs",
    label_map["Long-running HDI updates / ADO timeout limits"]: "Feature and Performance Needs",
    label_map["Teams notifications integration (Slack phase-out)"]: "Feature and Performance Needs",
    label_map["Vault secret rotation automation needed"]: "Feature and Performance Needs",
    # Miscellaneous
    label_map["Cumulus integration/visibility gaps"]: "Miscellaneous",
    label_map["Sonar integration delays/ambiguity"]: "Miscellaneous",
    label_map["Jenkins legacy limitations vs GHA"]: "Miscellaneous",
    label_map["Trend Micro integration desire (artifact/runtime)"]: "Miscellaneous",
    label_map["Multi-cloud deployments (AWS/SAP sovereign/Azure)"]: "Miscellaneous",
    label_map["Nightly builds/distribution build constraints (UI5/Fiori)"]: "Miscellaneous",
    label_map["Hyperspace IaC provisioning desire"]: "Miscellaneous",
    label_map["PR bot helpfulness / automated review value"]: "Miscellaneous",
}

display_order_within_group = {
    "Migration Complexity": [
        label_map["Azure DevOps primary / ADO->GHA migration"],
        label_map["Branching model constraints (main vs release/hotfix)"],
        label_map["Concourse/Converged Cloud integration path unclear"],
        label_map["GitHub org consolidation / repo strategy dependency"],
        label_map["Monorepo vs Hyperspace support gap"],
    ],
    "Documentation and Self-Service Gaps": [
        label_map["Documentation/onboarding/self-service needs"],
        label_map["Error logs not actionable; single support entry preferred"],
    ],
    "Feature and Performance Needs": [
        label_map["Decouple security scans from CI to improve velocity"],
        label_map["Helm-based multi-cluster deployments"],
        label_map["Long-running HDI updates / ADO timeout limits"],
        label_map["Teams notifications integration (Slack phase-out)"],
        label_map["Vault secret rotation automation needed"],
    ],
    "Miscellaneous": [
        label_map["Cumulus integration/visibility gaps"],
        label_map["Sonar integration delays/ambiguity"],
        label_map["Jenkins legacy limitations vs GHA"],
        label_map["Trend Micro integration desire (artifact/runtime)"],
        label_map["Multi-cloud deployments (AWS/SAP sovereign/Azure)"],
        label_map["Nightly builds/distribution build constraints (UI5/Fiori)"],
        label_map["Hyperspace IaC provisioning desire"],
        label_map["PR bot helpfulness / automated review value"],
    ],
}

# Validate grouping coverage
_all = [t for group in display_order_within_group.values() for t in group]
missing = sorted(set(simplified_trends) - set(_all))
extra = sorted(set(_all) - set(simplified_trends))
if missing or extra:
    raise ValueError(f"Grouping mismatch. Missing: {missing} Extra: {extra}")

# ----------------------------------------------------------------------
# Build strict y-order + section bands/separators for coverage
# ----------------------------------------------------------------------
sorted_trends = []  # final y-order (simplified labels)
band_spans = []     # background bands
separators = []     # separator rows
row = 0
for i, group in enumerate(display_category_order, start=1):
    items = display_order_within_group[group]
    start = row
    sorted_trends.extend(items)
    row += len(items)
    end = row - 1
    band_color = "#f2f6ff" if i % 2 == 1 else "#f8fafc"
    band_spans.append((start, end, band_color, 0.90))
    separators.append(row)
# Remove last separator
if separators:
    separators = separators[:-1]

# ----------------------------------------------------------------------
# DataFrame builders & plotting
# ----------------------------------------------------------------------
def df_presence_simple(trend_order=None, product_order=None):
    df = pd.DataFrame(presence_simple).T  # products × simplified trends
    df = df.T                              # simplified trends × products
    if trend_order is not None:
        df = df.loc[trend_order]
    if product_order is not None:
        df = df[product_order]
    return df

def plot_heatmap_categories(
    df, title, fname_png, fname_pdf,
    xlabel="Core Trends", ylabel="Products",
    cmap="Reds", annot=True, fmt="d",
    dpi=340, footnote=None,
    ytick_labels=None, yrotation=0
):
    sns.set_theme(style="white")
    # Make square cells suitable for slide (PowerPoint)
    ncols = max(1, df.shape[1])
    nrows = max(1, df.shape[0])
    per_cell = 0.6  # inches per cell (increase so squares are legible)
    # add margins, ensure minimum size so text remains legible
    fig_w = max(10, per_cell * ncols + 1.5)
    fig_h = max(4, per_cell * nrows + 1.2)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    ax.set_aspect('equal')

    # smaller annotation font to avoid overlap
    annot_kws = {"fontsize": 8}

    sns.heatmap(
        df, ax=ax, cmap=cmap, linewidths=0.35, linecolor="#dddddd",
        annot=annot, fmt=fmt, cbar=False, square=True, annot_kws=annot_kws
    )
    # Only set title if provided
    if title:
        ax.set_title(sanitize_text(title), fontsize=16, fontweight='bold', pad=10)
    # Make axis labels bold and move them away from axes
    ax.set_xlabel(sanitize_text(xlabel), fontweight='bold', labelpad=12)
    ax.set_ylabel(sanitize_text(ylabel), fontweight='bold', labelpad=12)

    # X-axis (products) labels: avoid angled labels where possible; angle if many columns
    if ncols > 14:
        x_rotation = 45
        x_ha = "right"
    else:
        x_rotation = 0
        x_ha = "center"
    ax.set_xticklabels([str(c) for c in df.columns], rotation=x_rotation, ha=x_ha)
    ax.tick_params(axis="x", pad=6, labelsize=11)

    # Y-axis ticks: allow multi-line labels & spacing if provided
    if ytick_labels is None:
        ytick_labels = [str(c) for c in df.index]
    ax.set_yticklabels(ytick_labels, rotation=yrotation, ha="right")
    ax.tick_params(axis="y", pad=6, labelsize=11)

    plt.tight_layout()
    # compact margins for slide output
    plt.subplots_adjust(left=0.18, right=0.98, top=0.92, bottom=0.12)

    # Footnote
    if footnote:
        fig.text(0.01, 0.01, sanitize_text(footnote), fontsize=7, ha="left", va="bottom")
    safe_save(fig, fname_png, fname_pdf)

def plot_heatmap_grouped(
    df, title, fname_png, fname_pdf,
    xlabel="Products", ylabel="Trends",
    cmap="Blues", vmin=0, vmax=1,
    band_spans=None, separators=None,
    footnote=None, dpi=340
):
    sns.set_theme(style="white")
    fig_w = max(20, 0.40 * df.shape[1])  # wider
    fig_h = max(14, 0.70 * df.shape[0])  # taller
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)

    # Background bands behind heatmap
    if band_spans:
        for (start, end, color, alpha) in band_spans:
            ax.axhspan(start - 0.5, end + 0.5, facecolor=color, alpha=alpha, zorder=0)

    sns.heatmap(
        df, ax=ax, cmap=cmap, vmin=vmin, vmax=vmax,
        linewidths=0.4, linecolor="#dddddd",
        cbar=False
    )
    ax.set_title(sanitize_text(title), fontsize=16, fontweight='bold', pad=12)
    ax.set_xlabel(sanitize_text(xlabel))
    ax.set_ylabel(sanitize_text(ylabel))

    # One-line labels — products may be long; slight angle improves legibility
    ax.set_xticklabels([str(c) for c in df.columns], rotation=30, ha="right")
    ax.tick_params(axis="x", labelsize=11)
    ax.set_yticklabels([str(i) for i in df.index], rotation=0)
    ax.tick_params(axis="y", labelsize=11)

    # FULL-WIDTH separators using actual axis limits
    if separators:
        x_left, x_right = ax.get_xlim()
        for y in separators:
            ax.hlines(y, x_left, x_right, colors="#C9CDD3", linewidth=3.2, zorder=10, clip_on=False)

    if footnote:
        fig.text(0.01, 0.01, sanitize_text(footnote), fontsize=8, ha="left", va="bottom")
    plt.subplots_adjust(left=0.25, bottom=0.15, right=0.98, top=0.92)
    safe_save(fig, fname_png, fname_pdf)

# ----------------------------------------------------------------------
# 1) CATEGORY heatmap (4 categories × products) — PORTRAIT
#    Count per category × product: sum of present simplified trends that belong to the category
# ----------------------------------------------------------------------
cat_counts = {cat: {p: 0 for p in products} for cat in display_category_order}
for t_simplified in simplified_trends:
    cat = trend_to_display_category[t_simplified]
    for p in products:
        cat_counts[cat][p] += presence_simple[p][t_simplified]

# Order products by total barriers across categories (high → low)
df_cat = pd.DataFrame(cat_counts).T  # categories × products
product_order = df_cat.sum(axis=0).sort_values(ascending=False).index

# Ensure landscape: categories (rows) × products (columns)
df_cat_landscape = df_cat.loc[display_category_order, product_order].rename(columns=prod_display_map)

png1, pdf1 = make_names("01_category_heatmap")
plot_heatmap_categories(
    df_cat_landscape,
    title="",
    fname_png=png1, fname_pdf=pdf1,
    xlabel="Products", ylabel="Core Trends",
    cmap="Reds", annot=True, fmt="d",
    dpi=340,
    yrotation=0
)

# ----------------------------------------------------------------------
# 2) COVERAGE heatmap (simplified trends × products) — presence (1) vs absence (0)
# ----------------------------------------------------------------------
df_cov = df_presence_simple(trend_order=[t for t in sorted_trends], product_order=product_order)
# Rename coverage columns to display (Title Case)
df_cov = df_cov.rename(columns=prod_display_map)
coverage_legend = (
    "Y-axis grouped into: (1) Migration Complexity, (2) Documentation & Self-Service Gaps, "
    "(3) Feature & Performance Needs, (4) Miscellaneous. Cells show presence (1) or absence (0) of each simplified trend."
)

png2, pdf2 = make_names("02_coverage_heatmap")
plot_heatmap_grouped(
    df_cov,
    title="Coverage heatmap - Trend Drill-Down",
    fname_png=png2, fname_pdf=pdf2,
    xlabel="Products", ylabel="Trends",
    cmap="Blues", vmin=0, vmax=1,
    band_spans=band_spans, separators=separators,
    footnote=coverage_legend,
    dpi=340,
)

# ----------------------- END -----------------------
