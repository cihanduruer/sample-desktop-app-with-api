---
mode: agent
description: Find and fix all SQL injection in the Python API and hash passwords.
---

# Secure the Python API

Work in `src/api`. Do all of the following, then build/run to verify:

1. Replace every SQL statement that is built with an f-string, `%` formatting, or `+`
   concatenation with a **parameterized query** (`cursor.execute(sql, params)`). Check
   `/login`, `/customers/{id}`, `/orders/{id}`, `/orders/{id}/status`, and `/search`.
2. Hash passwords with `werkzeug.security.generate_password_hash` on create and
   `check_password_hash` on login. Update the seed data accordingly.
3. Stop returning the `password` column from any endpoint.
4. Remove the hard-coded admin backdoor in `/login`.
5. Add input validation and return correct HTTP status codes (400/401/404), not always 200.

After editing: delete `src/api/orders.db`, restart the app, and confirm `/health`,
`/orders`, and a valid `/login` work. Summarize what changed and why each change removes a
specific vulnerability.
