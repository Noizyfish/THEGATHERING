#if canImport(ARKit) && os(iOS)
import ARKit
import Network

/// ARKit face tracking → 52 blendshapes → UDP JSON to Blender live-link (demo/avatars/blender/live_link_receiver.py, port 11111).
/// iPhone 15 Pro Max TrueDepth @ 60 Hz. Drives LUCY / GABRIEL / LINA avatars while RSP or LINA records.
public final class FaceStream: NSObject, ARSessionDelegate {
    private let session = ARSession()
    private let conn: NWConnection
    private var frame = 0
    public var avatar: String

    public init(host: String = "GOD.local", port: UInt16 = 11111, avatar: String = "LUCY") {
        self.avatar = avatar
        conn = NWConnection(host: NWEndpoint.Host(host), port: NWEndpoint.Port(rawValue: port)!, using: .udp)
        super.init()
        conn.start(queue: .global(qos: .userInteractive))
    }

    public func start() {
        guard ARFaceTrackingConfiguration.isSupported else { return }
        let cfg = ARFaceTrackingConfiguration(); cfg.maximumNumberOfTrackedFaces = 1
        session.delegate = self
        session.run(cfg, options: [.resetTracking])
    }
    public func stop() { session.pause() }

    public func session(_ session: ARSession, didUpdate anchors: [ARAnchor]) {
        guard let face = anchors.compactMap({ $0 as? ARFaceAnchor }).first else { return }
        frame &+= 1
        var shapes: [String: Float] = [:]
        for (k, v) in face.blendShapes { shapes[k.rawValue] = v.floatValue }
        let t = face.transform
        let msg: [String: Any] = ["avatar": avatar, "frame": frame, "t": Date().timeIntervalSince1970, "blendshapes": shapes,
                                  "head": [t.columns.3.x, t.columns.3.y, t.columns.3.z], "lookAt": [face.lookAtPoint.x, face.lookAtPoint.y, face.lookAtPoint.z]]
        if let d = try? JSONSerialization.data(withJSONObject: msg) { conn.send(content: d, completion: .idempotent) }
    }
}
#endif
