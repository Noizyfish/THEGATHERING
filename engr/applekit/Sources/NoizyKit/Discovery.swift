import Foundation
import Network

/// Bonjour: GOD advertises `_noizystdz._tcp` (hub :9790); LUCY/Watch/iPad find it without IPs.
public final class Discovery {
    public static let type = "_noizystdz._tcp"
    private var listener: NWListener?
    private var browser: NWBrowser?

    public init() {}

    public func advertise(port: UInt16 = 9790, name: String = "NOIZYSTDZ on GOD") throws {
        let l = try NWListener(using: .tcp, on: NWEndpoint.Port(rawValue: port)!)
        l.service = NWListener.Service(name: name, type: Discovery.type, txtRecord: NWTXTRecord(["hub": "\(port)", "osc": "9792", "face": "11111"]))
        l.newConnectionHandler = { $0.cancel() }      // the real hub is python; this only publishes the record
        l.start(queue: .main); listener = l
    }

    public func browse(_ found: @escaping (URL) -> Void) {
        let b = NWBrowser(for: .bonjour(type: Discovery.type, domain: nil), using: .tcp)
        b.browseResultsChangedHandler = { results, _ in
            for r in results {
                if case let .service(name, _, _, _) = r.endpoint, case let .bonjour(txt) = r.metadata, let port = txt.dictionary["hub"] {
                    _ = name; found(URL(string: "http://GOD.local:\(port)")!)   // resolve by hostname; NWConnection resolves the endpoint directly if needed
                }
            }
        }
        b.start(queue: .main); browser = b
    }
}
