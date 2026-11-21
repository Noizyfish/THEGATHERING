#!/usr/bin/env bash
# Harvest everything Claude (and Gemini) produced on this Mac into the CLAUDE-TODAY repo, daily.
# Runs on GOD (M2 Ultra). Captures: Claude Code project memory + session summaries, Claude worktrees index,
# Gemini/Antigravity MC96 reports, CLAUDE.md files across the home dir. Secrets are never copied (.env, keys, tokens).
#
#   scripts/gather-claude.sh                 harvest into ~/NOIZY/CLAUDE-TODAY and push
#   scripts/gather-claude.sh --dry-run       show what would be collected
# Env: CLAUDE_TODAY_REPO (default Noizyfish/CLAUDE-TODAY), NOIZY_ROOT (default ~/NOIZY)
set -euo pipefail
dry=0; [[ "${1:-}" == "--dry-run" ]] && dry=1
repo="${CLAUDE_TODAY_REPO:-Noizyfish/CLAUDE-TODAY}"
root="${NOIZY_ROOT:-$HOME/NOIZY}"
dest="$root/CLAUDE-TODAY"
today="$(date +%Y-%m-%d)"
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

if [[ $dry -eq 0 ]]; then
  if [[ ! -d "$dest/.git" ]]; then
    mkdir -p "$root"
    gh repo clone "$repo" "$dest" -- -q 2>/dev/null || git clone -q "https://github.com/$repo.git" "$dest"
  fi
  git -C "$dest" pull -q --ff-only 2>/dev/null || true
fi
day="$dest/days/$today"
[[ $dry -eq 0 ]] && mkdir -p "$day"/{claude-memory,claude-sessions,gemini,worktrees,claude-md}

put() { # put <src> <dst-subdir>
  local src="$1" sub="$2"
  [[ -e "$src" ]] || return 0
  if [[ $dry -eq 1 ]]; then echo "  would copy $src → $sub/"; return 0; fi
  rsync -a --exclude='.env*' --exclude='*secret*' --exclude='*token*' --exclude='*.key' --exclude='*.pem' \
        --exclude='node_modules' --exclude='.git' "$src" "$day/$sub/"
  echo "  $src → $sub/"
}

echo "harvesting Claude on $(hostname -s) for $today"

# 1. Claude Code project memory (MEMORY.md + topic files) for every project
for mem in "$HOME"/.claude/projects/*/memory; do
  [[ -d "$mem" ]] || continue
  proj="$(basename "$(dirname "$mem")")"
  put "$mem/" "claude-memory/$proj"
done

# 2. Session transcripts → lightweight index (first user message, turn count, date). Never the full transcript.
if [[ $dry -eq 0 ]]; then : > "$day/claude-sessions/index.jsonl"; fi
for jsonl in "$HOME"/.claude/projects/*/*.jsonl; do
  [[ -f "$jsonl" ]] || continue
  proj="$(basename "$(dirname "$jsonl")")"
  if [[ $dry -eq 1 ]]; then echo "  would index $jsonl"; continue; fi
  jq -c --arg proj "$proj" --arg file "$(basename "$jsonl")" -s '
    { project:$proj, file:$file, turns:length,
      started:(map(.timestamp // empty) | sort | .[0] // null),
      ended:(map(.timestamp // empty) | sort | .[-1] // null),
      first_prompt:((map(select(.type=="user") | .message.content) | .[0]) // "" | if type=="array" then (map(.text? // "") | join(" ")) else . end | .[0:200]) }' \
    "$jsonl" >> "$day/claude-sessions/index.jsonl" 2>/dev/null || true
done

# 3. Claude worktrees: just the branch list + last commit per worktree
if [[ -d "$HOME/.claude-worktrees" ]]; then
  if [[ $dry -eq 0 ]]; then : > "$day/worktrees/index.tsv"; fi
  find "$HOME/.claude-worktrees" -maxdepth 3 -name .git -prune -print 2>/dev/null | while read -r g; do
    wt="$(dirname "$g")"
    [[ $dry -eq 1 ]] && { echo "  would index worktree $wt"; continue; }
    printf '%s\t%s\t%s\n' "$wt" "$(git -C "$wt" rev-parse --abbrev-ref HEAD 2>/dev/null)" "$(git -C "$wt" log -1 --format='%cI %s' 2>/dev/null)" >> "$day/worktrees/index.tsv"
  done
fi

# 4. Gemini / Antigravity MC96 reports (plain reports only)
for f in "$HOME"/.gemini/mc96_*.md "$HOME"/.gemini/mc96_*.json "$HOME"/.gemini/mc96_*.txt "$HOME"/.gemini/robs_originals_report.md; do put "$f" gemini; done

# 5. Every CLAUDE.md in the usual code roots (the instructions Claude was given, per project)
for r in "$HOME/NOIZYLAB" "$HOME/NOIZYANTHROPIC" "$HOME/NOIZY" "$HOME/Documents/GABRIEL" "$HOME/projects"; do
  [[ -d "$r" ]] || continue
  find "$r" -maxdepth 4 -name 'CLAUDE.md' -not -path '*/node_modules/*' 2>/dev/null | while read -r f; do
    rel="${f#$HOME/}"; sub="claude-md/$(dirname "$rel")"
    [[ $dry -eq 1 ]] && { echo "  would copy $f"; continue; }
    mkdir -p "$day/$sub" && cp "$f" "$day/$sub/"
  done
done

[[ $dry -eq 1 ]] && exit 0

# Day summary + rolling README
{
  echo "# Claude on $(hostname -s) — $today"
  echo
  echo "- memory projects: $(ls "$day/claude-memory" 2>/dev/null | wc -l | tr -d ' ')"
  echo "- sessions indexed: $(wc -l < "$day/claude-sessions/index.jsonl" 2>/dev/null | tr -d ' ')"
  echo "- worktrees: $(wc -l < "$day/worktrees/index.tsv" 2>/dev/null | tr -d ' ')"
  echo "- gemini reports: $(ls "$day/gemini" 2>/dev/null | wc -l | tr -d ' ')"
  echo "- CLAUDE.md files: $(find "$day/claude-md" -name CLAUDE.md 2>/dev/null | wc -l | tr -d ' ')"
} > "$day/README.md"
{
  echo "# CLAUDE-TODAY"
  echo
  echo "Daily harvest of Claude Code memory, session index, worktrees, and Gemini MC96 reports from GOD (M2 Ultra). Written by \`THEGATHERING/scripts/gather-claude.sh\`."
  echo
  for d in $(ls -r "$dest/days"); do echo "- [$d](days/$d/README.md)"; done
} > "$dest/README.md"

cd "$dest"
git add -A
if git diff --cached --quiet; then echo "no changes"; exit 0; fi
git -c user.name="${GIT_AUTHOR_NAME:-gabriel-nightly}" -c user.email="${GIT_AUTHOR_EMAIL:-gabriel@noizy.ai}" commit -q -m "harvest: $today"
git push -q -u origin HEAD
echo "pushed $repo ($today)"
