# Data Quality Report — sales

## Run metadata

- **dataset**: sales
- **run_id**: sales_20260113_174910
- **generated_at**: 2026-01-13T17:49:10
- **raw_rows**: 125
- **clean_rows**: 120
- **raw_cols**: 10
- **clean_cols**: 10
- **failed_rules**: 5
- **total_rules**: 6

## Validation results

| Rule | Severity | Status | Failed | Description |
|---|---|---:|---:|---|
| S001_qty_positive | error | FAIL | 2 | qty must be >= 1 |
| S002_unit_price_reasonable | error | FAIL | 5 | unit_price must be between 1,000 and 200,000 |
| S003_order_date_present | error | FAIL | 94 | order_date must be a valid parsed date |
| S004_revenue_consistency | warn | FAIL | 14 | revenue should equal qty * unit_price (tolerance 1 peso) |
| S005_region_not_null | warn | FAIL | 1 | region must not be null |
| S006_order_id_unique | error | PASS | 0 | order_id must be unique after cleaning |

### Failed samples (up to 5 rows per rule)

#### S001_qty_positive — qty must be >= 1 (error)

|   order_id |   customer_id | region   | channel   | product          |   qty |   unit_price |   revenue | order_date          | notes   |
|-----------:|--------------:|:---------|:----------|:-----------------|------:|-------------:|----------:|:--------------------|:--------|
|       1016 |            29 | Oeste    | web       | Café Tradicional |    -1 |         9900 |      9900 | NaT                 |         |
|       1109 |             6 | Norte    | retail    | Café Tradicional |    -1 |        18000 |     72000 | 2025-07-20 00:00:00 |         |

#### S002_unit_price_reasonable — unit_price must be between 1,000 and 200,000 (error)

|   order_id |   customer_id | region   | channel   | product      |   qty |   unit_price |   revenue | order_date          | notes   |
|-----------:|--------------:|:---------|:----------|:-------------|------:|-------------:|----------:|:--------------------|:--------|
|       1004 |             5 | Oeste    | partner   | Café Premium |     7 |      nan     |    122500 | 2025-04-12 00:00:00 |         |
|       1018 |            49 | Bogotá   | web       | Café Premium |     6 |      nan     |     72000 | NaT                 |         |
|       1035 |            14 | Este     | retail    | Cafe Premium |     4 |      nan     |     70000 | NaT                 |         |
|       1062 |             6 | Este     | partner   | Cafe Premium |     1 |        1e+07 |         0 | NaT                 |         |
|       1105 |            15 | Oeste    | partner   | Café Premium |     1 |        1e+07 |     12000 | NaT                 |         |

#### S003_order_date_present — order_date must be a valid parsed date (error)

|   order_id |   customer_id | region   | channel   | product          |   qty |   unit_price |   revenue | order_date   | notes   |
|-----------:|--------------:|:---------|:----------|:-----------------|------:|-------------:|----------:|:-------------|:--------|
|       1002 |            26 | Norte    | partner   | Cafe Premium     |     4 |        15500 |     62000 | NaT          |         |
|       1003 |            39 | Oeste    | partner   | Café Tradicional |     4 |         9900 |     39600 | NaT          |         |
|       1005 |             9 | Centro   | retail    | Cafe Premium     |     1 |        17500 |     17500 | NaT          |         |
|       1006 |            34 | Centro   | web       | Café Premium     |     3 |         9900 |     29700 | NaT          |         |
|       1007 |            27 | Norte    | retail    | Café Tradicional |     7 |        18000 |    126000 | NaT          |         |

#### S004_revenue_consistency — revenue should equal qty * unit_price (tolerance 1 peso) (warn)

|   order_id |   customer_id | region   | channel   | product          |   qty |   unit_price |   revenue | order_date          | notes   |
|-----------:|--------------:|:---------|:----------|:-----------------|------:|-------------:|----------:|:--------------------|:--------|
|       1016 |            29 | Oeste    | web       | Café Tradicional |    -1 |         9900 |    9900   | NaT                 |         |
|       1024 |            30 | Este     | partner   | Café Premium     |     3 |        12000 |      36   | NaT                 |         |
|       1029 |             1 | Centro   | partner   | Café Tradicional |     5 |         9900 |      49.5 | 2025-04-23 00:00:00 |         |
|       1030 |             7 | Oeste    | web       | Café Tradicional |     5 |        12000 |       0   | NaT                 |         |
|       1032 |            34 | Norte    | retail    | Café Tradicional |     6 |        12000 |       0   | NaT                 |         |

#### S005_region_not_null — region must not be null (warn)

|   order_id |   customer_id | region   | channel   | product          |   qty |   unit_price |   revenue | order_date   | notes   |
|-----------:|--------------:|:---------|:----------|:-----------------|------:|-------------:|----------:|:-------------|:--------|
|       1050 |            49 |          | retail    | Cafe Tradicional |     4 |         9900 |     39600 | NaT          |         |

## Column profile (raw)

| column      | dtype          |   null_rate |   distinct | sample_values                                |
|:------------|:---------------|------------:|-----------:|:---------------------------------------------|
| notes       | string         |       0.968 |          2 | Revisar, urgente, urgente                    |
| order_date  | datetime64[ns] |       0.792 |         25 | 2025-02-01, 2025-09-19, 2025-04-12           |
| unit_price  | Float64        |       0.024 |          6 | 17500.0, 18000.0, 15500.0                    |
| region      | string         |       0.016 |          6 | Centro, Norte, Norte                         |
| channel     | string         |       0     |          3 | web, web, partner                            |
| product     | string         |       0     |          4 | Cafe Premium, Cafe Tradicional, Cafe Premium |
| qty         | Int64          |       0     |          8 | 4, 6, 4                                      |
| revenue     | Float64        |       0     |         36 | 70000.0, 108000.0, 62000.0                   |
| customer_id | Int64          |       0     |         46 | 5, 10, 26                                    |
| order_id    | Int64          |       0     |        120 | 1000, 1001, 1002                             |

## Column profile (clean)

| column      | dtype          |   null_rate |   distinct | sample_values                                |
|:------------|:---------------|------------:|-----------:|:---------------------------------------------|
| notes       | string         |  0.966667   |          2 | Revisar, urgente, urgente                    |
| order_date  | datetime64[ns] |  0.783333   |         25 | 2025-02-01, 2025-09-19, 2025-04-12           |
| unit_price  | Float64        |  0.025      |          6 | 17500.0, 18000.0, 15500.0                    |
| region      | string         |  0.00833333 |          6 | Centro, Norte, Norte                         |
| channel     | string         |  0          |          3 | web, web, partner                            |
| product     | string         |  0          |          4 | Cafe Premium, Cafe Tradicional, Cafe Premium |
| qty         | Int64          |  0          |          8 | 4, 6, 4                                      |
| revenue     | Float64        |  0          |         36 | 70000.0, 108000.0, 62000.0                   |
| customer_id | Int64          |  0          |         46 | 5, 10, 26                                    |
| order_id    | Int64          |  0          |        120 | 1000, 1001, 1002                             |

## Artifacts

- Raw input: `/mnt/data/upwork-data-cleaning-pack/data/sample_sales_raw.csv`
- Clean output: `/mnt/data/upwork-data-cleaning-pack/outputs/clean/sales_clean_sales_20260113_174910.csv`
- Log: see `outputs/logs/run_sales_20260113_174910.log`