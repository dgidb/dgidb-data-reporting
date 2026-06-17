# dgidb_analytics

[![image](https://img.shields.io/pypi/v/dgidb_analytics.svg)](https://pypi.python.org/pypi/dgidb_analytics)
[![image](https://img.shields.io/pypi/l/dgidb_analytics.svg)](https://pypi.python.org/pypi/dgidb_analytics)
[![image](https://img.shields.io/pypi/pyversions/dgidb_analytics.svg)](https://pypi.python.org/pypi/dgidb_analytics)
[![Actions status](https://github.com/dgidb/dgidb_analytics/actions/workflows/checks.yaml/badge.svg)](https://github.com/dgidb/dgidb_analytics/actions/checks.yaml)

<!-- description -->
Short project description
<!-- /description -->



---

## Installation

Install from [PyPI](https://pypi.org/project/dgidb_analytics/):

```shell
python3 -m pip install dgidb_analytics
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
