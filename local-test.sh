#!/bin/bash

set -euo pipefail

export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache}"
export UV_LINK_MODE="${UV_LINK_MODE:-copy}"

uv sync --all-groups
uv run ruff format --check app tests
uv run ruff check app
uv run pytest tests/ -v
