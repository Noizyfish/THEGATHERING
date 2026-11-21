// NOIZYBEAST.IDE frontend — vanilla TS. Talks to: Tauri commands (engr/noizystdz/empire/midi/osc/rustdesk), the NOIZYSTDZ hub (:9790 SSE), O-S-C (iframe).
import { invoke } from "@tauri-apps/api/core";
import { openUrl } from "@tauri-apps/plugin-opener";

type Exec = { ok: boolean; stdout: string; stderr: string };
type Voice = { id: string; name: string; category: string; performer: string; preset: string; script: string };
const HUB = localStorage.getItem("hub") ?? "http://127.0.0.1:9790";
const $ = <T extends HTMLElement>(s: string) => document.querySelector(s) as T;
const tauri = "__TAURI_INTERNALS__" in window;

async function engr(...args: string[]): Promise<Exec> {
  if (!tauri) return { ok: false, stdout: "", stderr: "not running inside Tauri — open in NOIZYBEAST.IDE" };
  return invoke<Exec>("engr", { args });
}
function log(el: HTMLElement, text: string, cls = "") { const d = document.createElement("div"); d.className = `seg ${cls}`; d.innerHTML = text; el.prepend(d); }
async function hub(path: string, body?: unknown) {
  const r = await fetch(HUB + path, body ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : undefined);
  return r.ok ? r.json() : Promise.reject(new Error(`${path} ${r.status}`));
}

// ── rail ──
document.querySelectorAll<HTMLButtonElement>("#rail button[data-panel]").forEach(b => b.onclick = () => {
  document.querySelectorAll(".panel, #rail button").forEach(e => e.classList.remove("on"));
  b.classList.add("on"); $(`#${b.dataset.panel}`).classList.add("on");
});

// ── studio ──
let roster: Voice[] = [];
async function loadRoster() {
  try {
    const r = await hub("/roster"); roster = r.voices;
    $<HTMLSelectElement>("#voice").innerHTML = roster.map((v, i) => `<option value="${v.id}">${i + 1}. ${v.name} (${v.category})</option>`).join("");
    $("#reelgrid").innerHTML = roster.map((v, i) => `<span id="rg-${v.id}" title="${v.name}">${i + 1}</span>`).join("");
    const st = await hub("/state"); status({ hub: "✅", voice: st.voice?.name });
  } catch { status({ hub: "❌ (start: noizystdz session <name>)" }); }
}
const stat: Record<string, string> = { hub: "…", midi: "…", voice: "—" };
function status(p: Partial<typeof stat>) { Object.assign(stat, p); $("#status").textContent = `hub: ${stat.hub} · midi: ${stat.midi} · voice: ${stat.voice}`; }

$<HTMLSelectElement>("#voice").onchange = e => hub("/voice", { id: (e.target as HTMLSelectElement).value }).catch(console.error);
$("#roll").onclick = async () => { await hub("/home/event", { event: "record_start" }).catch(() => {}); await engr("logic", "record"); await engr("home", "scene", "record"); };
$("#stop").onclick = async () => { await hub("/home/event", { event: "record_stop" }).catch(() => {}); await engr("logic", "stop"); await engr("home", "scene", "playback"); };
$("#mark").onclick = () => engr("logic", "marker");
$("#consent").onclick = async () => {
  const who = prompt("Speaker id (RSP, LINA_SRC, GUEST_B, GUEST_C)", "RSP"); if (!who) return;
  const name = prompt("Display name", who) ?? who;
  await hub("/consent", { speaker_id: who, display_name: name, scopes: ["record", "transcribe", "train"] });
};
function sse() {
  const es = new EventSource(HUB + "/events");
  es.addEventListener("state", e => { const s = JSON.parse(e.data); status({ voice: s.voice?.name ?? "—" }); if (s.voice) $<HTMLSelectElement>("#voice").value = s.voice.id; });
  es.addEventListener("segment", e => { const s = JSON.parse(e.data); log($("#transcript"), `<small>${(+s.t0).toFixed(1)}s</small> <b>${s.speaker}</b>${s.character ? ` <i>as ${s.character}</i>` : ""} ${s.text}`); if (s.character) document.getElementById(`rg-${s.character}`)?.classList.add("done"); });
  es.addEventListener("room", e => { const r = JSON.parse(e.data); log($("#roomlog"), `🏠 ${r.event}`); });
  es.onerror = () => { es.close(); setTimeout(sse, 3000); };
}

