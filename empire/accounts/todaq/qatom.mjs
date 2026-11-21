#!/usr/bin/env node
// Qatom (TODAQ Micro) v4 client — zero dependencies, Node ≥ 18.
// The official @todaqmicro/payment-node (0.4.0) still targets /v2 and logs secrets; this talks to /v4 directly.
//
//   node qatom.mjs signup [--env staging|production] [--descriptor "text" --cost 0.25]
//       → POST /v4/account, token, GET /v4/dq, POST /v4/twin, POST /v4/commodity. Prints `KEY=value` lines
//         (client secret is returned ONCE by Qatom — this is the only time you'll see it).
//   node qatom.mjs whoami                 token + twin balances (verifies TODAQ_* in env)
//   node qatom.mjs dq                     list digital quantities
//   node qatom.mjs commodity "descriptor" 0.25
//   node qatom.mjs validate <hash> <nonce> <timestamp> [--redeem]   GET checks, --redeem POSTs (one-shot)
//   node qatom.mjs revenue [catalog_item_id]
//   node qatom.mjs purchase <transaction_id>
// Env: TODAQ_BASE_URL (override), TODAQ_ENV, TODAQ_CLIENT_ID, TODAQ_CLIENT_SECRET, TODAQ_TWIN_ID, TODAQ_DQ. Reads empire/stack/.env if present.
import { readFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const envFile = resolve(here, "../../stack/.env");
if (existsSync(envFile)) {
  for (const line of readFileSync(envFile, "utf8").split("\n")) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
    if (m && !(m[1] in process.env)) process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
}

const HOSTS = { production: "https://pay.m.todaq.net", staging: "https://pay.stage.m.todaq.net" };
const args = process.argv.slice(2);
const BOOL_FLAGS = new Set(["redeem", "json"]);
const flag = (name, dflt) => { const i = args.indexOf(`--${name}`); return i >= 0 ? args[i + 1] : dflt; };
const has = (name) => args.includes(`--${name}`);
const positional = [];
for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith("--")) { if (!BOOL_FLAGS.has(args[i].slice(2))) i++; continue; }
  positional.push(args[i]);
}
const cmd = positional[0] ?? "help";
const env = flag("env", process.env.TODAQ_ENV || "staging");
const BASE = process.env.TODAQ_BASE_URL || HOSTS[env];   // TODAQ_BASE_URL overrides (tests/mocks)
if (!BASE) { console.error(`unknown env ${env}`); process.exit(2); }

