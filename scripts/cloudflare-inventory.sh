#!/usr/bin/env bash
# ALL CLOUDFLARE → empire/cloudflare-inventory.json
# Live account inventory via the API (zones, DNS counts, Workers, D1, KV, R2, Pages, Access apps, Tunnels, Workers AI
# models, Email Routing) + every wrangler.toml on disk under $NOIZY_ROOT / sources.json roots (declared bindings).
#
#   scripts/cloudflare-inventory.sh                 needs CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID (empire/stack/.env)
#   scripts/cloudflare-inventory.sh --local-only    just scan wrangler.toml files (no API)
#   scripts/cloudflare-inventory.sh --out path.json
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[[ -f "$here/empire/stack/.env" ]] && set -a && . "$here/empire/stack/.env" && set +a
out="$here/empire/cloudflare-inventory.json"; local_only=0
while [[ $# -gt 0 ]]; do case "$1" in
  --out) out="$2"; shift 2 ;; --local-only) local_only=1; shift ;;
  -h|--help) sed -n '2,8p' "$0"; exit 0 ;; *) echo "unknown arg: $1" >&2; exit 2 ;; esac; done
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }
API="https://api.cloudflare.com/client/v4"
tok="${CLOUDFLARE_API_TOKEN:-}"; acct="${CLOUDFLARE_ACCOUNT_ID:-}"

cf1() { # cf1 <path> <jq-path> <fallback> → single-object fetch, never empty
  local res; res=$(curl -sS --max-time 10 -H "Authorization: Bearer $tok" "$API$1" 2>/dev/null) || res=""
  jq -c "$2 // $3" <<<"${res:-null}" 2>/dev/null || echo "$3"
}
cf() { # cf <path> → .result (all pages, up to 20) or [] on error
  local path="$1" page=1 all='[]' res
  while :; do
    res=$(curl -sS --max-time 20 -H "Authorization: Bearer $tok" "$API$path$([[ "$path" == *\?* ]] && echo '&' || echo '?')per_page=100&page=$page" 2>/dev/null) || break
    jq -e '.success' >/dev/null 2>&1 <<<"$res" || { echo "  ! $path: $(jq -c '.errors[0].message // .errors' <<<"$res" 2>/dev/null | head -c 120)" >&2; break; }
    all=$(jq -c --argjson r "$(jq -c '.result // []' <<<"$res")" '. + (if ($r|type)=="array" then $r else [$r] end)' <<<"$all")
    local total; total=$(jq -r '.result_info.total_pages // 1' <<<"$res")
    [[ $page -ge $total || $page -ge 20 ]] && break; page=$((page+1))
  done
  echo "$all"
}

