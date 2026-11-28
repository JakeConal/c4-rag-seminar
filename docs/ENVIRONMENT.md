# Measurement environment

The CPU setup uses CPython 3.12 on Linux x86-64 with glibc 2.28 or newer. The test machine exposes four logical CPUs on an Intel Core i5-11400H and 12 GiB of RAM to WSL2. The benchmark uses four PyTorch threads.

- `make setup` obtains the pinned uv 0.9.15 executable and checks the release archive SHA-256. uv creates the local virtual environment, installs the complete hash-locked wheel set in `requirements.txt`, checks dependency consistency, and writes the installed package inventory to `results/environment/requirements.resolved.txt`.
- `requirements.in` records the six direct dependencies. It specifies the official PyTorch 2.8.0 CPU wheel URL and SHA-256 for CPython 3.12 on Linux x86-64.
- `make prepare` resolves the immutable revisions in `config.json`, caches the SciFact inputs and both model snapshots, and writes their file hashes and the prepared data hash to `data/manifest.json`.
- `make doctor` checks package imports and creates a CPU tensor. [environment-check.json](environment-check.json) records the local check.

The initial workspace lacked system pip and ensurepip. The repository-local uv installation creates and manages the virtual environment independently of those modules. The environment and artifact caches live in `.venv/` and `.cache/` and can be regenerated from the pinned inputs.

The initial offline package sync encountered an uncached wheel. Setup completed with the public package indexes enabled, and all 34 installed versions matched the lock. Offline preparation produced 5,183 documents, 12,434 chunks and 300 labeled test queries. A single-pass pilot loaded both models and completed 10 seeded queries in 4 minutes 46 seconds, including corpus embedding and warmup. [Installed package inventory](../results/environment/requirements.resolved.txt) · [Pilot environment and input hashes](../results/pilot-20261121T095719458683Z/environment.json).

The official study then ran from a new clone of source commit `a3d85f5` with a newly created virtual environment and only download caches shared. The documented setup succeeded online, preparation and inference ran offline, and `make study` completed with exit status 0. It recorded five complete paired passes over all 300 queries and a separate vector-only 96-token window comparison. All source/model/data hashes were checked independently. [Full study environment](../results/20261121T122915162545Z/environment.json) · [Fresh-clone transcript](../results/verification/fresh-clone.log) · [Independent review](REVIEW.md).

Release references checked on 2026-11-21. [uv 0.9.15 release](https://github.com/astral-sh/uv/releases/tag/0.9.15) · [PyTorch CPU wheel index](https://download.pytorch.org/whl/cpu/torch/) · [Pinned data and model sources](SOURCES.md).
