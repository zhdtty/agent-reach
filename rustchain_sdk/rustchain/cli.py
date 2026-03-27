import argparse
from .client import RustChainClient

def main() -> None:
    parser = argparse.ArgumentParser(prog="rustchain")
    sub = parser.add_subparsers(dest="command")
    bal = sub.add_parser("balance")
    bal.add_argument("wallet")
    args = parser.parse_args()

    client = RustChainClient()
    if args.command == "balance":
        print(client.balance(args.wallet))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