live='{}'
if [[ $local_only -eq 0 ]]; then
  [[ -n "$tok" && -n "$acct" ]] || { echo "CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID not set — run: empire signup cloudflare (or --local-only)" >&2; exit 1; }
  echo "cloudflare: account $acct"
  verify=$(cf1 "/user/tokens/verify" '.result' '{}')
  zones=$(cf "/zones?account.id=$acct")
  zone_detail='[]'
  for z in $(jq -r '.[].id' <<<"$zones"); do
    zname=$(jq -r --arg z "$z" '.[] | select(.id==$z) | .name' <<<"$zones")
    echo "  zone $zname"
    dns=$(cf "/zones/$z/dns_records")
    er=$(cf1 "/zones/$z/email/routing" '.result' '{}')
    zone_detail=$(jq -c --arg id "$z" --arg name "$zname" --argjson dns "$dns" --argjson er "$er" \
      '. + [{id:$id, name:$name, dnsRecords:($dns|length), dnsByType:($dns|group_by(.type)|map({(.[0].type):length})|add // {}),
             hostnames:($dns|map(select(.type=="CNAME" or .type=="A" or .type=="AAAA")|.name)|unique), emailRouting:($er.enabled // false)}]' <<<"$zone_detail")
  done
  workers=$(cf "/accounts/$acct/workers/scripts")
  domains=$(cf "/accounts/$acct/workers/domains")
  subdomain=$(cf1 "/accounts/$acct/workers/subdomain" '.result.subdomain' '""' | jq -r .)
  d1=$(cf "/accounts/$acct/d1/database")
  kv=$(cf "/accounts/$acct/storage/kv/namespaces")
  r2=$(cf1 "/accounts/$acct/r2/buckets" '.result.buckets' '[]')
  pages=$(cf "/accounts/$acct/pages/projects")
  access=$(cf "/accounts/$acct/access/apps")
  tunnels=$(cf "/accounts/$acct/cfd_tunnel?is_deleted=false")
  ai=$(cf "/accounts/$acct/ai/models/search")
  live=$(jq -n --argjson v "$verify" --arg sub "$subdomain" --argjson zones "$zone_detail" --argjson workers "$workers" --argjson domains "$domains" \
     --argjson d1 "$d1" --argjson kv "$kv" --argjson r2 "$r2" --argjson pages "$pages" --argjson access "$access" --argjson tunnels "$tunnels" --argjson ai "$ai" '
    { token: {id:$v.id, status:$v.status},
      workersSubdomain: (if $sub=="" then null else "\($sub).workers.dev" end),
      zones: $zones,
      workers: ($workers | map({name:.id, createdOn:.created_on, modifiedOn:.modified_on, usageModel:.usage_model, handlers:.handlers, tail:(.tail_consumers//[]|length)})),
      workerDomains: ($domains | map({hostname, service, zone:.zone_name})),
      d1: ($d1 | map({name, uuid, createdAt:.created_at, version, sizeBytes:(.file_size//null), tables:(.num_tables//null)})),
      kv: ($kv | map({title, id})),
      r2: ($r2 | map({name, createdOn:.creation_date, location, storageClass:.storage_class})),
      pages: ($pages | map({name, subdomain, domains, createdOn:.created_on, source:(.source.type//null), production:(.canonical_deployment.url//null)})),
      access: ($access | map({name, domain, type, createdAt:.created_at})),
      tunnels: ($tunnels | map({name, id, status, createdAt:.created_at, connections:(.connections//[]|length)})),
      workersAI: { models:($ai|length), byTask:($ai|group_by(.task.name)|map({(.[0].task.name):length})|add // {}) } }')
fi

# wrangler.toml scan — declared Workers/bindings living in local code (what the repos *think* exists)
roots=()
[[ -n "${NOIZY_ROOT:-}" && -d "${NOIZY_ROOT:-}" ]] && roots+=("$NOIZY_ROOT")
[[ -f "$here/empire/sources.json" ]] && while IFS= read -r r; do r="${r/#\~/$HOME}"; [[ -d "$r" ]] && roots+=("$r"); done < <(jq -r '.roots[]? // empty' "$here/empire/sources.json" 2>/dev/null)
[[ ${#roots[@]} -eq 0 ]] && roots+=("$here")
wr='[]'
while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  name=$(grep -m1 -E '^name\s*=' "$f" | sed -E 's/^name\s*=\s*"([^"]*)".*/\1/')
  main=$(grep -m1 -E '^main\s*=' "$f" | sed -E 's/^main\s*=\s*"([^"]*)".*/\1/')
  d1n=$(grep -E '^\s*database_name\s*=' "$f" | sed -E 's/.*=\s*"([^"]*)".*/\1/' | jq -R . | jq -sc 'unique')
  r2n=$(grep -E '^\s*bucket_name\s*=' "$f" | sed -E 's/.*=\s*"([^"]*)".*/\1/' | jq -R . | jq -sc 'unique')
  kvb=$(awk '/^\[\[kv_namespaces\]\]/{f=1;next} /^\[/{f=0} f && /^[ \t]*binding[ \t]*=/{sub(/^[^"]*"/,"");sub(/".*$/,"");print}' "$f" | jq -R . | jq -sc 'unique')
  ai=$( grep -qE '^\[ai\]' "$f" && echo true || echo false)
  routes=$(grep -E '^\s*(pattern|route|routes)\s*=' "$f" | sed -E 's/.*=\s*//' | tr -d '"[]' | tr ',' '\n' | sed 's/^ *//;/^$/d' | jq -R . | jq -sc 'unique')
  wr=$(jq -c --arg f "${f#$HOME/}" --arg name "$name" --arg main "$main" --argjson d1 "$d1n" --argjson r2 "$r2n" --argjson kv "$kvb" --argjson ai "$ai" --argjson routes "$routes" \
      '. + [{file:$f, name:$name, main:$main, d1:$d1, r2:$r2, kvBindings:$kv, workersAI:$ai, routes:$routes}]' <<<"$wr")
done < <(find "${roots[@]}" -name 'wrangler.toml' -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | sort -u)
echo "wrangler.toml files: $(jq length <<<"$wr")"

jq -n --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg host "$(hostname -s)" --arg acct "$acct" --argjson live "$live" --argjson wr "$wr" '
  { scannedAt:$at, host:$host, accountId:(if $acct=="" then null else $acct end), live:$live, wrangler:$wr,
    totals: { zones:($live.zones//[]|length), workers:($live.workers//[]|length), d1:($live.d1//[]|length), kv:($live.kv//[]|length),
              r2:($live.r2//[]|length), pages:($live.pages//[]|length), access:($live.access//[]|length), tunnels:($live.tunnels//[]|length),
              wranglerFiles:($wr|length),
              declaredWorkers:($wr|map(.name)|map(select(.!=""))|unique|length),
              declaredD1:($wr|map(.d1[])|unique|length), declaredR2:($wr|map(.r2[])|unique|length) },
    drift: { declaredNotDeployed: (($wr|map(.name)|map(select(.!=""))|unique) - ($live.workers//[]|map(.name))),
             deployedNotDeclared: (($live.workers//[]|map(.name)) - ($wr|map(.name)|unique)) } }' > "$out"
jq -r '"cloudflare → \(.totals.zones) zones · \(.totals.workers) workers (\(.totals.declaredWorkers) declared in \(.totals.wranglerFiles) wrangler.toml) · \(.totals.d1) D1 · \(.totals.kv) KV · \(.totals.r2) R2 · \(.totals.pages) Pages · \(.totals.access) Access · \(.totals.tunnels) tunnels"' "$out"
