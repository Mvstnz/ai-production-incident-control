# Implementierungsbacklog

Status bei Übergabe: **alle Pakete offen**. Es wurde eine Spezifikation erstellt, keine Anwendung implementiert. Der PM ersetzt „offen“ nur gegen nachgewiesene Ergebnisse. M0 muss zuerst abgeschlossen sein.

| ID | Phase / Paket | Abhängigkeiten | Verantwortungsbereich | Überprüfbares Ergebnis | Status |
|---|---|---|---|---|---|
| P01 | M0: Versionen und Laufzeit-Spike | keine | Plattform / n8n | Fixierte Images; externer Runner; importierter Code-Subworkflow über veröffentlichten Trigger ausgeführt; zweiter Import und Neustart funktionieren. T01–T02. | offen |
| P02 | M0: Vertragsentwurf | P01 | PM + API + Domain | JSON-Schemas für Event, Snapshot, Analysis, Risk, Action und Approval; OpenAPI; eindeutige IDs/Revisionen; Fixtures validieren. T03. | offen |
| P03 | M0: Bootstrap-Vertrag | P01 | Plattform | Unterstützter Weg für Secrets, Owner-Einrichtung, Migrations-/Importreihenfolge und PowerShell/POSIX dokumentiert und minimal erprobt. T01. | offen |
| P04 | M1: Migrationen und Seed | P02 | API / Datenbank | ERP-/Ops-Schemas, Constraints, synthetische Daten aus Golden Fixture, idempotentes Seed und geschützter Reset. T04. | offen |
| P05 | M1: Auth und Zustands-API | P02, P04 | API / Security | Sessions, Rollen, interne Serviceberechtigung, atomare Revision-/Statusprüfungen und Audit. T16–T19, T30. | offen |
| P06 | M1: Persistierter Eingang und Queue | P04, P05 | API / n8n | Atomare Source-Deduplizierung, Content-Konflikt, Work Items, Leases und Claim-Token. T05–T06, T22. | offen |
| P07 | M1/M2: Domain-Core | P02, P04 | Domain / Tests | Zeitabhängige Versorgung, Auftragswert und Score als reine TS-Funktionen; Bundle identisch mit n8n-Code. T07–T12. | offen |
| P08 | M2: KI-Adapter und Prüfung | P02, P04 | n8n / AI | Reproduzierbarer Mock, unbekannte Eingaben in Review, JSON- und ERP-Prüfung, Quellenbelege, Templatefallback. T13–T15. | offen |
| P09 | M2: WF01/WF02 Eingang | P03, P06 | n8n | EML-Fixture und API-/Formeingang laufen über veröffentlichte Trigger in denselben Vertrag. T05–T06. | offen |
| P10 | M2: WF03–WF05 Analyse | P07, P08, P09 | n8n | Golden A über echte Ausführung: 24 fehlende Stück, 126.400 EUR, Score 85; Audit und Plan persistiert. T07–T09. | offen |
| P11 | M2: Sandbox-Adapter | P04, P06 | API / Integration | Persistente Tickets, interne Benachrichtigung, lokale Mail-Capture-Integration und Adapter-Ergebnisvertrag. T20–T21. | offen |
| P12 | M2: WF06/WF07 Approval & Action | P05, P10, P11 | n8n / Security | Exakte Planfreigabe, Rollenprüfung, einmalige erlaubte Ausführung, unklare Zustellung nicht blind wiederholt. T16–T21. | offen |
| P13 | M2: Minimale UI | P02, P05, P10 | UI | Incident-Liste/-Detail, Quellen, Risiko und funktionierende Freigabeseite; reale Daten statt Fakefortschritt. T16–T19, T29. | offen |
| P14 | M3: Revisionen | P10, P12 | Domain / API / n8n | Verbindliche 10+30-Teillieferung am selben Incident; Score 70; alte Freigabe ungültig. T10–T11, T17. | offen |
| P15 | M3: WF08 Recovery & SLA | P06, P12, P14 | n8n / Reliability | Dispatcher, Claim-Recovery, Fristen, deduplizierte Eskalation, keine verfrühte Lösung. T22–T24, T28. | offen |
| P16 | M3: WF09 Fehler & Replay | P06, P12 | n8n / Reliability | Reale automatische Fehlerauslösung, Retryklassifikation, Dead Letter, sicherer Replay mit Audit. T21–T23. | offen |
| P17 | M3: WF10 Digest | P10, P15 | n8n | Ein Bericht pro Datum/Zeitzone mit union-basiertem Auftragswert, Sandbox-Zustellung und Referenz. T12, T24. | offen |
| P18 | M4: Maschinenausfall | P07, P12, P15 | Domain / n8n | Explizite Operations-/Slotprüfung, freigegebene Umplanung im Mock-ERP und Neuberechnung. T25. | offen |
| P19 | M4: Qualitätsproblem | P05, P07, P12 | Domain / n8n | Chargenrückverfolgung, sichere Mock-Sperre, Severity-Override, kontrollierte Entsperrung. T26–T27. | offen |
| P20 | M4: UI vervollständigen | P13–P19 | UI / QA | Fünf Ansichten, Rollen, Lade-/Fehler-/Leerzustände, Demo-Labor, sichtbare Uhr/AI-Modus, Tastaturbedienung. T29–T30. | offen |
| P21 | M4/M5: Live-AI & Evaluation | P08, P10, P18, P19 | AI / QA | Ein realer konfigurierbarer Adapter; 60 Fälle; nachvollziehbarer Report. Ohne Credentials ehrlich NOT RUN für Live-Messungen. T31. | offen |
| P22 | M5: CI und Security-Checks | P01–P21 | QA / Plattform | Statische Checks, Unit-/Vertrags-/DB-/Workflow-/UI-Tests, Secret-Scan und frischer Build. T01–T32. | offen |
| P23 | M5: Portfolio-Unterlagen | P20–P22 | PM / Dokumentation | Englisches README, echte Screenshots, Demo-Guide, Grenzen, Architektur, tatsächliche Ergebnisse und Video-Skript. T32. | offen |
| P24 | M5: Unabhängige Abnahme | P23 | Reviewer / PM | Frischer Start anhand README; Ergebnisse reproduzierbar; optionale ungetestete Adapter separat ausgewiesen. T01–T32. | offen |

