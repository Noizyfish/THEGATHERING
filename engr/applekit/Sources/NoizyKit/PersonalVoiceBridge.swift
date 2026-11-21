import AVFoundation

/// Apple Personal Voice (iOS 17+/macOS 14+): RSP and LINA each record ~150 phrases in Settings → Accessibility → Personal Voice.
/// With the user's permission the app can speak with that voice — an on-device, Apple-sandboxed twin for LUCY/LINA *until* NOIZYVOX models exist.
/// Not a replacement: Personal Voice can't be exported, trained on, or run on GOD. It's the interim voice and a consent reference point.
public final class PersonalVoiceBridge: NSObject, AVSpeechSynthesizerDelegate {
    private let synth = AVSpeechSynthesizer()
    public private(set) var voices: [AVSpeechSynthesisVoice] = []

    public override init() { super.init(); synth.delegate = self }

    public static func authorize() async -> Bool {
        #if os(iOS) || os(macOS) || os(visionOS)
        if #available(iOS 17, macOS 14, *) {
            return await withCheckedContinuation { c in AVSpeechSynthesizer.requestPersonalVoiceAuthorization { c.resume(returning: $0 == .authorized) } }
        }
        #endif
        return false
    }

    public func refresh() {
        if #available(iOS 17, macOS 14, *) {
            voices = AVSpeechSynthesisVoice.speechVoices().filter { $0.voiceTraits.contains(.isPersonalVoice) }
        }
    }

    /// Speak as a named Personal Voice ("Robert", "LINA") or the first available.
    public func speak(_ text: String, as name: String? = nil, rate: Float = 0.48, pitch: Float = 1.0) {
        let u = AVSpeechUtterance(string: text)
        u.voice = voices.first { name == nil || $0.name.localizedCaseInsensitiveContains(name!) } ?? AVSpeechSynthesisVoice(language: "en-CA")
        u.rate = rate; u.pitchMultiplier = pitch
        synth.speak(u)
    }
}
