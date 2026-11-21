#if canImport(HomeKit)
import HomeKit

/// HomeKit from the devices that have it (iOS/iPadOS/watchOS/tvOS — not macOS). Same scene names as engr/home.json so the
/// Mac (`engr home scene record` via Shortcuts) and LUCY (this class) are interchangeable.
@MainActor
public final class StudioHome: NSObject, HMHomeManagerDelegate {
    private let manager = HMHomeManager()
    private var ready: CheckedContinuation<Void, Never>?
    public var homeName = "Studio"
    public static let scenes: [String: String] = ["standby": "Studio Standby", "session": "Studio Session", "record": "Studio Record", "playback": "Studio Playback", "sleep": "Studio Sleep", "wrap": "Studio Wrap", "friday": "Studio Friday"]

    public override init() { super.init(); manager.delegate = self }
    public func homeManagerDidUpdateHomes(_ m: HMHomeManager) { ready?.resume(); ready = nil }
    private func waitReady() async { if manager.homes.isEmpty { await withCheckedContinuation { ready = $0 } } }
    private var home: HMHome? { manager.homes.first { $0.name == homeName } ?? manager.primaryHome }

    public func scene(_ key: String) async throws {
        await waitReady()
        guard let h = home, let name = StudioHome.scenes[key], let s = h.actionSets.first(where: { $0.name == name }) else { throw NSError(domain: "NoizyKit", code: 2, userInfo: [NSLocalizedDescriptionKey: "scene \(key) not found in Home"]) }
        try await h.executeActionSet(s)
    }

    /// ON AIR light: red / amber / off.
    public func onAir(_ state: String, accessoryName: String = "ON AIR") async throws {
        await waitReady()
        guard let acc = home?.accessories.first(where: { $0.name == accessoryName }),
              let svc = acc.services.first(where: { $0.serviceType == HMServiceTypeLightbulb }) else { return }
        func set(_ type: String, _ v: Any) async throws { if let c = svc.characteristics.first(where: { $0.characteristicType == type }) { try await c.writeValue(v) } }
        switch state {
        case "off": try await set(HMCharacteristicTypePowerState, false)
        case "red": try await set(HMCharacteristicTypePowerState, true); try await set(HMCharacteristicTypeHue, 0); try await set(HMCharacteristicTypeSaturation, 100); try await set(HMCharacteristicTypeBrightness, 100)
        case "amber": try await set(HMCharacteristicTypePowerState, true); try await set(HMCharacteristicTypeHue, 40); try await set(HMCharacteristicTypeSaturation, 100); try await set(HMCharacteristicTypeBrightness, 80)
        default: try await set(HMCharacteristicTypePowerState, true)
        }
    }

    public func lock(_ locked: Bool, accessoryName: String = "Studio Door") async throws {
        await waitReady()
        guard let acc = home?.accessories.first(where: { $0.name == accessoryName }),
              let c = acc.services.flatMap(\.characteristics).first(where: { $0.characteristicType == HMCharacteristicTypeTargetLockMechanismState }) else { return }
        try await c.writeValue(locked ? HMCharacteristicValueLockMechanismState.secured.rawValue : HMCharacteristicValueLockMechanismState.unsecured.rawValue)
    }
}
#endif
