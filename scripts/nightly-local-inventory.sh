#!/usr/bin/env bash
# Nightly on the M2 Ultra: inventory local repos/projects/docs (with file birth dates), regenerate the
# Empire map, commit + push so n8n/Claude/Siri see the latest story. Installed by the launchd plist.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$here"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

git pull -q --ff-only || true
scripts/gather-local.sh ${GATHER_LOCAL_ARGS:-} 
node scripts/build-empire.mjs
if ! git diff --quiet -- empire/local-inventory.json empire/EMPIRE.md; then
  git add empire/local-inventory.json empire/EMPIRE.md
  git -c user.name="${GIT_AUTHOR_NAME:-gabriel-nightly}" -c user.email="${GIT_AUTHOR_EMAIL:-gabriel@noizy.ai}" \
    commit -q -m "chore(empire): nightly local inventory $(date -u +%Y-%m-%d)"
  git push -q
  echo "inventory pushed"
else
  echo "no changes"
fi
