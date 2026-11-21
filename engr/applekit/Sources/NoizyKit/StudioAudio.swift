import AVFoundation
#if canImport(CoreAudio) && os(macOS)
import CoreAudio
#endif

/// AVAudioEngine capture with one tap feeding: LiveCaptions (Speech), RoomEars (SoundAnalysis) and an optional raw UDP stream.
/// iPhone: .playAndRecord/.voiceChat so LUCY talks and listens. macOS: can open BlackHole 16ch directly as the engine input (Swift twin of engine/capture.py).
public final class StudioAudio {
    public let engine = AVAudioEngine()
    public var onBuffer: ((AVAudioPCMBuffer, AVAudioTime) -> Void)?

    public init() {}

    #if os(iOS) || os(visionOS)
    public func configureSession() throws {
        let s = AVAudioSession.sharedInstance()
        try s.setCategory(.playAndRecord, mode: .voiceChat, options: [.allowBluetoothA2DP, .defaultToSpeaker, .mixWithOthers])
        try s.setPreferredSampleRate(48000); try s.setPreferredIOBufferDuration(0.010)
        try s.setActive(true)
    }
    #endif

    public func start(bufferSize: AVAudioFrameCount = 1024) throws {
        let input = engine.inputNode
        let fmt = input.outputFormat(forBus: 0)
        input.installTap(onBus: 0, bufferSize: bufferSize, format: fmt) { [weak self] buf, when in self?.onBuffer?(buf, when) }
        try engine.start()
    }
    public func stop() { engine.inputNode.removeTap(onBus: 0); engine.stop() }
    public var format: AVAudioFormat { engine.inputNode.outputFormat(forBus: 0) }

    #if os(macOS)
    /// List CoreAudio devices (name, id, inputs) — finds BlackHole 16ch / Loopback "NOIZYSTDZ IN" like `engr doctor`.
    public static func devices() -> [(name: String, id: AudioDeviceID, inputs: Int)] {
        var addr = AudioObjectPropertyAddress(mSelector: kAudioHardwarePropertyDevices, mScope: kAudioObjectPropertyScopeGlobal, mElement: kAudioObjectPropertyElementMain)
        var size: UInt32 = 0
        AudioObjectGetPropertyDataSize(AudioObjectID(kAudioObjectSystemObject), &addr, 0, nil, &size)
        var ids = [AudioDeviceID](repeating: 0, count: Int(size) / MemoryLayout<AudioDeviceID>.size)
        AudioObjectGetPropertyData(AudioObjectID(kAudioObjectSystemObject), &addr, 0, nil, &size, &ids)
        return ids.map { id in
            var nameAddr = AudioObjectPropertyAddress(mSelector: kAudioObjectPropertyName, mScope: kAudioObjectPropertyScopeGlobal, mElement: kAudioObjectPropertyElementMain)
            var name: CFString = "" as CFString; var ns = UInt32(MemoryLayout<CFString>.size)
            AudioObjectGetPropertyData(id, &nameAddr, 0, nil, &ns, &name)
            var cfgAddr = AudioObjectPropertyAddress(mSelector: kAudioDevicePropertyStreamConfiguration, mScope: kAudioDevicePropertyScopeInput, mElement: kAudioObjectPropertyElementMain)
            var cs: UInt32 = 0; AudioObjectGetPropertyDataSize(id, &cfgAddr, 0, nil, &cs)
            let bl = UnsafeMutablePointer<AudioBufferList>.allocate(capacity: Int(cs)); defer { bl.deallocate() }
            AudioObjectGetPropertyData(id, &cfgAddr, 0, nil, &cs, bl)
            let chans = UnsafeMutableAudioBufferListPointer(bl).reduce(0) { $0 + Int($1.mNumberChannels) }
            return (name as String, id, chans)
        }
    }

    /// Use a specific input device (e.g. the Loopback 16-channel "NOIZYSTDZ IN") for the engine.
    public func useInput(named name: String) throws {
        guard let d = StudioAudio.devices().first(where: { $0.name.contains(name) }) else { throw NSError(domain: "NoizyKit", code: 3, userInfo: [NSLocalizedDescriptionKey: "input device \(name) not found"]) }
        var id = d.id
        let unit = engine.inputNode.audioUnit!
        AudioUnitSetProperty(unit, kAudioOutputUnitProperty_CurrentDevice, kAudioUnitScope_Global, 0, &id, UInt32(MemoryLayout<AudioDeviceID>.size))
    }
    #endif
}
