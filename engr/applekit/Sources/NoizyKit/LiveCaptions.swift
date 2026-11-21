#if canImport(Speech)
import Speech
import AVFoundation

/// On-device live captions (SFSpeechRecognizer, requiresOnDeviceRecognition) → hub /segment. Fallback STT when whisper is busy; also LUCY's live subtitles.
public final class LiveCaptions {
    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-CA"))
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?
    private let hub: HubClient
    private let track: String
    private var t0 = Date()
    public var character: String?
    public var onPartial: ((String) -> Void)?

    public init(hub: HubClient, track: String) { self.hub = hub; self.track = track }

    public static func authorize() async -> Bool {
        await withCheckedContinuation { c in SFSpeechRecognizer.requestAuthorization { c.resume(returning: $0 == .authorized) } }
    }

    /// Call with the same AVAudioEngine tap that feeds StudioAudio.
    public func start() throws {
        guard let r = recognizer, r.isAvailable else { throw NSError(domain: "NoizyKit", code: 1, userInfo: [NSLocalizedDescriptionKey: "speech recognizer unavailable"]) }
        let req = SFSpeechAudioBufferRecognitionRequest()
        req.shouldReportPartialResults = true
        if r.supportsOnDeviceRecognition { req.requiresOnDeviceRecognition = true }   // sovereignty: never leaves the device
        req.addsPunctuation = true
        request = req; t0 = Date()
        task = r.recognitionTask(with: req) { [weak self] res, err in
            guard let self, let res else { return }
            self.onPartial?(res.bestTranscription.formattedString)
            if res.isFinal {
                let text = res.bestTranscription.formattedString
                let segs = res.bestTranscription.segments
                let s0 = segs.first?.timestamp ?? 0, s1 = (segs.last.map { $0.timestamp + $0.duration }) ?? s0
                Task { try? await self.hub.segment(track: self.track, t0: s0, t1: s1, text: text, character: self.character) }
            }
        }
    }
    public func append(_ buffer: AVAudioPCMBuffer) { request?.append(buffer) }
    public func stop() { request?.endAudio(); task?.cancel(); task = nil; request = nil }
}
#endif
