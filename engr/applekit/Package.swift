// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "NoizyKit",
    platforms: [.iOS(.v17), .macOS(.v14), .watchOS(.v10), .tvOS(.v17), .visionOS(.v1)],
    products: [.library(name: "NoizyKit", targets: ["NoizyKit"])],
    targets: [
        .target(name: "NoizyKit", path: "Sources/NoizyKit"),
        .testTarget(name: "NoizyKitTests", dependencies: ["NoizyKit"], path: "Tests/NoizyKitTests"),
    ]
)
