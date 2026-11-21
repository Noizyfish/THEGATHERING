import Foundation
import CryptoKit
#if canImport(LocalAuthentication)
import LocalAuthentication
#endif

/// Human Voice Sovereignty consent — byte-compatible with noizystdz/engine/consent.py (Ed25519 over canonical JSON, sorted keys, no spaces).
public struct Consent: Codable, Equatable {
    public var speaker_id: String
    public var display_name: String
    public var scopes: [String]
    public var session_id: String
    public var granted_at: String
    public var expires_at: String?
    public var revoked_at: String?
    public var name_hash: String?
    public var salt: String
    public var terms_version: String = "HVS-1.0"
    public var consent_id: String
    public var public_key: String?
    public var signature: String?

    public static let allScopes = ["record", "transcribe", "train", "synthesize", "commercial", "share"]

    public init(speaker: String, displayName: String, scopes: [String], session: String) {
        speaker_id = speaker; display_name = displayName; self.scopes = scopes; session_id = session
        granted_at = Consent.now(); salt = Consent.hex(8); consent_id = "cns_" + Consent.hex(8)
    }

    static func now() -> String { let f = ISO8601DateFormatter(); f.formatOptions = [.withInternetDateTime]; return f.string(from: Date()) }
    static func hex(_ n: Int) -> String { (0..<n).map { _ in String(format: "%02x", UInt8.random(in: 0...255)) }.joined() }

    /// Canonical payload: every field except `signature`, keys sorted, compact separators, nulls included (matches Python asdict+json.dumps).
    public func payload() throws -> Data {
        let m = Mirror(reflecting: self)
        var dict: [String: Any] = [:]
        for c in m.children { guard let k = c.label, k != "signature" else { continue }
            switch c.value {
            case let s as String: dict[k] = s
            case let a as [String]: dict[k] = a
            case let o as String?: dict[k] = o as Any? ?? NSNull()
            default: dict[k] = NSNull()
            }
        }
        return try JSONSerialization.data(withJSONObject: dict, options: [.sortedKeys, .withoutEscapingSlashes])
    }

    public mutating func setLegalName(_ name: String) {
        let d = SHA256.hash(data: Data((name.trimmingCharacters(in: .whitespaces).lowercased() + salt).utf8))
        name_hash = d.map { String(format: "%02x", $0) }.joined()
    }

    public mutating func sign(with key: Curve25519.Signing.PrivateKey) throws {
        public_key = key.publicKey.rawRepresentation.map { String(format: "%02x", $0) }.joined()
        signature = try key.signature(for: payload()).map { String(format: "%02x", $0) }.joined()
    }

    public func verify() -> Bool {
        guard let pk = public_key, let sig = signature, let pkd = Data(hex: pk), let sd = Data(hex: sig),
              let key = try? Curve25519.Signing.PublicKey(rawRepresentation: pkd), let p = try? payload() else { return false }
        return key.isValidSignature(sd, for: p)
    }

    public var isActive: Bool {
        let n = Consent.now()
        if let r = revoked_at, r <= n { return false }
        if let e = expires_at, e <= n { return false }
        return true
    }
    public func allows(_ s: String...) -> Bool { isActive && s.allSatisfy(scopes.contains) }

    /// Speaker's key lives in their own Keychain-backed file; generated on first use.
    public static func speakerKey(_ speaker: String, dir: URL) throws -> Curve25519.Signing.PrivateKey {
        let url = dir.appendingPathComponent("\(speaker).ed25519")
        if let d = try? Data(contentsOf: url) { return try Curve25519.Signing.PrivateKey(rawRepresentation: d) }
        let k = Curve25519.Signing.PrivateKey()
        try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        try k.rawRepresentation.write(to: url, options: [.atomic, .completeFileProtection])
        return k
    }

    #if canImport(LocalAuthentication) && !os(tvOS)
    /// Face ID / Touch ID before signing. Throws if the user cancels.
    public static func authenticate(reason: String = "Sign your voice consent") async throws {
        let ctx = LAContext()
        guard try await ctx.evaluatePolicy(.deviceOwnerAuthentication, localizedReason: reason) else { throw CocoaError(.userCancelled) }
    }
    #endif
}

extension Data {
    init?(hex: String) {
        guard hex.count % 2 == 0 else { return nil }
        var d = Data(); var i = hex.startIndex
        while i < hex.endIndex { let j = hex.index(i, offsetBy: 2); guard let b = UInt8(hex[i..<j], radix: 16) else { return nil }; d.append(b); i = j }
        self = d
    }
}
