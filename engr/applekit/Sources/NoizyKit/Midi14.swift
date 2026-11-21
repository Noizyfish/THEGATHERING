import Foundation
#if canImport(CoreMIDI)
import CoreMIDI
#endif

/// 14-bit MIDI, mirroring engr/osc/midi14.py exactly (same packing, same MCU map).
public enum Midi14 {
    public static let max14 = 16383

    public static func to14(_ x: Double) -> Int { Int((min(1, max(0, x)) * Double(max14)).rounded()) }
    public static func from14(_ v: Int) -> Double { Double(min(max14, max(0, v))) / Double(max14) }
    public static func split(_ v: Int) -> (msb: UInt8, lsb: UInt8) {
        let c = min(max14, max(0, v)); return (UInt8((c >> 7) & 0x7F), UInt8(c & 0x7F))
    }
    public static func join(msb: UInt8, lsb: UInt8) -> Int { (Int(msb & 0x7F) << 7) | Int(lsb & 0x7F) }

    /// CC pair (MSB on cc, LSB on cc+32). channel 1-16, cc 0-31.
    public static func cc(channel: Int, cc: Int, value: Double) -> [[UInt8]] {
        precondition((0...31).contains(cc), "14-bit CC MSB must be 0-31")
        let st = UInt8(0xB0 | ((channel - 1) & 0x0F)); let (m, l) = split(to14(value))
        return [[st, UInt8(cc), m], [st, UInt8(cc + 32), l]]
    }

    /// Mackie Control fader position as pitch bend [status, lsb, msb].
    public static func pitchBend(channel: Int, value: Double) -> [UInt8] {
        let st = UInt8(0xE0 | ((channel - 1) & 0x0F)); let (m, l) = split(to14(value)); return [st, l, m]
    }

    public enum MCU: UInt8 { case rewind = 91, ffwd = 92, stop = 93, play = 94, record = 95, cycle = 86, click = 89, marker = 84 }
    public static func mcuNote(_ n: MCU, on: Bool) -> [UInt8] { [0x90, n.rawValue, on ? 127 : 0] }
    public static func strip(_ bank: String, _ ch: Int) -> UInt8 {
        let base: UInt8 = ["arm": 0, "solo": 8, "mute": 16, "select": 24][bank] ?? 0
        return base + UInt8(max(1, min(8, ch)) - 1)
    }
}

#if canImport(CoreMIDI) && !os(watchOS)
/// CoreMIDI sender: finds the `ENGR MCU` IAC bus (macOS) or publishes a virtual source "NOIZYSTDZ" (iOS, over Network MIDI).
public final class MidiOut {
    private var client = MIDIClientRef(); private var port = MIDIPortRef(); private var dest = MIDIEndpointRef(); private var virtualSrc = MIDIEndpointRef()
    public private(set) var destinationName: String?

    public init(busName: String = "ENGR MCU") throws {
        MIDIClientCreateWithBlock("NOIZYSTDZ" as CFString, &client, nil)
        MIDIOutputPortCreate(client, "out" as CFString, &port)
        for i in 0..<MIDIGetNumberOfDestinations() {
            let d = MIDIGetDestination(i); var name: Unmanaged<CFString>?
            MIDIObjectGetStringProperty(d, kMIDIPropertyDisplayName, &name)
            if let n = name?.takeRetainedValue() as String?, n.contains(busName) { dest = d; destinationName = n; break }
        }
        if dest == 0 { MIDISourceCreateWithProtocol(client, "NOIZYSTDZ" as CFString, ._1_0, &virtualSrc) }
    }

    public func send(_ bytes: [UInt8]) {
        var pkt = MIDIEventList(); let p = MIDIEventListInit(&pkt, ._1_0)
        let words = toUMP(bytes)
        _ = words.withUnsafeBufferPointer { MIDIEventListAdd(&pkt, 1024, p, 0, $0.count, $0.baseAddress!) }
        if dest != 0 { MIDISendEventList(port, dest, &pkt) } else { MIDIReceivedEventList(virtualSrc, &pkt) }
    }
    public func send(_ msgs: [[UInt8]]) { msgs.forEach(send) }

    /// MIDI 1.0 channel voice message → one UMP word (message type 2, group 0).
    func toUMP(_ b: [UInt8]) -> [UInt32] {
        guard b.count >= 2 else { return [] }
        return [UInt32(0x20) << 24 | UInt32(b[0]) << 16 | UInt32(b[1]) << 8 | UInt32(b.count > 2 ? b[2] : 0)]
    }

    // Convenience — same verbs as `engr logic …`
    public func fader(_ ch: Int, _ value: Double) { send(Midi14.pitchBend(channel: ch, value: value)) }
    public func knob14(_ cc: Int, _ value: Double, channel: Int = 1) { send(Midi14.cc(channel: channel, cc: cc, value: value)) }
    public func press(_ n: Midi14.MCU) { send(Midi14.mcuNote(n, on: true)); send(Midi14.mcuNote(n, on: false)) }
    public func strip(_ bank: String, _ ch: Int) { let n = Midi14.strip(bank, ch); send([0x90, n, 127]); send([0x90, n, 0]) }
}
#endif