async function api(method, path, { body, token, basic } = {}) {
  const headers = { accept: "application/json" };
  if (body) headers["content-type"] = "application/json";
  if (token) headers.authorization = `Bearer ${token}`;
  if (basic) headers.authorization = `Basic ${Buffer.from(basic).toString("base64")}`;
  const res = await fetch(BASE + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  const text = await res.text();
  let json; try { json = text ? JSON.parse(text) : null; } catch { json = { raw: text }; }
  if (!res.ok) throw new Error(`${method} ${path} → ${res.status} ${text.slice(0, 300)}`);
  return json;
}

const need = (k) => { const v = process.env[k]; if (!v) { console.error(`missing ${k} (run: qatom.mjs signup)`); process.exit(1); } return v; };

async function token() {
  const r = await api("POST", "/v4/account/oauth/token", { basic: `${need("TODAQ_CLIENT_ID")}:${need("TODAQ_CLIENT_SECRET")}` });
  return r.access_token;
}

async function signup() {
  const acct = await api("POST", "/v4/account");
  const s = Array.isArray(acct.secrets) ? acct.secrets[0] : acct.secrets;
  if (!s?.client_id || !s?.client_secret) throw new Error(`unexpected /v4/account response: ${JSON.stringify(acct).slice(0, 300)}`);
  process.env.TODAQ_CLIENT_ID = s.client_id; process.env.TODAQ_CLIENT_SECRET = s.client_secret;
  const tok = await token();
  const dqs = await api("GET", "/v4/dq", { token: tok });
  const list = Array.isArray(dqs) ? dqs : dqs.dqs ?? dqs.result ?? [];
  const dq = list.find((d) => /usd/i.test(d.shortcode ?? d.name ?? "")) ?? list[0];
  if (!dq) throw new Error("no digital quantity returned by /v4/dq");
  const dqHash = dq.hash ?? dq.id;
  const twin = await api("POST", "/v4/twin", { token: tok, body: { dq: dqHash } });
  const descriptor = flag("descriptor", "NOIZY test line — one voice line");
  const cost = Number(flag("cost", "0.25"));
  const commodity = await api("POST", "/v4/commodity", { token: tok, body: { descriptor, cost, dq: dqHash, twin_id: twin.id } });
  const out = {
    TODAQ_ENV: env,
    TODAQ_ACCOUNT_ID: acct.id,
    TODAQ_CLIENT_ID: s.client_id,
    TODAQ_CLIENT_SECRET: s.client_secret,
    TODAQ_PUBLIC_SECRET: s.public_secret,
    TODAQ_DQ: dqHash,
    TODAQ_TWIN_ID: twin.id,
    TODAQ_TWIN_KEY: twin.key,
    TODAQ_TWIN_HOSTNAME: twin.hostname,
    TODAQ_TEST_COMMODITY_HASH: commodity.hash,
  };
  if (has("json")) console.log(JSON.stringify(out, null, 2));
  else for (const [k, v] of Object.entries(out)) if (v !== undefined) console.log(`${k}=${v}`);
  console.error(`\n✅ Qatom ${env} account ${acct.id} · twin ${twin.id} (${dq.shortcode ?? dq.name}) · test item "${descriptor}" @ ${cost} → hash ${commodity.hash}`);
  console.error("⚠ client_secret and twin key are shown once. Store them (empire/stack/.env + Proton Pass).");
}

async function whoami() {
  const tok = await token();
  const twinId = need("TODAQ_TWIN_ID");
  let twin; try { twin = await api("GET", `/v4/twin/${twinId}`, { token: tok }); } catch { twin = await api("GET", "/v4/twins", { token: tok }); }
  console.log(JSON.stringify({ env, base: BASE, client_id: process.env.TODAQ_CLIENT_ID, twin }, null, 2));
}

const commands = {
  help: async () => console.log(readFileSync(fileURLToPath(import.meta.url), "utf8").split("\n").slice(1, 14).join("\n").replace(/^\/\/ ?/gm, "")),
  signup,
  whoami,
  dq: async () => console.log(JSON.stringify(await api("GET", "/v4/dq", { token: await token() }), null, 2)),
  commodity: async () => {
    const [, descriptor, cost] = positional;
    if (!descriptor || !cost) { console.error('usage: commodity "descriptor" 0.25'); process.exit(2); }
    const r = await api("POST", "/v4/commodity", { token: await token(), body: { descriptor, cost: Number(cost), dq: need("TODAQ_DQ"), twin_id: need("TODAQ_TWIN_ID") } });
    console.log(JSON.stringify(r, null, 2));
  },
  validate: async () => {
    const [, hash, nonce, timestamp] = positional;
    if (!hash || !nonce || !timestamp) { console.error("usage: validate <hash> <nonce> <timestamp> [--redeem]"); process.exit(2); }
    const tok = await token();
    const r = has("redeem")
      ? await api("POST", `/v4/payment/${hash}/validate`, { token: tok, body: { nonce, timestamp: Number(timestamp) } })
      : await api("GET", `/v4/payment/${hash}/validate?nonce=${encodeURIComponent(nonce)}&timestamp=${encodeURIComponent(timestamp)}`, { token: tok });
    console.log(JSON.stringify(r, null, 2));
  },
  revenue: async () => {
    const q = positional[1] ? `?catalog_item_id=${encodeURIComponent(positional[1])}` : "";
    console.log(JSON.stringify(await api("GET", `/v4/catalog/revenue${q}`, { token: await token() }), null, 2));
  },
  purchase: async () => {
    if (!positional[1]) { console.error("usage: purchase <transaction_id>"); process.exit(2); }
    console.log(JSON.stringify(await api("GET", `/v4/catalog/purchases/${positional[1]}`, { token: await token() }), null, 2));
  },
};

(commands[cmd] ?? commands.help)().catch((e) => {
  const net = /fetch failed|ENOTFOUND|ECONNREFUSED/.test(String(e.cause ?? e.message));
  console.error(`qatom: ${e.message}${net ? ` — cannot reach ${BASE} (network/DNS)` : ""}`);
  process.exit(1);
});
