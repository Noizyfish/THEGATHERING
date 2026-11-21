"""OSC bridge :9792 — Open Stage Control → engine / ENGR / HomeKit. Stdlib UDP + minimal OSC decoder (no python-osc needed).

  /noizystdz/voice <id>          → hub POST /voice   (switches FX + labels takes)
  /noizystdz/preset <name>       → hub POST /voice {preset override}
  /noizystdz/consent <speaker>   → hub POST /consent (display name = speaker; refine on the hub page)
  /engr/home/scene <name>        → engr home scene <name>
  /engr/home <acc> <state…>      → engr home <acc> <state>
  /engr/hijack <start|stop> <S>  → engr hijack …
  /engr/logic <action> [arg]     → engr logic …
  /fx/<param> <0..16383>         → hub POST /fx {param: float}   (14-bit from O-S-C, if you route FX knobs here instead of MIDI)
MIDI (faders, arm/mute/solo, transport, 14-bit CC knobs) goes straight from O-S-C to the IAC bus — not through here — for zero added latency.
"""
from __future__ import annotations

import json
import socket
import struct
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGR = str(HERE.parent / "engr")
HUB = "http://127.0.0.1:9790"


def decode(data: bytes):
    def s(i):
        e = data.index(b"\0", i)
        return data[i:e].decode(), (e + 4) & ~3
    addr, i = s(0)
    if i >= len(data) or data[i:i + 1] != b",":
        return addr, []
    tags, i = s(i)
    args = []
    for t in tags[1:]:
        if t == "i":
            args.append(struct.unpack(">i", data[i:i + 4])[0]); i += 4
        elif t == "f":
            args.append(struct.unpack(">f", data[i:i + 4])[0]); i += 4
        elif t == "s":
            v, i = s(i); args.append(v)
        elif t == "T":
            args.append(True)
        elif t == "F":
            args.append(False)
    return addr, args


def post(path: str, body: dict) -> None:
    req = urllib.request.Request(HUB + path, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=2).read()
    except Exception as e:
        print(f"hub {path}: {e}", file=sys.stderr)


def handle(addr: str, args: list, dry: bool = False) -> str | None:
    # O-S-C buttons send their preArgs + on/off value (1/0). Ignore releases; strip the trailing value on presses.
    if addr.startswith(("/engr", "/noizystdz")) and args and isinstance(args[-1], (int, float, bool)) and not isinstance(args[-1], str):
        if args[-1] in (0, 0.0, False):
            return None
        args = args[:-1]
    if addr.startswith("/fx/"):
        v = args[0] if args else 0
        body = {addr[4:]: (v / 16383.0 if isinstance(v, int) else float(v))}
        return f"POST /fx {body}" if dry else post("/fx", body)
    if addr == "/noizystdz/voice":
        return f"POST /voice {args[0]}" if dry else post("/voice", {"id": args[0]})
    if addr == "/noizystdz/preset":
        return f"POST /voice preset={args[0]}" if dry else post("/voice", {"preset": args[0]})
    if addr == "/noizystdz/consent":
        return f"POST /consent {args[0]}" if dry else post("/consent", {"speaker_id": args[0], "display_name": args[0], "scopes": ["record", "transcribe", "train"]})
    if addr.startswith("/engr/"):
        parts = addr.split("/")[2:] + [str(a) for a in args]
        cmd = [ENGR, *parts]
        if dry:
            return " ".join(cmd)
        subprocess.Popen(cmd)
        return None
    return f"ignored {addr}" if dry else None


def main(port: int = 9792) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    print(f"OSC bridge on udp/{port} → hub {HUB}, engr {ENGR}", file=sys.stderr)
    while True:
        data, _ = sock.recvfrom(4096)
        try:
            addr, args = decode(data)
            handle(addr, args)
        except Exception as e:
            print(f"bad packet: {e}", file=sys.stderr)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 9792)
