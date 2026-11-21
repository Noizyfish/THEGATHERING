"""NOIZYSTDZ hub — stdlib HTTP + SSE on :9790. Phones/laptops in the room open it; the engine posts to it.

    GET  /                      → studio page (who's live, current voice, transcript stream, consent buttons)
    GET  /events                → SSE: transcript segments, voice changes, consent changes
    GET  /roster                → characters/roster.json
    GET  /presets               → list of presets
    POST /voice {id}            → set the current voice/character (engine labels RSP takes with it; switches FX)
    POST /consent {speaker_id, display_name, scopes[]}  → signs an HVS consent record for this session
    POST /segment {...Segment}  → engine → hub → everyone in the room sees the line appear
    GET  /state                 → json
No frameworks on purpose: this must run on GOD forever with nothing but python3.
"""
from __future__ import annotations

import argparse
import json
import queue
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import config as cfg
from .consent import Consent, load_key, save, sign

STATE: dict = {"session": None, "voice": None, "live": [], "consents": {}, "segments": [], "fx": {}, "room": []}
PRIVATE = ("10.", "192.168.", "127.", "172.16.", "172.17.", "172.18.", "172.19.", "172.2", "172.30.", "172.31.")
SUBS: list[queue.Queue] = []
LOCK = threading.Lock()


def broadcast(kind: str, data: dict) -> None:
    msg = f"event: {kind}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    with LOCK:
        for q in list(SUBS):
            q.put(msg)


PAGE = """<!doctype html><meta charset=utf-8><title>NOIZYSTDZ</title>
<meta name=viewport content="width=device-width,initial-scale=1">
<style>body{font:16px/1.4 -apple-system,system-ui;background:#0b0b10;color:#eee;margin:0;padding:1rem}
h1{font-weight:900;letter-spacing:.08em;margin:0 0 .5rem}#voice{font-size:1.6rem;color:#ffd166}
button{font:inherit;padding:.6rem 1rem;border-radius:.6rem;border:0;background:#2a2a3a;color:#eee;margin:.2rem}
button.on{background:#06d6a0;color:#000}#log{margin-top:1rem}.seg{padding:.3rem 0;border-bottom:1px solid #222}
.seg b{color:#8ecae6}.seg i{color:#ffd166}small{color:#888}</style>
<h1>NOIZYSTDZ</h1><div>session <b id=sess>—</b> · voice <span id=voice>—</span></div>
<div id=roster></div><div id=consent></div><div id=log></div>
<script>
const $=s=>document.querySelector(s);
fetch('/roster').then(r=>r.json()).then(r=>{$('#roster').innerHTML=r.voices.map(v=>`<button data-id="${v.id}" title="${v.script}">${v.name}</button>`).join('');
 $('#roster').onclick=e=>{const id=e.target.dataset.id;if(id)fetch('/voice',{method:'POST',body:JSON.stringify({id})})}});
$('#consent').innerHTML=['RSP','LINA_SRC','GUEST_B','GUEST_C'].map(s=>`<button data-s="${s}">consent: ${s}</button>`).join('');
$('#consent').onclick=e=>{const s=e.target.dataset.s;if(!s)return;const name=prompt('Display name for '+s);if(!name)return;
 fetch('/consent',{method:'POST',body:JSON.stringify({speaker_id:s,display_name:name,scopes:['record','transcribe','train']})})};
const es=new EventSource('/events');
es.addEventListener('state',e=>{const s=JSON.parse(e.data);$('#sess').textContent=s.session||'—';$('#voice').textContent=s.voice?s.voice.name:'—';
 document.querySelectorAll('#consent button').forEach(b=>b.classList.toggle('on',!!s.consents[b.dataset.s]))});
es.addEventListener('segment',e=>{const s=JSON.parse(e.data);const d=document.createElement('div');d.className='seg';
 d.innerHTML=`<small>${s.t0.toFixed(1)}s</small> <b>${s.speaker}</b>${s.character?` <i>as ${s.character}</i>`:''} ${s.text}`;$('#log').prepend(d)});
</script>"""


