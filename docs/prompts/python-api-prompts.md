# Prompts — Python Flask API (`src/api`)

Copy-paste prompts for modernizing the Python API. Prefer **Agent mode** for multi-step
tasks. Always review the diff and run the verify step.

## Security — SQL injection & passwords
> Secure `src/api/app.py` and `database.py`. Replace every SQL statement built with
> f-strings, `%`, or `+` with **parameterized queries** (`cursor.execute(sql, params)`).
> Hash passwords using `werkzeug.security` (`generate_password_hash`/`check_password_hash`)
> on customer creation and verify on `/login`; update the seed data; remove the hard-coded
> admin backdoor; and stop returning the `password` column anywhere. After changes, delete
> `orders.db`, restart, and confirm `/orders` and a valid `/login` work.

> Move the hard-coded secrets (`API_KEY`, signing keys) out of source into environment
> variables read via `os.environ`, and document them in the README.

## Correctness — error handling & status codes
> Replace bare `except:` blocks that swallow errors and return HTTP 200. Add input
> validation and return proper status codes (400 for bad input, 401 for bad credentials,
> 404 when not found, 500 on server error). Use Flask error handlers for consistency.

## Data model
> Add real schema constraints in `database.py`: primary keys, `NOT NULL`, **foreign keys**
> (`orders.customer_id → customers.id`, `order_items.order_id → orders.id`,
> `order_items.product_id → products.id`), and indexes on the FK columns. Store money as
> integer cents or `NUMERIC` and round responses to 2 decimals. Enable
> `PRAGMA foreign_keys = ON`.

## Performance — N+1 & pagination
> Rewrite `GET /orders` to avoid the N+1 query pattern: fetch orders, customers and items in
> a small number of queries (e.g. a JOIN or grouped lookups) and compute totals in SQL. Add
> `limit`/`offset` pagination with sensible defaults and a total count.

> Remove the artificial `time.sleep` in `/reports/revenue` and compute the totals with a
> single aggregate SQL query (`SUM(quantity*unit_price)` grouped by status).

## Concurrency & config
> Replace the single global SQLite connection (`check_same_thread=False`) with a per-request
> connection (Flask `g` + teardown) or a connection pool. Disable `debug=True` for non-dev
> and read host/port/debug from environment.

## Tests
> Add a `pytest` suite under `src/api/tests` covering `/login` (valid + invalid),
> `/orders` (list + pagination), and an injection attempt that must now fail safely. Add
> `pytest` to `requirements.txt` and run it.

## CORS
> Restrict CORS to the known web origins (`http://localhost:5173`, `http://localhost:5080`)
> instead of `*`, and don't combine credentials with a wildcard origin.
