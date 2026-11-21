#!/usr/bin/env bash
# Inventory every git repo, loose project and doc tree on this machine + mounted drives,
# write empire/local-inventory.json, and optionally push every local repo into Forgejo.
#
#   scripts/gather-local.sh                 scan roots from empire/sources.json
#   scripts/gather-local.sh --roots /Volumes/ARCHIVE,/Users/me/Code
#   scripts/gather-local.sh --push          also create+push each repo to Forgejo (needs FORGEJO_URL/TOKEN/OWNER)
#   scripts/gather-local.sh --docs          also rsync doc files into $NOIZY_ROOT/docs/<root-name>/
#   scripts/gather-local.sh --out path.json
# Runs on macOS (M2 Ultra) or Linux. Needs: bash 3.2+, jq, git. Optional: rsync, du.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sources="$here/empire/sources.json"
out="$here/empire/local-inventory.json"
root_override=""; push=0; docs=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --roots) root_override="$2"; shift 2 ;;
    --push) push=1; shift ;;
    --docs) docs=1; shift ;;
    --out) out="$2"; shift 2 ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
command -v jq >/dev/null || { echo "jq is required (brew install jq)" >&2; exit 1; }
command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
if [[ $push -eq 1 ]]; then
  : "${FORGEJO_URL:?--push needs FORGEJO_URL}"; : "${FORGEJO_TOKEN:?--push needs FORGEJO_TOKEN}"; : "${FORGEJO_OWNER:?--push needs FORGEJO_OWNER}"
fi

host="$(hostname -s 2>/dev/null || hostname)"
noizy_root="${NOIZY_ROOT:-$HOME/NOIZY}"
max_depth=$(jq -r '.maxDepth // 6' "$sources")
docs_dest="$noizy_root/$(jq -r '.docsDest // "docs"' "$sources")"

# ── resolve roots (expand globs, drop system volumes) ───────────────────────
roots=()
if [[ -n "$root_override" ]]; then
  IFS=',' read -r -a roots <<<"$root_override"
else
  while IFS= read -r pat; do
    for p in $pat; do [[ -d "$p" ]] && roots+=("$p"); done
  done < <(jq -r '.roots[]' "$sources")
