#!/usr/bin/env python3
"""Download global yield curves and run PCA on weekly yield changes."""

from __future__ import annotations

import argparse
import io
import os
import re
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))

import matplotlib.pyplot as plt  # noqa: E402


TENORS = ["2Y", "5Y", "10Y", "20Y", "30Y"]
TENOR_YEARS = {tenor: int(tenor[:-1]) for tenor in TENORS}
REGION_NAMES = {"US": "United States", "EA": "Euro area", "JP": "Japan"}
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)

US_TREASURY_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/"
    "interest-rates/TextView?type=daily_treasury_yield_curve"
)
ECB_URL_TEMPLATE = (
    "https://data-api.ecb.europa.eu/service/data/YC/"
    "B.U2.EUR.4F.G_N_C.SV_C_YM.SR_{tenor}"
    "?startPeriod=2004-09-06&format=csvdata"
)
JAPAN_FETCHSERIES_XLSX = (
    "https://www.fetchseries.com/interest-rates/"
    "japan-constant-maturity-government-bond-yield-curve-ministry-of-finance/"
    "japan-constant-maturity-government-bond-yield-curve-ministry-of-finance.xlsx"
)


@dataclass(frozen=True)
class ScopeResult:
    variance: pd.DataFrame
    loadings: pd.DataFrame
    scores: pd.DataFrame
    interpretations: pd.DataFrame


def download_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def parse_tenor_year(feature: str) -> int:
    match = re.search(r"_(\d+)Y$", feature)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d+)Y$", feature)
    if match:
        return int(match.group(1))
    raise ValueError(f"Could not parse tenor from {feature}")


def parse_region(feature: str, default: str | None = None) -> str:
    if "_" in feature:
        return feature.split("_", 1)[0]
    if default:
        return default
    return "Curve"


def display_feature(feature: str, default_region: str | None = None) -> str:
    region = parse_region(feature, default_region)
    tenor = f"{parse_tenor_year(feature)}Y"
    return f"{region} {tenor}"


def fetch_us_treasury(raw_dir: Path, max_pages: int = 80) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    seen_page_markers: set[tuple[str, ...]] = set()

    for page in range(max_pages):
        url = US_TREASURY_URL if page == 0 else f"{US_TREASURY_URL}&page={page}"
        html = download_bytes(url)

        tables = pd.read_html(io.BytesIO(html))
        if not tables:
            break
        frame = tables[0]
        if "Date" not in frame.columns:
            break

        marker = tuple(frame["Date"].astype(str).head(5))
        if marker in seen_page_markers:
            break
        seen_page_markers.add(marker)
        frames.append(frame)

        if len(frame) < 300:
            break
        time.sleep(0.1)

    if not frames:
        raise RuntimeError("No U.S. Treasury tables were downloaded.")

    df = pd.concat(frames, ignore_index=True)
    column_map = {"2 Yr": "2Y", "5 Yr": "5Y", "10 Yr": "10Y", "20 Yr": "20Y", "30 Yr": "30Y"}
    missing = [source for source in column_map if source not in df.columns]
    if missing:
        raise RuntimeError(f"Missing U.S. Treasury columns: {missing}")

    out = df[["Date", *column_map.keys()]].rename(columns={"Date": "date", **column_map})
    out["date"] = pd.to_datetime(out["date"], format="%m/%d/%Y")
    for tenor in TENORS:
        out[tenor] = pd.to_numeric(out[tenor], errors="coerce")
    out = out.drop_duplicates("date").sort_values("date").set_index("date")
    out.to_csv(raw_dir / "us_treasury_curve.csv")
    return out[TENORS]


