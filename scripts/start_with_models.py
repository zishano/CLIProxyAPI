"""Start the proxy and export its authenticated model catalog on each launch."""

import datetime
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

import yaml


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "available-models.json"


def save(value):
    with tempfile.NamedTemporaryFile(mode="w", dir=ROOT, encoding="utf-8", delete=False) as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(f.name, OUTPUT)


def main():
    args = sys.argv[1:]
    config_path = "config.yaml"
    for i, arg in enumerate(args):
        if arg in ("-config", "--config"):
            config_path = args[i + 1]
        elif arg.startswith(("-config=", "--config=")):
            config_path = arg.split("=", 1)[1]
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    server = config.get("server", config)
    host = server.get("host") or "127.0.0.1"
    if host in ("0.0.0.0", "::", "[::]"):
        host = "127.0.0.1"
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    scheme = "https" if server.get("tls", {}).get("enable") else "http"
    base = f"{scheme}://{host}:{server.get('port', 8317)}/v1"
    keys = config.get("access", {}).get("api-keys", config.get("api-keys", []))
    if not isinstance(keys, list):
        raise ValueError("Client API keys must be configured in access.api-keys")
    headers = {"Authorization": "Bearer " + keys[0]} if keys else {}
    request = urllib.request.Request(base + "/models", headers=headers)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    snapshot = {
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "base_url": base,
        "status": "starting",
        "note": "Models advertised by /v1/models; upstream availability and quota are not tested.",
        "model_ids": [],
        "data": [],
    }
    save(snapshot)
    child = subprocess.Popen([str(ROOT / "bin/cli-proxy-api"), *args])
    def forward(signum, _frame):
        if child.poll() is None:
            child.send_signal(signum)
    signal.signal(signal.SIGTERM, forward)
    signal.signal(signal.SIGINT, forward)
    try:
        deadline = time.monotonic() + 60
        stable_ids = None
        stable_since = None
        while child.poll() is None and time.monotonic() < deadline:
            try:
                with opener.open(request, timeout=2) as response:
                    data = json.load(response)["data"]
                ids = sorted({item["id"] for item in data})
                snapshot.update(status="ready", model_ids=ids, data=data)
                save(snapshot)
                # Allow authentication files to load before accepting the catalog.
                if ids and ids == stable_ids:
                    if time.monotonic() - stable_since >= 3:
                        print(f"Saved {len(ids)} model IDs to {OUTPUT}", flush=True)
                        break
                else:
                    stable_ids, stable_since = ids, time.monotonic()
            except (urllib.error.URLError, ValueError, KeyError, TypeError):
                pass
            time.sleep(0.5)
        else:
            if snapshot["status"] == "starting":
                snapshot["status"] = "unavailable"
                save(snapshot)
                print("Model catalog unavailable; see proxy logs. Snapshot contains no stale models.", file=sys.stderr)
            else:
                print(f"Saved {len(snapshot['model_ids'])} model IDs to {OUTPUT}", flush=True)
        return child.wait()
    finally:
        if child.poll() is None:
            child.terminate()
            child.wait()


if __name__ == "__main__":
    sys.exit(main())
