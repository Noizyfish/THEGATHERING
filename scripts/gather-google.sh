#!/usr/bin/env bash
# FOSS alternative to the n8n Google workflow: inventory Google Drive with rclone (birth dates from Drive createdTime)
# and write empire/google-inventory.json in the same shape the generator + Claude read.
#   brew install rclone && rclone config   # create a "gdrive" remote (Google Drive, full scope)
#   scripts/gather-google.sh [--remote gdrive:] [--out empire/google-inventory.json]
# Add YouTube/Gmail via the n8n workflow (empire/stack/n8n/google-inventory.json) or Google Takeout.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
remote="gdrive:"; out="$here/empire/google-inventory.json"
while [[ $# -gt 0 ]]; do case "$1" in
  --remote) remote="$2"; shift 2 ;; --out) out="$2"; shift 2 ;;
  -h|--help) sed -n '2,7p' "$0"; exit 0 ;; *) echo "unknown arg: $1" >&2; exit 2 ;; esac; done
command -v rclone >/dev/null || { echo "rclone is required (brew install rclone)" >&2; exit 1; }
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

echo "listing $remote (this walks the whole Drive)…"
# --metadata exposes btime (Drive createdTime) alongside ModTime.
rclone lsjson "$remote" --recursive --files-only --metadata --drive-shared-with-me 2>/dev/null \
| jq --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
  def kind(m): if (m|test("audio|midi|wav|flac|aiff|mpeg";"i")) then "audio"
    elif (m|test("javascript|python|x-sh|typescript|zip|x-tar|gzip|xml|html|css|swift|rust|x-c|java";"i")) then "code"
    elif (m|test("document|spreadsheet|presentation|pdf|text|markdown|json|rtf|msword|officedocument";"i")) then "doc" else "file" end;
  map({source:"Google:Drive", kind:kind(.MimeType//""), id:.ID, name:.Name, path:.Path, mime:(.MimeType//""),
       born:(.Metadata.btime // .ModTime), modified:.ModTime, bytes:(.Size // 0)})
  | sort_by(.born)
  | {source:"google", scannedAt:$at, gmail:null,
     totals:{items:length, drive:length, youtube:0,
             docs:(map(select(.kind=="doc"))|length), code:(map(select(.kind=="code"))|length), audio:(map(select(.kind=="audio"))|length),
             bytes:(map(.bytes)|add // 0), oldest:(.[0].born // null), newest:(.[-1].born // null)},
     byYear:(group_by(.born[:4]) | map({year:.[0].born[:4], files:length})),
     items:.}' > "$out"
jq -r '.totals | "wrote '"$out"': \(.items) files · \(.docs) docs · \(.code) code · \(.audio) audio · \(.oldest[:10]) → \(.newest[:10])"' "$out"
