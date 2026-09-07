# Verifizierte Primärquellen

Abruf-/Prüfstand: 7. September 2026. Diese Quellen belegen Herstellerfunktionen und Integrationsgrenzen. Die fachlichen Schwellen, Beispieldaten, Architekturentscheidungen und Abnahmekriterien sind eigene Projektvorgaben. Bei der Implementierung die Dokumentation passend zur ausgewählten und fixierten Version erneut prüfen.

## S1 — n8n Queue Mode

https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode

Dokumentiert den skalierenden Betrieb mit Main-/Worker-Prozessen und Redis. Daraus folgt nicht, dass Redis für jede lokale Einzelinstanz erforderlich ist. Die Entscheidung für den kleineren Demo-Stack ist eine Projektentscheidung.

## S2 — n8n Export and Import

https://docs.n8n.io/build/manage-workflows/export-and-import

Dokumentiert JSON-Exporte/-Importe und weist auf Credential-Namen/-IDs und möglicherweise sensible Inhalte in exportierten Workflows hin. Ein syntaktisch valides JSON allein belegt keine korrekt ausführbare Integration.

## S3 — n8n Command Line / Save and Publish

https://docs.n8n.io/deploy/host-n8n/configure-n8n/use-the-command-line

https://docs.n8n.io/build/understand-workflows/save-and-publish-workflows

Grundlage zur Prüfung unterstützter Import-/Veröffentlichungsabläufe. CLI-Verhalten und konkreten Bootstrap auf der gewählten Version testen, nicht aus früheren Versionsannahmen übernehmen.

## S4 — n8n External Task Runners

https://docs.n8n.io/deploy/host-n8n/configure-n8n/set-up-task-runners

https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/harden-task-runners

Dokumentiert externe Runner-Container und die erforderliche Übereinstimmung der n8n-/Runner-Version. Der Plan sieht separate Code-Ausführung und keine frei freigeschalteten Fremdmodule vor.

## S5 — n8n Wait

https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.wait

Dokumentiert Warten und Wiederaufnahme von Ausführungen sowie generierte Resume-URLs. Die Entscheidung, fachliche Freigaben als versionierte Datenbankobjekte zu führen, ist eine eigene Architekturentscheidung; keine Behauptung eines generellen Wait-Fehlers.

## S6 — n8n Error Trigger / Error Handling

https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.errortrigger

https://docs.n8n.io/build/flow-logic/handle-errors-gracefully

Error-Workflows reagieren auf fehlgeschlagene automatische Ausführungen. Manuelle Editorläufe sind kein gleichwertiger Nachweis dafür. Die zusätzliche Behandlung persistierter Fehler und abgelaufener Leases ist Teil des Projekts.

## S7 — OpenAI Codex: AGENTS.md

https://developers.openai.com/codex/agent-configuration/agents-md

Offizielle Beschreibung projektbezogener Anweisungen über AGENTS.md. Der Übergabeplan erfordert keine bestimmte automatische Delegation oder zusätzliche Agenteninstallation.

## Kontext aus dem ursprünglichen Skill

Im Gespräch wurden `grill-with-docs`, `grilling` und `domain-modeling` aus `mattpocock/skills` gelesen. Ihre für diese Übergabe übernommenen Arbeitsprinzipien sind: Entscheidungen prüfen, Begriffe vereinheitlichen und bedeutende Architekturentscheidungen knapp dokumentieren. Es wird keine native Installation dieses Repositories behauptet.

https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md

https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md

https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md

## Noch zu prüfen bei M0

Offizielle Installations-/Versionsdetails von FastAPI, React/Vite, PostgreSQL, Mailpit und dem gewählten Live-LLM-Anbieter anhand der tatsächlich eingesetzten Versionen prüfen. Sie sind Stack-Entscheidungen des Plans, keine hier bereits ausgeführte Kompatibilitätsprüfung.
