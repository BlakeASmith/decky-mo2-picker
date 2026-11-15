#!/usr/bin/env bash
# Build release/public from main; push to Origin and/or public GitHub.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_BRANCH="${SOURCE_BRANCH:-main}"
TARGET_BRANCH="${TARGET_BRANCH:-release/public}"
EXCLUDE_FILE="$ROOT/scripts/public-exclude.txt"
REMOTE="${REMOTE:-origin}"
PUBLIC_REMOTE_URL="${PUBLIC_REMOTE_URL:-https://github.com/BlakeASmith/decky-mo2-picker.git}"
PUBLIC_BRANCH="${PUBLIC_BRANCH:-main}"

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

push_public_github() {
  if command -v gh >/dev/null 2>&1; then
    gh auth setup-git 2>/dev/null || true
  fi
  if ! git -C "$ROOT" push "$PUBLIC_REMOTE_URL" \
    "${TARGET_BRANCH}:refs/heads/${PUBLIC_BRANCH}" --force-with-lease; then
    echo "Public GitHub push failed. Log in with: gh auth login" >&2
    echo "  Then: git push $PUBLIC_REMOTE_URL $TARGET_BRANCH:$PUBLIC_BRANCH" >&2
    return 1
  fi
  echo "Pushed to public GitHub $PUBLIC_BRANCH (releases CI uses built-in GITHUB_TOKEN)."
}

if [[ "${PUSH:-0}" == "1" ]]; then
  git -C "$ROOT" push "$REMOTE" "$TARGET_BRANCH"
  echo "Pushed $TARGET_BRANCH to $REMOTE."
fi

if [[ "${PUSH_PUBLIC:-${PUSH:-0}}" == "1" ]]; then
  push_public_github
elif [[ "${PUSH:-0}" != "1" ]]; then
  echo "When ready:"
  echo "  git push $REMOTE $TARGET_BRANCH"
  echo "  git push $PUBLIC_REMOTE_URL $TARGET_BRANCH:$PUBLIC_BRANCH   # uses gh/SSH credentials"
fi