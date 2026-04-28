# Interest Rate PCA Component Interpretation

Generated: 2026-04-28

## Sample

- Weekly aligned yield levels: 2006-02-10 to 2026-04-24.
- Weekly yield changes used in PCA: 2006-02-17 to 2026-04-24.
- Observations: 1,053.
- Features: 15 region-tenor series.

The PCA input is weekly yield changes in basis points, standardized feature by feature.

## Explained Variance

- US: PC1 85.5%, PC2 12.5%, PC3 1.5%, PC4 0.3%, PC5 0.2%. Top retained cumulative share: 100.0%.
- EA: PC1 77.0%, PC2 16.0%, PC3 5.3%, PC4 1.6%, PC5 0.2%. Top retained cumulative share: 100.0%.
- JP: PC1 72.0%, PC2 20.9%, PC3 4.7%, PC4 1.4%, PC5 0.9%. Top retained cumulative share: 100.0%.
- Global: PC1 50.6%, PC2 16.1%, PC3 11.7%, PC4 8.0%, PC5 5.5%. Top retained cumulative share: 91.9%.

## Component Interpretations

### United States

- **PC1 (level, 85.5%)**: PC1 is mainly a level factor. A positive score means broadly higher weekly yield changes across the United States curve. It explains 85.5% of standardized weekly-change variance. Positive side: US 10Y, US 20Y, US 5Y, US 30Y. Negative side: none.
- **PC2 (slope, 12.5%)**: PC2 is mainly a slope factor. A positive score raises the long-end exposures relative to the short-end exposures, so it behaves like a steepening move. It explains 12.5% of standardized weekly-change variance. Positive side: US 30Y, US 20Y, US 10Y. Negative side: US 2Y, US 5Y.
- **PC3 (curvature, 1.5%)**: PC3 is mainly a curvature factor. A positive score moves the belly of the curve against the wings, similar to a butterfly move. It explains 1.5% of standardized weekly-change variance. Positive side: US 2Y, US 30Y, US 20Y. Negative side: US 5Y, US 10Y.
- **PC4 (slope, 0.3%)**: PC4 is mainly a slope factor. A positive score raises the long-end exposures relative to the short-end exposures, so it behaves like a steepening move. It explains 0.3% of standardized weekly-change variance. Positive side: US 10Y, US 2Y, US 20Y. Negative side: US 5Y, US 30Y.
- **PC5 (curvature, 0.2%)**: PC5 is mainly a curvature factor. A positive score moves the belly of the curve against the wings, similar to a butterfly move. It explains 0.2% of standardized weekly-change variance. Positive side: US 30Y, US 10Y. Negative side: US 20Y, US 5Y, US 2Y.

### Euro area

- **PC1 (level, 77.0%)**: PC1 is mainly a level factor. A positive score means broadly higher weekly yield changes across the Euro area curve. It explains 77.0% of standardized weekly-change variance. Positive side: EA 10Y, EA 20Y, EA 5Y, EA 30Y. Negative side: none.
- **PC2 (slope, 16.0%)**: PC2 is mainly a slope factor. A positive score raises the long-end exposures relative to the short-end exposures, so it behaves like a steepening move. It explains 16.0% of standardized weekly-change variance. Positive side: EA 30Y, EA 20Y. Negative side: EA 2Y, EA 5Y, EA 10Y.
- **PC3 (curvature, 5.3%)**: PC3 is mainly a curvature factor. A positive score moves the belly of the curve against the wings, similar to a butterfly move. It explains 5.3% of standardized weekly-change variance. Positive side: EA 10Y, EA 5Y, EA 20Y. Negative side: EA 2Y, EA 30Y.
- **PC4 (curvature, 1.6%)**: PC4 is mainly a curvature factor. A positive score moves the belly of the curve against the wings, similar to a butterfly move. It explains 1.6% of standardized weekly-change variance. Positive side: EA 20Y, EA 2Y, EA 10Y. Negative side: EA 5Y, EA 30Y.
- **PC5 (localized, 0.2%)**: PC5 is a more localized residual factor. It is driven most by EA 10Y, EA 30Y, EA 2Y, offset against EA 20Y, EA 5Y. It explains 0.2% of standardized weekly-change variance. Positive side: EA 10Y, EA 30Y, EA 2Y. Negative side: EA 20Y, EA 5Y.

