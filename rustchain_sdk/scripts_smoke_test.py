from rustchain import RustChainClient


def main() -> None:
    client = RustChainClient(base_url="https://50.28.86.131", verify=False)
    print("health:", client.health())
    print("epoch:", client.epoch())
    miners = client.miners()
    print("miners_count:", len(miners) if isinstance(miners, list) else miners)
    print("stats:", client.stats())
    print("openapi_version:", client.openapi().get("info", {}).get("version"))


if __name__ == "__main__":
    main()
