#!/usr/bin/env node
// Renders empire/EMPIRE.md from empire/repos.json (+ empire/local-inventory.json, empire/google-inventory.json,
// empire/cloudflare-inventory.json when present).
//   node scripts/build-empire.mjs          -> write EMPIRE.md
//   node scripts/build-empire.mjs --check  -> exit 1 if EMPIRE.md is stale or manifest is invalid

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const manifestPath = join(root, "empire", "repos.json");
const outPath = join(root, "empire", "EMPIRE.md");
const check = process.argv.includes("--check");

const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
const TIERS = ["core", "tooling", "personal", "upstream", "planned"];

function validate(m) {
  const errors = [];
  const seen = new Set();
  for (const r of m.repos) {
    const id = `${r.owner}/${r.name}`;
    if (seen.has(id)) errors.push(`duplicate repo ${id}`);
    seen.add(id);
    for (const k of ["name", "owner", "tier", "role", "visibility"]) {
      if (!r[k] && r[k] !== "") errors.push(`${id}: missing ${k}`);
    }
    if (!TIERS.includes(r.tier)) errors.push(`${id}: unknown tier ${r.tier}`);
    if (r.tier !== "planned" && !(r.createdAt && r.pushedAt)) {
      errors.push(`${id}: missing createdAt/pushedAt`);
    }
    if (r.forkOf && !/^[\w.-]+\/[\w.-]+$/.test(r.forkOf)) errors.push(`${id}: bad forkOf`);
  }
  if (!seen.has(m.hub)) errors.push(`hub ${m.hub} is not in repos`);
  return errors;
}

const url = (r) => `https://github.com/${r.owner}/${r.name}`;
const link = (r) => `[${r.owner}/${r.name}](${url(r)})`;
const month = (d) => (d || "").slice(0, 7);

function tierTable(tier) {
  const rows = manifest.repos
    .filter((r) => r.tier === tier)
    .sort((a, b) => (a.createdAt ?? "9999").localeCompare(b.createdAt ?? "9999"));
  if (rows.length === 0) return "";
  const lines = [
    `### ${tier.toUpperCase()}`,
    "",
    `> ${manifest.tiers[tier]}`,
    "",
    "| Repo | Brand | Role | Lang | Vis | Created | Last push |",
    "|---|---|---|---|---|---|---|",
  ];
  for (const r of rows) {
    const extra = [];
    if (r.forkOf) extra.push(`fork of \`${r.forkOf}\``);
    if (r.site) extra.push(`[site](${r.site})`);
    const role = [r.role, ...extra].join(" — ");
    lines.push(
      `| ${link(r)} | ${r.brand || "—"} | ${role} | ${r.language || "—"} | ${r.visibility} | ${r.createdAt || "—"} | ${r.pushedAt || "—"} |`,
    );
  }
  return lines.join("\n") + "\n";
}

const inventoryPath = join(root, "empire", "local-inventory.json");
let inventory = null;
try { inventory = JSON.parse(readFileSync(inventoryPath, "utf8")); } catch {}
const googlePath = join(root, "empire", "google-inventory.json");
let google = null;
try { google = JSON.parse(readFileSync(googlePath, "utf8")); } catch {}
const cloudflarePath = join(root, "empire", "cloudflare-inventory.json");
let cloudflare = null;
try { cloudflare = JSON.parse(readFileSync(cloudflarePath, "utf8")); } catch {}
// Only code-ish and video items become story events; docs/audio/files are summarised per year.
const googleStoryItems = () => (google?.items ?? []).filter((i) => i.kind === "code" || i.kind === "video");

const fmtBytes = (n) => {
  if (!n) return "0 B";
  const u = ["B", "KB", "MB", "GB", "TB"]; let i = 0; let v = n;
  while (v >= 1024 && i < u.length - 1) { v /= 1024; i++; }
  return `${v.toFixed(i ? 1 : 0)} ${u[i]}`;
};
const srcTag = (path) => (path.startsWith("/Volumes/") ? `HDD:${path.split("/")[2]}` : (inventory?.host ?? "local").toUpperCase());

