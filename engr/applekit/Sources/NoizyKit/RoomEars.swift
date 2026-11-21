#if canImport(SoundAnalysis)
import SoundAnalysis
import AVFoundation

/// SoundAnalysis on the booth mic: speech/music/door/cough/dog… → hub /home/event. Flags noisy takes; later swap in a Create ML
/// model trained on NOIZYVOX so the room knows which of the 50 characters is being performed.
public final class RoomEars: NSObject, SNResultsObserving {
    private var analyzer: SNAudioStreamAnalyzer?
    private let hub: HubClient
    private var last: [String: Date] = [:]
    public var interesting: Set<String> = ["door_slam", "door", "knock", "cough", "dog", "dog_bark", "siren", "telephone_bell_ringing", "music", "vehicle"]
    public var threshold: Double = 0.7

    public init(hub: HubClient) { self.hub = hub }

    public func attach(format: AVAudioFormat, customModel: URL? = nil) throws {
        let a = SNAudioStreamAnalyzer(format: format)
        let req: SNRequest
        if let url = customModel, let model = try? MLModel(contentsOf: url) { req = try SNClassifySoundRequest(mlModel: model) }
        else { let r = try SNClassifySoundRequest(classifierIdentifier: .version1); r.windowDuration = CMTime(seconds: 1.0, preferredTimescale: 48000); req = r }
        try a.add(req, withObserver: self)
        analyzer = a
    }
    public func analyze(_ buffer: AVAudioPCMBuffer, at time: AVAudioFramePosition) { analyzer?.analyze(buffer, atAudioFramePosition: time) }

    public func request(_ request: SNRequest, didProduce result: SNResult) {
        guard let r = result as? SNClassificationResult, let top = r.classifications.first, top.confidence >= threshold else { return }
        let id = top.identifier
        let now = Date()
        if interesting.contains(id), (last[id].map { now.timeIntervalSince($0) > 5 } ?? true) {
            last[id] = now
            Task { try? await hub.roomEvent(id == "music" ? "noise" : id) }
        }
    }
}
import CoreML
#endif
