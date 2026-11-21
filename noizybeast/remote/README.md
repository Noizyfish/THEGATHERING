# Remote — RustDesk inside NOIZYBEAST.IDE

RustDesk (open source, Rust) gives every device a window onto **GOD** (the M2 Ultra) and onto each other: RSP one-handed from the iPhone/iPad, LINA from her laptop, Nicholas watching the Friday reel from anywhere, and ENGR debugging the booth iPad. The IDE's *Remote* panel wraps it; the relay is ours, not RustDesk's public servers.

## 1. Relay (once)
```bash
cd noizybeast/remote
RUSTDESK_RELAY_HOST=relay.noizy.ai docker compose -f docker-compose.rustdesk.yml up -d
cat data/id_ed25519.pub            # → RS_PUB_KEY for every client
```
DNS: `relay.noizy.ai` → the VM (Cloudflare DNS, **grey cloud** — not proxied). Open 21115-21119 tcp + 21116 udp.

## 2. Clients
- macOS GOD: `brew install --cask rustdesk`; Settings → Network → ID server `relay.noizy.ai`, Key = pubkey. Set a permanent password; enable *Unattended access*; turn on *Allow remote configuration modification* OFF.
- iOS/iPadOS: RustDesk from the App Store, same server/key. Add GOD as a favourite.
- Mass-config URL (RustDesk ≥1.2.3): `rustdesk://config/<base64 of {"host":"relay.noizy.ai","key":"<pubkey>"}>` — the IDE's Remote panel prints it.

## 3. From the IDE
Remote panel → enter GOD's 9-digit ID (+ password) → `rustdesk://connect/<id>?password=…` is opened by the OS; the password is never persisted by NOIZYBEAST. `rustdesk_id` shows this machine's ID so it can be added elsewhere.

## 4. Security posture
- Relay traffic is E2E encrypted (NaCl) between peers; hbbs/hbbr only broker. Still, restrict relay ports to your IPs via the VM firewall where possible, and keep *Direct IP access* off.
- GOD: deny-list everyone except the family's IDs (Settings → Security → Access → *Only allow listed IDs*).
- Prefer Tailscale/Proton VPN into the LAN and connect by LAN IP when both ends are on it; RustDesk falls back to the relay otherwise.
- Nothing from RustDesk touches NOIZYVOX audio; it's screen/keyboard only.
