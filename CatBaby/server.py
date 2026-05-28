import argparse
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCAL_DEPS = os.path.join(PROJECT_ROOT, ".deps")
if os.path.isdir(LOCAL_DEPS):
    sys.path.insert(0, LOCAL_DEPS)

from catbaby.http_server import run_server  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="CatBaby local deal monitor")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    run_server(PROJECT_ROOT, args.host, args.port)


if __name__ == "__main__":
    main()
