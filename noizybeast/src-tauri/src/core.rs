//! Pure-Rust core — no Tauri. 14-bit MIDI (mirrors engr/osc/midi14.py and NoizyKit/Midi14.swift byte-for-byte), OSC, RustDesk links.

pub const MAX14: u16 = 16383;

pub fn to14(x: f64) -> u16 { (x.clamp(0.0, 1.0) * MAX14 as f64).round() as u16 }
pub fn from14(v: u16) -> f64 { v.min(MAX14) as f64 / MAX14 as f64 }
pub fn split14(v: u16) -> (u8, u8) { let v = v.min(MAX14); (((v >> 7) & 0x7F) as u8, (v & 0x7F) as u8) }
pub fn join14(msb: u8, lsb: u8) -> u16 { ((msb as u16 & 0x7F) << 7) | (lsb as u16 & 0x7F) }

/// 14-bit CC pair: MSB on `cc` (0-31), LSB on `cc+32`. channel 1-16.
pub fn cc14(channel: u8, cc: u8, x: f64) -> Result<[[u8; 3]; 2], String> {
    if cc > 31 { return Err("14-bit CC MSB number must be 0-31".into()); }
    let st = 0xB0 | ((channel.saturating_sub(1)) & 0x0F);
    let (m, l) = split14(to14(x));
    Ok([[st, cc, m], [st, cc + 32, l]])
}

/// Mackie fader position as pitch bend [status, lsb, msb].
pub fn pitchbend14(channel: u8, x: f64) -> [u8; 3] {
    let st = 0xE0 | ((channel.saturating_sub(1)) & 0x0F);
    let (m, l) = split14(to14(x));
    [st, l, m]
}

pub fn mcu_note(action: &str) -> Result<u8, String> {
    let parts: Vec<&str> = action.split_whitespace().collect();
    match parts.as_slice() {
        ["rewind"] => Ok(91), ["ffwd"] => Ok(92), ["stop"] => Ok(93), ["play"] => Ok(94), ["record"] => Ok(95),
        ["cycle"] => Ok(86), ["click"] => Ok(89), ["marker"] => Ok(84), ["save"] => Ok(80), ["undo"] => Ok(81),
        [bank, n] => {
            let base = match *bank { "arm" => 0, "solo" => 8, "mute" => 16, "select" => 24, _ => return Err(format!("unknown bank {bank}")) };
            let ch: u8 = n.parse().map_err(|_| "channel must be 1-8".to_string())?;
            if !(1..=8).contains(&ch) { return Err("MCU channel strips are 1-8".into()); }
            Ok(base + ch - 1)
        }
        _ => Err(format!("unknown MCU action {action:?}")),
    }
}

/// `rustdesk://connect/<id>?password=…` deep link (RustDesk ≥1.2). Password optional; never log it.
pub fn rustdesk_url(id: &str, password: Option<&str>) -> String {
    let id: String = id.chars().filter(|c| c.is_ascii_digit()).collect();
    match password { Some(p) if !p.is_empty() => format!("rustdesk://connect/{id}?password={}", urlencode(p)), _ => format!("rustdesk://connect/{id}") }
}

fn urlencode(s: &str) -> String {
    s.bytes().map(|b| match b { b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => (b as char).to_string(), _ => format!("%{b:02X}") }).collect()
}

/// OSC packet for the NOIZYSTDZ bridge (:9792). Strings and ints/floats only.
pub fn osc(addr: &str, args: &[OscArg]) -> Vec<u8> {
    let mut out = Vec::new();
    pad(&mut out, addr.as_bytes());
    let mut tags = String::from(",");
    for a in args { tags.push(match a { OscArg::I(_) => 'i', OscArg::F(_) => 'f', OscArg::S(_) => 's' }); }
    pad(&mut out, tags.as_bytes());
    for a in args {
        match a { OscArg::I(i) => out.extend(i.to_be_bytes()), OscArg::F(f) => out.extend(f.to_be_bytes()), OscArg::S(s) => pad(&mut out, s.as_bytes()) }
    }
    out
}
fn pad(out: &mut Vec<u8>, b: &[u8]) { out.extend(b); out.push(0); while out.len() % 4 != 0 { out.push(0); } }

#[derive(Debug, Clone, PartialEq)]
pub enum OscArg { I(i32), F(f32), S(String) }

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn roundtrip() { for v in [0u16, 1, 127, 128, 8192, 16383] { let (m, l) = split14(v); assert_eq!(join14(m, l), v); } assert_eq!(to14(0.5), 8192); }
    #[test] fn matches_python_and_swift() {
        assert_eq!(cc14(1, 7, 0.75).unwrap(), [[176, 7, 95], [176, 39, 127]]);
        assert_eq!(pitchbend14(3, 0.0), [0xE2, 0, 0]);
        assert_eq!(pitchbend14(9, 1.0), [0xE8, 127, 127]);
        assert!(cc14(1, 40, 0.5).is_err());
    }
    #[test] fn mcu() { assert_eq!(mcu_note("play").unwrap(), 94); assert_eq!(mcu_note("mute 8").unwrap(), 23); assert!(mcu_note("arm 9").is_err()); }
    #[test] fn rustdesk() {
        assert_eq!(rustdesk_url("123 456 789", None), "rustdesk://connect/123456789");
        assert_eq!(rustdesk_url("123456789", Some("p@ss w")), "rustdesk://connect/123456789?password=p%40ss%20w");
    }
    #[test] fn osc_packet() {
        let p = osc("/noizystdz/voice", &[OscArg::S("anim-01".into())]);
        assert_eq!(&p[..20], b"/noizystdz/voice\0\0\0\0");
        assert_eq!(&p[20..24], b",s\0\0");
        assert_eq!(&p[24..], b"anim-01\0");
    }
}
