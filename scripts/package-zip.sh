#!/usr/bin/env bash
# Package a Decky-compatible plugin zip without Docker (Python-only plugins).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${OUT_DIR:-$ROOT/out}"
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"

cd "$ROOT"
pnpm install --frozen-lockfile 2>/dev/null || pnpm install
pnpm run build

PLUGIN_NAME="$(python3 - <<'PY'
import json
from pathlib import Path
print(json.loads(Path("plugin.json").read_text())["name"])
PY
)"
VERSION="$(python3 - <<'PY'
import json
from pathlib import Path
print(json.loads(Path("package.json").read_text()).get("version", "0.0.0"))
PY
)"
SAFE_NAME="$(echo "$PLUGIN_NAME" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"
if [ -n "${ZIP_BASENAME:-}" ]; then
  ZIP_NAME="$ZIP_BASENAME"
else
  ZIP_NAME="${SAFE_NAME}-v${VERSION}.zip"
fi
STAGING="$(mktemp -d)"
PLUGIN_DIR="$STAGING/$SAFE_NAME"
mkdir -p "$PLUGIN_DIR/dist"

cp plugin.json package.json main.py LICENSE README.md THIRD_PARTY_NOTICES.md "$PLUGIN_DIR/"
if [ -f LLM-DISCLAIMER.md ]; then
  cp LLM-DISCLAIMER.md "$PLUGIN_DIR/"
fi
cp dist/index.js "$PLUGIN_DIR/dist/"
if [ -d py_modules ]; then
  cp -r py_modules "$PLUGIN_DIR/"
fi
if [ -d defaults ] && [ -n "$(ls -A defaults 2>/dev/null)" ]; then
  cp -r defaults "$PLUGIN_DIR/"
fi
if [ -d assets ] && [ -n "$(ls -A assets 2>/dev/null)" ]; then
  mkdir -p "$PLUGIN_DIR/public"
  cp -r assets/* "$PLUGIN_DIR/public/" 2>/dev/null || true
fi

find "$PLUGIN_DIR" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

rm -f "$OUT_DIR/$ZIP_NAME"
(
  cd "$STAGING"
  zip -r "$OUT_DIR/$ZIP_NAME" "$SAFE_NAME" -x "**/__pycache__/*"
)
rm -rf "$STAGING"

echo "$OUT_DIR/$ZIP_NAME"
