#if canImport(AppIntents)
import AppIntents
import Foundation

// NOIZY Empire App Intents — Siri, Shortcuts, Spotlight, Action Button, Apple Watch, Mac, CarPlay (via Shortcuts).
// Pure Foundation + AppIntents: add this file to any Apple target (iOS 17+, macOS 14+, watchOS 10+, visionOS 1+).
// Backend: the n8n "NOIZY Empire — Thru-Line" workflow (empire/stack/n8n/empire-thru-line.json).

// MARK: - Config + transport

enum EmpireConfig {
    static let defaults = UserDefaults(suiteName: "group.ai.noizy.gabriel") ?? .standard
    static let webhookURLKey = "empire_webhook_url"
    static let webhookKeyKey = "empire_webhook_key"
    static let manifestURLKey = "empire_manifest_url"
    static let manifestCacheKey = "empire_manifest_cache"
    static let defaultManifestURL = "https://raw.githubusercontent.com/Noizyfish/THEGATHERING/main/empire/repos.json"

    static var webhookURL: URL? { defaults.string(forKey: webhookURLKey).flatMap(URL.init(string:)) }
    static var webhookKey: String { defaults.string(forKey: webhookKeyKey) ?? "" }
    static var manifestURL: URL { URL(string: defaults.string(forKey: manifestURLKey) ?? defaultManifestURL)! }
    static var isConfigured: Bool { webhookURL != nil && !webhookKey.isEmpty }
}

enum EmpireIntentError: LocalizedError {
    case notConfigured
    case badResponse(String)
    case repoNotFound(String)

    var errorDescription: String? {
        switch self {
        case .notConfigured: return "Run “Configure Empire Webhook” first (URL ending in /webhook/empire + your shared key)."
        case .badResponse(let s): return s
        case .repoNotFound(let s): return "No repo matches “\(s)”."
        }
    }
}

struct EmpireDigest: Decodable {
    let ok: Bool
    let date: String?
    let repoCount: Int?
    let mirrored: Int?
    let digest: String?
    let error: String?
}

enum EmpireWebhook {
    static func call(action: String, question: String? = nil, extra: [String: Any] = [:]) async throws -> EmpireDigest {
        guard let url = EmpireConfig.webhookURL, EmpireConfig.isConfigured else { throw EmpireIntentError.notConfigured }
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.timeoutInterval = 180
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.setValue(EmpireConfig.webhookKey, forHTTPHeaderField: "X-Noizy-Key")
        var body: [String: Any] = ["action": action, "source": "app-intent"]
        if let question, !question.isEmpty { body["question"] = question }
        body.merge(extra) { _, new in new }
        req.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, response) = try await URLSession.shared.data(for: req)
        let status = (response as? HTTPURLResponse)?.statusCode ?? 0
        guard let digest = try? JSONDecoder().decode(EmpireDigest.self, from: data) else {
            throw EmpireIntentError.badResponse("HTTP \(status)")
        }
        guard digest.ok else { throw EmpireIntentError.badResponse(digest.error ?? "HTTP \(status)") }
        return digest
    }
}

// MARK: - Manifest (empire/repos.json) as App Entities

struct EmpireManifest: Decodable {
    struct Repo: Decodable {
        let name: String
        let owner: String
        let tier: String
        let brand: String?
        let role: String
        let language: String?
        let visibility: String
        let site: String?
        let createdAt: String?
        let pushedAt: String?
    }
    let hub: String
    let repos: [Repo]

    static func load() async throws -> EmpireManifest {
        let d = EmpireConfig.defaults
        if let (data, _) = try? await URLSession.shared.data(from: EmpireConfig.manifestURL),
           let m = try? JSONDecoder().decode(EmpireManifest.self, from: data) {
            d.set(data, forKey: EmpireConfig.manifestCacheKey)
            return m
        }
        if let cached = d.data(forKey: EmpireConfig.manifestCacheKey) {
            return try JSONDecoder().decode(EmpireManifest.self, from: cached)
        }
        throw EmpireIntentError.badResponse("Could not load the Empire manifest.")
    }
}

struct EmpireRepoEntity: AppEntity, Identifiable {
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "NOIZY Repo"
    static var defaultQuery = EmpireRepoQuery()

