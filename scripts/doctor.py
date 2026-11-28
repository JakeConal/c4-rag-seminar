"""Report the Python runtime and test that the study imports succeed."""

import argparse
import importlib.metadata
import importlib.util
import json
import platform
import socket
import sys
from pathlib import Path


PACKAGES = ("torch", "sentence-transformers", "numpy", "transformers", "huggingface-hub", "pyarrow")
HOSTS = ("pypi.org", "download-r2.pytorch.org", "huggingface.co")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit nonzero when the CPU environment fails")
    args = parser.parse_args()

    packages = {}
    for package in PACKAGES:
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = None

    executable = Path(sys.executable)
    if executable.is_relative_to(Path.cwd()):
        executable = executable.relative_to(Path.cwd())
    checks = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "executable": str(executable),
        "virtual_environment": sys.prefix != sys.base_prefix,
        "ensurepip_available": importlib.util.find_spec("ensurepip") is not None,
        "packages": packages,
    }
    imports_ok = False
    if all(packages.values()):
        try:
            import pyarrow.parquet
            import torch
            from sentence_transformers import CrossEncoder, SentenceTransformer

            if torch.version.cuda is not None or torch.version.hip is not None:
                raise RuntimeError("Expected the CPU build of PyTorch")
            checks["cpu_tensor"] = torch.ones(1, device="cpu").item()
            imports_ok = True
            checks["runtime"] = "CPU dependencies imported successfully"
        except Exception as exc:
            checks["runtime"] = f"{type(exc).__name__}: {exc}"
    else:
        checks["runtime"] = "Missing dependencies"

    checks["dns"] = {}
    for host in HOSTS:
        try:
            socket.getaddrinfo(host, 443)
            checks["dns"][host] = "resolved"
        except OSError:
            checks["dns"][host] = "unavailable"

    print(json.dumps(checks, indent=2))
    return int(args.strict and not imports_ok)


if __name__ == "__main__":
    sys.exit(main())
