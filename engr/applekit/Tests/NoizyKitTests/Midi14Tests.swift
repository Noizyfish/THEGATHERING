import XCTest
@testable import NoizyKit

final class Midi14Tests: XCTestCase {
    func testRoundTrip() {
        for v in [0, 1, 127, 128, 8192, 16383] { let (m, l) = Midi14.split(v); XCTAssertEqual(Midi14.join(msb: m, lsb: l), v) }
        XCTAssertEqual(Midi14.to14(1.0), 16383); XCTAssertEqual(Midi14.to14(0.5), 8192)
    }
    func testCCPairMatchesPython() {
        // python: cc14(1, 7, 0.75) → [[176,7,95],[176,39,127]]  (0.75*16383=12287 → msb 95, lsb 127)
        XCTAssertEqual(Midi14.cc(channel: 1, cc: 7, value: 0.75), [[176, 7, 95], [176, 39, 127]])
        XCTAssertEqual(Midi14.pitchBend(channel: 3, value: 0.0), [0xE2, 0, 0])
    }
    func testConsentSignVerify() throws {
        var c = Consent(speaker: "LINA_SRC", displayName: "LINA", scopes: ["record", "train"], session: "t")
        try c.sign(with: .init())
        XCTAssertTrue(c.verify()); c.scopes.append("commercial"); XCTAssertFalse(c.verify())
    }
}
