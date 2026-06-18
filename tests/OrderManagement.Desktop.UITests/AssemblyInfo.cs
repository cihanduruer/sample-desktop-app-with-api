// UI automation tests must not run in parallel — only one app window is driven at a time.
[assembly: Xunit.CollectionBehavior(DisableTestParallelization = true)]
