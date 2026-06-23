# dgidb_analytics

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
