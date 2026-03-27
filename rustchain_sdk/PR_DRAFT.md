# PR Draft for RustChain Python SDK

## Summary
Implements a Python SDK for RustChain with:
- sync + async clients
- typed exception layer
- CLI entrypoint (`rustchain balance <wallet>`)
- README quickstart
- 20+ unit tests

## Notes on live API compatibility
The bounty text references explorer endpoints that do not appear in the live OpenAPI at `https://50.28.86.131/openapi.json`.
To stay compatible with the live node, this SDK maps explorer helper methods to currently exposed endpoints:
- `explorer.blocks()` -> `/api/stats`
- `explorer.transactions()` -> `/metrics`

## Wallet
RTC wallet address: `RTC0b882cafcc7748c4be955e5503d33e7de38fed01`

## Validation
- 21 tests passing locally
- live endpoint smoke test performed against production API
