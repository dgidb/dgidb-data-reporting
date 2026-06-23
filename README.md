# dgidb-report

Generate crude diffs between versioned DGIdb databases.

## Usage

Ingest a previous, complete release to use as a benchmark:

```console
% dgidb-report ingest --postgres-dsn postgresql://postgres@localhost:5432/dgidb_2024_12 --snapshot-name='2024_12' dgidb_analytics.db
% dgidb-report save-snapshot dgidb_analytics.db '2024_12'
```

Then ingest a candidate release:
```console
% dgidb-report ingest --postgres-dsn postgresql://postgres@localhost:5432/dgidb --snapshot-name='2026_06' dgidb_analytics.db
```

Finally, generate a report:

```console
% dgidb-report dgidb_analytics.db '2026_06'
Latest release snapshot: 2024_12
Status    Scope    Source               Metric                                        Previous    Current  Delta    % Change
--------  -------  -------------------  ------------------------------------------  ----------  ---------  -------  ----------
DROP      global   -                    drug_applications                                 9838       8815  -1023    -10.4%
DROP      global   -                    drug_approval_ratings                            13332      12453  -879     -6.6%
DROP      global   -                    drugs                                            39581      27628  -11953   -30.2%
GAIN      source   CIViC                gene_claims                                        706        732  26       3.7%
GAIN      source   CIViC                interaction_claims                                1096       1182  86       7.8%
GAIN      source   CKB-CORE             gene_claims                                         50         51  1        2.0%
GAIN      source   CKB-CORE             interaction_claim_attributes                     16558      16559  1        0.0%
GAIN      source   CKB-CORE             interaction_claims                                2050       2051  1        0.0%
```

---

## Development

Clone the repo and create a virtual environment:

```shell
git clone https://github.com/dgidb/dgidb_analytics
cd dgidb_analytics
python3 -m virtualenv venv
source venv/bin/activate
```

Install development dependencies and `prek`:

```shell
python3 -m pip install -e '.[dev,tests]'
prek install
```

Check style with `ruff`:

```shell
python3 -m ruff format . && python3 -m ruff check --fix .
```

Run tests with `pytest`:

```shell
pytest
```