// One event per thing that was born, from every source, so the story can be told in order.
function storyEvents() {
  const ev = [];
  for (const r of manifest.repos) {
    if (!r.createdAt || r.tier === "upstream") continue;
    ev.push({ date: r.createdAt, src: "GitHub", label: link(r), brand: r.brand || r.tier, role: r.role, until: r.pushedAt });
  }
  if (inventory) {
    for (const r of inventory.repos ?? []) {
      const date = (r.firstCommit || r.oldestFileBorn || r.born || "").slice(0, 10);
      if (!date) continue;
      const mirrored = r.remote && /github\.com[/:](RSPNOIZY|Noizyfish)\//i.test(r.remote);
      if (mirrored) continue; // already told via its GitHub repo
      ev.push({ date, src: srcTag(r.path), label: `\`${r.path}\``, brand: "local git", role: `${r.commits} commits${r.dirty ? ", uncommitted changes" : ""}${r.remote ? "" : ", NO REMOTE"} · ${fmtBytes(r.bytes)}`, until: (r.lastCommit || r.newestFileBorn || "").slice(0, 10) });
    }
    for (const p of inventory.looseProjects ?? []) {
      const date = (p.oldestFileBorn || p.born || p.modified || "").slice(0, 10);
      if (!date) continue;
      ev.push({ date, src: srcTag(p.path), label: `\`${p.path}\``, brand: "loose project", role: `${p.marker} · not in git · ${fmtBytes(p.bytes)}`, until: (p.newestFileBorn || p.modified || "").slice(0, 10) });
    }
  }
  for (const w of cloudflare?.live?.workers ?? []) {
    const date = (w.createdOn || "").slice(0, 10);
    if (date) ev.push({ date, src: "Cloudflare", label: `\`${w.name}\` (Worker)`, brand: "edge", role: `Worker${w.usageModel ? ` · ${w.usageModel}` : ""}`, until: (w.modifiedOn || "").slice(0, 10) });
  }
  for (const d of cloudflare?.live?.d1 ?? []) {
    const date = (d.createdAt || "").slice(0, 10);
    if (date) ev.push({ date, src: "Cloudflare", label: `\`${d.name}\` (D1)`, brand: "edge", role: `D1 database${d.tables != null ? ` · ${d.tables} tables` : ""}${d.sizeBytes ? ` · ${fmtBytes(d.sizeBytes)}` : ""}` });
  }
  for (const b of cloudflare?.live?.r2 ?? []) {
    const date = (b.createdOn || "").slice(0, 10);
    if (date) ev.push({ date, src: "Cloudflare", label: `\`${b.name}\` (R2)`, brand: "edge", role: `R2 bucket${b.location ? ` · ${b.location}` : ""}` });
  }
  for (const p of cloudflare?.live?.pages ?? []) {
    const date = (p.createdOn || "").slice(0, 10);
    if (date) ev.push({ date, src: "Cloudflare", label: p.production ? `[${p.name}](${p.production})` : `\`${p.name}\``, brand: "edge", role: "Pages project" });
  }
  for (const i of googleStoryItems()) {
    const date = (i.born || i.modified || "").slice(0, 10);
    if (!date) continue;
    ev.push({ date, src: i.source, label: i.url ? `[${i.name}](${i.url})` : `\`${i.path ?? i.name}\``, brand: i.kind, role: `${i.mime || i.kind}${i.bytes ? ` · ${fmtBytes(i.bytes)}` : ""}`, until: (i.modified || "").slice(0, 10) });
  }
  return ev.sort((a, b) => a.date.localeCompare(b.date));
}

