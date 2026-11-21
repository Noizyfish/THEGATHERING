#if canImport(AppIntents)
import AppIntents
#if canImport(CoreHaptics)
import CoreHaptics
#endif
#if canImport(UserNotifications)
import UserNotifications
#endif

/// Siri / Shortcuts / Action Button / Watch / CarPlay / HomePod → the studio. Extends empire's EmpireIntents.swift.
public enum StudioConfig { public static var hub = HubClient(); public static var engrURL = URL(string: "http://GOD.local:9792")! }

public struct RollIntent: AppIntent {
    public static let title: LocalizedStringResource = "Roll NOIZY"
    public static let description = IntentDescription("Count-in haptic, then Logic records and the ON AIR light goes red.")
    public init() {}
    public func perform() async throws -> some IntentResult & ProvidesDialog {
        await Haptics.countIn()
        try await StudioConfig.hub.roomEvent("record_start")       // hub → engr logic record + scene record
        return .result(dialog: "Rolling.")
    }
}
public struct StopIntent: AppIntent {
    public static let title: LocalizedStringResource = "Stop NOIZY"
    public init() {}
    public func perform() async throws -> some IntentResult & ProvidesDialog { try await StudioConfig.hub.roomEvent("record_stop"); return .result(dialog: "Stopped.") }
}
public struct MarkIntent: AppIntent {
    public static let title: LocalizedStringResource = "Mark that"
    public init() {}
    public func perform() async throws -> some IntentResult { try await StudioConfig.hub.roomEvent("marker"); return .result() }
}
public struct SetVoiceIntent: AppIntent {
    public static let title: LocalizedStringResource = "Set NOIZY voice"
    @Parameter(title: "Voice") public var voice: String
    public init() {}
    public init(voice: String) { self.voice = voice }
    public func perform() async throws -> some IntentResult & ProvidesDialog {
        try await StudioConfig.hub.post("/voice", ["id": voice]); return .result(dialog: "Voice set to \(voice).")
    }
}
public struct StudioSceneIntent: AppIntent {
    public static let title: LocalizedStringResource = "Studio scene"
    @Parameter(title: "Scene") public var scene: String
    public init() {}
    public init(scene: String) { self.scene = scene }
    public func perform() async throws -> some IntentResult & ProvidesDialog {
        #if canImport(HomeKit)
        try await StudioHome().scene(scene)
        #else
        try await StudioConfig.hub.roomEvent("scene_\(scene)")
        #endif
        return .result(dialog: "\(scene) scene.")
    }
}
public struct TakeSavedIntent: AppIntent {
    public static let title: LocalizedStringResource = "Announce take saved"
    @Parameter(title: "Done") public var done: Int
    public init() {}
    public func perform() async throws -> some IntentResult {
        #if canImport(UserNotifications)
        let c = UNMutableNotificationContent(); c.title = "NOIZYSTDZ"; c.body = "Take saved · \(done)/50"; c.sound = .default
        try? await UNUserNotificationCenter.current().add(UNNotificationRequest(identifier: UUID().uuidString, content: c, trigger: nil))
        #endif
        return .result()
    }
}

public struct StudioShortcuts: AppShortcutsProvider {
    public static var appShortcuts: [AppShortcut] {
        AppShortcut(intent: RollIntent(), phrases: ["Roll \(.applicationName)", "Rolling in \(.applicationName)", "\(.applicationName) record"], shortTitle: "Roll", systemImageName: "record.circle")
        AppShortcut(intent: StopIntent(), phrases: ["Stop \(.applicationName)", "Cut in \(.applicationName)"], shortTitle: "Stop", systemImageName: "stop.circle")
        AppShortcut(intent: MarkIntent(), phrases: ["Mark that in \(.applicationName)"], shortTitle: "Mark", systemImageName: "flag")
        AppShortcut(intent: SetVoiceIntent(), phrases: ["Set voice to \(\.$voice) in \(.applicationName)"], shortTitle: "Voice", systemImageName: "person.wave.2")
        AppShortcut(intent: StudioSceneIntent(), phrases: ["\(\.$scene) scene in \(.applicationName)", "LINA time in \(.applicationName)"], shortTitle: "Scene", systemImageName: "lightbulb")
    }
}

public enum Haptics {
    /// 3-2-1-roll: silent count-in so nothing bleeds into the mic.
    public static func countIn() async {
        #if canImport(CoreHaptics) && !os(macOS) && !os(tvOS)
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics, let eng = try? CHHapticEngine() else { return }
        try? eng.start()
        for i in 0..<4 {
            let ev = CHHapticEvent(eventType: .hapticTransient, parameters: [CHHapticEventParameter(parameterID: .hapticIntensity, value: i == 3 ? 1.0 : 0.6), CHHapticEventParameter(parameterID: .hapticSharpness, value: i == 3 ? 1.0 : 0.3)], relativeTime: 0)
            if let p = try? CHHapticPattern(events: [ev], parameters: []), let pl = try? eng.makePlayer(with: p) { try? pl.start(atTime: 0) }
            try? await Task.sleep(nanoseconds: 500_000_000)
        }
        #endif
    }
}
#endif
