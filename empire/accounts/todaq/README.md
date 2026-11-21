# TODAQ Micro → Qatom — integration notes (verified 2026-11-21)

TODAQ Micro now trades as **Qatom** (TODAQ Financial Inc, Toronto). USD-denominated wallet-to-wallet micropayments on the TODA/ADOT protocols. Wallets are **twins** holding **USD-TDN** (1 = USD 1). 0% take rate, no gas; sub-second settlement; each payment is a TODA file with its own proof of provenance.

Sources: `github.com/TODAQmicro/docs` (source of docs.m.todaq.net, updated 2026-11-18), `TODAQmicro/qatom-skill`, npm registry, qatom.ai. Items we could **not** verify live: KYC for cash-out, Console URL, buyer geography, CAD pricing (only a USD DQ was found).

## Hosts

| | |
|---|---|
| Production API | `https://pay.m.todaq.net` |
| Staging API (own accounts, own DQ) | `https://pay.stage.m.todaq.net` |
| Docs (Scalar, from `/v4/openapi.json`) | `https://docs.m.todaq.net` |
| Browser SDK | `https://cdn.m.todaq.net/micropay.js` · npm `@todaqmicro/payment-js@^0.5.6` |
| Wallet top-up | `https://load.m.todaq.net` |
| MCP server (agents) | `https://mcp.m.todaq.net/mcp` |

## Sign-up is an API call

```bash
scripts/empire signup todaq --auto          # staging
TODAQ_ENV=production scripts/empire signup todaq --auto
```
which runs [`qatom.mjs signup`](qatom.mjs):

1. `POST /v4/account` (no auth) → `id`, `secrets[{public_secret, client_id, client_secret}]` — **client_secret is returned once**.
2. `POST /v4/account/oauth/token` with HTTP Basic `client_id:client_secret` → `access_token` (1 h).
3. `GET /v4/dq` → digital quantities (production: `USD TDN`).
4. `POST /v4/twin {dq}` → `id, hostname, key, balances` — `key` is a secret.
5. `POST /v4/commodity {descriptor, cost, dq, twin_id}` → `hash` (what the payment element needs). `cost` is in dollars: `0.25` = 25¢. Min paid price 0.001.

`qatom.mjs` also does `whoami`, `dq`, `commodity`, `validate [--redeem]`, `revenue`, `purchase`.

## Selling a voice line on the web (PWA / Gabriel dashboard)

```html
<script src="https://cdn.m.todaq.net/micropay.js"></script>
<div id="buy"></div>
<script>
  const mp = loadMicroPayments("<TODAQ_PUBLIC_SECRET>", { apiVersion: "main" });   // apiVersion is mandatory
  mp.elements().create("payment", { hash: "<COMMODITY_HASH>", theme: "dark", leading: "Hear the line", decimalPoints: 2 }).mount("#buy");
  document.addEventListener("payment", async (e) => {
    const { hash, hostname, nonce, timestamp } = e.detail;               // anyone can fire this — never trust it client-side
    const r = await fetch("/purchases", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ hash, nonce, timestamp }) });
    if (r.ok) playTheLine(await r.json());
  });
</script>
```

Server (Gabriel daemon / Express) redeems **once**, then delivers:

```js
// POST /purchases
const tok = await qatomToken();                                           // Basic client_id:client_secret → Bearer
const r = await fetch(`${BASE}/v4/payment/${hash}/validate`, { method: "POST", headers: { authorization: `Bearer ${tok}`, "content-type": "application/json" }, body: JSON.stringify({ nonce, timestamp }) });
if (r.status !== 200) return res.status(402).end();                       // 400 = already redeemed or unknown
ledger.record({ hash, nonce, timestamp });                                 // persist — replay protection is yours
res.json({ url: signedAudioUrl(hash) });
```

`GET /v4/payment/{hash}/validate?nonce=&timestamp=` checks without redeeming (`used_at` null until redeemed).

**No webhooks exist.** Confirmation is pull-based (event → your server → validate). For agent/API paywalls (`POST /v4/paywall`), Qatom calls *your* fulfillment URL with `X-Qatom-Transaction-Id`; confirm expensive ones with `GET /v4/catalog/purchases/{transaction_id}`.

## Repeated charges / "Sign in with Qatom"

`elements().create("auth", { hash })` → `authorized` event with `detail.session` (1 h). Use the session with `/v4/paywall` for one-approval-at-a-time or budgeted charges — right for a LUCY conversation that bills per line.

## Money

- Plans (USD): Builder free (1 agent, 5 items, 25 tx/mo) · Pro 20/mo · Max 300/mo. 0% take rate.
- Buyers top up 5/10/20/50 by card or Apple Pay (Stripe; card min ≈ USD 0.50) → price sub-50¢ items for **funded wallets**, or bundle.
- Cash-out: ACH to a **US or Canadian** bank, USD 1 flat, 10 USD-TDN minimum, 2–5 business days (reserves held at RBC). At 5¢ a line you need ≥ 200 sales per payout.
- On-ramp by wire/ACH: email support@todaq.net ("Buy TDN", 0.50–100 USD).

## SDK reality check

| Package | State | Use? |
|---|---|---|
| `@todaqmicro/payment-js` 0.5.6 (browser) | current (2026-11-18) | **yes** |
| `@todaqmicro/payment-node` 0.4.0 | targets `/v2`, README names a non-existent package, logs client secret + tokens to console | **no** — use `qatom.mjs` / plain `fetch` on `/v4` |
| `payment-ios`, `payment-android`, `payment-flutter` | empty stubs (2023) | no — LUCY hosts the payment element in a `WKWebView` and relays the `payment` event to the daemon |
| `qatom-skill` (MCP) | current | yes, for Gabriel-as-agent buying/selling |

## Where it lands in the empire

- `_mc96-common/gabriel` daemon: `/purchases` route + ledger (D1 `mc96-central` or Forgejo issue via n8n).
- LUCY iOS: WKWebView payment sheet → `payment` event → daemon → audio. Apple IAP rules for digital goods are a separate legal question — check before App Store submission.
- n8n: `todaq` webhook path → validate → Forgejo ledger issue → nightly Claude digest counts revenue (`GET /v4/catalog/revenue`).
- TODA proof-of-provenance = receipt trail for voice IP. **Consent logic (HVS) stays in our backend** — Qatom has no rights-management features.