    var id: String            // owner/name
    var name: String
    var owner: String
    var tier: String
    var brand: String
    var role: String
    var githubURL: URL { URL(string: "https://github.com/\(id)")! }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)", subtitle: "\(brand.isEmpty ? tier : brand) · \(owner)")
    }

    init(_ r: EmpireManifest.Repo) {
        id = "\(r.owner)/\(r.name)"; name = r.name; owner = r.owner; tier = r.tier
        brand = r.brand ?? ""; role = r.role
    }
}

struct EmpireRepoQuery: EntityStringQuery {
    func entities(for identifiers: [String]) async throws -> [EmpireRepoEntity] {
        let all = try await EmpireManifest.load().repos.map(EmpireRepoEntity.init)
        return all.filter { identifiers.contains($0.id) }
    }

    func entities(matching string: String) async throws -> [EmpireRepoEntity] {
        let q = string.lowercased().replacingOccurrences(of: " ", with: "")
        return try await EmpireManifest.load().repos.map(EmpireRepoEntity.init).filter {
            $0.name.lowercased().replacingOccurrences(of: "-", with: "").replacingOccurrences(of: "_", with: "").contains(q)
                || $0.brand.lowercased().replacingOccurrences(of: " ", with: "").contains(q)
                || $0.id.lowercased().contains(q)
        }
    }

    func suggestedEntities() async throws -> [EmpireRepoEntity] {
        try await EmpireManifest.load().repos
            .filter { $0.tier == "core" || $0.tier == "tooling" }
            .map(EmpireRepoEntity.init)
    }
}

// MARK: - Intents

struct GatherEmpireIntent: AppIntent {
    static var title: LocalizedStringResource = "Gather the Empire"
    static var description = IntentDescription("Mirror every NOIZY repo into Forgejo and write today's thru-line digest with Claude.")
    static var openAppWhenRun = false

    @Parameter(title: "Include personal vaults and forks", default: false)
    var includeAll: Bool

    func perform() async throws -> some IntentResult & ProvidesDialog & ReturnsValue<String> {
        let r = try await EmpireWebhook.call(action: includeAll ? "gather-all" : "gather")
        let summary = "\(r.repoCount ?? 0) repos scanned, \(r.mirrored ?? 0) new mirrors. Thru-line filed for \(r.date ?? "today")."
        return .result(value: r.digest ?? "", dialog: IntentDialog(stringLiteral: summary))
    }
}

struct AskEmpireIntent: AppIntent {
    static var title: LocalizedStringResource = "Ask the Empire"
    static var description = IntentDescription("Ask Claude anything about the whole NOIZY codebase, GitHub + local drives.")
    static var openAppWhenRun = false

    @Parameter(title: "Question", requestValueDialog: "What do you want to know about the Empire?")
    var question: String

    func perform() async throws -> some IntentResult & ProvidesDialog & ReturnsValue<String> {
        let r = try await EmpireWebhook.call(action: "digest", question: question)
        let text = r.digest ?? ""
        return .result(value: text, dialog: IntentDialog(stringLiteral: String(text.prefix(400))))
    }
}

struct RepoBriefIntent: AppIntent {
    static var title: LocalizedStringResource = "Brief Me on a Repo"
    static var description = IntentDescription("Claude explains one repo: what it is, where it sits in the thru-line, what to do next.")
    static var openAppWhenRun = false

    @Parameter(title: "Repo")
    var repo: EmpireRepoEntity

    static var parameterSummary: some ParameterSummary { Summary("Brief me on \(\.$repo)") }

    func perform() async throws -> some IntentResult & ProvidesDialog & ReturnsValue<String> {
        let q = "Focus only on \(repo.id) (\(repo.brand.isEmpty ? repo.tier : repo.brand)): \(repo.role). What is it, how does it connect to the rest, and what are the next 3 moves?"
        let r = try await EmpireWebhook.call(action: "digest", question: q, extra: ["repo": repo.id])
        let text = r.digest ?? ""
        return .result(value: text, dialog: IntentDialog(stringLiteral: String(text.prefix(400))))
    }
}

struct OpenRepoIntent: AppIntent {
    static var title: LocalizedStringResource = "Open a NOIZY Repo"
    static var description = IntentDescription("Open any Empire repo on GitHub.")
    static var openAppWhenRun = false

    @Parameter(title: "Repo")
    var repo: EmpireRepoEntity

    static var parameterSummary: some ParameterSummary { Summary("Open \(\.$repo)") }

    func perform() async throws -> some IntentResult & OpensIntent {
        .result(opensIntent: OpenURLIntent(repo.githubURL))
    }
}

