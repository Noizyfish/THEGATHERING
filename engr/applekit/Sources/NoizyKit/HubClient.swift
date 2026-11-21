import Foundation

/// Minimal client for the NOIZYSTDZ hub (:9790). Shared by every kit integration.
public struct HubClient: Sendable {
    public var base: URL
    public init(base: URL = URL(string: "http://GOD.local:9790")!) { self.base = base }

    @discardableResult
    public func post(_ path: String, _ body: [String: Any]) async throws -> Data {
        var req = URLRequest(url: base.appendingPathComponent(path))
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "content-type")
        req.httpBody = try JSONSerialization.data(withJSONObject: body)
        let (data, resp) = try await URLSession.shared.data(for: req)
        guard let http = resp as? HTTPURLResponse, (200..<300).contains(http.statusCode) else { throw URLError(.badServerResponse) }
        return data
    }

    public func setVoice(_ id: String) async throws { try await post("/voice", ["id": id]) }
    public func setPreset(_ name: String) async throws { try await post("/voice", ["preset": name]) }
    public func fx(_ params: [String: Double]) async throws { try await post("/fx", params) }
    public func roomEvent(_ event: String) async throws { try await post("/home/event", ["event": event]) }
    public func segment(track: String, t0: Double, t1: Double, text: String, character: String?) async throws {
        var b: [String: Any] = ["track": track, "speaker": track, "t0": t0, "t1": t1, "text": text, "file": "live"]
        if let c = character { b["character"] = c }
        try await post("/segment", b)
    }

    /// Server-sent events as an async stream of (event, json).
    public func events() -> AsyncThrowingStream<(String, String), Error> {
        AsyncThrowingStream { cont in
            let task = Task {
                let (bytes, _) = try await URLSession.shared.bytes(from: base.appendingPathComponent("events"))
                var event = "message"
                for try await line in bytes.lines {
                    if line.hasPrefix("event: ") { event = String(line.dropFirst(7)) }
                    else if line.hasPrefix("data: ") { cont.yield((event, String(line.dropFirst(6)))) }
                }
                cont.finish()
            }
            cont.onTermination = { _ in task.cancel() }
        }
    }
}