function timeline() {
  const events = storyEvents();
  const start = manifest.storyStart ?? "0000-00";
  const prologue = events.filter((e) => month(e.date) < start);
  const story = events.filter((e) => month(e.date) >= start);
  const byMonth = new Map();
  for (const e of story) { const m = month(e.date); if (!byMonth.has(m)) byMonth.set(m, []); byMonth.get(m).push(e); }
  const months = [...byMonth.keys()].sort();
  const last = story.map((e) => e.until || e.date).sort().at(-1) ?? "";
  const srcs = [...new Set(story.map((e) => e.src))];
  const lines = [
    "## The Thru-Line",
    "",
    `**${manifest.storyLabel ?? start}** — ${months[0] ?? start} to ${month(last)}. ${story.length} things born across ${srcs.join(", ")}. Read top to bottom: this is the story.`,
    "",
  ];
  if (inventory) {
    lines.push(`_Local inventory from **${inventory.host}** scanned ${inventory.scannedAt.slice(0, 10)}: ${inventory.totals.repos} git repos (${inventory.totals.noRemote} with no remote, ${inventory.totals.dirty} dirty), ${inventory.totals.looseProjects} loose projects, ${inventory.totals.docFiles} doc files (${fmtBytes(inventory.totals.docBytes)})._`, "");
  } else {
    lines.push("_No local inventory yet. Run `scripts/gather-local.sh` on the M2 Ultra with the drives mounted to colour in the local half of the story._", "");
  }
  if (google) {
    const g = google.totals;
    lines.push(`_Google scanned ${google.scannedAt.slice(0, 10)}: ${g.drive} Drive files (${g.docs} docs, ${g.code} code, ${g.audio} audio, ${fmtBytes(g.bytes)}), ${g.youtube} YouTube uploads${google.gmail ? `, ${google.gmail.messagesTotal} Gmail messages` : ""}; oldest ${(g.oldest || "?").slice(0, 10)}._`, "");
  } else {
    lines.push("_No Google inventory yet. Import `empire/stack/n8n/google-inventory.json` into n8n (Drive + YouTube + Gmail) or run `scripts/gather-google.sh` with rclone._", "");
  }
  if (cloudflare) {
    const t = cloudflare.totals;
    const drift = cloudflare.drift ?? {};
    lines.push(`_Cloudflare scanned ${cloudflare.scannedAt.slice(0, 10)}: ${t.zones} zones, ${t.workers} Workers live (${t.declaredWorkers} declared in ${t.wranglerFiles} wrangler.toml), ${t.d1} D1, ${t.kv} KV, ${t.r2} R2, ${t.pages} Pages, ${t.access} Access apps, ${t.tunnels} tunnels${(drift.declaredNotDeployed?.length) ? ` · **${drift.declaredNotDeployed.length} declared but not deployed**: ${drift.declaredNotDeployed.map((n) => `\`${n}\``).join(", ")}` : ""}${(drift.deployedNotDeclared?.length) ? ` · **${drift.deployedNotDeclared.length} deployed but not in any repo**: ${drift.deployedNotDeclared.map((n) => `\`${n}\``).join(", ")}` : ""}._`, "");
  } else {
    lines.push("_No Cloudflare inventory yet. `empire signup cloudflare` then `empire run --only cloudflare` to pull every zone, Worker, D1, KV, R2, Pages, Access app and tunnel into the story._", "");
  }
  for (const m of months) {
    lines.push(`- **${m}**`);
    for (const e of byMonth.get(m)) {
      lines.push(`  - \`${e.src}\` ${e.label} · ${e.brand} · ${e.role}${e.until && e.until !== e.date ? ` _(→ ${e.until})_` : ""}`);
    }
  }
  const archiveStart = manifest.archiveStart ?? "0000-00";
  const archive = prologue.filter((e) => month(e.date) >= archiveStart);
  const before = prologue.filter((e) => month(e.date) < archiveStart);
  {
    lines.push("", `## ${manifest.archiveLabel ?? `Archive — before ${start}`}`, "");
    if (!archive.length) {
      lines.push(`_Nothing dated ${archiveStart.slice(0, 4)}–${start} yet. Mount the HDDs and run \`scripts/gather-local.sh --docs\`; every file's birth date fills this in automatically._`);
    } else {
      lines.push(`${archive.length} items born ${archive[0].date.slice(0, 4)}–${archive.at(-1).date.slice(0, 4)}, told year by year from file birth dates.`, "");
      const byYear = new Map();
      for (const e of archive) { const y = e.date.slice(0, 4); if (!byYear.has(y)) byYear.set(y, []); byYear.get(y).push(e); }
      for (const [y, items] of [...byYear.entries()].sort()) {
        lines.push(`- **${y}** · ${items.length} item${items.length === 1 ? "" : "s"}`);
        for (const e of items.slice(0, 12)) lines.push(`  - \`${e.src}\` ${e.label} · ${e.brand} · ${e.role}`);
        if (items.length > 12) lines.push(`  - _…and ${items.length - 12} more_`);
      }
    }
    // Document archives also tell the year-by-year story even when they aren't code.
    const docYears = new Map();
    for (const d of inventory?.docs ?? []) for (const y of d.byYear ?? []) docYears.set(y.year, (docYears.get(y.year) ?? 0) + y.files);
    for (const y of google?.byYear ?? []) docYears.set(y.year, (docYears.get(y.year) ?? 0) + y.files);
    const docRows = [...docYears.entries()].filter(([y]) => y >= archiveStart.slice(0, 4)).sort();
    if (docRows.length) {
      lines.push("", "### Documents & Drive files born per year", "", "| Year | Files |", "|---|---|");
      for (const [y, n] of docRows) lines.push(`| ${y} | ${n} |`);
    }
  }
  if (before.length) lines.push("", `_${before.length} items carry birth dates before ${archiveStart.slice(0, 4)} (likely copied media or clock-reset files); earliest ${before[0].date}._`);
  if (inventory?.docs?.length) {
    lines.push("", "### Document archives (by file birth date)", "", "| Root | Files | Size | Oldest | Newest |", "|---|---|---|---|---|");
    for (const d of inventory.docs) lines.push(`| \`${d.root}\` | ${d.count} | ${fmtBytes(d.bytes)} | ${(d.oldestFileBorn || "—").slice(0, 10)} | ${(d.newestFileBorn || "—").slice(0, 10)} |`);
  }
  return lines.join("\n") + "\n";
}


