# Fortsetzung nach korrigierter Übergabe — v1.1

## Warum Codex nachgefragt hat

Frühere Übergaben verwendeten denselben ZIP-Dateinamen für unterschiedliche Paketstände. Ein Stand enthielt `docs/BUILD_PLAN.md` mit M0–M5; der spätere Startauftrag verwies auf `CODEX_BUILD_SPEC.md` mit M0–M7. Das war ein Fehler in der Übergabe, kein Fehler des Implementierers.

Das jetzt eindeutig benannte Paket `APIC_Codex_Handoff_v1_1.zip` enthält die maßgebliche `CODEX_BUILD_SPEC.md`, `AGENTS.md`, 36 Abnahmekriterien, passende Fixtures und vier ADRs. Die Dateien stehen direkt im ZIP-Hauptverzeichnis. Es enthält keine Zugangsdaten und stellt keine n8n-Verbindung her.

## Antwort für den laufenden Codex-Dialog

```text
Die Rückfrage ist berechtigt: Die vorherige Übergabe enthielt zwei
verschiedene Planstände. Das neu beigefügte Paket
APIC_Codex_Handoff_v1_1.zip ersetzt die alte Spezifikation.

Entpacke es zunächst separat und lies START_HERE.md, AGENTS.md und
CODEX_BUILD_SPEC.md. Verbindlich sind M0–M7 und die 36 Abnahmekriterien.
Die ältere docs/BUILD_PLAN.md mit M0–M5 ist nicht mehr maßgeblich.
Prüfe und erhalte bereits geschriebene Implementierung; keinen Arbeitsstand
pauschal löschen oder von null neu anfangen. Alte Projektregeln sorgfältig
zusammenführen und erforderliche Änderungen dokumentieren.

Zur n8n-Verbindung: Ein Connectorname ist in dieser Übergabe nicht bekannt.
Prüfe die tatsächlich angebotenen Tools und gegebenenfalls die vorhandene
lokale MCP-Konfiguration, ohne Secrets auszugeben. Erfinde keinen Zugriff.
Falls keine nutzbare autorisierte Verbindung verfügbar ist, dokumentiere
BLOCKED_TARGET_CONNECTION und arbeite an der lokalen Demo und allen
unabhängigen Aufgaben weiter. M6 und AC31 bleiben bis zum echten
Zielinstanz-Test offen. Keine wiederholte allgemeine Connector-Rückfrage.

Fahre jetzt mit dem nächsten unblocked Arbeitspaket fort. Kennzeichne
nicht ausführbare Tests ehrlich als BLOCKED oder NOT_RUN; keine
Erfolgsbehauptung nur aufgrund vorhandener Dateien.
```

## Geprüft und nicht geprüft

`HANDOFF_VALIDATION.json` enthält die tatsächlich ausgeführte Paket-/Fixture-Prüfung. Dies ist keine Anwendungsausführung. Es wurden keine Workflows auf einer Nutzerinstanz angelegt und keine Verbindung zur fremden Codex-Sitzung geprüft oder eingerichtet. Anwendungsabnahme bleibt NOT_RUN.

## Technische Quelle zur MCP-Diagnose

Offizielle Codex-Dokumentation (abgerufen am 7. September 2026):
https://developers.openai.com/codex/mcp

Dort sind Konfigurationsdateien, `codex mcp list` und die Trennung zwischen lokalem Clientzugriff und gehostetem Webzugriff beschrieben. Die tatsächlichen Berechtigungen der konkreten Sitzung müssen beobachtet werden; dieser Bauplan kann sie nicht erteilen.
