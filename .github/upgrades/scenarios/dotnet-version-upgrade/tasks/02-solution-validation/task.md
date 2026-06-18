# 02-solution-validation: Validate build, tests, and document deferred items

Perform the final solution-wide validation after the upgrade. Build the entire solution in Release and Debug as appropriate, run any automated tests present, and smoke-check that both applications start. Record any deferred recommendations for future cleanup (for example, adopting Central Package Management later if the solution grows, and runtime verification of the behavioral `Uri`/`HttpContent` changes).

Scope and assessment context: The solution has no incompatible packages and no flagged test failures in assessment, but the 8 behavioral changes are runtime-only and should be exercised. If no test projects exist, validation is a clean build plus a brief manual run note.

**Done when**: the full solution builds cleanly (0 errors, 0 warnings), all existing tests pass (or it is confirmed there are none), and deferred recommendations are recorded.
