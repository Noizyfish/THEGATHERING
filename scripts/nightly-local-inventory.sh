#!/usr/bin/env bash
# Nightly on GOD (M2 Ultra), installed by empire/stack/launchd/ai.noizy.empire.nightly.plist.
# Thin wrapper kept for backwards compatibility — the flow lives in `scripts/empire run`.
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$here/scripts/empire" run --quiet "$@"