// ── Auto-grouping: everything from everywhere, clustered by brand family ─────
function groupOf(text) {
  const t = text.toLowerCase();
  for (const [g, pats] of Object.entries(manifest.groups ?? {})) {
    if (g.startsWith("_")) continue;
    if (pats.some((p) => t.includes(p))) return g;
  }
  return null;
}

function allThings() {
  const things = [];
  for (const r of manifest.repos) {
    if (r.tier === "upstream") continue;
    things.push({ key: r.name.toLowerCase(), group: (r.brand && r.brand !== "") ? r.brand : groupOf(`${r.name} ${r.role}`), src: "GitHub", label: link(r), date: r.createdAt ?? "", kind: r.tier === "planned" ? "planned" : "repo", remote: `github.com/${r.owner}/${r.name}` });
  }
  for (const r of inventory?.repos ?? []) {
    const gh = (r.remote || "").match(/github\.com[/:]([^/]+)\/([^/.]+)/i);
    things.push({ key: r.name.toLowerCase(), group: groupOf(r.path), src: srcTag(r.path), label: `\`${r.path}\``, date: (r.firstCommit || r.oldestFileBorn || r.born || "").slice(0, 10), kind: gh ? `clone of ${gh[1]}/${gh[2]}` : (r.remote ? "git (other remote)" : "git NO REMOTE"), remote: gh ? `github.com/${gh[1]}/${gh[2]}` : r.remote });
  }
  for (const p of inventory?.looseProjects ?? []) {
    things.push({ key: p.name.toLowerCase(), group: groupOf(p.path), src: srcTag(p.path), label: `\`${p.path}\``, date: (p.oldestFileBorn || p.born || p.modified || "").slice(0, 10), kind: `loose (${p.marker})`, remote: "" });
  }
  const cfThing = (name, kind, date) => things.push({ key: name.toLowerCase(), group: groupOf(name), src: "Cloudflare", label: `\`${name}\``, date: (date || "").slice(0, 10), kind, remote: "" });
  for (const w of cloudflare?.live?.workers ?? []) cfThing(w.name, "Worker", w.createdOn);
  for (const d of cloudflare?.live?.d1 ?? []) cfThing(d.name, "D1 database", d.createdAt);
  for (const b of cloudflare?.live?.r2 ?? []) cfThing(b.name, "R2 bucket", b.createdOn);
  for (const p of cloudflare?.live?.pages ?? []) cfThing(p.name, "Pages project", p.createdOn);
  for (const w of cloudflare?.wrangler ?? []) if (w.name) things.push({ key: w.name.toLowerCase(), group: groupOf(`${w.file} ${w.name}`), src: "wrangler.toml", label: `\`${w.file}\``, date: "", kind: "declared Worker", remote: "" });
  for (const i of googleStoryItems()) {
    things.push({ key: (i.name || "").toLowerCase().replace(/\.[a-z0-9]+$/, ""), group: groupOf(`${i.path ?? ""} ${i.name ?? ""}`), src: i.source, label: i.url ? `[${i.name}](${i.url})` : `\`${i.path ?? i.name}\``, date: (i.born || i.modified || "").slice(0, 10), kind: i.kind === "video" ? "YouTube upload" : `Drive ${i.mime || "file"}`, remote: i.url || "" });
  }
  return things;
}

