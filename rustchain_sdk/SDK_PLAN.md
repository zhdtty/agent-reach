# RustChain Python SDK Plan

## Goal
Build `rustchain` Python package for RustChain public API with sync/async support, typed exceptions, README examples, and 20+ tests.

## Core API
- client.health()
- client.epoch()
- client.miners()
- client.balance(wallet_id)
- client.transfer(from_, to, amount, signature)
- client.attestation_status(miner_id)
- client.explorer.blocks()
- client.explorer.transactions()

## Architecture
- `rustchain/client.py` sync wrapper
- `rustchain/async_client.py` async client
- `rustchain/explorer.py` explorer helpers
- `rustchain/models.py` typed dataclasses
- `rustchain/exceptions.py` typed errors
- `rustchain/cli.py` optional CLI bonus

## Stack
- `httpx` for sync + async
- `pydantic` optional, otherwise dataclasses + typing
- `pytest` for tests

## Milestones
1. Scaffold package
2. Implement base HTTP transport
3. Add public methods
4. Add typed errors/models
5. Write tests
6. Add README + CLI bonus
