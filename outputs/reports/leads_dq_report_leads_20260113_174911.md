# Data Quality Report — leads

## Run metadata

- **dataset**: leads
- **run_id**: leads_20260113_174911
- **generated_at**: 2026-01-13T17:49:11
- **raw_rows**: 94
- **clean_rows**: 90
- **raw_cols**: 9
- **clean_cols**: 9
- **failed_rules**: 4
- **total_rules**: 5

## Validation results

| Rule | Severity | Status | Failed | Description |
|---|---|---:|---:|---|
| L001_email_format | error | FAIL | 12 | email must be valid format |
| L002_phone_length | warn | FAIL | 8 | phone must have 10 digits (Colombia mobile standard) |
| L003_created_at_valid | error | FAIL | 54 | created_at must be a valid parsed date |
| L004_score_range | warn | FAIL | 12 | score must be between 0 and 100 |
| L005_lead_id_unique | error | PASS | 0 | lead_id must be unique after cleaning |

### Failed samples (up to 5 rows per rule)

#### L001_email_format — email must be valid format (error)

|   lead_id | email             |      phone | source     | status    | created_at          | city         |   score | notes   |
|----------:|:------------------|-----------:|:-----------|:----------|:--------------------|:-------------|--------:|:--------|
|      5003 | voqkrugmail.com   | 3724949433 | referral   | won       | 2025-08-07 00:00:00 | Bogota       |      36 |         |
|      5019 |                   | 3984601105 | referral   | contacted | NaT                 | Medellín     |      93 |         |
|      5023 | baxcayexample.com | 3110629467 | referral   | contacted | NaT                 | Bogotá       |      64 |         |
|      5048 | nioecrgmail.com   | 3846007560 | google ads | won       | 2025-10-28 00:00:00 | Bogotá       |     109 |         |
|      5053 | qsznklempresa.co  | 3539239997 | referral   | won       | NaT                 | Barranquilla |      19 |         |

#### L002_phone_length — phone must have 10 digits (Colombia mobile standard) (warn)

|   lead_id | email              |    phone | source     | status    | created_at          | city         |   score | notes   |
|----------:|:-------------------|---------:|:-----------|:----------|:--------------------|:-------------|--------:|:--------|
|      5005 | czxqqk@example.com | 33164681 | google ads | new       | 2025-12-03 00:00:00 | Barranquilla |      46 |         |
|      5008 | zehvtz@empresa.co  | 30047125 | facebook   | lost      | 2025-11-03 00:00:00 | Barranquilla |      96 |         |
|      5011 | bcqgwl@example.com | 32629773 | facebook   | contacted | 2025-08-20 00:00:00 | Medellin     |      67 |         |
|      5050 | xeqkis@mail.com    | 32585382 | facebook   | won       | NaT                 | Cartagena    |     nan |         |
|      5056 | gjkhfr@gmail.com   | 35709781 | google ads | new       | NaT                 | Bogota       |      14 |         |

#### L003_created_at_valid — created_at must be a valid parsed date (error)

|   lead_id | email             |      phone | source     | status    | created_at   | city         |   score | notes   |
|----------:|:------------------|-----------:|:-----------|:----------|:-------------|:-------------|--------:|:--------|
|      5002 | eybqgf@mail.com   | 3995610627 | web        | new       | NaT          | Bogotá       |      92 |         |
|      5004 | mrwjnl@gmail.com  | 3120166143 | google ads | new       | NaT          | Barranquilla |      56 |         |
|      5009 | zizgkb@gmail.com  | 3221928085 | web        | contacted | NaT          | Bogota       |      26 |         |
|      5010 | aybjcy@empresa.co | 3657026580 | facebook   | contacted | NaT          | Bogota       |      42 |         |
|      5012 | rkwnju@gmail.com  | 3709640259 | web        | new       | NaT          | Medellin     |      95 |         |

#### L004_score_range — score must be between 0 and 100 (warn)

|   lead_id | email              |      phone | source     | status    | created_at          | city         |   score | notes   |
|----------:|:-------------------|-----------:|:-----------|:----------|:--------------------|:-------------|--------:|:--------|
|      5020 | cubxsl@example.com | 3490512099 | referral   | contacted | NaT                 | Medellín     |     nan |         |
|      5027 | gdudrs@example.com | 3172943936 | google ads | new       | NaT                 | Barranquilla |     109 |         |
|      5033 | lcuxsw@gmail.com   | 3798097434 | referral   | contacted | NaT                 | Bogotá       |     107 |         |
|      5034 | usyxqk@empresa.co  | 3319132488 | referral   | won       | NaT                 | Cartagena    |     102 |         |
|      5048 | nioecrgmail.com    | 3846007560 | google ads | won       | 2025-10-28 00:00:00 | Bogotá       |     109 |         |

## Column profile (raw)

| column     | dtype          |   null_rate |   distinct | sample_values                                       |
|:-----------|:---------------|------------:|-----------:|:----------------------------------------------------|
| notes      | string         |   1         |          0 |                                                     |
| created_at | datetime64[ns] |   0.595745  |         33 | 2025-12-15, 2025-09-02, 2025-08-07                  |
| score      | Float64        |   0.0425532 |         59 | 22.0, 33.0, 92.0                                    |
| email      | string         |   0.0425532 |         86 | qiarft@empresa.co, vqdnlv@mail.com, eybqgf@mail.com |
| source     | string         |   0         |          4 | facebook, facebook, web                             |
| status     | string         |   0         |          4 | won, lost, new                                      |
| city       | string         |   0         |          7 | Barranquilla, Bogotá, Bogotá                        |
| lead_id    | Int64          |   0         |         90 | 5000, 5001, 5002                                    |
| phone      | object         |   0         |         90 | 3711505280, 3835456547, 3995610627                  |

## Column profile (clean)

| column     | dtype          |   null_rate |   distinct | sample_values                                       |
|:-----------|:---------------|------------:|-----------:|:----------------------------------------------------|
| notes      | string         |   1         |          0 |                                                     |
| created_at | datetime64[ns] |   0.6       |         33 | 2025-12-15, 2025-09-02, 2025-08-07                  |
| score      | Float64        |   0.0444444 |         59 | 22.0, 33.0, 92.0                                    |
| email      | string         |   0.0444444 |         86 | qiarft@empresa.co, vqdnlv@mail.com, eybqgf@mail.com |
| source     | string         |   0         |          4 | facebook, facebook, web                             |
| status     | string         |   0         |          4 | won, lost, new                                      |
| city       | string         |   0         |          7 | Barranquilla, Bogotá, Bogotá                        |
| lead_id    | Int64          |   0         |         90 | 5000, 5001, 5002                                    |
| phone      | object         |   0         |         90 | 3711505280, 3835456547, 3995610627                  |

## Artifacts

- Raw input: `/mnt/data/upwork-data-cleaning-pack/data/sample_leads_raw.csv`
- Clean output: `/mnt/data/upwork-data-cleaning-pack/outputs/clean/leads_clean_leads_20260113_174911.csv`
- Log: see `outputs/logs/run_leads_20260113_174911.log`