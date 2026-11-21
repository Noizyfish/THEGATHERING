#!/usr/bin/env bash
# Clone or fast-forward every NOIZY Empire repo into one workspace.
#   scripts/gather.sh            core + tooling tiers
#   scripts/gather.sh --all      + personal + upstream tiers
#   scripts/gather.sh --list     print targets, touch nothing
# Env: NOIZY_ROOT (default ~/NOIZY), GATHER_JOBS (default 4)
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="$here/empire/repos.json"
root="${NOIZY_ROOT:-$HOME/NOIZY}"
jobs="${GATHER_JOBS:-4}"
all=0; list=0
for a in "$@"; do
  case "$a" in
    --all) all=1 ;;
    --list) list=1 ;;
    -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
    *) echo "unknown arg: $a" >&2; exit 2 ;;
  esac
done

command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }
command -v git >/dev/null || { echo "git is required" >&2; exit 1; }

if [[ $all -eq 1 ]]; then tiers='["core","tooling","personal","upstream"]'
else tiers='["core","tooling"]'; fi

targets=$(jq -r --argjson t "$tiers" '.repos[] | select(.tier as $x | $t | index($x)) | "\(.owner)/\(.name)"' "$manifest")

if [[ $list -eq 1 ]]; then printf '%s\n' $targets; exit 0; fi

mkdir -p "$root"
echo "gathering $(wc -w <<<"$targets" | tr -d ' ') repos into $root"

sync_one() {
  local full="$1" owner name dest
  owner="${full%/*}"; name="${full#*/}"
  dest="$root/$owner/$name"
  if [[ -d "$dest/.git" ]]; then
    git -C "$dest" pull --ff-only -q && echo "  updated  $full" || echo "  SKIPPED  $full (diverged)"
  else
    mkdir -p "$(dirname "$dest")"
    if command -v gh >/dev/null; then gh repo clone "$full" "$dest" -- -q
    else git clone -q "https://github.com/$full.git" "$dest"; fi
    echo "  cloned   $full"
  fi
}
export -f sync_one; export root

printf '%s\n' $targets | xargs -P "$jobs" -I{} bash -c 'sync_one "$@"' _ {}
echo "done: $root"
