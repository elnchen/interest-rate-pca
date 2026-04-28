# Six-Month PCA Factor Forecast

Generated: 2026-04-28

## Method

The forecast uses the first 5 global principal components of standardized weekly yield changes across the U.S., euro-area, and Japan curves. A multi-output ordinary least squares regression predicts next week's PC scores from this week's PC scores. Forecasted PC scores are then mapped back into yield changes and accumulated from the latest observed curve.

- Latest observed weekly curve: 2026-04-24.
- Forecast horizon: 26 weeks, ending 2026-10-23.
- Units: yields are percentage points; changes are basis points.

## Six-Month Endpoint

### United States

| Tenor | Latest yield | Forecast yield | Forecast change |
| --- | ---: | ---: | ---: |
| 2Y | 3.780% | 3.766% | -1.4 bp |
| 5Y | 3.920% | 3.914% | -0.6 bp |
| 10Y | 4.310% | 4.314% | +0.4 bp |
| 20Y | 4.880% | 4.892% | +1.2 bp |
| 30Y | 4.910% | 4.928% | +1.8 bp |

### Euro area

| Tenor | Latest yield | Forecast yield | Forecast change |
| --- | ---: | ---: | ---: |
| 2Y | 2.630% | 2.632% | +0.2 bp |
| 5Y | 2.917% | 2.922% | +0.5 bp |
| 10Y | 3.483% | 3.494% | +1.2 bp |
| 20Y | 4.021% | 4.039% | +1.7 bp |
| 30Y | 4.025% | 4.040% | +1.5 bp |

### Japan

| Tenor | Latest yield | Forecast yield | Forecast change |
| --- | ---: | ---: | ---: |
| 2Y | 1.363% | 1.393% | +3.0 bp |
| 5Y | 1.842% | 1.870% | +2.8 bp |
| 10Y | 2.443% | 2.471% | +2.8 bp |
| 20Y | 3.318% | 3.355% | +3.7 bp |
| 30Y | 3.660% | 3.697% | +3.7 bp |

## In-Sample One-Week Factor Fit

| Component | R^2 | RMSE |
| --- | ---: | ---: |
| PC1 | 0.010 | 2.741 |
| PC2 | 0.010 | 1.548 |
| PC3 | 0.022 | 1.310 |
| PC4 | 0.016 | 1.085 |
| PC5 | 0.008 | 0.899 |
