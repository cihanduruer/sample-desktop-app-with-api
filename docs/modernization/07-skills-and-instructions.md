# Lab 07 — Skills & instructions (steering Copilot)

**Goal:** understand and use the mechanisms that make Copilot follow *your* standards in
*this* repo: **custom instructions**, **path-specific instructions**, **prompt files**, and
a note on **skillsets / Copilot Extensions**.

**Time:** ~20 min

---

## What ships in this repo

```
.github/
  copilot-instructions.md              # repo-wide custom instructions (always in context)
  instructions/
    python-api.instructions.md         # applyTo: src/api/**
    dotnet.instructions.md             # applyTo: **/*.cs
    react.instructions.md              # applyTo: ClientApp/**
  prompts/
    secure-python-api.prompt.md        # a reusable, runnable prompt (mode: agent)
```

### 1. Repo-wide custom instructions — `.github/copilot-instructions.md`
Automatically added to Copilot Chat requests for this repo. Ours tells Copilot what the
project is, that `BAD:`-tagged code is intentional, and the priorities (security first,
async all the way, `decimal` money, fix N+1/O(n²), keep it runnable).

### 2. Path-specific instructions — `.github/instructions/*.instructions.md`
Each file has a YAML `applyTo` glob and only applies to matching files. So when you edit
`src/api/app.py`, the *Python* rules apply (parameterized SQL, hashing); when you edit a
`.cs` file, the *.NET* rules apply (no `.Result`, `IHttpClientFactory`, `decimal`).

### 3. Prompt files — `.github/prompts/*.prompt.md`
Reusable, parameterizable prompts you can run on demand (VS Code: run a prompt file from the
Chat view). `secure-python-api.prompt.md` encapsulates the entire Lab 05 task so anyone can
re-run it consistently.

### 4. Skillsets / Copilot Extensions (concept)
Beyond text instructions, **skillsets** and **Copilot Extensions** let Copilot call your own
tools/APIs (e.g. an internal "order service" skill). Out of scope to build here, but mention:
they extend Copilot with custom **skills** the agent can invoke. See the GitHub docs on
building Copilot Extensions/skillsets.

## Exercise — see instructions change behavior

1. **Baseline:** in a `.cs` file, ask Copilot: *"add a method that fetches `/orders` from the
   Python API."* Note whether it uses `new HttpClient()` and `.Result`.
2. **With instructions:** because `dotnet.instructions.md` says "async all the way /
   `IHttpClientFactory`," Copilot should now produce an `async Task` method using a typed
   client. 
3. **Toggle test:** temporarily rename `dotnet.instructions.md` (so it doesn't apply), ask
   again, and compare. Restore it afterwards.
4. Repeat in `src/api/app.py`: ask for a new query and watch it default to **parameterized**
   SQL because of `python-api.instructions.md`.

## Authoring tips
- Keep instructions **short, imperative, and specific** ("money is `decimal`", not essays).
- Use `applyTo` to avoid cross-talk between tiers (Python rules shouldn't reach `.cs`).
- Put genuinely repo-wide context in `copilot-instructions.md`; put tier rules in
  `instructions/`.
- Turn frequently-repeated tasks into **prompt files** so the whole class runs the same thing.

## Talking points
- Instructions are how you encode **team standards** so every suggestion starts closer to
  "right."
- This is the cheapest, highest-leverage Copilot customization — no extension to build.
- It composes with agent mode (Labs 05/06): the agent obeys these rules while it works.