function groups() {
  const things = allThings();
  const order = Object.keys(manifest.groups ?? {}).filter((g) => !g.startsWith("_"));
  const byGroup = new Map();
  for (const t of things) {
    const g = t.group ?? "UNGROUPED";
    if (!byGroup.has(g)) byGroup.set(g, []);
    byGroup.get(g).push(t);
  }
  const names = [...byGroup.keys()].sort((a, b) => {
    if (a === "UNGROUPED") return 1; if (b === "UNGROUPED") return -1;
    const ia = order.indexOf(a), ib = order.indexOf(b);
    return (ia < 0 ? 999 : ia) - (ib < 0 ? 999 : ib) || a.localeCompare(b);
  });
  const lines = ["## Everything, grouped", "", `${things.length} things from ${[...new Set(things.map((t) => t.src))].join(", ")} clustered into ${names.length} families by name and path (rules: \`groups\` in repos.json).`, ""];
  for (const g of names) {
    const items = byGroup.get(g).sort((a, b) => a.date.localeCompare(b.date));
    lines.push(`### ${g} · ${items.length}`, "");
    for (const t of items) lines.push(`- \`${t.src}\` ${t.label} · ${t.kind}${t.date ? ` · born ${t.date}` : ""}`);
    lines.push("");
  }
  // Copies: same name living in more than one place.
  const byKey = new Map();
  for (const t of things) { const k = t.key.replace(/[-_ ]/g, ""); if (!byKey.has(k)) byKey.set(k, []); byKey.get(k).push(t); }
  const dups = [...byKey.values()].filter((v) => v.length > 1 && new Set(v.map((t) => t.src + t.label)).size > 1);
  if (dups.length) {
    lines.push("### Same thing, many places", "", "Candidates to merge or delete. A local clone of its own GitHub repo is fine; two unrelated copies are not.", "");
    for (const v of dups) lines.push(`- **${v[0].key}** → ${v.map((t) => `\`${t.src}\` ${t.label}`).join(" · ")}`);
    lines.push("");
  }
  const orphans = things.filter((t) => t.kind === "git NO REMOTE" || t.kind.startsWith("loose"));
  if (orphans.length) {
    lines.push("### Only on a drive (no remote)", "", `${orphans.length} items exist nowhere but local storage. \`scripts/gather-local.sh --push\` puts every git one into Forgejo; loose ones need \`git init\` first.`, "");
  }
  return lines.join("\n") + "\n";
}

function header() {
  const live = manifest.repos.filter((r) => r.tier !== "planned").length;
  const planned = manifest.repos.filter((r) => r.tier === "planned").length;
  return [
    "<!-- GENERATED FILE. Edit empire/repos.json then run: node scripts/build-empire.mjs -->",
    "",
    "# MC96ECO UNIVERSE — THE NOIZY EMPIRE, ONE MAP",
    "",
    `> ${live} repositories across **RSPNOIZY** (org) and **Noizyfish** (personal), ${planned} planned, plus every git repo, loose project and document on the M2 Ultra and the drives. Hub: ${manifest.hub}.`,
    "",
    `**killSwitchHolder:** ${manifest.killSwitchHolder} | **covenant:** ${manifest.covenant} | **canon:** ${manifest.canon}`,
    "",
    "## How to pull everything into one workspace",
    "",
    "```sh",
    "scripts/gather.sh          # clones/pulls core + tooling into ~/NOIZY",
    "scripts/gather.sh --all    # also personal vaults and upstream forks",
    "scripts/gather.sh --list   # just print what would be cloned",
    "```",
    "",
    "## Flow of code",
    "",
    "```",
    "experiment  ->  RSPNOIZY/NOIZYLAB  (canonical lab)",
    "                      |  fork",
    "               Noizyfish/THEGATHERING  (this hub: manifest + working branch)",
    "                      |  promote tested modules",
    "               NOIZYVOX/governance/schemas  (planned)",
    "                      |  consumed by",
    "   NOIZYFISH . NOIZYKIDZ . NOIZYWORLD . DREAMCHAMBER . THE-OLD-GUARD . FISHMUSICINC . 2NDACT",
    "```",
    "",
  ].join("\n");
}

const errors = validate(manifest);
if (errors.length) {
  console.error("empire/repos.json invalid:\n  " + errors.join("\n  "));
  process.exit(1);
}

const out = [header(), timeline(), groups(), "## Registry by tier", "", ...TIERS.map(tierTable)].join("\n");

if (check) {
  let current = "";
  try {
    current = readFileSync(outPath, "utf8");
  } catch {}
  if (current !== out) {
    console.error("empire/EMPIRE.md is stale. Run: node scripts/build-empire.mjs");
    process.exit(1);
  }
  console.log("empire/EMPIRE.md is up to date.");
} else {
  writeFileSync(outPath, out);
  console.log(`wrote ${outPath}`);
}
