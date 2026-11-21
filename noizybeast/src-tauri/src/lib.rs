//! NOIZYBEAST.IDE — Tauri commands. Thin: real work lives in engr/, noizystdz/, scripts/empire (sidecars) and the Rust `core`.
pub mod core;

use serde::Serialize;
use std::{net::UdpSocket, path::PathBuf, process::Command, sync::Mutex};
use tauri::State;

pub struct Beast { pub root: PathBuf, pub midi: Mutex<Option<midir::MidiOutputConnection>> }

#[derive(Serialize)]
pub struct Exec { pub ok: bool, pub stdout: String, pub stderr: String }

fn run(cmd: PathBuf, args: &[String]) -> Exec {
    match Command::new(&cmd).args(args).output() {
        Ok(o) => Exec { ok: o.status.success(), stdout: String::from_utf8_lossy(&o.stdout).into(), stderr: String::from_utf8_lossy(&o.stderr).into() },
        Err(e) => Exec { ok: false, stdout: String::new(), stderr: format!("{}: {e}", cmd.display()) },
    }
}

/// `engr …` — Logic Pro / apps / HomeKit / Talon. Same CLI the Stream Deck and Talon use.
#[tauri::command]
pub fn engr(state: State<Beast>, args: Vec<String>) -> Exec { run(state.root.join("engr/engr"), &args) }

/// `noizystdz …` and `empire …`
#[tauri::command]
pub fn noizystdz(state: State<Beast>, args: Vec<String>) -> Exec { run(state.root.join("noizystdz/noizystdz"), &args) }
#[tauri::command]
pub fn empire(state: State<Beast>, args: Vec<String>) -> Exec { run(state.root.join("scripts/empire"), &args) }

/// Open the `ENGR MCU` IAC bus (or any port containing `name`).
#[tauri::command]
pub fn midi_open(state: State<Beast>, name: String) -> Result<String, String> {
    let out = midir::MidiOutput::new("NOIZYBEAST").map_err(|e| e.to_string())?;
    let port = out.ports().into_iter().find(|p| out.port_name(p).map(|n| n.contains(&name)).unwrap_or(false)).ok_or(format!("MIDI port containing {name:?} not found"))?;
    let pname = out.port_name(&port).unwrap_or_default();
    let conn = out.connect(&port, "noizybeast").map_err(|e| e.to_string())?;
    *state.midi.lock().unwrap() = Some(conn);
    Ok(pname)
}

/// 14-bit: `kind` = "cc" (cc 0-31 → pair) | "pb" (Mackie fader) | "mcu" (button by name: play/arm 3/…)
#[tauri::command]
pub fn midi14(state: State<Beast>, kind: String, channel: u8, cc: u8, value: f64, action: Option<String>) -> Result<(), String> {
    let mut g = state.midi.lock().unwrap();
    let conn = g.as_mut().ok_or("MIDI not open — call midi_open first")?;
    match kind.as_str() {
        "cc" => { for m in core::cc14(channel, cc, value)? { conn.send(&m).map_err(|e| e.to_string())?; } }
        "pb" => conn.send(&core::pitchbend14(channel, value)).map_err(|e| e.to_string())?,
        "mcu" => { let n = core::mcu_note(action.as_deref().unwrap_or(""))?; conn.send(&[0x90, n, 127]).map_err(|e| e.to_string())?; conn.send(&[0x90, n, 0]).map_err(|e| e.to_string())?; }
        _ => return Err("kind must be cc | pb | mcu".into()),
    }
    Ok(())
}

/// OSC to the NOIZYSTDZ bridge (:9792) or Open Stage Control.
#[tauri::command]
pub fn osc_send(target: String, addr: String, args: Vec<serde_json::Value>) -> Result<(), String> {
    let a: Vec<core::OscArg> = args.into_iter().map(|v| match v {
        serde_json::Value::Number(n) if n.is_i64() => core::OscArg::I(n.as_i64().unwrap() as i32),
        serde_json::Value::Number(n) => core::OscArg::F(n.as_f64().unwrap() as f32),
        other => core::OscArg::S(other.as_str().map(|s| s.to_string()).unwrap_or_else(|| other.to_string())),
    }).collect();
    let s = UdpSocket::bind("0.0.0.0:0").map_err(|e| e.to_string())?;
    s.send_to(&core::osc(&addr, &a), target).map_err(|e| e.to_string())?;
    Ok(())
}

/// RustDesk: id of this machine / connect to GOD.
#[tauri::command]
pub fn rustdesk_id() -> Exec { run(PathBuf::from("/Applications/RustDesk.app/Contents/MacOS/RustDesk"), &["--get-id".into()]) }
#[tauri::command]
pub fn rustdesk_connect_url(id: String, password: Option<String>) -> String { core::rustdesk_url(&id, password.as_deref()) }

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run_app() {
    let root = std::env::var("NOIZY_GATHERING").map(PathBuf::from)
        .unwrap_or_else(|_| dirs_home().join("THEGATHERING"));
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .manage(Beast { root, midi: Mutex::new(None) })
        .invoke_handler(tauri::generate_handler![engr, noizystdz, empire, midi_open, midi14, osc_send, rustdesk_id, rustdesk_connect_url])
        .run(tauri::generate_context!())
        .expect("error while running NOIZYBEAST.IDE");
}

fn dirs_home() -> PathBuf { PathBuf::from(std::env::var("HOME").unwrap_or_else(|_| "/Users/m2ultra".into())) }