fi
skip_vol_re="$(jq -r '.skipVolumes | map(gsub("\\.";"\\\\.")) | join("|")' "$sources")"
filtered=()
for r in "${roots[@]}"; do
  base="$(basename "$r")"
  if [[ "$r" == /Volumes/* && "$base" =~ ^($skip_vol_re)$ ]]; then continue; fi
  filtered+=("$r")
done
roots=("${filtered[@]}")
[[ ${#roots[@]} -eq 0 ]] && { echo "no roots found; edit empire/sources.json or pass --roots" >&2; exit 1; }

# find(1) prune expression for skipDirs
prune_args=()
while IFS= read -r d; do prune_args+=( -name "$d" -o ); done < <(jq -r '.skipDirs[]' "$sources")
prune_args+=( -name '.git' )

markers_re="$(jq -r '.projectMarkers | join("|")' "$sources")"
doc_ext_re="$(jq -r '.docExtensions | join("|")' "$sources")"

echo "scanning ${#roots[@]} roots on $host"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
: > "$tmp/repos.jsonl"; : > "$tmp/loose.jsonl"; : > "$tmp/docs.jsonl"

is_mac=0; [[ "$(uname -s)" == Darwin ]] && is_mac=1
dir_size() { du -sk "$1" 2>/dev/null | cut -f1 | awk '{print $1*1024}'; }
fsize() { if [[ $is_mac -eq 1 ]]; then stat -f %z "$1" 2>/dev/null; else stat -c %s "$1" 2>/dev/null; fi || echo 0; }
mtime() { if [[ $is_mac -eq 1 ]]; then stat -f %m "$1" 2>/dev/null; else stat -c %Y "$1" 2>/dev/null; fi || echo 0; }
# Birth (creation) time. macOS/APFS: stat -f %B. Linux: stat -c %W (0 when the fs doesn't record it) → fall back to mtime.
btime() {
  local b
  if [[ $is_mac -eq 1 ]]; then b=$(stat -f %B "$1" 2>/dev/null); else b=$(stat -c %W "$1" 2>/dev/null); fi
  [[ "${b:-0}" =~ ^[0-9]+$ && "${b:-0}" -gt 0 ]] && echo "$b" || mtime "$1"
}
iso() { [[ "${1:-0}" -gt 0 ]] || { echo ""; return; }; date -u -r "$1" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "@$1" +%Y-%m-%dT%H:%M:%SZ; }
# Earliest + latest birth time of files beneath a dir (bounded by maxDepth and skipDirs).
birth_range() {
  local dir="$1" min=0 max=0 b
  while IFS= read -r f; do
    b=$(btime "$f"); [[ -z "$b" || "$b" -le 0 ]] && continue
    (( min == 0 || b < min )) && min=$b
    (( b > max )) && max=$b
  done < <(find "$dir" -maxdepth "$max_depth" \( "${prune_args[@]}" \) -prune -o -type f -print 2>/dev/null | head -5000)
  echo "$min $max"
}

for root in "${roots[@]}"; do
  echo "  $root"
  # git repos: stop descending at .git and at skipDirs
  while IFS= read -r gitdir; do
    repo="$(dirname "$gitdir")"
    remote="$(git -C "$repo" remote get-url origin 2>/dev/null || true)"
    branch="$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
    last="$(git -C "$repo" log -1 --format=%cI 2>/dev/null || true)"
    first="$(git -C "$repo" log --reverse --format=%cI 2>/dev/null | head -1 || true)"
    commits="$(git -C "$repo" rev-list --count HEAD 2>/dev/null || echo 0)"
    dirty=false; [[ -n "$(git -C "$repo" status --porcelain 2>/dev/null | head -1)" ]] && dirty=true
    read -r bmin bmax <<<"$(birth_range "$repo")"
    jq -nc --arg root "$root" --arg path "$repo" --arg name "$(basename "$repo")" --arg remote "$remote" \
      --arg branch "$branch" --arg last "$last" --arg first "$first" --argjson commits "${commits:-0}" --argjson dirty "$dirty" \
      --arg born "$(iso "$(btime "$repo")")" --arg oldest "$(iso "$bmin")" --arg newest "$(iso "$bmax")" \
      --argjson bytes "$(dir_size "$repo")" \
      '{root:$root,path:$path,name:$name,remote:$remote,branch:$branch,firstCommit:$first,lastCommit:$last,commits:$commits,dirty:$dirty,
        born:$born,oldestFileBorn:$oldest,newestFileBorn:$newest,bytes:$bytes}' \
      >> "$tmp/repos.jsonl"
  done < <(find "$root" -maxdepth "$max_depth" \( "${prune_args[@]}" \) -prune -print 2>/dev/null | grep '/\.git$')

  # loose projects: has a marker file, no .git in itself (ancestor repos already prune)
  while IFS= read -r marker; do
    proj="$(dirname "$marker")"
    [[ -d "$proj/.git" ]] && continue
    read -r bmin bmax <<<"$(birth_range "$proj")"
    jq -nc --arg root "$root" --arg path "$proj" --arg name "$(basename "$proj")" --arg marker "$(basename "$marker")" \
      --arg born "$(iso "$(btime "$proj")")" --arg oldest "$(iso "$bmin")" --arg newest "$(iso "$bmax")" \
      --arg modified "$(iso "$(mtime "$proj")")" --argjson bytes "$(dir_size "$proj")" \
      '{root:$root,path:$path,name:$name,marker:$marker,born:$born,oldestFileBorn:$oldest,newestFileBorn:$newest,modified:$modified,bytes:$bytes}' >> "$tmp/loose.jsonl"
  done < <(find "$root" -maxdepth "$max_depth" \( "${prune_args[@]}" \) -prune -o -type f -print 2>/dev/null \
            | grep -E "/($markers_re)$" | awk -F/ '{ OFS="/"; $NF=""; print }' | sort -u | sed 's#/$##' \
            | while read -r d; do ls "$d" 2>/dev/null | grep -E "^($markers_re)$" | head -1 | sed "s#^#$d/#"; done)

  # docs: count + bytes + birth range + per-year histogram (lists can be enormous on a 40-year archive)
  doc_count=0; doc_bytes=0; dmin=0; dmax=0; : > "$tmp/years.txt"
  while IFS= read -r f; do
    doc_count=$((doc_count+1)); sz=$(fsize "$f"); doc_bytes=$((doc_bytes+sz))
    b=$(btime "$f"); if [[ -n "$b" && "$b" -gt 0 ]]; then
      (( dmin == 0 || b < dmin )) && dmin=$b; (( b > dmax )) && dmax=$b
      iso "$b" | cut -c1-4 >> "$tmp/years.txt"
    fi
  done < <(find "$root" -maxdepth "$max_depth" \( "${prune_args[@]}" \) -prune -o -type f -print 2>/dev/null | grep -Ei "\.($doc_ext_re)$")
  years_json=$(sort "$tmp/years.txt" | uniq -c | awk '{printf "%s{\"year\":\"%s\",\"files\":%d}", (NR>1?",":""), $2, $1} END{print ""}')
  jq -nc --arg root "$root" --arg name "$(basename "$root")" --argjson count "$doc_count" --argjson bytes "$doc_bytes" \
    --arg oldest "$(iso "$dmin")" --arg newest "$(iso "$dmax")" --argjson years "[${years_json}]" \
    '{root:$root,name:$name,count:$count,bytes:$bytes,oldestFileBorn:$oldest,newestFileBorn:$newest,byYear:$years}' >> "$tmp/docs.jsonl"

  if [[ $docs -eq 1 ]] && command -v rsync >/dev/null; then
    dest="$docs_dest/$(basename "$root")"
    mkdir -p "$dest"
    inc=(); for e in $(jq -r '.docExtensions[]' "$sources"); do inc+=( --include="*.$e" ); done
    exc=(); for d in $(jq -r '.skipDirs[]' "$sources"); do exc+=( --exclude="$d/" ); done
    rsync -a --prune-empty-dirs "${exc[@]}" --include='*/' "${inc[@]}" --exclude='*' "$root/" "$dest/" && echo "    docs → $dest"
  fi
done

jq -s --arg host "$host" --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --argjson roots "$(printf '%s\n' "${roots[@]}" | jq -R . | jq -s .)" \
  --slurpfile loose "$tmp/loose.jsonl" --slurpfile docs "$tmp/docs.jsonl" \
  '{host:$host,scannedAt:$at,roots:$roots,repos:.,looseProjects:$loose,docs:$docs,
    totals:{repos:length,looseProjects:($loose|length),docFiles:($docs|map(.count)|add // 0),docBytes:($docs|map(.bytes)|add // 0),
            repoBytes:(map(.bytes)|add // 0),noRemote:(map(select(.remote==""))|length),dirty:(map(select(.dirty))|length)}}' \
  "$tmp/repos.jsonl" > "$out"
echo "wrote $out"
jq -r '.totals | "  repos \(.repos) (no remote \(.noRemote), dirty \(.dirty)) · loose projects \(.looseProjects) · docs \(.docFiles) files"' "$out"

# ── optional: push every local repo into Forgejo ────────────────────────────
if [[ $push -eq 1 ]]; then
  api() { curl -fsS -H "Authorization: token $FORGEJO_TOKEN" -H "Content-Type: application/json" "$@"; }
  ssh_or_http="$FORGEJO_URL"
  jq -c '.repos[]' "$out" | while read -r r; do
    path=$(jq -r .path <<<"$r"); name=$(jq -r .name <<<"$r")
    slug="local--${host}--$(echo "$name" | tr -c 'A-Za-z0-9._-' '-' | sed 's/-*$//')"
    if ! api "$FORGEJO_URL/api/v1/repos/$FORGEJO_OWNER/$slug" >/dev/null 2>&1; then
      api -X POST "$FORGEJO_URL/api/v1/user/repos" -d "$(jq -n --arg n "$slug" --arg d "local: $path" '{name:$n,description:$d,private:true,auto_init:false}')" >/dev/null \
        || api -X POST "$FORGEJO_URL/api/v1/orgs/$FORGEJO_OWNER/repos" -d "$(jq -n --arg n "$slug" --arg d "local: $path" '{name:$n,description:$d,private:true,auto_init:false}')" >/dev/null \
        || { echo "  FAILED create $slug" >&2; continue; }
    fi
    url="$ssh_or_http/$FORGEJO_OWNER/$slug.git"
    git -C "$path" remote get-url forgejo >/dev/null 2>&1 || git -C "$path" remote add forgejo "$url"
    git -C "$path" remote set-url forgejo "$url"
    if git -C "$path" push -q forgejo --all && git -C "$path" push -q forgejo --tags; then echo "  pushed   $slug"; else echo "  FAILED push $slug" >&2; fi
  done
fi
