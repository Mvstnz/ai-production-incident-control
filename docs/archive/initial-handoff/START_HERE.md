# Übergabe an Codex und den PM

Dieses Paket enthält die überprüfte Planskizze für **AI Production Incident Control**, ein n8n-Referenzprojekt für Bewerbungen. Die Anwendung ist noch nicht gebaut. Es sind keine funktionsfähigen n8n-JSON-Workflows, Container oder API-Zugänge enthalten.

## Verwenden

Paket in einen neuen Projektordner entpacken oder die Planungsdateien gezielt in das vorgesehene Repository übernehmen. Bestehende Projektregeln nicht überschreiben. Anschließend Codex beziehungsweise dem koordinierenden PM den Inhalt von `HANDOFF_PROMPT.md` geben.

`docs/BUILD_PLAN.md` ist die vollständige Umsetzungsvorgabe. `docs/BACKLOG.md` legt Reihenfolge und Abhängigkeiten fest. `docs/ACCEPTANCE_TESTS.md` definiert überprüfbare Fertig-Kriterien. `AGENTS.md` enthält die Arbeitsregeln, `CONTEXT.md` das Fachglossar und `docs/adr/` die wesentlichen Architekturentscheidungen.

`fixtures/supplier-delay-golden.json` und die E-Mail-Fixture fixieren das Hauptbeispiel. Die berechneten Sollwerte wurden bei Erstellung des Plans arithmetisch gegengeprüft; damit ist noch kein n8n-/API-/Integrationstest bestanden.

## Umfang

Der erste vollständige Schnitt ist eine Lieferverzögerung: Eingang → Extraktion → ERP-Analyse → Risiko → konkreter Entwurf → menschliche Freigabe → Sandbox-Aktion → Nachverfolgung. Danach werden Maschinenausfall und Qualitätsmangel ergänzt. Der Standardmodus funktioniert ohne bezahlte Konten oder Live-Credentials.

„PM von Netra“ wird als die vom Nutzer eingesetzte Koordinationsrolle behandelt. Dieses Paket konfiguriert oder behauptet keine bestimmte Netra-Schnittstelle.

Stand: 7. September 2026 · Version 1.0.