## Parallelisierung

Nach P02/P04 können Domain-Core, API-Auth und UI-Grundgerüst parallel entstehen, solange sie dieselben Verträge verwenden. Workflow-Integration hängt von tatsächlichen Endpunkten und dem Laufzeit-Spike ab. Änderungen an gemeinsamen Schemas werden durch einen verantwortlichen Integrator koordiniert; keine parallelen konkurrierenden Definitionen.

Bei nur einem verfügbaren Build-Agenten dieselbe Abhängigkeitsreihenfolge nacheinander abarbeiten. Keine bestimmte Zahl gleichzeitig laufender Agenten voraussetzen.

## PM-Protokoll je abgeschlossenem Paket

Festhalten: Paket-ID, betroffene Dateien, kurze Entscheidung, konkrete Testbefehle, Testresultat samt Nachweisdatei, nicht ausgeführte Tests und Grund, bekannte Folgeprobleme. Ein Fehler darf in ein neues Paket aufgeteilt werden, aber nicht durch Umbenennen aus dem Lieferumfang verschwinden.

## Hauptrisiken

Das früheste technische Risiko ist der reproduzierbare n8n-Import mit Code-Runner und Triggerveröffentlichung; deshalb P01 vor Massenimplementierung. Das wichtigste fachliche Risiko ist eine falsche Mengen-/Terminzuordnung; deshalb Golden Fixture und reine Funktionen. Das wichtigste Sicherheitsrisiko ist die Ausführung einer veralteten oder nicht exakt genehmigten Aktion; deshalb atomare Prüfung vor dem Seiteneffekt. Das wichtigste Portfolio-Risiko ist ein umfangreiches UI ohne echte n8n-Läufe; deshalb zuerst M2 komplett nachweisen.
