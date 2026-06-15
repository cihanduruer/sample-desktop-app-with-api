---
applyTo: "src/api/**"
---

# Instructions for the Python Flask API

This is the authoritative data service. When editing files under `src/api`:

- Use **parameterized queries** (`cursor.execute(sql, params)`) — never f-strings or
  `%`/`+` string building in SQL. There are several planted SQL-injection sites.
- Never return or store **plaintext passwords**. Hash with `bcrypt`/`werkzeug.security`.
  Remove the hard-coded admin backdoor.
- Add **input validation** and return correct HTTP status codes (400/401/404/500), not
  always 200.
- Open a connection **per request** (or use a pooled, thread-safe approach); the current
  global `check_same_thread=False` connection is a bug.
- Add **pagination** to list endpoints and fix the **N+1** query patterns.
- Do not enable `debug=True` or bind `0.0.0.0` in anything resembling production.
- Keep `requirements.txt` pinned and minimal.
