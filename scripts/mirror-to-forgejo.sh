#!/usr/bin/env bash
# Mirror every NOIZY Empire repo from GitHub into a self-hosted Forgejo (pull-mirror, auto-synced).
#   scripts/mirror-to-forgejo.sh           core + tooling tiers
#   scripts/mirror-to-forgejo.sh --all     + personal + upstream tiers
# Env (required): FORGEJO_URL, FORGEJO_TOKEN, FORGEJO_OWNER
# Env (optional): GITHUB_TOKEN (needed for private repos), MIRROR_INTERVAL (default 8h0m0s)
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="$here/empire/repos.json"
: "${FORGEJO_URL:?set FORGEJO_URL e.g. http://localhost:3000}"
: "${FORGEJO_TOKEN:?set FORGEJO_TOKEN (Forgejo personal access token with repo scope)}"
: "${FORGEJO_OWNER:?set FORGEJO_OWNER (user or org that will hold the mirrors)}"
interval="${MIRROR_INTERVAL:-8h0m0s}"

tiers='["core","tooling"]'
[[ "${1:-}" == "--all" ]] && tiers='["core","tooling","personal","upstream"]'
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

api() { curl -fsS -H "Authorization: token $FORGEJO_TOKEN" -H "Content-Type: application/json" "$@"; }

jq -c --argjson t "$tiers" '.repos[] | select(.tier as $x | $t | index($x))' "$manifest" | while read -r r; do
  owner=$(jq -r .owner <<<"$r"); name=$(jq -r .name <<<"$r"); vis=$(jq -r .visibility <<<"$r")
  # Same repo name can exist under both GitHub owners; namespace with owner prefix.
  local_name="${owner}--${name}"
  if api "$FORGEJO_URL/api/v1/repos/$FORGEJO_OWNER/$local_name" >/dev/null 2>&1; then
    echo "  exists   $FORGEJO_OWNER/$local_name"; continue
  fi
  body=$(jq -n \
    --arg addr "https://github.com/$owner/$name.git" \
    --arg name "$local_name" \
    --arg owner "$FORGEJO_OWNER" \
    --arg desc "$(jq -r .role <<<"$r")" \
    --arg tok "${GITHUB_TOKEN:-}" \
    --arg iv "$interval" \
    --argjson priv "$([[ $vis == private ]] && echo true || echo false)" \
    '{clone_addr:$addr, repo_name:$name, repo_owner:$owner, description:$desc, mirror:true,
      mirror_interval:$iv, private:$priv, service:"github", wiki:true, issues:true, releases:true}
     + (if $tok != "" then {auth_token:$tok} else {} end)')
  if api -X POST "$FORGEJO_URL/api/v1/repos/migrate" -d "$body" >/dev/null; then
    echo "  mirrored $owner/$name -> $FORGEJO_OWNER/$local_name"
  else
    echo "  FAILED   $owner/$name" >&2
  fi
done
