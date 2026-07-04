import json
import os
import sys


def _handle(request: dict) -> dict:
    cmd = request.get("cmd")
    if cmd == "fetch":
        from conic.datasets import fetch_dataset

        fetch_dataset(request["source"], request.get("test_type", "all"))
        return {"status": "ok"}
    return {"status": "error", "message": f"unknown command {cmd!r}"}


def main() -> None:
    channel = sys.stdout

    with open(os.devnull, "w") as sink:
        sys.stdout = sink

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                response = _handle(json.loads(line))
            except Exception as error:
                response = {"status": "error", "message": str(error)}
            channel.write(json.dumps(response) + "\n")
            channel.flush()


if __name__ == "__main__":
    main()