### Japan

- **PC1 (level, 72.0%)**: PC1 is mainly a level factor. A positive score means broadly higher weekly yield changes across the Japan curve. It explains 72.0% of standardized weekly-change variance. Positive side: JP 10Y, JP 5Y, JP 20Y, JP 30Y. Negative side: none.
- **PC2 (slope, 20.9%)**: PC2 is mainly a slope factor. A positive score raises the long-end exposures relative to the short-end exposures, so it behaves like a steepening move. It explains 20.9% of standardized weekly-change variance. Positive side: JP 30Y, JP 20Y. Negative side: JP 2Y, JP 5Y, JP 10Y.
- **PC3 (curvature, 4.7%)**: PC3 is mainly a curvature factor. A positive score moves the belly of the curve against the wings, similar to a butterfly move. It explains 4.7% of standardized weekly-change variance. Positive side: JP 10Y, JP 5Y. Negative side: JP 2Y, JP 30Y, JP 20Y.
- **PC4 (slope, 1.4%)**: PC4 is mainly a slope factor. A positive score raises the long-end exposures relative to the short-end exposures, so it behaves like a steepening move. It explains 1.4% of standardized weekly-change variance. Positive side: JP 10Y, JP 2Y, JP 20Y. Negative side: JP 5Y, JP 30Y.
- **PC5 (localized, 0.9%)**: PC5 is a more localized residual factor. It is driven most by JP 20Y, JP 5Y, offset against JP 30Y, JP 10Y, JP 2Y. It explains 0.9% of standardized weekly-change variance. Positive side: JP 20Y, JP 5Y. Negative side: JP 30Y, JP 10Y, JP 2Y.

### Global

- **PC1 (level, 50.6%)**: PC1 is mainly a level factor. A positive score means broadly higher weekly yield changes across the global curve set. It explains 50.6% of standardized weekly-change variance. Positive side: US 10Y, US 20Y, US 5Y, US 30Y. Negative side: none.
- **PC2 (regional spread, 16.1%)**: PC2 is mainly a regional spread factor. A positive score separates the strongest positive regional loadings from the negative regional loadings. It explains 16.1% of standardized weekly-change variance. Positive side: JP 5Y, JP 10Y, JP 20Y, JP 2Y. Negative side: EA 10Y, EA 5Y, EA 20Y, EA 2Y.
- **PC3 (regional spread, 11.7%)**: PC3 is mainly a regional spread factor. A positive score separates the strongest positive regional loadings from the negative regional loadings. It explains 11.7% of standardized weekly-change variance. Positive side: US 20Y, US 10Y, US 30Y, US 5Y. Negative side: EA 2Y, EA 5Y, EA 20Y, EA 10Y.
- **PC4 (slope, 8.0%)**: PC4 is mainly a slope factor. A positive score raises the long-end exposures relative to the short-end exposures, so it behaves like a steepening move. It explains 8.0% of standardized weekly-change variance. Positive side: JP 30Y, JP 20Y, EA 30Y, EA 20Y. Negative side: JP 2Y, US 2Y, JP 5Y, EA 2Y.
- **PC5 (localized, 5.5%)**: PC5 is a more localized residual factor. It is driven most by EA 30Y, JP 2Y, EA 20Y, JP 5Y, offset against EA 2Y, JP 30Y, JP 20Y, US 2Y. It explains 5.5% of standardized weekly-change variance. Positive side: EA 30Y, JP 2Y, EA 20Y, JP 5Y. Negative side: EA 2Y, JP 30Y, JP 20Y, US 2Y.

## Reading the signs

PCA signs are arbitrary, so the pipeline orients each component to make the main level or long-end exposure positive where possible. A positive score therefore follows the interpretation text, but flipping all signs would not change the statistical factor.