// ── engr console ──
$<HTMLFormElement>("#engrform").onsubmit = async e => {
  e.preventDefault(); const inp = $<HTMLInputElement>("#engrcmd"); const text = inp.value.trim(); if (!text) return; inp.value = "";
  const args = text.startsWith("engr ") ? text.slice(5).split(/\s+/) : /^(logic|app|home|hijack|shortcut|talon|doctor|fcp)\b/.test(text) ? text.split(/\s+/) : ["do", text];
  log($("#engrlog"), `<b>› engr ${args.join(" ")}</b>`);
  const r = await engr(...args); log($("#engrlog"), (r.stdout || "") + (r.stderr ? `<i>${r.stderr}</i>` : ""), r.ok ? "" : "err");
};

// ── surface ──
$("#oscgo").onclick = () => { $<HTMLIFrameElement>("#oscframe").src = $<HTMLInputElement>("#oscurl").value; };

// ── room ──
const SCENES = ["standby", "session", "record", "playback", "sleep", "wrap", "friday"];
$("#scenes").innerHTML = SCENES.map(s => `<button data-scene="${s}" aria-label="Scene ${s}">${s.toUpperCase()}</button>`).join("");
$("#accs").innerHTML = [["onair red", "ON AIR", "hot"], ["onair off", "OFF AIR", ""], ["door lock", "LOCK", ""], ["door unlock", "UNLOCK", ""], ["homepods pause", "PODS ⏸", ""], ["boothfan off", "FAN OFF", ""]].map(([c, l, k]) => `<button data-acc="${c}" class="${k}">${l}</button>`).join("");
$("#scenes").onclick = e => { const s = (e.target as HTMLElement).dataset.scene; if (s) engr("home", "scene", s).then(r => log($("#roomlog"), `scene ${s} → ${r.ok ? "ok" : r.stderr}`)); };
$("#accs").onclick = e => { const c = (e.target as HTMLElement).dataset.acc; if (c) engr("home", ...c.split(" ")).then(r => log($("#roomlog"), `${c} → ${r.ok ? "ok" : r.stderr}`)); };

// ── remote ──
if (tauri) invoke<Exec>("rustdesk_id").then(r => { $("#rdid").textContent = r.ok ? r.stdout.trim() : "RustDesk not installed"; });
$<HTMLFormElement>("#rdform").onsubmit = async e => {
  e.preventDefault();
  const id = $<HTMLInputElement>("#rdtarget").value, pw = $<HTMLInputElement>("#rdpass").value || null;
  const url = tauri ? await invoke<string>("rustdesk_connect_url", { id, password: pw }) : `rustdesk://connect/${id.replace(/\D/g, "")}`;
  $<HTMLInputElement>("#rdpass").value = "";
  if (tauri) await openUrl(url); else location.href = url;
};

// ── thru-line ──
$("#gather").onclick = async () => { $("#thru").textContent = "running empire run …"; const r = tauri ? await invoke<Exec>("empire", { args: ["run", "--quiet"] }) : { ok: false, stdout: "", stderr: "Tauri only" }; $("#thru").textContent = (r.stdout + "\n" + r.stderr).trim(); };
fetch(HUB.replace(/:\d+$/, ":9790") + "/healthz").catch(() => {});

// ── midi ──
if (tauri) invoke<string>("midi_open", { name: "ENGR MCU" }).then(n => status({ midi: `✅ ${n}` })).catch(e => status({ midi: `❌ ${e}` }));

loadRoster().then(sse);
