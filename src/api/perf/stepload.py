"""Stepped (staged) load shape for the Order Management API.

Reuses the tasks defined in ``locustfile.OrderManagementUser`` but drives a stepped
ramp instead of a flat user count: start at ``STEP_USERS`` and add ``STEP_USERS`` more
every ``STEP_TIME`` seconds, until ``RUN_TIME`` is reached.

Defaults model the requested profile: **+10 users every 5 seconds for 3 minutes**.

Run (from ``src/api``)::

    .\\.venv\\Scripts\\locust -f perf\\stepload.py --host http://localhost:5001 \\
        --headless --csv perf\\step_results --html perf\\step_report.html

The ``LoadTestShape`` controls the user count and run duration, so ``-u``/``-r``/``-t``
are ignored. Override the profile with environment variables: ``STEP_USERS``,
``STEP_TIME``, ``SPAWN_RATE``, ``RUN_TIME``.
"""
from __future__ import annotations

import os

from locust import LoadTestShape

# Re-export the user behavior so this file is a self-contained locustfile.
from locustfile import OrderManagementUser  # noqa: F401


class StepLoadShape(LoadTestShape):
    """Add a fixed batch of users at fixed intervals for a fixed duration."""

    step_users = int(os.environ.get("STEP_USERS", 10))
    step_time = int(os.environ.get("STEP_TIME", 5))
    spawn_rate = int(os.environ.get("SPAWN_RATE", 10))
    run_time = int(os.environ.get("RUN_TIME", 180))

    def tick(self):
        elapsed = self.get_run_time()
        if elapsed > self.run_time:
            return None

        completed_steps = int(elapsed // self.step_time)
        target_users = self.step_users * (completed_steps + 1)
        return target_users, self.spawn_rate
