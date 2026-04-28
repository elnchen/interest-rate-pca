# Interest Rate PCA

This project downloads yield-curve data for U.S. Treasuries, euro-area government bonds, and Japanese government bonds, aligns common tenors, runs PCA on weekly yield changes, and writes both tables and plain-English component interpretations.

## Markets and tenors

The default common-tenor set is:

`2Y, 5Y, 10Y, 20Y, 30Y`

Those tenors exist across the three selected regions and are long enough to capture the usual level, slope, and curvature behavior.

## Data sources

| Region | Source used by the pipeline | Notes |
| --- | --- | --- |
| United States | U.S. Department of the Treasury, Daily Treasury Par Yield Curve Rates: https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve | Official Treasury par curve table. The script pages through the Treasury HTML table because the CSV endpoint may reject direct automated downloads. |
| Euro area | ECB Data Portal API, Financial market data - yield curve, all euro-area government bonds, spot rates: `YC.B.U2.EUR.4F.G_N_C.SV_C_YM.SR_*` | Official ECB daily estimated euro-area government-bond spot curve. |
| Japan | FetchSeries workbook for "Japan constant-maturity government-bond yield curve (Ministry of Finance)": https://www.fetchseries.com/interest-rates/japan-constant-maturity-government-bond-yield-curve-ministry-of-finance/ | FetchSeries is the downloadable provider; the dataset metadata identifies Japan's Ministry of Finance as the source. |

## Method

1. Download raw data into `data/raw/`.
2. Convert each curve into a wide daily yield table.
3. Align all markets to Friday weekly observations using the last available quote in each week.
4. Compute weekly yield changes in basis points.
5. Standardize each feature and run PCA.
6. Run separate regional PCAs and one global PCA over all region-tenor features.

PCA is performed on changes, not yield levels, because level series are highly persistent. Standardization makes the component patterns comparable across regions and tenors.

## Outputs

| Path | Description |
| --- | --- |
| `data/raw/` | Downloaded source files plus standardized raw CSV extracts. |
| `data/processed/aligned_weekly_yields.csv` | Friday-aligned weekly yield levels. |
| `data/processed/weekly_yield_changes_bps.csv` | PCA input: weekly yield changes in basis points. |
| `results/pca_explained_variance.csv` | Explained variance by scope and component. |
| `results/pca_loadings.csv` | Component weights for every retained PCA. |
| `results/pca_scores.csv` | Weekly component score history. |
| `results/component_interpretations.csv` | Structured interpretation for each retained component. |
| `results/component_interpretation.md` | Human-readable report. |
| `figures/` | Variance and loading plots. |

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_pipeline.py
```

To change the number of components:

```bash
python scripts/run_pipeline.py --components 5
```

