# Arbeitsregeln für Codex — AI Production Incident Control

## Auftrag und Prioritäten

Lies `CODEX_BUILD_SPEC.md` vollständig, bevor du die Implementierung planst. Sie ist der vollständige Bauauftrag; der vorherige Ideation-Chat ist nicht erforderlich. Lies außerdem vorhandene Projektregeln und `CONTEXT.md`. Bei Einfügung in ein bestehendes Repo vorhandene `AGENTS.md` ergänzen, nicht blind ersetzen. Fachbegriffe in `CONTEXT.md`; Architekturentscheidungen in `docs/adr/`; Fortschritt in `docs/implementation/progress.md`.

Implementiere das Produkt einschließlich tatsächlich ausführbarer n8n-Workflows, nicht nur dessen Beschreibung. Die Regeln dieser Datei sind Projektvorgaben innerhalb der tatsächlich erteilten Tool-, Secret- und Ressourcenberechtigungen; sie erweitern diese Berechtigungen nicht.

## Kommunikation und selbstständige Arbeit

Mit dem Nutzer Deutsch sprechen. Code, Oberfläche, öffentliche README und Portfolio-Texte Englisch verfassen. Getroffene Entscheidungen nicht wiederholt abfragen. Gewöhnliche Implementierungsdetails anhand des Bauplans sinnvoll entscheiden und dokumentieren. Nur unvermeidbare fehlende Zugriffe, Secrets, Zielressourcen oder genehmigungspflichtige externe Auswirkungen als echte Blocker melden. Andere Aufgaben weiterführen.

M0 bis M7 durchlaufen und Fortschritt mit konkreten Testbelegen pflegen. Keine bloßen Statusmeldungen als Endergebnis. Bei längerer Arbeit den Nutzer mit kurzen sachlichen Updates informieren. Ein PM-/Koordinator-Agent benutzt denselben Plan und dieselben Exit-Gates.

## Vor Schreibzugriffen

Repo, Branch, uncommittete Änderungen und n8n-Zielinstanz prüfen. n8n-Connector-Tools und deren Schemata tatsächlich entdecken. Keine Toolnamen oder API-Parameter raten. Nur Projektressourcen mit `APIC |` / `apic-portfolio` ändern; fremde Ressourcen erhalten. Vor Änderungen bestehende Projektworkflows exportieren. Keine produktiven Workflows aktivieren, E-Mails versenden oder kostenpflichtige Infrastruktur anlegen, nur weil ein Credential vorhanden ist.

## Architektur

n8n orchestriert die zehn modularen Workflows. Backend übernimmt autorisierte, atomare Zustandsänderungen und einmal implementierte, testbare Impact-/Risk-Funktionen. Keine komplette Orchestrierung hinter einem einzelnen HTTP-Node verstecken. Mock ERP ist synthetisch und per API abgegrenzt. PostgreSQL ist fachliche Source of Truth; interne n8n-Tabellen bleiben unangetastet.

Basisprofil ohne Redis; Queue-Profil optional. Versionen und Dependency-Lockfiles nach Kompatibilitätsprüfung pinnen. Verwendbare Node-Typen/-Versionen aus der Zielinstanz oder offizieller passender Dokumentation ermitteln. Keine `latest`-Releaseabhängigkeit und keine unnötigen Community-Nodes.

## Fachliche Invarianten

- KI darf keine Mengen, IDs, Termine, Scores oder Severity erfinden. Selbstberichtete Confidence ist kein Entscheidungs-Gate.
- Vorgeschlagene Teillieferungen bleiben außerhalb der bestätigten Baseline. Bestätigte Splits ersetzen den Lieferplan, statt Mengen doppelt hinzuzufügen.
- Geprüfte und tatsächlich beeinträchtigte Aufträge getrennt zählen. Offene Positionswerte einmal pro eindeutiger Position zählen, auch im Dashboard über mehrere Incidents.
- Genehmigt werden exakter Inhalt, Empfänger, Parameter, Planversion und Hash. Änderungen verlangen gegebenenfalls neue Freigabe.
- LOW hebt die Freigabepflicht für externe Aktionen nicht auf. Wait-Resume ist keine fachliche Autorisierung.
- Versand-Timeout mit unbekanntem Ergebnis darf keine blinde Wiederholung auslösen. Keine pauschale Exactly-once-Zusage.
- Eine Nachricht oder ein Ticket löst den fachlichen Incident nicht. MONITORING ist nicht RESOLVED.
- Hero-Basis: 24 Fehlmenge, zwei betroffene MOs, €126.400, 88 CRITICAL. Bestätigter Split: 14 Fehlmenge, ein betroffener MO, €54.400, 69 HIGH. Diese Werte berechnen, nicht hardcoden.

## Tests und Änderungen

Verträge vor paralleler Implementierung stabilisieren. Möglichst Verhalten an API-/Workflow-Grenzen testen; reine Domain-Funktionen zusätzlich unit-testen. Zeitsensitives Verhalten über eine Clock-Abstraktion testen; n8n-Wait benutzt unabhängig davon reale Zeit. Fixtures, echte LLM-Evaluation und Zielinstanz-Tests separat kennzeichnen.

Nach jeder fachlichen Änderung passende Tests ausführen. Nach Workflow-Änderungen aus n8n zurücklesen, validieren, ausführen und bereinigten Export synchronisieren. Redeployment muss idempotent sein. Für die gesamte Abnahme die 36 Kriterien in `CODEX_BUILD_SPEC.md` verwenden. Niemals Testergebnisse oder Execution-IDs erfinden.

## Sicherheit

Nur synthetische Daten. Secrets in Credential-/Secret-Management, nie in Prompts, Git oder Logs. `.env.example` nur mit Platzhaltern. User-/Service-Auth, serverseitige Rollen, Scope-Isolation, CSRF, erlaubte Ziele und Payload-Limits durchsetzen. Keine freie SQL-/Code-/URL-Ausführung aus eingehenden Nachrichten oder LLM-Ausgaben. Kein Freigabe-GET mit Seiteneffekt. Reset nur im eigenen Demo-Scope.

## Fertigstellungsbericht

Liefere Commit-/Branch-Referenz, Startbefehle, echte Workflow-IDs/Zustände, Testcommands und Resultate, E2E-Execution-IDs, Screenshots, Live-Evaluation oder deren klaren Nichtlauf, offene Zugriffsblocker und Rollback-Anleitung. Trenne IMPLEMENTED, LOCAL_TESTED, TARGET_TESTED, BLOCKED und NOT_RUN. JSON-Erstellung allein bedeutet nicht, dass ein Workflow funktioniert. `AGENTS.md` und diese Spezifikation dokumentieren den Auftrag, nicht eine bereits fertige Implementierung.

## Inherited workspace rule

All shell commands are prefixed with `rtk`, as specified in `C:/Users/marvi/.codex/RTK.md`.

## Superseded handoff

The original AGENTS.md is preserved in `docs/archive/initial-handoff/AGENTS.md`. The subsequently supplied CODEX_BUILD_SPEC.md and rules above supersede conflicting original requirements (including the old TypeScript engine, score 85/70, and automatic quality block). Do not implement the archived plan.