struct FindReposIntent: AppIntent {
    static var title: LocalizedStringResource = "Find NOIZY Repos"
    static var description = IntentDescription("List Empire repos by brand or tier — feed the result into other Shortcuts actions.")
    static var openAppWhenRun = false

    @Parameter(title: "Search", default: "")
    var search: String

    func perform() async throws -> some IntentResult & ReturnsValue<[EmpireRepoEntity]> & ProvidesDialog {
        let q = EmpireRepoQuery()
        let hits = search.isEmpty ? try await q.suggestedEntities() : try await q.entities(matching: search)
        return .result(value: hits, dialog: "\(hits.count) repos.")
    }
}

struct EmpireStatusIntent: AppIntent {
    static var title: LocalizedStringResource = "Empire Status"
    static var description = IntentDescription("Quick health read: manifest size, Heaven API, webhook configured.")
    static var openAppWhenRun = false

    func perform() async throws -> some IntentResult & ProvidesDialog & ReturnsValue<String> {
        var parts: [String] = []
        if let m = try? await EmpireManifest.load() {
            let live = m.repos.filter { $0.tier != "planned" }.count
            parts.append("\(live) repos in the manifest, hub \(m.hub).")
        } else { parts.append("Manifest unreachable.") }
        parts.append(EmpireConfig.isConfigured ? "Empire webhook configured." : "Empire webhook NOT configured.")
        if let h = try? await HeavenAPI.shared.health() { parts.append("Heaven: \(h.status).") } else { parts.append("Heaven: unreachable.") }
        let s = parts.joined(separator: " ")
        return .result(value: s, dialog: IntentDialog(stringLiteral: s))
    }
}

struct ConfigureEmpireWebhookIntent: AppIntent {
    static var title: LocalizedStringResource = "Configure Empire Webhook"
    static var description = IntentDescription("Store the n8n webhook URL and shared key (synced to every device via the app group).")
    static var openAppWhenRun = false

    @Parameter(title: "Webhook URL", requestValueDialog: "n8n webhook URL (…/webhook/empire)")
    var url: URL

    @Parameter(title: "Shared key", requestValueDialog: "INTENT_SHARED_SECRET value")
    var key: String

    @Parameter(title: "Manifest URL (optional)")
    var manifestURL: URL?

    func perform() async throws -> some IntentResult & ProvidesDialog {
        let d = EmpireConfig.defaults
        d.set(url.absoluteString, forKey: EmpireConfig.webhookURLKey)
        d.set(key, forKey: EmpireConfig.webhookKeyKey)
        if let manifestURL { d.set(manifestURL.absoluteString, forKey: EmpireConfig.manifestURLKey) }
        return .result(dialog: "Empire webhook saved.")
    }
}

// MARK: - Siri phrases (no setup; appear in Shortcuts + Spotlight the moment the app is installed)

struct EmpireShortcuts: AppShortcutsProvider {
    static var shortcutTileColor: ShortcutTileColor = .purple

    static var appShortcuts: [AppShortcut] {
        AppShortcut(intent: GatherEmpireIntent(),
                    phrases: ["Gather the Empire with \(.applicationName)",
                              "Bring everything together in \(.applicationName)",
                              "Run the NOIZY thru-line in \(.applicationName)"],
                    shortTitle: "Gather Empire", systemImageName: "point.3.connected.trianglepath.dotted")
        AppShortcut(intent: AskEmpireIntent(),
                    phrases: ["Ask the Empire in \(.applicationName)",
                              "Ask \(.applicationName) about the Empire"],
                    shortTitle: "Ask Empire", systemImageName: "sparkles.rectangle.stack")
        AppShortcut(intent: RepoBriefIntent(),
                    phrases: ["Brief me on \(\.$repo) in \(.applicationName)",
                              "\(.applicationName) what is \(\.$repo)"],
                    shortTitle: "Repo Brief", systemImageName: "doc.text.magnifyingglass")
        AppShortcut(intent: OpenRepoIntent(),
                    phrases: ["Open \(\.$repo) in \(.applicationName)"],
                    shortTitle: "Open Repo", systemImageName: "arrow.up.right.square")
        AppShortcut(intent: EmpireStatusIntent(),
                    phrases: ["Empire status in \(.applicationName)",
                              "How is the Empire, \(.applicationName)"],
                    shortTitle: "Status", systemImageName: "waveform.path.ecg")
    }
}
#endif
