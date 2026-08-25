# Simple Flow Phase 4 Test Project

This repository is reset by the Phase 4 harness before each scenario.

## Joke teller

Install the project in editable mode, then run the offline CLI:

```powershell
python -m pip install -e .
joke
joke --category programming
```

The command selects one joke from the bundled local collection. It supports
the `general`, `programming`, and `dad` categories and does not make network
requests or require an API key. The module form is also available after
installation:

```powershell
python -m simple_flow_test_app.joke_teller --category dad
```
