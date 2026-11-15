#!/usr/bin/env bash
# Build release/public from main and optionally push to Origin.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_BRANCH="${SOURCE_BRANCH:-main}"
TARGET_BRANCH="${TARGET_BRANCH:-release/public}"
EXCLUDE_FILE="$ROOT/scripts/public-exclude.txt"
REMOTE="${REMOTE:-origin}"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git -C "$ROOT" clone --local --branch "$SOURCE_BRANCH" "$ROOT" "$TMP/repo"
cd "$TMP/repo"

while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -z "$line" || "$line" =~ ^# ]] && continue
  rm -rf "./$line"
done < "$EXCLUDE_FILE"

cp "$ROOT/public/README.md" README.md

git checkout -B "$TARGET_BRANCH"
git add -A
if git diff --cached --quiet; then
  echo "No public changes since last publish"
  exit 0
fi

git -c user.name="decky-mo2-picker publish" -c user.email="publish@users.noreply.local" \
  commit -m "chore: publish public mirror from ${SOURCE_BRANCH}"

git -C "$TMP/repo" push "$ROOT" "HEAD:refs/heads/$TARGET_BRANCH"
REV="$(git -C "$ROOT" rev-parse "$TARGET_BRANCH")"
echo "Updated $TARGET_BRANCH at $REV"

if [[ "${PUSH:-0}" == "1" ]]; then
  git -C "$ROOT" push "$REMOTE" "$TARGET_BRANCH"
  echo "Pushed $TARGET_BRANCH to $REMOTE (sync workflow will update public GitHub)."
else
  echo "Push when ready: git push $REMOTE $TARGET_BRANCH"
fi