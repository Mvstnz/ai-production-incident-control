# Codex-Übergabe — hier starten

**Dieses Paket ist ein fertiger Bauauftrag, nicht die fertige Anwendung.** Es enthält keine n8n-Zugangsdaten, keine produktiven Daten und keine vorgetäuschten Workflow-Exporte.

## Verwendung

Das Paket in das für das Projekt bestimmte Repository legen oder Codex bereitstellen. Bestehende Dateien und Regeln vorher prüfen; eine vorhandene `AGENTS.md` nicht blind überschreiben. Für den ausführlichen selbstständigen Auftrag reicht `CODEX_BUILD_SPEC.md`; das komplette Paket ergänzt Regeln, Begriffe, ADRs und maschinenlesbare Abnahmedaten.

## Startauftrag für Codex

```text
Lies CODEX_BUILD_SPEC.md vollständig und beachte die vorhandene AGENTS.md.
Implementiere AI Production Incident Control bis zur beschriebenen Abnahme.
Die fachlichen Entscheidungen sind getroffen; beginne nicht mit einer neuen
Ideenfindungs- oder Fragerunde.

Nutze den bereitgestellten n8n-Connector: Stelle zunächst die tatsächlich
angebotenen Tools, Rechte, Node-Versionen und die Zielinstanz fest. Baue dann
die Anwendung und die zehn Workflows, konfiguriere sie auf der autorisierten
n8n-Instanz, führe echte Sandbox-Tests aus und synchronisiere bereinigte Exporte
mit dem Repository. JSON-Dateien allein erfüllen den Auftrag nicht.

Arbeite M0 bis M7 mit den Exit-Gates ab. Die lokale Demo muss ohne externe
Konten funktionieren. Live-Credentials/OAuth und fehlende Rechte konkret als
Blocker dokumentieren; alle davon unabhängigen Teile weiter fertigstellen.
Keine fremden Workflows verändern, keine echten Betriebsdaten verwenden und
keine nicht freigegebenen externen Nachrichten oder kostenpflichtigen Ressourcen
auslösen. Prüfe insbesondere Teilmengen, Idempotenz, Planversionen und Rollen.

Am Ende liefere den ausführbaren Projektstand, Startbefehle, Workflow-IDs,
Testnachweise und E2E-Execution-IDs, Screenshots, Dokumentation und eine ehrliche
Liste verbleibender Blocker. Nicht ausgeführte Tests nicht als bestanden melden.
```

Ein zusätzlich eingesetzter PM-/Koordinator erhält denselben Auftrag und verwendet die Meilensteine und Abnahmekriterien aus der Spezifikation als Arbeitsgrundlage.

## Enthalten

| Datei | Zweck |
|---|---|
| `CODEX_BUILD_SPEC.md` | Selbstständiger vollständiger Bauplan mit 23 Abschnitten, zehn Workflows und 36 Abnahmekriterien. |
| `AGENTS.md` | Kurze dauerhafte Agentenregeln für das Repository. |
| `CONTEXT.md` | Fachglossar ohne Implementierungsdetails. |
| `docs/adr/` | Vier begründete Architekturentscheidungen dieses Bauplans. |
| `fixtures/hero_supplier_delay.json` | Maschinenlesbare synthetische Eingaben und erwartete Ergebnisse. |
| `acceptance/acceptance-matrix.json` | 36 Kriterien mit anfänglichem Status NOT_RUN. |
| `verify_handoff.py` | Lokaler Konsistenzcheck für Fixture-Rechnung und Paket; kein Test der noch zu bauenden Anwendung. |
| `HANDOFF_VALIDATION.json` | Tatsächliches Ergebnis des Paket-Konsistenzchecks. |

Geschäftsregeln und Risikoschwellen sind nachvollziehbare Demo-Annahmen, keine empirisch belegten Risikomodelle. Score und Beträge sind berechnet, nicht frei vorgegebene Dashboard-Anzeigen. Details und Quellen stehen in der Spezifikation.
