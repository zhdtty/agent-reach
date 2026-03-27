# rustchain

Python SDK for interacting with RustChain nodes.

## Install

```bash
pip install rustchain
```

## Quickstart

```python
from rustchain import RustChainClient

client = RustChainClient(base_url="https://50.28.86.131", verify=False)

print(client.health())
print(client.epoch())
print(client.miners())
print(client.stats())
print(client.balance("RTC14f06ee294f327f5685d3de5e1ed501cffab33e7"))
```

## Async example

```python
import asyncio
from rustchain import AsyncRustChainClient

async def main():
    client = AsyncRustChainClient(base_url="https://50.28.86.131", verify=False)
    print(await client.health())
    print(await client.epoch())
    await client.aclose()

asyncio.run(main())
```

## CLI

```bash
rustchain balance RTC14f06ee294f327f5685d3de5e1ed501cffab33e7
```

## Notes
- The live API exposes `/api/stats` and `/metrics`; these are used for explorer helper compatibility.
- For local testing, the project currently uses 21 unit tests.