class H(BaseHTTPRequestHandler):
    roster: dict = {}
    session_dir: Path = Path(".")

    def log_message(self, *a):  # quiet
        pass

    def _json(self, code: int, data) -> None:
        b = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(b)))
        self.send_header("access-control-allow-origin", "*")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/":
            b = PAGE.encode()
            self.send_response(200); self.send_header("content-type", "text/html; charset=utf-8"); self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b)
        elif self.path == "/roster":
            self._json(200, self.roster)
        elif self.path == "/presets":
            self._json(200, sorted(p.stem for p in (cfg.ROOT / "presets").glob("*.json")))
        elif self.path == "/state":
            self._json(200, STATE)
        elif self.path == "/healthz":
            self._json(200, {"ok": True, "service": "noizystdz-hub"})
        elif self.path == "/events":
            q: queue.Queue = queue.Queue()
            with LOCK:
                SUBS.append(q)
            self.send_response(200); self.send_header("content-type", "text/event-stream"); self.send_header("cache-control", "no-cache"); self.end_headers()
            try:
                self.wfile.write(f"event: state\ndata: {json.dumps(STATE)}\n\n".encode()); self.wfile.flush()
                while True:
                    try:
                        m = q.get(timeout=15)
                    except queue.Empty:
                        m = ": ping\n\n"
                    self.wfile.write(m.encode()); self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                with LOCK:
                    if q in SUBS:
                        SUBS.remove(q)
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("content-length") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/voice":
            if "preset" in body and "id" not in body:
                v = dict(STATE["voice"] or {"id": "manual", "name": "manual"}); v["preset"] = body["preset"]
            else:
                v = next((v for v in self.roster.get("voices", []) if v["id"] == body.get("id")), None)
            if not v:
                return self._json(404, {"error": "unknown voice"})
            STATE["voice"] = v
            (self.session_dir / "current_voice.json").write_text(json.dumps(v))
            broadcast("state", STATE)
            return self._json(200, v)
        if self.path == "/consent":
            c = Consent(speaker_id=body["speaker_id"], display_name=body["display_name"], scopes=list(body.get("scopes") or ["record"]), session_id=STATE["session"] or "unknown")
            sign(c, load_key(self.session_dir / "keys" / f"{c.speaker_id}.ed25519"))
            save(c, self.session_dir / "consent")
            STATE["consents"][c.speaker_id] = {"consent_id": c.consent_id, "scopes": c.scopes, "display_name": c.display_name}
            broadcast("state", STATE)
            return self._json(201, {"consent_id": c.consent_id})
        if self.path == "/fx":
            STATE["fx"].update({k: float(v) for k, v in body.items()})
            (self.session_dir / "fx_live.json").write_text(json.dumps(STATE["fx"]))   # engine polls this for 14-bit knob moves
            broadcast("fx", STATE["fx"])
            return self._json(202, STATE["fx"])
        if self.path == "/home/event":
            if not self.client_address[0].startswith(PRIVATE):
                return self._json(403, {"error": "LAN only"})
            ev = {"event": body.get("event"), "t": __import__("time").time()}
            STATE["room"] = (STATE["room"] + [ev])[-50:]
            with (self.session_dir / "room_events.jsonl").open("a") as f:
                f.write(json.dumps(ev) + "\n")
            broadcast("room", ev)
            if ev["event"] in ("door_open", "noise") and shutil.which("engr"):
                subprocess.Popen(["engr", "logic", "marker"])
            return self._json(202, ev)
        if self.path == "/segment":
            STATE["segments"] = (STATE["segments"] + [body])[-200:]
            broadcast("segment", body)
            return self._json(202, {"ok": True})
        return self._json(404, {"error": "not found"})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="noizystdz hub")
    ap.add_argument("--session", required=True)
    ap.add_argument("--root", type=Path)
    ap.add_argument("--port", type=int)
    ap.add_argument("--host")
    a = ap.parse_args(argv)
    conf = cfg.load()
    H.roster = json.loads((cfg.ROOT / "characters" / "roster.json").read_text())
    H.session_dir = (a.root or cfg.ROOT / "sessions") / a.session
    H.session_dir.mkdir(parents=True, exist_ok=True)
    STATE["session"] = a.session
    host, port = a.host or conf.hub.get("host", "0.0.0.0"), a.port or int(conf.hub.get("port", 9790))
    srv = ThreadingHTTPServer((host, port), H)
    print(f"NOIZYSTDZ hub http://{host}:{port}  session={a.session}", file=sys.stderr)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