def fetch_ecb(raw_dir: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for tenor in TENORS:
        data = download_bytes(ECB_URL_TEMPLATE.format(tenor=tenor))
        (raw_dir / f"ecb_euro_area_spot_{tenor}.csv").write_bytes(data)
        raw = pd.read_csv(io.BytesIO(data))
        if not {"TIME_PERIOD", "OBS_VALUE"}.issubset(raw.columns):
            raise RuntimeError(f"Unexpected ECB CSV schema for {tenor}.")
        series = raw[["TIME_PERIOD", "OBS_VALUE"]].rename(
            columns={"TIME_PERIOD": "date", "OBS_VALUE": tenor}
        )
        series["date"] = pd.to_datetime(series["date"])
        series[tenor] = pd.to_numeric(series[tenor], errors="coerce")
        frames.append(series.set_index("date")[[tenor]])

    out = pd.concat(frames, axis=1).sort_index()
    out.to_csv(raw_dir / "ecb_euro_area_spot_curve.csv")
    return out[TENORS]


def fetch_japan(raw_dir: Path) -> pd.DataFrame:
    workbook = download_bytes(JAPAN_FETCHSERIES_XLSX)
    workbook_path = raw_dir / "japan_mof_fetchseries_yield_curve.xlsx"
    workbook_path.write_bytes(workbook)

    raw = pd.read_excel(workbook_path, sheet_name="Nominal yields")
    raw = raw.iloc[1:].copy()

    date_col = "Unnamed: 1"
    if date_col not in raw.columns:
        raise RuntimeError("Unexpected Japan workbook schema: date column not found.")

    column_map: dict[str, str] = {}
    for column in raw.columns:
        match = re.match(r"(\d+)-year yield", str(column))
        if not match:
            continue
        tenor = f"{match.group(1)}Y"
        if tenor in TENORS:
            column_map[column] = tenor

    missing = [tenor for tenor in TENORS if tenor not in column_map.values()]
    if missing:
        raise RuntimeError(f"Missing Japan tenor columns: {missing}")

    out = raw[[date_col, *column_map.keys()]].rename(columns={date_col: "date", **column_map})
    out["date"] = pd.to_datetime(out["date"])
    for tenor in TENORS:
        out[tenor] = pd.to_numeric(out[tenor], errors="coerce")
    out = out.drop_duplicates("date").sort_values("date").set_index("date")
    out.to_csv(raw_dir / "japan_mof_fetchseries_curve.csv")
    return out[TENORS]


def align_curves(us: pd.DataFrame, ea: pd.DataFrame, jp: pd.DataFrame, processed_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    combined = pd.concat(
        [
            us.add_prefix("US_"),
            ea.add_prefix("EA_"),
            jp.add_prefix("JP_"),
        ],
        axis=1,
    ).sort_index()
    combined.index.name = "date"
    combined.to_csv(processed_dir / "combined_daily_yields.csv")

    weekly = combined.resample("W-FRI").last().dropna(how="any")
    # Resampling early in a week labels the partial bucket with the coming Friday.
    # Drop that incomplete bucket so generated samples never carry future dates.
    weekly = weekly[weekly.index <= combined.index.max()]
    weekly.index.name = "week"
    changes_bps = weekly.diff().dropna(how="any") * 100.0
    changes_bps.index.name = "week"

    weekly.to_csv(processed_dir / "aligned_weekly_yields.csv")
    changes_bps.to_csv(processed_dir / "weekly_yield_changes_bps.csv")
    return combined, weekly, changes_bps


def orient_component(loadings: np.ndarray, features: list[str]) -> int:
    abs_sum = float(np.abs(loadings).sum())
    total = float(loadings.sum())
    if abs_sum == 0:
        return 1
    if abs(total) > 0.2 * abs_sum:
        return 1 if total >= 0 else -1

    tenors = np.array([parse_tenor_year(feature) for feature in features])
    short = float(loadings[tenors <= 5].mean())
    long = float(loadings[tenors >= 10].mean())
    if abs(long - short) > 0.05:
        return 1 if (long - short) >= 0 else -1

    largest = float(loadings[np.argmax(np.abs(loadings))])
    return 1 if largest >= 0 else -1


def classify_component(loadings: pd.DataFrame, scope: str) -> str:
    values = loadings["loading"].to_numpy()
    mean_abs = float(np.abs(values).mean())
    positive_share = float((values > 0).mean())
    negative_share = float((values < 0).mean())

    if max(positive_share, negative_share) >= 0.8 and abs(values.mean()) >= 0.35 * mean_abs:
        return "level"

    region_means = loadings.groupby("region")["loading"].mean()
    if scope == "Global" and len(region_means) > 1:
        if region_means.max() > 0 and region_means.min() < 0:
            if (region_means.max() - region_means.min()) >= 0.8 * mean_abs:
                return "regional spread"

    short = float(loadings.loc[loadings["tenor_years"] <= 5, "loading"].mean())
    long = float(loadings.loc[loadings["tenor_years"] >= 10, "loading"].mean())
    if short * long < 0 and abs(long - short) >= 0.8 * mean_abs:
        return "slope"

    belly_mask = loadings["tenor_years"].isin([5, 10])
    wing_mask = loadings["tenor_years"].isin([2, 20, 30])
    belly = float(loadings.loc[belly_mask, "loading"].mean())
    wings = float(loadings.loc[wing_mask, "loading"].mean())
    if belly * wings < 0 and abs(belly - wings) >= 0.7 * mean_abs:
        return "curvature"

    return "localized"


def describe_component(loadings: pd.DataFrame, scope: str, component: str, variance_ratio: float) -> dict[str, str | float]:
    positive = loadings[loadings["loading"] > 0].sort_values("loading", ascending=False).head(4)
    negative = loadings[loadings["loading"] < 0].sort_values("loading").head(4)

    positive_names = ", ".join(display_feature(feature, scope if scope != "Global" else None) for feature in positive["feature"])
    negative_names = ", ".join(display_feature(feature, scope if scope != "Global" else None) for feature in negative["feature"])
    if not positive_names:
        positive_names = "none"
    if not negative_names:
        negative_names = "none"

    scope_label = "the global curve set" if scope == "Global" else f"the {REGION_NAMES[scope]} curve"
    label = classify_component(loadings, scope)

    if label == "level":
        interpretation = (
            f"{component} is mainly a level factor. A positive score means broadly higher "
            f"weekly yield changes across {scope_label}."
        )
    elif label == "slope":
        interpretation = (
            f"{component} is mainly a slope factor. A positive score raises the long-end "
            f"exposures relative to the short-end exposures, so it behaves like a steepening move."
        )
    elif label == "curvature":
        interpretation = (
            f"{component} is mainly a curvature factor. A positive score moves the belly "
            f"of the curve against the wings, similar to a butterfly move."
        )
    elif label == "regional spread":
        interpretation = (
            f"{component} is mainly a regional spread factor. A positive score separates "
            f"the strongest positive regional loadings from the negative regional loadings."
        )
    else:
        if negative_names == "none":
            interpretation = (
                f"{component} is a more localized residual factor. It is driven most by "
                f"{positive_names}, with no negative loading among the largest retained exposures."
            )
        else:
            interpretation = (
                f"{component} is a more localized residual factor. It is driven most by "
                f"{positive_names}, offset against {negative_names}."
            )

    interpretation += (
        f" It explains {variance_ratio:.1%} of standardized weekly-change variance. "
        f"Positive side: {positive_names}. Negative side: {negative_names}."
    )

    return {
        "label": label,
        "positive_exposures": positive_names,
        "negative_exposures": negative_names,
        "interpretation": interpretation,
    }


def fit_pca_scope(changes_bps: pd.DataFrame, scope: str, features: list[str], n_components: int) -> ScopeResult:
    data = changes_bps[features].dropna()
    scaler = StandardScaler()
    scaled = scaler.fit_transform(data)

    component_count = min(n_components, scaled.shape[1], scaled.shape[0])
    pca = PCA(n_components=component_count)
    scores_array = pca.fit_transform(scaled)
    components = pca.components_.copy()

    for idx in range(component_count):
        sign = orient_component(components[idx], features)
        components[idx] *= sign
        scores_array[:, idx] *= sign

    component_names = [f"PC{idx + 1}" for idx in range(component_count)]

    variance = pd.DataFrame(
        {
            "scope": scope,
            "component": component_names,
            "explained_variance_ratio": pca.explained_variance_ratio_,
            "cumulative_explained_variance": np.cumsum(pca.explained_variance_ratio_),
        }
    )

    loadings = pd.DataFrame(components.T, index=features, columns=component_names)
    loadings = loadings.reset_index(names="feature").melt(
        id_vars="feature", var_name="component", value_name="loading"
    )
    loadings.insert(0, "scope", scope)
    loadings["region"] = loadings["feature"].map(lambda value: parse_region(value, scope if scope != "Global" else None))
    loadings["tenor_years"] = loadings["feature"].map(parse_tenor_year)
    loadings["abs_loading"] = loadings["loading"].abs()

    scores = pd.DataFrame(scores_array, index=data.index, columns=component_names)
    scores.insert(0, "scope", scope)
    scores = scores.reset_index().rename(columns={"index": "week"})

    interpretation_rows = []
    for component in component_names:
        component_loadings = loadings[loadings["component"] == component].copy()
        var_ratio = float(variance.loc[variance["component"] == component, "explained_variance_ratio"].iloc[0])
        description = describe_component(component_loadings, scope, component, var_ratio)
        interpretation_rows.append(
            {
                "scope": scope,
                "component": component,
                "explained_variance_ratio": var_ratio,
                **description,
            }
        )

    interpretations = pd.DataFrame(interpretation_rows)
    return ScopeResult(variance=variance, loadings=loadings, scores=scores, interpretations=interpretations)


def run_all_pcas(changes_bps: pd.DataFrame, n_components: int) -> ScopeResult:
    results: list[ScopeResult] = []
    for region in ["US", "EA", "JP"]:
        features = [f"{region}_{tenor}" for tenor in TENORS]
        results.append(fit_pca_scope(changes_bps, region, features, n_components=len(features)))

    global_features = [f"{region}_{tenor}" for region in ["US", "EA", "JP"] for tenor in TENORS]
    results.append(fit_pca_scope(changes_bps, "Global", global_features, n_components=n_components))

    return ScopeResult(
        variance=pd.concat([result.variance for result in results], ignore_index=True),
        loadings=pd.concat([result.loadings for result in results], ignore_index=True),
        scores=pd.concat([result.scores for result in results], ignore_index=True),
        interpretations=pd.concat([result.interpretations for result in results], ignore_index=True),
    )


def plot_explained_variance(variance: pd.DataFrame, figures_dir: Path) -> None:
    for scope, group in variance.groupby("scope"):
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(group["component"], group["explained_variance_ratio"], color="#33658A")
        ax.plot(group["component"], group["cumulative_explained_variance"], marker="o", color="#D1495B")
        ax.set_ylim(0, 1.02)
        ax.set_ylabel("Variance share")
        ax.set_title(f"{scope} PCA explained variance")
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        fig.savefig(figures_dir / f"{scope.lower()}_explained_variance.png", dpi=160)
        plt.close(fig)


def plot_regional_loadings(loadings: pd.DataFrame, figures_dir: Path) -> None:
    colors = {"PC1": "#2A9D8F", "PC2": "#E76F51", "PC3": "#4C78A8"}
    for scope in ["US", "EA", "JP"]:
        subset = loadings[(loadings["scope"] == scope) & (loadings["component"].isin(["PC1", "PC2", "PC3"]))]
        fig, ax = plt.subplots(figsize=(7, 4))
        for component, group in subset.groupby("component"):
            group = group.sort_values("tenor_years")
            ax.plot(
                group["tenor_years"],
                group["loading"],
                marker="o",
                linewidth=2,
                color=colors.get(component),
                label=component,
            )
        ax.axhline(0, color="#333333", linewidth=0.8)
        ax.set_xticks([2, 5, 10, 20, 30])
        ax.set_xlabel("Tenor in years")
        ax.set_ylabel("Loading")
        ax.set_title(f"{REGION_NAMES[scope]} PCA loadings")
        ax.legend()
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(figures_dir / f"{scope.lower()}_regional_loadings.png", dpi=160)
        plt.close(fig)


def plot_global_heatmap(loadings: pd.DataFrame, figures_dir: Path) -> None:
    subset = loadings[loadings["scope"] == "Global"].copy()
    subset["feature_order"] = subset["region"].map({"US": 0, "EA": 1, "JP": 2}) * 100 + subset["tenor_years"]
    ordered_features = (
        subset[["feature", "feature_order"]]
        .drop_duplicates()
        .sort_values("feature_order")["feature"]
        .tolist()
    )
    matrix = subset.pivot(index="feature", columns="component", values="loading").loc[ordered_features]

    fig, ax = plt.subplots(figsize=(8, 6))
    image = ax.imshow(matrix.values, aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(matrix.shape[1]), labels=matrix.columns)
    ax.set_yticks(range(matrix.shape[0]), labels=matrix.index)
    ax.set_title("Global PCA loadings")
    fig.colorbar(image, ax=ax, label="Loading")
    fig.tight_layout()
    fig.savefig(figures_dir / "global_loadings_heatmap.png", dpi=160)
    plt.close(fig)


def write_markdown_report(
    report_path: Path,
    weekly: pd.DataFrame,
    changes_bps: pd.DataFrame,
    variance: pd.DataFrame,
    interpretations: pd.DataFrame,
) -> None:
    lines: list[str] = []
    lines.append("# Interest Rate PCA Component Interpretation")
    lines.append("")
    lines.append(f"Generated: {datetime.now().date().isoformat()}")
    lines.append("")
    lines.append("## Sample")
    lines.append("")
    lines.append(f"- Weekly aligned yield levels: {weekly.index.min().date()} to {weekly.index.max().date()}.")
    lines.append(f"- Weekly yield changes used in PCA: {changes_bps.index.min().date()} to {changes_bps.index.max().date()}.")
    lines.append(f"- Observations: {len(changes_bps):,}.")
    lines.append(f"- Features: {changes_bps.shape[1]} region-tenor series.")
    lines.append("")
    lines.append("The PCA input is weekly yield changes in basis points, standardized feature by feature.")
    lines.append("")
    lines.append("## Explained Variance")
    lines.append("")
    for scope, group in variance.groupby("scope", sort=False):
        top = group.head(5)
        summary = ", ".join(
            f"{row.component} {row.explained_variance_ratio:.1%}"
            for row in top.itertuples(index=False)
        )
        cumulative = float(top["explained_variance_ratio"].sum())
        lines.append(f"- {scope}: {summary}. Top retained cumulative share: {cumulative:.1%}.")
    lines.append("")
    lines.append("## Component Interpretations")
    lines.append("")
    for scope, group in interpretations.groupby("scope", sort=False):
        title = REGION_NAMES.get(scope, scope)
        lines.append(f"### {title}")
        lines.append("")
        for row in group.itertuples(index=False):
            lines.append(
                f"- **{row.component} ({row.label}, {row.explained_variance_ratio:.1%})**: "
                f"{row.interpretation}"
            )
        lines.append("")
    lines.append("## Reading the signs")
    lines.append("")
    lines.append(
        "PCA signs are arbitrary, so the pipeline orients each component to make the "
        "main level or long-end exposure positive where possible. A positive score "
        "therefore follows the interpretation text, but flipping all signs would not "
        "change the statistical factor."
    )
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(result: ScopeResult, weekly: pd.DataFrame, changes_bps: pd.DataFrame, results_dir: Path, figures_dir: Path) -> None:
    result.variance.to_csv(results_dir / "pca_explained_variance.csv", index=False)
    result.loadings.to_csv(results_dir / "pca_loadings.csv", index=False)
    result.scores.to_csv(results_dir / "pca_scores.csv", index=False)
    result.interpretations.to_csv(results_dir / "component_interpretations.csv", index=False)

    plot_explained_variance(result.variance, figures_dir)
    plot_regional_loadings(result.loadings, figures_dir)
    plot_global_heatmap(result.loadings, figures_dir)
    write_markdown_report(
        results_dir / "component_interpretation.md",
        weekly,
        changes_bps,
        result.variance,
        result.interpretations,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--components", type=int, default=5, help="Retained components for the global PCA.")
    parser.add_argument("--max-us-pages", type=int, default=80, help="Maximum Treasury HTML pages to scan.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    raw_dir = ROOT / "data" / "raw"
    processed_dir = ROOT / "data" / "processed"
    results_dir = ROOT / "results"
    figures_dir = ROOT / "figures"
    for path in [raw_dir, processed_dir, results_dir, figures_dir, ROOT / ".mplconfig"]:
        path.mkdir(parents=True, exist_ok=True)

    print("Downloading U.S. Treasury curve...")
    us = fetch_us_treasury(raw_dir, max_pages=args.max_us_pages)
    print(f"  U.S. rows: {len(us):,}, {us.index.min().date()} to {us.index.max().date()}")

    print("Downloading ECB euro-area curve...")
    ea = fetch_ecb(raw_dir)
    print(f"  Euro-area rows: {len(ea):,}, {ea.index.min().date()} to {ea.index.max().date()}")

    print("Downloading Japan yield curve...")
    jp = fetch_japan(raw_dir)
    print(f"  Japan rows: {len(jp):,}, {jp.index.min().date()} to {jp.index.max().date()}")

    print("Aligning weekly data and computing changes...")
    _, weekly, changes_bps = align_curves(us, ea, jp, processed_dir)
    print(f"  PCA sample: {len(changes_bps):,} weekly changes from {changes_bps.index.min().date()} to {changes_bps.index.max().date()}")

    print("Running PCA...")
    result = run_all_pcas(changes_bps, n_components=args.components)
    write_outputs(result, weekly, changes_bps, results_dir, figures_dir)
    print("Done. See results/component_interpretation.md")


if __name__ == "__main__":
    main()
