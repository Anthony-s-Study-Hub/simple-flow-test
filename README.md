# Simple Flow Phase 4 Test Project

This repository is reset by the Phase 4 harness before each scenario.

## Joke teller

Install the project in editable mode, then run the offline CLI:

```powershell
python -m pip install -e .
joke
joke --category programming
joke-teller --count 2
```

The commands select jokes from the bundled local collection. They support the
`general`, `programming`, and `dad` categories, accept a positive `--count`,
and prompt for a whole-number rating from 0 through 5 after each joke. Ratings
are kept only in the current session. The commands do not make network
requests or require an API key. The module form is also available after
installation:

```powershell
python -m simple_flow_test_app.joke_teller --category dad
```
