# ELM369 Matrix API

This API is a local simulation service. It does not route physical shipments or
move money.

## Run with Docker Compose

Set a non-default Grafana password, then launch the API and monitoring services:

```sh
export GRAFANA_ADMIN_PASSWORD='choose-a-strong-local-password'
docker compose up --build -d
```

The API is available at `http://localhost:8000`, its OpenAPI documentation at
`http://localhost:8000/docs`, Prometheus at `http://localhost:9090`, and Grafana
at `http://localhost:3000`. The API persists simulated transaction ledgers in a
Docker volume. Prometheus scrapes `/metrics` every 15 seconds. Grafana's initial
username defaults to `admin`; set `GRAFANA_ADMIN_USER` to change it.

## Simulation behavior

- `POST /influence` calculates `reach × viral_velocity × (1 + sentiment_delta)`.
  Reach and velocity are non-negative; sentiment delta is in `[-1, 1]`.
- `POST /logistics` uses an illustrative fixed network of Kokomo, Indianapolis,
  Chicago, Detroit, and Cincinnati. Costs are simulation indices, not distance
  or shipping quotes.
- `POST /transaction` calculates `base_amount × (1 + supply_volatility) ×
  (1 + demand_flux)`, rounds the adjusted amount to cents, allocates 1% of that
  adjusted amount to charity (rounded to cents), and persists the ledger in
  SQLite. Both adjustment inputs are in `[-1, 1]`; the base amount must be
  greater than zero and at most `1e12`. This endpoint is not a payment processor.
- `GET /health` reports service status. `GET /metrics` exposes request counts
  and cumulative request duration in Prometheus text format.

Request validation errors return HTTP 422. Unknown logistics nodes return HTTP
400. Configure `ELM369_DB_PATH` to select a different SQLite database path when
running outside Compose.

## Tests

Install the project test extra and run:

```sh
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
```
