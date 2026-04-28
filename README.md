# Interest Rate PCA

This project downloads yield-curve data for U.S. Treasuries, euro-area government bonds, and Japanese government bonds, aligns common tenors, runs PCA on weekly yield changes, and here's the generated table and component interpretations.

## Markets and tenors

The default common-tenor set is:

`2Y, 5Y, 10Y, 20Y, 30Y`

Those tenors exist across the three selected regions and are long enough to capture the usual level, slope, and curvature behavior.

## Data sources

| Region | Source used by the pipeline | Notes |
| --- | --- | --- |
| United States | [U.S. Department of the Treasury, Daily Treasury Par Yield Curve Rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve) | Official Treasury par curve table. The script pages through the Treasury HTML table because the CSV endpoint may reject direct automated downloads. |
| Euro area | [ECB Data Portal API yield-curve CSV endpoint](https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_C.SV_C_YM.SR_10Y?startPeriod=2004-09-06&format=csvdata), using `YC.B.U2.EUR.4F.G_N_C.SV_C_YM.SR_*` for each tenor | Official ECB daily estimated euro-area government-bond spot curve. See also the [ECB yield curve methodology](https://data.ecb.europa.eu/methodology/yield-curves). |
| Japan | [FetchSeries workbook for "Japan constant-maturity government-bond yield curve (Ministry of Finance)"](https://www.fetchseries.com/interest-rates/japan-constant-maturity-government-bond-yield-curve-ministry-of-finance/) | FetchSeries is the downloadable provider; the dataset metadata identifies Japan's Ministry of Finance as the source. |

The ECB pipeline downloads one CSV per tenor by replacing `SR_10Y` in the linked example with `SR_2Y`, `SR_5Y`, `SR_10Y`, `SR_20Y`, and `SR_30Y`.

## Method

1. Download raw data into `data/raw/`.
2. Convert each curve into a wide daily yield table.
3. Align all markets to Friday weekly observations using the last available quote in each week.
4. Compute weekly yield changes in basis points.
5. Standardize each feature and run PCA.
6. Run separate regional PCAs and one global PCA over all region-tenor features.
7. Forecast the next 26 weekly curves by fitting a linear regression from current global PC scores to next-week global PC scores, then mapping the forecast scores back into yield changes.

PCA is performed on changes, not yield levels, because level series are highly persistent. Standardization makes the component patterns comparable across regions and tenors.

The six-month forecast is a simple PCA-factor linear model. 

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
| `results/forecast_6m_report.md` | Human-readable six-month forecast report. |
| `results/forecast_6m_weekly_yields.csv` | Forecast yield curves for each future week. |
| `results/forecast_6m_weekly_changes_bps.csv` | Forecast weekly yield changes in basis points. |
| `results/forecast_6m_endpoint.csv` | Latest actual curve versus six-month forecast endpoint. |
| `results/forecast_model_*.csv` | Linear-regression coefficients and in-sample fit diagnostics. |
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

To change the forecast horizon:

```bash
python scripts/run_pipeline.py --forecast-weeks 26
```
