#!/usr/bin/env bash
# Build release/public from main; push to Origin and/or public GitHub.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_BRANCH="${SOURCE_BRANCH:-main}"
TARGET_BRANCH="${TARGET_BRANCH:-release/public}"
EXCLUDE_FILE="$ROOT/scripts/public-exclude.txt"
REMOTE="${REMOTE:-origin}"
PUBLIC_OWNER="${PUBLIC_OWNER:-BlakeASmith}"
PUBLIC_REPO="${PUBLIC_REPO:-decky-mo2-picker}"
PUBLIC_REMOTE_URL="${PUBLIC_REMOTE_URL:-https://github.com/${PUBLIC_OWNER}/${PUBLIC_REPO}.git}"
PUBLIC_BRANCH="${PUBLIC_BRANCH:-main}"

public_remote_push_url() {
  if [[ -n "${PUBLIC_MIRROR_TOKEN:-}" ]]; then
    printf 'https://x-access-token:%s@github.com/%s/%s.git' \
      "$PUBLIC_MIRROR_TOKEN" "$PUBLIC_OWNER" "$PUBLIC_REPO"
  else
    printf '%s' "$PUBLIC_REMOTE_URL"
  fi
}

build_release_public() {
  local tmp rev
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN

  git -C "$ROOT" clone --local --branch "$SOURCE_BRANCH" "$ROOT" "$tmp/repo"
  cd "$tmp/repo"

  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    rm -rf "./$line"
  done < "$EXCLUDE_FILE"

  cp "$ROOT/public/README.md" README.md

  git checkout -B "$TARGET_BRANCH"
  git add -A
  if git diff --cached --quiet; then
    echo "No public changes since last publish"
    return 1
  fi

  git -c user.name="decky-mo2-picker publish" -c user.email="publish@users.noreply.local" \
    commit -m "chore: publish public mirror from ${SOURCE_BRANCH}"

  git -C "$tmp/repo" push "$ROOT" "HEAD:refs/heads/$TARGET_BRANCH" --force
  rev="$(git -C "$ROOT" rev-parse "$TARGET_BRANCH")"
  echo "Updated $TARGET_BRANCH at $rev"
}

push_public_github() {
  local url
  url="$(public_remote_push_url)"
  if ! git -C "$ROOT" push "$url" \
    "${TARGET_BRANCH}:refs/heads/${PUBLIC_BRANCH}" --force; then
    echo "Public GitHub push failed." >&2
    echo "  Prefer Origin Actions「Prepare public release branch」with PUBLIC_MIRROR_TOKEN set." >&2
    return 1
  fi
  echo "Pushed to public GitHub ${PUBLIC_BRANCH} (Build and Release uses built-in GITHUB_TOKEN)."
}

# Mirror-only mode: release/public already built locally or on a previous CI step.
if [[ "${PUSH_PUBLIC_ONLY:-0}" == "1" ]]; then
  push_public_github
  exit 0
fi

if ! build_release_public; then
  exit 0
fi

if [[ "${PUSH:-0}" == "1" ]]; then
  git -C "$ROOT" push "$REMOTE" "$TARGET_BRANCH"
  echo "Pushed $TARGET_BRANCH to $REMOTE."
fi

if [[ "${PUSH_PUBLIC:-0}" == "1" ]]; then
  push_public_github
elif [[ "${PUSH:-0}" != "1" ]]; then
  echo "When ready: run Origin Actions workflow「Prepare public release branch」, or:"
  echo "  git push $REMOTE $TARGET_BRANCH"
  echo "  PUBLIC_MIRROR_TOKEN=... PUSH_PUBLIC=1 $0"
fi