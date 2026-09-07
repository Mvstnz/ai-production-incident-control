# Hier starten — APIC Codex Handoff v1.1

**Verbindliche Spezifikation:** `CODEX_BUILD_SPEC.md` (Version 1.1)  
**Meilensteine:** M0–M7  
**Abnahme:** 36 Kriterien, AC01–AC36  
**Status:** Bauauftrag, nicht fertig implementierte Anwendung.

Dieses eindeutig benannte Paket ersetzt frühere Übergabepakete. Die ältere `docs/BUILD_PLAN.md` mit M0–M5 ist nicht enthalten und nicht mehr maßgeblich. Das neue Paket nicht mit alten Spezifikationen zu einem widersprüchlichen Gesamtplan mischen.

## Bereits gestartete Umsetzung

Lies zuerst `RESUME_AFTER_HANDOFF_FIX.md`. Dort steht die Antwort auf die offene Codex-Rückfrage. Bestehende Arbeit erhalten und notwendige Abweichungen gezielt anpassen, nicht alles neu aufsetzen. Entpacken zunächst separat, damit eine bestehende `AGENTS.md` oder Implementierung nicht blind überschrieben wird.

## Lesereihenfolge

`AGENTS.md` → `CODEX_BUILD_SPEC.md` → `CONTEXT.md` → `docs/adr/` → `acceptance/acceptance-matrix.json`.

## Lokaler Konsistenzcheck

```bash
python verify_handoff.py
```

Benötigt nur Python-Standardbibliothek. Prüft vorhandene Dateien, Spezifikationsversion, Meilensteine, 36 Abnahmekriterien und die synthetische Beispielrechnung. Es testet **keine Anwendung und keine n8n-Verbindung**. Das Ergebnis steht in `HANDOFF_VALIDATION.json`.

## n8n-Zugriff

Dieses Paket enthält keine Credentials und installiert keinen Connector. Die tatsächlich verfügbaren Tools prüfen. Ohne autorisierten Zielzugriff `BLOCKED_TARGET_CONNECTION` dokumentieren und an den unabhängigen lokalen Teilen weiterarbeiten. M6 und AC31 bleiben blockiert. Details in Abschnitt 5.4 der Spezifikation.

## Dateien

| Datei | Zweck |
|---|---|
| `CODEX_BUILD_SPEC.md` | Einziger vollständiger Bauplan; 23 nummerierte Abschnitte, M0–M7, 36 Abnahmekriterien. |
| `AGENTS.md` | Dauerhafte Arbeitsregeln; mit bestehenden Regeln zusammenführen. |
| `RESUME_AFTER_HANDOFF_FIX.md` | Antwort auf die offene Codex-Rückfrage und Fortsetzungsregeln. |
| `CONTEXT.md` | Fachglossar. |
| `docs/adr/` | Vier Architekturentscheidungen. |
| `fixtures/hero_supplier_delay.json` | Konsistente synthetische Eingaben und Sollwerte. |
| `acceptance/acceptance-matrix.json` | AC01–AC36; Anwendungsprüfungen initial NOT_RUN. |
| `verify_handoff.py` | Paket- und Fixture-Konsistenzprüfung. |
| `HANDOFF_VALIDATION.json` | Ergebnis der tatsächlich ausgeführten Paketprüfung. |
| `PACKAGE_MANIFEST.json` | Versionsangaben und SHA-256-Hashes des ausgelieferten Paketinhalts. |

Die Geschäftsregeln der M0–M7-Fassung wurden in v1.1 nicht geändert. Korrigiert wurden Paketzuordnung, Einstieg und Umgang mit fehlendem Zielzugriff. Prüfungen nach Übergabe dürfen Ergebnisdateien ändern; Manifest-Hashes beschreiben den ausgelieferten Stand, nicht spätere Codex-Arbeit.
