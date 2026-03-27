# Real API Notes

Validated against `https://50.28.86.131/openapi.json` on 2026-03-27.

## Confirmed working endpoints
- `/health`
- `/epoch`
- `/api/miners`
- `/api/stats`
- `/metrics`
- `/balance/{miner_pk}`
- `/openapi.json`
- `/withdraw/history/{miner_pk}`
- `/withdraw/request`

## Observed mismatch with bounty text
Bounty text mentions explorer block/transaction endpoints, but the live OpenAPI currently exposes `/api/stats` and `/metrics` instead of `/api/explorer/blocks` and `/api/explorer/transactions`.

SDK currently maps:
- `explorer.blocks()` -> `/api/stats`
- `explorer.transactions()` -> `/metrics`

This should be called out in PR notes as a live API compatibility choice.
