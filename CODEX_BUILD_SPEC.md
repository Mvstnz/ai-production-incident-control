# AI Production Incident Control — verbindlicher Codex-Bauplan

**Version:** 1.1 · **Stand:** 7. September 2026  
**Status:** Implementierungsauftrag; noch kein implementiertes oder abgenommenes System.  
**Repository-Vorschlag:** `ai-production-incident-control`  
**Produktname:** AI Production Incident Control · **Workflow-Präfix:** `APIC |`  
**Sprache:** Abstimmung mit dem Nutzer Deutsch; Anwendung, Code, README und öffentliche Projektdokumentation Englisch.

> **Auftrag an Codex:** Implementiere dieses Projekt vollständig als reproduzierbares, öffentlich vorzeigbares n8n-Portfolio-System. Prüfe den tatsächlich in deiner Sitzung verfügbaren n8n-Zugriff. Nutze einen autorisierten n8n-Connector zum Erstellen, Konfigurieren, Testen und Bereitstellen der Workflows, sobald er verfügbar ist. Ein im Prompt erwähnter Connector ist kein nachgewiesener Zugriff. Fehlender Zielzugriff blockiert nur die davon abhängigen Arbeiten, nicht die lokale Implementierung. Eine Sammlung von JSON-Dateien ohne nachgewiesene Ausführung ist kein fertiges Ergebnis. Arbeite die Meilensteine bis zur Abnahme ab. Trenne implementiert, lokal getestet, auf der Zielinstanz getestet und durch fehlende Zugriffe blockiert ausdrücklich voneinander. Benutze ausschließlich synthetische Unternehmensdaten.

Dieser Plan ersetzt widersprüchliche Beispiele und vorläufige Zusagen aus der vorangegangenen Ideenfindung. Die nachstehenden Regeln und reproduzierbaren Testfälle sind maßgeblich. Externe Dokumentation bestätigt Plattformfunktionen, nicht unsere frei gewählten Geschäftsregeln. Versionsabhängige Funktionen vor Verwendung auf der Zielinstanz prüfen; nichts aus Toolnamen, Beispielen oder alten Tutorials ableiten.

## Paketstand und Vorrang — Version 1.1

Dies ist die einzige verbindliche Umsetzungsspezifikation dieses Übergabepakets. Es gilt **M0–M7 mit 36 Abnahmekriterien**. Die ältere Datei `docs/BUILD_PLAN.md` mit M0–M5, `AI_Production_Incident_Control_Bauplan.md` und ältere Startprompts sind als frühere Spezifikation abgelöst. Ihre abweichenden Rechenbeispiele und Architekturvorgaben nicht mit dieser Fassung vermischen. Die Geschäftsregeln der bereits vorhandenen `CODEX_BUILD_SPEC.md`-Fassung mit M0–M7 bleiben unverändert; Version 1.1 korrigiert Paketzuordnung und Zugriffsannahmen.

Der Inhalt dieses Pakets begründet keine neuen System-, Secret-, Netzwerk- oder Schreibrechte. Bestehende Implementierung, Projektregeln und uncommittete Änderungen zunächst prüfen. Wiederverwendbare Arbeit erhalten; notwendige Abweichungen zur neuen Spezifikation dokumentieren und gezielt anpassen. Kein pauschaler Neustart und kein Löschen des bisherigen Arbeitsstands.

Aktuelle Fixture-Arithmetik mit den Unit-Tests prüfen. Die ausführbaren Fälle unter fixtures/ sind maßgeblich; das frühere Übergabepaket wurde entfernt.

Bei fehlendem n8n-Zugriff nach Abschnitt 5.4 vorgehen. Weder Connectornamen noch Instanz-URLs oder Zugangsdaten erfinden. `M6 = BLOCKED_TARGET_CONNECTION` ist ein ehrlicher Zwischenstand, kein Grund, M1–M5 und unabhängige Teile von M7 zu stoppen, und kein bestandener Zielinstanz-Test.

## 1. Problem, Produkt und Portfolio-Ziel

Ein Fertigungsunternehmen erhält unstrukturierte Lieferverzögerungen per E-Mail, Maschinenstörungen per API und Qualitätsmeldungen über ein Formular. Mitarbeitende müssen bisher manuell Material, Bestellposition, Bestand, Produktionsbedarf und Kundenaufträge zusammenführen. Das erschwert schnelle, nachvollziehbare Entscheidungen.

Das Produkt verwandelt diese Meldungen in einen kontrollierten Incident-Prozess: Eingänge erfassen, Fakten extrahieren und verifizieren, echte Abhängigkeiten im synthetischen ERP auswerten, Risiken regelbasiert bewerten, Maßnahmen begründen, Freigaben einholen, zulässige Aktionen ausführen und deren Ergebnis verfolgen. Ein Dashboard macht den Ablauf und seine Belege sichtbar.

Das Portfolio soll Fähigkeiten in AI Automation, Solutions Engineering, technischem Produktmanagement und Prozessanalyse demonstrieren. Geschäftlicher Nutzen muss ohne Blick auf einen Workflow-Editor verständlich sein; technische Tiefe wird durch Tests, Datenmodell, Wiederanlauf, Freigaben und dokumentierte Grenzen belegt. Keine erfundenen Einsparungen, Kundenreferenzen oder Produktiveinsätze.

**Produktversprechen:** “From an unstructured incident to a verified impact assessment, a human-approved response and an auditable action trail.”

**Leitsatz:** KI interpretiert und formuliert. Verifizierte Daten und versionierte Regeln bestimmen die Entscheidung. Menschen genehmigen folgenreiche Aktionen.

### Nutzerrollen und wesentliche User Stories

| Rolle | Erwartetes Verhalten |
|---|---|
| Purchasing specialist | Liefermeldung erfassen; PO und Position erkennen; bestätigte und nur angebotene Teillieferungen unterscheiden; Lieferantenentwurf prüfen. |
| Production manager | Betroffene Fertigungsaufträge und Zeitengpässe sehen; Ausweichmaschine und Umplanungsvorschlag prüfen; kritische Maßnahmen freigeben. |
| Quality manager | Betroffene Charge und Lieferpositionen nachvollziehen; synthetische Versandsperre freigeben; Freigabe einer Sperre gesondert entscheiden. |
| Operations analyst | Unklare Meldungen korrigieren; Quellenbelege sehen; Incidents suchen und filtern; Revisionen und erneute Bewertung nachvollziehen. |
| Administrator | Fehlerfälle, Retries, Dead Letter Queue und Connector-Status prüfen; gescheiterte Jobs kontrolliert erneut ausführen. |
| Recruiter / viewer | Drei geführte Demos ohne echte Kundendaten ansehen; Risikofaktoren, Freigabe und Ausführungsnachweise verstehen; keine realen Aktionen auslösen. |

## 2. Fester Scope und bewusste Begrenzungen

**Zum vollständigen Portfolio-Release gehören:** drei Incident-Typen (`SUPPLIER_DELAY`, `MACHINE_BREAKDOWN`, `QUALITY_ISSUE`), zehn modulare n8n-Workflows, PostgreSQL, synthetisches ERP mit REST-Schnittstelle, nachvollziehbare Impact- und Risk-Berechnung, menschliche Freigaben, sichere Aktionsausführung, Fehlerbehandlung, Dashboard, Tests, AI-Evaluation, Docker-basierter Start und öffentliche Dokumentation.

Zuerst einen vertikalen Lieferverzögerungsfall vollständig durch das System bringen. Danach Maschinen- und Qualitätsfälle ergänzen. Der erste Meilenstein ist nicht der vollständige Release.

**Nicht Bestandteil:** echtes SAP/Comarch/Produktionssystem; Änderungen an Anlagen; reale Beschaffung oder Bestellungen; automatische Zusagen an Kunden; reale Schicht- oder Maschinensteuerung; vollständiges MRP/APS; mehrstufige BOM-Explosion; Multi-Tenant-SaaS; SSO-Plattform; Kubernetes; Bezahlung; eigenständiges Agenten-Netzwerk; Vector-DB/RAG/MCP zur Laufzeit nur als Dekoration. Keine zehn Microservices für zehn Workflows.

Standardmäßig keine PDF-Anhänge, OCR oder beliebigen E-Mail-Anhangsdownloads. Nur Plaintext/normalisierter HTML-Mailtext und strukturierte Formular-/API-Daten. Nicht unterstützte Anhänge sind als solche sichtbar und landen bei notwendigem Inhalt in `MANUAL_REVIEW`.

### Korrekturen gegenüber der Ideenfindung

| Früherer Entwurf | Verbindliche Umsetzung |
|---|---|
| Die AI liefert `confidence: 0.97`; ab 0.80 automatisch weiter. | Keine selbstbewertete Modellwahrscheinlichkeit als Freigabekriterium. JSON-Schema, Quellenbeleg und ERP-Abgleich entscheiden. |
| 76 Bedarf minus 24 Bestand genügt als Analyse. | Zeitbezogene Allokation mit reservierten/gesperrten Beständen, Bedarfsterminen, Lieferplan und getrennten Was-wäre-wenn-Szenarien. |
| Drei geprüfte Produktionsaufträge sind automatisch drei verspätete. | Geprüfte und tatsächlich beeinträchtigte Aufträge getrennt ausweisen. Im festen Hero-Fall: drei geprüft, zwei beeinträchtigt. |
| €55.400 sind prognostizierter Umsatzverlust. | Wert betroffener offener Kundenauftragspositionen; keine Verlustwahrscheinlichkeit und kein nachgewiesener Umsatzverlust. |
| Ein Hash garantiert keine doppelte E-Mail. | Eindeutige DB-Constraints, transaktionale Outbox und providerspezifische Behandlung unklarer Versandresultate. |
| Reject oder API-Fehler sind endgültige Incident-Zustände. | Incident, Analysejob, Freigabe und Aktion haben getrennte Statusmodelle. Ablehnung einer Maßnahme beseitigt die Störung nicht. |
| Entwurf wird nach Freigabe erzeugt und dann verschickt. | Exakter Empfänger, Betreff, Inhalt und Aktionsparameter gehören vor Freigabe zum genehmigten Plan. Änderungen erfordern erneute Freigabe. |
| Redis ist immer nötig. | Im Basisprofil Single-Instance-n8n ohne Redis. Optionales Queue-Profil erst nach funktionierender Basis. |
| Docker starten ersetzt OAuth und Zugriffsrechte. | Reproduzierbare lokale Demo ohne externe Konten; Live-Sandbox benötigt tatsächlich erteilte Credentials und Netzwerkzugriff. |

## 3. Zwei ausführbare Betriebsarten

### A. `DEMO_LOCAL` — verpflichtend und ohne externe API-Kosten

Nach initialem Image-/Dependency-Download läuft die Demo ohne LLM-, Gmail-, Slack- oder Cloud-Konto. Lokales n8n, Postgres und die APIs führen echte Workflows aus. Externe Effekte gehen an lokale Sandbox-Adapter. Ein deterministischer Fixture-LLM liefert für die mitgelieferten Testmails kontrollierte strukturierte Antworten; die Oberfläche kennzeichnet diesen Modus deutlich als **simulated AI**. Er ist keine Behauptung über die Qualität eines echten Modells.

Unbekannte freie Texte dürfen im Fixture-Modus nicht mit angeblich verstandenen Inhalten beantwortet werden. Sie führen zu `MANUAL_REVIEW` oder zu einer klaren Meldung, dass für freie Eingaben der Live-AI-Modus nötig ist. API/Form-Eingang und vorgegebene Demos bleiben nutzbar.

### B. `CONNECTED_SANDBOX` — mit dem bereitgestellten n8n-Connector

Die echte n8n-Zielinstanz erhält die zehn Workflows. Live-LLM und ein gesondertes Test-Mailkonto sowie ein privater Slack-Testkanal können angebunden werden. Empfänger-Allowlist, Namespace und Ausgabenlimit bleiben verpflichtend. Es werden weiterhin nur synthetische ERP-Daten verarbeitet; keine echten Betriebsdaten und keine produktiven ERP-Änderungen.

Fehlende OAuth-Einwilligung, API-Schlüssel oder Schreibrechte werden als konkreter Konfigurationsblocker protokolliert. Codex baut und testet alle davon unabhängigen Teile weiter. Ein nicht getesteter Live-Adapter wird nicht als erfolgreich integriert ausgegeben.

**Externe Effekte sind standardmäßig aus:** `EXTERNAL_ACTIONS_ENABLED=false`. Ein vorhandener Credential-Eintrag ist keine Freigabe, reale Adressaten zu kontaktieren.

## 4. Architektur und Verantwortungsgrenzen

```text
Gmail-Testkonto / synthetische Mail / API / manuelles Formular
                             |
                      WF01 / WF02
                             |
                dauerhafte Eingangserfassung
                             |
                 WF03 Normalize + Verify
                             |
                WF04 ERP Impact Analysis
                             |
              WF05 Risk + AI + Action Plan
                             |
             WF06 Approval / WF07 Execution
                             |
              WF08 SLA + Recovery Monitor

WF09: zentrale Fehleraufnahme     WF10: Management-Digest

Dashboard <--> Operations API <--> PostgreSQL: ops
n8n      <--> Operations API
n8n      <--> Mock ERP API     <--> PostgreSQL: erp
n8n      <--> LLM-/Notification-/Ticket-Adapter
n8n internals                  --> eigene n8n-Datenbank
```

**n8n bleibt der Orchestrator.** Trigger, Verzweigungen, Sub-Workflow-Aufrufe, LLM-Schritte, Freigabe-Warten, Aktionsadapter, Zeitpläne und Fehlerpfade müssen im Canvas nachvollziehbar sein. Nicht das ganze Projekt hinter einen einzigen HTTP-Request an einen Python-Monolithen verlagern.

**Operations API:** Validierung, Autorisierung, atomare Schreiboperationen, Locking, Statusübergänge, Freigabekonsum, Outbox, UI-Lesezugriffe und reine Berechnungsfunktionen. Sie führt nicht heimlich die gesamte Orchestrierung aus.

**Mock ERP API:** Klar abgegrenzte simulierte ERP-Lesezugriffe; nur explizite, freigegebene Demo-Schreibkommandos. n8n liest oder verändert nicht direkt ERP-Tabellen. Direkte SQL-Nutzung ist nicht grundsätzlich unprofessionell; hier ist die API eine bewusste Integrationsgrenze.

**Reine Domain-Funktionen:** Impact-Allokation und Risk Score im Backend einmal implementieren, umfassend testen und von n8n aufrufen. Nicht als abweichende Formel gleichzeitig im Frontend und in fünf Code-Nodes duplizieren.

### Technische Defaults

Backend Python/FastAPI mit typisierten Modellen, Migrationen und pytest; Frontend React/TypeScript mit Vite, einer schlanken Komponentenbibliothek und Playwright; PostgreSQL als Persistenz. Abhängigkeiten und Container-Versionen nach Kompatibilitätsprüfung exakt pinnen und Lockfiles committen. Keine erfundene aktuelle Versionsnummer und kein `latest` als reproduzierbare Release-Referenz.

Ein Repository, ein Backend-Codepaket, aber getrennte Startpunkte für Operations API und Mock ERP API. Kein weiterer Server nötig, um jede Tabelle einzeln anzubieten. In der Basis Compose-Dienste: `postgres`, `n8n`, `ops-api`, `mock-erp`, `dashboard`, ein lokaler Mail-Sink. Einmalige Bootstrap-/Migration-/Deployment-Tasks sind keine dauerhaft laufenden Microservices.

Postgres erhält eine eigene Datenbank für n8n und eine Anwendungsdatenbank mit `erp`-/`ops`-Schemas. Eigene DB-Rollen; niemals direkt n8n-interne Tabellen patchen. Optionales Queue-Profil ergänzt Redis, Worker und die für die ausgewählte n8n-Version erforderlichen Runner. Queue Mode ist eine Skalierungsoption, nicht Voraussetzung unseres Workflows. [S05]

## 5. Codex, PM-Rolle und n8n-Connector: verbindliches Vorgehen

Eine optionale PM-/Koordinator-Rolle nutzt denselben Plan und dieselben Abnahmekriterien. Sie zerlegt Aufgaben und prüft Ergebnisse; sie darf vereinbarten Scope nicht stillschweigend streichen. Kein spezielles PM-Produkt wird vorausgesetzt. Parallele Agenten dürfen nach fixierten API-Contracts Frontend, Tests und Integrationsadapter bearbeiten; keine gleichzeitigen konkurrierenden Änderungen an denselben Workflows.

### 5.1 Discovery vor dem ersten Schreibzugriff

1. Aktuelles Arbeitsverzeichnis und zugängliches GitHub-Repository feststellen; bestehende `AGENTS.md`, Dokumentation, Änderungen und Projektkonventionen lesen. Vorhandene uncommittete Arbeit nicht überschreiben. Kein fremdes Repository als Ziel erraten.
2. n8n-Connector-Tools tatsächlich auflisten: lesen/suchen, Nodes/Schemata entdecken, Workflow erstellen/ändern, Credentials zuordnen, veröffentlichen/aktivieren, ausführen, Executions lesen. Exakte Argumente aus den angebotenen Tool-Schemata übernehmen; keine Toolnamen halluzinieren.
3. Zielinstanz, Version, unterstützte Node-Versionen, Projekt-/Tag-Funktionen und Rechte dokumentieren. Der aktuelle n8n-MCP-Werkzeugumfang umfasst auch Workflow-Erstellung; das sagt aber nichts über die Rechte oder Version der konkreten Verbindung aus. [S01, S02]
4. Sicherstellen, dass n8n die Backend-URLs erreicht. Ein Cloud-n8n erreicht einen Compose-Hostnamen wie `http://ops-api:8000` nicht ohne passende Vernetzung. Für entfernte Instanzen autorisierte HTTPS-Endpunkte oder vorhandenen gesicherten Tunnel nutzen. Keine eigenmächtige Firewallöffnung oder kostenpflichtige Infrastruktur anlegen.
5. Ergebnis ohne Geheimnisse in `docs/implementation/environment-report.md` dokumentieren: Capability, tatsächliches Tool, getestet ja/nein, Grenzen, Ziel-URL ohne Tokens.

### 5.2 Ownership und Schutz der Zielinstanz

Eigener Namespace/Tag `apic-portfolio`; Workflow-Namen `APIC | WF01 | Email Intake` usw. Nur Ressourcen dieses Projekts verändern. Bestehende Versionen vor Änderungen exportieren. Keine fremden Workflows deaktivieren oder Credential-Werte auslesen. Tags sind Kennzeichnung, keine Sicherheitsgrenze.

Zuerst inaktiv bzw. unveröffentlicht anlegen. IDs für Sub-Workflows in einem Deployment-Manifest abbilden. Abhängigkeiten verbinden, tatsächliche Node-`typeVersion` prüfen, Credential-Referenzen binden, Konfiguration validieren. Anschließend nur Sandbox-Trigger gezielt aktivieren/veröffentlichen, um echte End-to-End-Tests auszuführen. Veröffentlichung und Aktivierung müssen dem Modell der Zielversion entsprechen. [S02, S03]

### 5.3 Synchronisation und Nachweis

Repository enthält bereinigte, importierbare Exporte aller zehn Workflows. Erneutes Deployment aktualisiert dieselben Projekt-Workflows anstatt Duplikate anzulegen. Verbindungen, Expression-Referenzen und Error-Workflow-ID ebenfalls prüfen; ein syntaktisch korrektes JSON genügt nicht.

Nach Änderungen aus n8n zurücklesen, mit dem Sollstand vergleichen und Testläufe protokollieren. `deployment-manifest.json` enthält logische Workflow-Keys, instanzbezogene IDs, Zielversion, Export-Hash, Zustand und Teststatus — keine Credential-Werte. Instanzspezifische Mapping-Dateien nach Geheimnis-/Metadatenprüfung von öffentlichen Dateien trennen.

Falls der Connector keine notwendige Operation anbietet: einen bereits autorisierten, dokumentierten n8n-API-/CLI-Weg verwenden. Keine nicht öffentlichen Endpoints reverse engineeren, Rechte umgehen oder ungeprüfte Admin-Schlüssel verlangen. Wenn kein erlaubter Schreibweg existiert, lokale Demo und Exporte fertigstellen und genau den Deploy-Schritt als blockiert melden. [S03, S04]

`AGENTS.md` hält die dauerhaften Repo-Regeln fest; diese Spezifikation enthält den ausführlichen Bauauftrag. Codex unterstützt projektbezogene Regeln über `AGENTS.md` und externe Tools über MCP. [S10, S11]

### 5.4 Wenn die Sitzung keinen n8n-Connector anbietet

Zunächst die tatsächlich verfügbaren Tools über die vorhandene Discovery prüfen. In einer lokalen Codex-Umgebung zusätzlich die vorhandene MCP-Konfiguration prüfen; bei verfügbarer CLI kann `codex mcp list` konfigurierte Server anzeigen. Nur Namen, Aktivierungs-/Authentifizierungsstatus und redigierte Fehlermeldungen dokumentieren, niemals Tokens, Headerwerte, komplette Secret-Dateien oder unredigierte URLs ausgeben. Die globale Konfigurationsdatei liegt standardmäßig unter `~/.codex/config.toml`, projektbezogene Konfiguration unter `.codex/config.toml`; nicht voraussetzen, dass jeder Client auf diese lokalen Dateien zugreifen kann. [S11]

Einen vorhandenen Eintrag nicht automatisch für funktionsfähig halten: angebotene Tools tatsächlich entdecken und einen erlaubten Lesezugriff prüfen. Dokumentationssuche oder ein reiner Workflow-Ausführungszugriff ist kein Nachweis für Workflow-Erstellung, -Änderung oder -Veröffentlichung.

Falls kein verwendbarer, autorisierter Zugriff verfügbar ist, `BLOCKED_TARGET_CONNECTION` in Environment-Report und Fortschritt festhalten. Notiere, was beobachtet wurde: z. B. kein Tool angeboten, Konfiguration deaktiviert, Authentifizierung erforderlich, Ziel nicht erreichbar oder fehlendes Schreibrecht. Keine pauschale Aussage über alle Konten und keine wiederholte Nachfrage nach einem unbekannten Connectornamen.

**Danach weiterarbeiten:** Repository, Compose, Datenmodell, Backend, Frontend, lokale n8n-Workflows, synthetische Daten und alle lokal möglichen Tests umsetzen. Die lokale n8n-Demo nach dem vorgesehenen Bootstrap-Verfahren aufbauen; eine fehlende entfernte Verbindung ist kein fehlender lokaler n8n-Server. Falls auch die lokale Runtime/Docker-Umgebung fehlt, die exakt betroffenen Ausführungstests als BLOCKED/NOT_RUN dokumentieren und weiterhin verfügbare Implementierungs- und Testarbeiten erledigen. Keine Runtime-Verfügbarkeit oder erfolgreichen Import behaupten, ohne sie geprüft zu haben.

M0 darf für unabhängige Arbeiten mit dokumentiertem Zielzugriffsblocker abgeschlossen werden. M6 und AC31 bleiben blockiert, bis die autorisierte Zielinstanz tatsächlich eingerichtet und getestet ist. Ein bereits autorisierter öffentlicher API-/CLI-Weg gemäß Abschnitt 5.3 ist zulässig, aber kein Vorwand, Zugangsbeschränkungen zu umgehen. Erst wenn der Nutzer die Verbindung bereitstellt, Capability-Discovery wiederholen und echte Zieltests durchführen. Eine neue allgemeine Planungsrunde ist nicht erforderlich.

## 6. Datenmodell

UUIDs für interne Identitäten; lesbare Geschäftsnummern separat. Zeitstempel UTC, Anzeige und Geschäftsdatum in `Europe/Berlin`. Datumswerte ohne Uhrzeit nicht stillschweigend zu UTC-Mitternacht umdeuten. EUR als einzige Währung des Seed-Systems; Geld in Integer-Cents oder `NUMERIC`, nie binärem Float. Mengen mit Einheit und festem Decimal-Typ.

Jeder Demo-Lauf erhält `scope_id`; alle zusammengehörigen ERP-/Operations-Datensätze und Idempotency-Keys sind entsprechend isoliert. Das ist Demo-Isolation, keine behauptete vollständige Mandantenplattform. Fremdschlüssel müssen Scope-übergreifende Beziehungen verhindern. Reset darf nur den ausgewählten synthetischen Scope betreffen.

### ERP-Entitäten

| Tabelle / Aggregat | Mindestinhalt und Zweck |
|---|---|
| `suppliers`, `supplier_materials` | Lieferant, zugelassene Materialien, Ersatzlieferantenstatus und verfügbare Alternative; Zulassung allein ist noch keine termingerechte Lieferung. |
| `materials` | Materialnummer, Bezeichnung, Einheit, Materialart. |
| `purchase_orders`, `purchase_order_items` | Bestellnummer, Lieferant, Position, Material, bestellte/offene Menge. Materialnummer allein identifiziert keine PO-Position. |
| `supply_schedules` | Mengen, Verfügbarkeitszeitpunkte, bestätigter/provisorischer Status und Revision einer Lieferung; Summe darf offene Bestellmenge nicht überschreiten. |
| `inventory_lots`, `inventory_reservations` | Standort, Charge, physische Menge, Qualitätsstatus, Reservierungsempfänger; keine doppelte Bestandsanrechnung. |
| `production_orders`, `production_requirements` | Produktionsmenge, Materialbedarf, Bedarfstermin, offene Menge und Priorität. |
| `production_operations`, `machines`, `machine_capabilities`, `capacity_calendar` | Geplante Operation, Maschinenzuordnung, benötigte Stunden und qualifizierte freie Alternativkapazität. |
| `customers`, `sales_orders`, `sales_order_items` | Kundenpriorität, Kundenliefertermin, offene Menge und offener Netto-Positionswert. |
| `production_sales_allocations` | Mengenmäßige Zuordnung Produktion → Kundenposition; nicht fälschlich immer 1:1 annehmen. |
| `shipments`, `shipment_items`, `lot_allocations`, `quality_inspections` | Chargenbezug zur Lieferposition, Freigabe-/Sperrstatus und verifizierte Prüfung. Einfache nachvollziehbare Genealogie für den Qualitätsfall. |

### Operations-Entitäten

| Tabelle / Aggregat | Mindestinhalt und Zweck |
|---|---|
| `source_events` | Scope, Kanal, Quellkonto, Quell-ID, Payload-Hash, Rohdatenverweis, Empfangszeit, Authentifizierungsergebnis, Zustand. |
| `incidents` | Nummer, Typ, Objektbezug, Zustand, aktuelle Revision, aktuelle Bewertung, Titel. |
| `incident_revisions`, `incident_sources` | Unveränderliche normalisierte Fakten mit Herkunft; mehrere Quellen können denselben Incident belegen. |
| `analysis_jobs` | Job-/Lease-ID, Schritt, Versuchszahl, Status, nächste Ausführung, Korrelations-ID und Worker-/Execution-Referenz. |
| `impact_assessments`, `incident_impacts` | Eingabesnapshot, ERP-Revision, Methodenversion, geprüft/betroffen, terminbezogene Fehlmengen, betroffene Kundenpositions-IDs. |
| `risk_assessments` | Policy-Version, Faktoren, Score oder unbekannt, Severity, Overrides und Gründe. |
| `action_plans`, `incident_actions` | Versionierter Plan, Hash, Ziel, exakter genehmigbarer Payload, Status und Provider-Referenz je Aktion. |
| `approvals` | Planversion/-Hash, zuständige Rolle, Status, Ablauf, Akteur, Entscheidung, Kommentar; Token nur gehasht, falls verwendet. |
| `outbox_events` | In derselben DB-Transaktion persistierte Arbeits-/Wakeup-Aufträge, eindeutiger Event-Key, Lease und Zustellstatus. |
| `audit_events` | Append-only Ereignis, Akteur/System, Objekt, Vorgang, Zeit, Korrelations-ID, redigierte Änderung. |
| `workflow_errors` | Fehlerklasse, Workflow/Execution/Job, Retrybarkeit, nächster Versuch, Dead-Letter-Status, redigierter Fehler. |
| `evaluation_runs`, `evaluation_results` | Datensatz-/Prompt-/Modellversion, Eingabesplit, Resultate, Laufzeit und tatsächliche Kosten soweit verfügbar. |

DDL enthält Constraints, Unique-Indizes und Indizes für `scope_id`, Zustand, Fälligkeit und Fremdschlüssel. Alle Zustandsänderungen erfolgen über Domänenkommandos mit optimistischer Versionsprüfung oder geeigneten Zeilensperren. Ein vorgelagertes `SELECT`, gefolgt von einem ungesicherten `INSERT`, verhindert keine Konkurrenzduplikate.

## 7. Eingangsvertrag, Extraktion und Deduplizierung

### Canonical Envelope

```json
{
  "schema_version": "1.0",
  "scope_id": "<uuid>",
  "source": "EMAIL",
  "source_account_id": "sandbox-mailbox",
  "source_id": "<provider-message-id>",
  "received_at": "2026-10-10T01:00:00Z",
  "sender": "supplier@example.test",
  "subject": "Delivery Update – PO DEMO-PO-8264 / Item 10",
  "content_text": "<untrusted supplier text>",
  "correlation_id": "<uuid>"
}
```

Maximalgrößen, erlaubte Typen und Zeitformate serverseitig validieren. Quellen-IDs aus der jeweiligen vertrauenswürdigen Integration ableiten; ein frei angelieferter Absendername ist kein Nachweis einer Lieferantenidentität. `source_account_id` verhindert Kollisionen zwischen Postfächern.

**Ingestion ist vor Bestätigung dauerhaft:** WF01/WF02 lassen zuerst Event und Analysejob transaktional speichern. Erst danach antwortet der Webhook mit `202`, `source_event_id` und Status-URL. n8n kann WF03 sofort anstoßen; WF08 stellt liegen gebliebene Jobs später erneut zu. Kein frühes `202` vor Speicherung mit anschließend möglichem Datenverlust.

### Extraktionsvertrag

Discriminated Union nach Incident-Typ; alle relevanten Felder besitzen `value`, `evidence` oder eine explizite Angabe `missing/ambiguous`. Speichere Rohtextausschnitt und Position/Verweis zur Herkunft. Fehlende Felder `null`, nicht erfunden. Lieferfall: PO, PO-Position, Material, Menge/Einheit, ursprüngliches Datum, revidierter Lieferplan, **confirmed/proposed** je Teillieferung und Grund. Maschinenfall: Maschinen-ID, Ausfallbeginn/-ende oder unbekannt, betroffene Operation. Qualitätsfall: Chargen-/Prüfungsreferenz, Material, Menge und gemeldete Fehlerart.

Validierungsreihenfolge: gültiges Schema → Quellenbeleg → eindeutig passende ERP-Entität → Mengen-/Datumsplausibilität → ausreichende Pflichtfelder. Kein `confidence >= 0.80`-Gate. ERP-Abweichungen und Angaben wie “next Friday”, fehlendes Jahr oder mehrere passende PO-Positionen erzeugen nachvollziehbare Klärung statt stillschweigender Zuordnung.

Ein Modell darf E-Mail-Inhalte niemals als Systemanweisung behandeln, daraus URLs abrufen, Tools freischalten oder SQL/Code erzeugen und ausführen. Keine Secrets im Prompt. KI bekommt nur die für den jeweiligen Schritt erforderlichen redigierten Daten.

### Drei unterschiedliche Identitäten

1. **Transportduplikat:** DB-Unique auf `(scope_id, source, source_account_id, source_id)`. Identische wiederholte Nachricht liefert dieselbe Event-Referenz. Bei derselben Quell-ID mit abweichendem Inhalt Konflikt markieren, nicht still überschreiben.
2. **Incident-Identität:** Typ + eindeutig identifiziertes Geschäftsobjekt + aktive Störungsepisode. Bei Lieferfällen insbesondere PO-Position; bei Qualität Charge/Prüfung; bei Maschinen Maschine und Ausfallepisode. Bestandsincident mit neuer Nachricht erhält eine Revision, nicht automatisch einen zweiten Incident.
3. **Revisions-Fingerprint:** kanonisch sortierte fachliche Fakten einschließlich Lieferplan, Mengen, Verbindlichkeit und Grund hashen. Gleiche Geschäftsdaten aus Mail und Formular als weitere Quelle verknüpfen. Abweichungen ändern die Revision. Ein später erneut auftretendes Problem nach Abschluss ist eine neue Episode; unsichere Zuordnung → Review.

Ein SHA-Hash ist keine semantische Ähnlichkeitsanalyse. Automatisches Zusammenführen mittels LLM-Ähnlichkeit ist nicht vorgesehen. Parallel eintreffende gleichartige Meldungen müssen durch atomare Anlage/Locks zu einem eindeutigen Ergebnis führen.

## 8. Aktuelle Demo-Fälle: greifbare Fertigungsbeispiele

Die Nutzerkorrektur ersetzt sämtliche früheren Referenzprodukte und Fantasiemarken. Verbindlich sind ausschließlich die aktuellen drei JSON-Dateien unter `fixtures/`.

Analysezeit: 9. November 2026, 08:00 Europe/Berlin. Sämtliche Firmen, Bestellungen, Maschinenkennungen und Vorgänge sind erfunden.

- Stahlstangen (Durchmesser 20 mm, Länge 2 m) für vier Montagerahmen-Aufträge. 75 Stück verspätet; Lkw-Panne. Anfangsbestand 42 minus 10 Fremdreservierungen minus 8 Quarantäne = 24. Bedarf 18/26/20/12; Fehlmengen 0/20/20/0. Zwei betroffene Aufträge, 55.400 EUR, Score 83 CRITICAL. Ein bestätigter Split 30 + 45 ersetzt den ursprünglichen Plan: Fehlmenge 10, ein betroffener Auftrag, 21.600 EUR, Score 56 HIGH.
- Bandsäge S-01: Antriebsriemen gerissen, zwei Tage Stillstand. 10 von 16 Stunden ungedeckt. S-02 kann mit sechs Stunden einen Auftrag übernehmen. Eine Bohrmaschine ist keine Alternative. Score 62 HIGH.
- Montageplatten: 11-mm-Bohrungen statt 10 mm. 48 Teile einer Charge liegen in zwei ausstehenden Sendungen mit 30/18 Teilen. Eine andere fehlerfreie Charge bleibt getrennt. Score 70, CRITICAL durch verifizierten Qualitätsbefund. Versandsperre nur nach Quality-Freigabe.

Die Werte sind Ergebnisse der Berechnung, keine im Anwendungscode hinterlegten Ausgaben. Alte Fixtures, Beispielarchive und Screenshots werden nicht als Regressionseingaben weitergeführt.

## 9. Impact Engine: exakte Rechenregeln

### 9.1 Material und Lieferverzögerung

Vergleiche einen konsistenten Vorher-ERP-Snapshot mit demselben Snapshot plus der verifizierten Incident-Änderung. Alle API-Antworten innerhalb einer Analyse gehören zu derselben Snapshot-ID/Revision. Unterschiedliche ERP-Stände nicht unbemerkt zusammenmischen; bei Konflikt neu lesen.

Verfügbarer Bestand berücksichtigt physische Bestände minus Sperr-/Quarantänemengen und feste Fremdreservierungen. Reservierungen für die betrachteten eigenen Bedarfe gehören weiterhin zu deren gedeckter Menge. Nicht zweimal abziehen. Eine bestandsbezogene Dateninkonsistenz wird als Fehler markiert, nicht durch `max(0, ...)` unsichtbar gemacht.

Erzeuge eine zeitliche Ressourcenfolge aus brauchbaren Zugängen und offenen Bedarfen. Sortierung: Zeitpunkt, Zugang vor Bedarf, dann fachliche Priorität, dann stabile ID. Vergib jede Einheit höchstens einmal. Führe offene Rückstände fort, sodass spätere Zugänge zuerst den festgelegten Allokationsregeln folgen. Der Lieferverspätungs-Override ersetzt den betroffenen ursprünglichen Zugang; er addiert keinen zweiten Zugang.

Für jeden Bedarf ausgeben: Sollmenge, zum Bedarfstermin gedeckte Menge, Fehlmenge, frühestmögliche vollständige Deckung, ursprüngliche vs. neue voraussichtliche Fertigstellung, betroffene Kundenpositionen. Teilmengenunterstützung explizit modellieren. Der einfache erste Scope nimmt kein beliebiges Splitting einer Fertigungsoperation ohne entsprechende Freigabe an.

`affected` bedeutet: durch diese Änderung gegenüber der Baseline neu oder stärker beeinträchtigt. Bereits vorher verspätete Aufträge getrennt kennzeichnen; nicht vollständig dem Incident zuschreiben. `at_risk_sales_line` bedeutet: die modellierte Bereitstellung überschreitet den Kundenliefertermin oder eine benötigte Ressource ist bis dahin nicht deckbar.

### 9.2 Geldwerte

`affected_open_order_value = SUM(open_net_line_value)` über **eindeutige betroffene Kundenpositions-IDs**, jeweils einmal. Im Hero-Modell gilt die gesamte offene Position als betroffen, wenn sie nicht vollständig termingerecht erfüllt werden kann. Das ist eine offen dokumentierte Vollpositions-Konvention, keine anteilig berechnete Verlustsumme.

Dashboard-Gesamtwert über mehrere offene Incidents ebenfalls anhand der Vereinigungsmenge der Positions-IDs berechnen. Incident-Summen einfach zu addieren würde mehrfach betroffene Positionen doppelt zählen. Historische abgeschlossene Bewertungen und Was-wäre-wenn-Varianten nicht in den aktuellen Gesamtwert addieren.

### 9.3 Maschinenstörung

Ausfallintervall mit geplanten Operationen und benötigter Kapazität schneiden. Betroffene Stunden und daraus veränderte Auftragstermine berechnen. Alternativmaschine nur dann als vorhanden ausweisen, wenn Capability, Standort und freie Zeit passen. Ein Vorschlag reserviert noch keine Kapazität; tatsächliche Umplanung nur als genehmigtes synthetisches ERP-Kommando. Keine behauptete Optimallösung eines APS.

Vorgegebener Test: 16 Stunden Bedarf; zehn Stunden fehlen; Ressourcengap 0,625; zwei Tage Disruption; €41.200 gefährdete Positionen; erster Bedarf in höchstens 24 Stunden; die zweite Säge kann nur einen Auftrag übernehmen, keine vollständige Alternative; kein strategischer Kunde. Erwartete Policy-Summe: **62 / HIGH**. Ein Allokations-/Kalenderfixture muss diese Eingaben reproduzierbar erzeugen.

### 9.4 Qualitätsproblem

Prüf-/Chargenreferenz im ERP validieren, betroffene Lieferpositionen verfolgen und unbrauchbaren Bestand von nutzbaren Mengen ausschließen. Eine verifizierte fehlgeschlagene Prüfung einer für eine noch nicht versandte Lieferung reservierten Charge löst den Hard Override `VERIFIED_DEFECTIVE_LOT_PENDING_SHIPMENT` aus: **CRITICAL**, unabhängig vom Summenscore.

Nur Behauptung im Freitext ohne verifizierte Prüfungsdaten → dringende manuelle Klärung, nicht erfundener bestätigter Defekt. Sperrung in der Demo benötigt Quality-Manager-Freigabe; reale Sicherheitssysteme werden nicht ersetzt. Keine automatisierte Entsperrung. Bereits versandte Charge → eigener Review-/Eskalationsfall, kein behaupteter Rückrufvollzug.

## 10. Risk Policy v1 — testbare Geschäftsannahme

Der Score ist eine transparente **Demo-Policy**, keine empirisch validierte Risikowahrscheinlichkeit. Policy in einer versionierten Konfigurationsdatei ablegen; jeder Bewertung deren Version zuordnen.

| Faktor | Definition / Punkte |
|---|---|
| `disruption_days` (max. 25) | 0 Tage: 0; >0 bis 2: 10; >2 bis 5: 15; >5 bis 7: 20; >7: 25. Quelle je Typ: verifizierte Verfügbarkeitsverschiebung, Kapazitätsausfall oder Ersatzverfügbarkeit. |
| `affected_open_order_value_eur` (max. 20) | 0: 0; >0 bis <25.000: 5; 25.000 bis <50.000: 10; 50.000 bis <100.000: 15; ab 100.000: 20. |
| `hours_to_first_relevant_demand` (max. 20) | >168 h: 0; >72 bis 168: 10; >24 bis 72: 16; <=24: 20. Überfälliger Bedarf zählt ebenfalls 20. |
| `uncovered_resource_ratio` (max. 15) | 0: 0; >0 bis <0,25: 5; 0,25 bis <0,50: 8; 0,50 bis <0,75: 12; 0,75 bis 1,00: 15. Material = vor Zugang ungedeckter Bedarf / relevanter Bedarf; Maschine = ungedeckte / erforderliche Kapazität. |
| `qualified_alternative_available` (max. 10) | Geeignete, im relevanten Zeitfenster nutzbare Alternative vorhanden: 0; nachweislich keine: 10. Unbekannt nicht als Nein ausgeben. |
| `strategic_customer_affected` (max. 10) | Mindestens eine betroffene Position eines strategischen Kunden: 10, sonst 0. |

Für Lieferfälle bezieht sich `hours_to_first_relevant_demand` auf den ersten Bedarf im zu prüfenden Fenster, auch wenn dieser durch Restbestand noch gedeckt ist. Der eigene Fehlmengenfaktor bildet ab, wie viel tatsächlich ausfällt. Diese Definition erklärt die 48 Stunden im Stahlstangen-Fall.

**Severity:** 0–24 LOW; 25–49 MEDIUM; 50–74 HIGH; 75–100 CRITICAL. Hero-Basis: `20+15+16+12+10+10 = 83`. Bestätigte Teillieferung: `20+5+16+5+10+0 = 56` (nur der Standardkunde bleibt betroffen). Maschinenfixture: `10+10+20+12+10+0 = 62`.

Wenn eine notwendige Zahl nicht belegbar ist, `risk_score=null`, `data_complete=false`, fehlende Faktoren und `MANUAL_REVIEW` anzeigen; keine erfundenen Nullen. Ein belegter Hard Override kann Severity trotzdem setzen. Bei nachweislich null zusätzlicher operativer Beeinträchtigung und keinem Override: `NO_OPERATIONAL_IMPACT`, Score 0, LOW; keine künstliche Eskalation allein wegen einer Meldung.

Alle Schwellenübergänge, Nullbedarfe, negative/ungültige Werte, Zeitzonen und Overrides als Unit-Tests abdecken. AI erhält die bereits berechnete Bewertung; sie darf weder Faktorwerte noch Severity ändern.

## 11. Zehn n8n-Workflows — ausführbare Aufteilung

Die angegebenen Node-Namen beschreiben Funktionen; die tatsächlich verfügbare Node-Version und ihr Schema auf der Zielinstanz feststellen. Sub-Workflows haben typisierte Eingänge, wohldefinierte Ergebnisse und keine versteckten globalen Abhängigkeiten. n8n unterstützt Execute Sub-workflow einschließlich Warten auf das Ergebnis. [S06]

| Workflow | Trigger und Abfolge | Persistiertes Ergebnis / Verhalten bei Fehler |
|---|---|---|
| **WF01 Email Intake** | Gmail-Testlabel oder authentifizierter synthetischer Mail-Eingang → vollständigen Mailtext holen → Größe/Quelle prüfen → Canonical Envelope → Event dauerhaft aufnehmen → WF03 anstoßen. | Event-/Job-ID; Label erst nach dauerhafter Erfassung setzen. Kein gesamtes persönliches Postfach scannen. Fixture-Eingang ausdrücklich als solcher markieren. |
| **WF02 API / Form Intake** | Authentifizierter Webhook und n8n Form Trigger → Typ-/Feldvalidierung → dieselbe Eingangserfassung → `202` nach Commit → WF03 anstoßen. | Gleicher Vertrag wie WF01. Formular serverseitig schützen; kein anonymer Zugriff auf Live-Aktionen. Strukturiertes Formular benötigt keine LLM-Extraktion. |
| **WF03 Normalize + Verify + Dedupe** | Execute Sub-workflow Trigger mit Event-ID → Job/Lease atomar claimen → Quelle laden → Live- oder Fixture-Extraktion → Schema/Evidence/ERP-Identität prüfen → Incident/Revision atomar zuordnen → WF04 → WF05. | Original Event/Incident/Revision unverwechselbar referenziert. Bei unklaren Daten Review, bei technischer Störung Retry/Fehlerworkflow. Kein zweiter Incident nach Neustart. |
| **WF04 ERP Impact Analysis** | Snapshot öffnen → nach Typ PO-/Bestands-/Bedarfsdaten, Kapazitätsdaten oder Chargentrace lesen → geprüfte Fakten an reine Impact-Funktion geben → Baseline und Incident-Ergebnis speichern. | Unveränderliche Bewertung mit Snapshot-/Methodenversion. Snapshot-Konflikt neu versuchen; Businessdatenmangel manuell klären. |
| **WF05 Risk + AI + Action Plan** | Deterministische Risk Policy ausführen → zulässige Maßnahmen anhand versionierter SOP-/Action-Kataloge auswählen → AI-Zusammenfassung und Entwürfe erzeugen → Zahlen/IDs/Schema prüfen → vollständigen Plan speichern → WF06 oder zulässige automatische Aktionen via WF07. | Score, Quellen und exakte Drafts. Bei fehlender AI funktioniert deterministischer Summary-/Template-Fallback mit sichtbarer Kennzeichnung; keine erdachten Empfehlungen. |
| **WF06 Human Approval** | Plan laden → erforderliche rollenbezogene Freigaben anlegen → Approval-Link intern bekanntmachen → geschützte Wait-Fortsetzung registrieren → warten → DB-Entscheidung erneut lesen → Plan/Ablauf prüfen → WF07 oder Review/neue Planversion. | Keine Entscheidung aus bloßem Webhook-Payload übernehmen. Ablehnung, Änderung, Ablauf, Duplikat und superseded Approval explizit behandeln. |
| **WF07 Action Execution** | Plan-/Aktions-ID → Autorisierung und genehmigten Hash prüfen → Aktion atomar claimen → nach erlaubtem Typ routen → lokalen oder Live-Adapter aufrufen → Provider-Resultat persistieren → nächste fällige Aktion. | Pro Aktion Status, Versuch, Provider-ID und Audit. Nach Versand nur MONITORING, nicht automatisch RESOLVED. Keine freien Agenten-Toolaufrufe. |
| **WF08 SLA + Recovery Monitor** | Schedule alle 60 Sekunden; zusätzlich abgesicherter Test-/Sub-Workflow-Eingang → fällige Jobs/Outbox/Approvals/Störungen atomar claimen → zuständige Workflows aufrufen → Stale-Leases, Wait-Wakeup, Reassessment und SLA-Stufen abarbeiten. | DB-Fälligkeiten, keine minutenlangen Schleifen im Code-Node. Pro Incident und Eskalationsstufe eindeutiger Schlüssel. Leere Abfrage endet ohne Fehler. |
| **WF09 Error + Dead Letter Handler** | Error Trigger und definierter Sub-Workflow-Eingang → Fehlermetadaten normalisieren/redigieren → betroffenen Job/Aktion feststellen → Retry oder DLQ → interne Meldung. | Keine pauschale Wiederholung kompletter Abläufe nach bereits ausgeführten Effekten. Keine Selbst-Fehlerschleife. Fataler DB-Ausfall zusätzlich in strukturierten Runtime-Logs sichtbar. |
| **WF10 Daily Management Digest** | Schedule täglich 08:00 Berlin; manuell im Demo-Modus → konsistenten KPI-Snapshot lesen → deterministischen Bericht erstellen → optional sprachlich zusammenfassen → internen Entwurf/Sandbox-Digest ablegen. | Eindeutig je Scope, Geschäftsdatum und Kanal. Zahlen stammen aus API, nicht LLM. Keine versprochenen Einsparungen. |

**Sub-Workflow-Verträge:** mindestens `schema_version`, `scope_id`, `correlation_id`, `source_event_id` und, sobald vorhanden, `incident_id`, `revision`, `job_id`. Große Rohtexte/Snapshots in der DB halten und per Referenz laden statt durch alle Nodes zu vervielfältigen. Keine `$node`-Referenzen auf in dem jeweiligen Branch nicht ausgeführte Nodes; leere Items und Mehrfach-Items testen.

**Canvas-Qualität:** nach Prozessabschnitt gruppierte und benannte Nodes, kurze Sticky Notes für Geschäftszweck, klare Error-Zweige, keine unlesbare 120-Node-Kette. Eingabebeispiele ausschließlich synthetisch. In exportierten Workflows keine echten Executions, Secrets oder sensiblen `pinData`.

## 12. Statusmodelle und Konsistenz

### Incident-Zustand

```text
NEW → ANALYZING → ASSESSED
                    ├→ WAITING_APPROVAL → ACTION_IN_PROGRESS → MONITORING
                    ├→ ACTION_IN_PROGRESS → MONITORING
                    └→ MONITORING  (keine Aktion erforderlich)
MONITORING → RESOLVED → CLOSED
```

`MANUAL_REVIEW` ist ein betreuter Klärungszustand. Eine nachvollziehbare Korrektur führt mit neuer Revision zurück nach `ANALYZING`. Neue fachliche Fakten können aus ASSESSED, WAITING_APPROVAL, ACTION_IN_PROGRESS oder MONITORING eine neue Analyse auslösen. Bereits ausgeführte Aktionen werden nicht rückwirkend gelöscht; noch nicht ausgeführte Aktionen können gesperrt/superseded werden. Wiedereröffnung nach CLOSED erzeugt bei neuer Störung eine neue Episode mit Verweis auf den alten Incident.

**Approval:** `PENDING | APPROVED | REJECTED | EXPIRED | SUPERSEDED`. MODIFY erzeugt eine neue Planversion und Freigabe; es ändert nicht heimlich eine bereits genehmigte Version.

**Aktion:** `PLANNED | WAITING_APPROVAL | READY | IN_PROGRESS | SUCCEEDED | RETRY_SCHEDULED | FAILED | UNKNOWN_OUTCOME | CANCELLED`.

**Analysejob:** `PENDING | RUNNING | RETRY_SCHEDULED | SUCCEEDED | DEAD_LETTER`. Vorübergehender technischer Fehler ist kein gelöstes oder endgültig abgelehntes Geschäftsproblem.

Jeder Übergang besitzt erlaubte Ausgangszustände, erwartete Objektversion, autorisierte Rolle und Audit-Ereignis. APIs müssen verbotene/überholte Übergänge mit `409` oder `403` abweisen. Zulässige Wiederholungen geben dasselbe Resultat zurück. Nicht nur Frontend-Buttons deaktivieren.

**Resolution:** `RESOLVED` erfordert belegte fachliche Erledigung, z. B. bestätigten Materialeingang und neu gedeckten Bedarf, wiederhergestellte Kapazität oder dokumentierte Quality-Disposition. Ein verschicktes Ticket oder eine Supplier-E-Mail genügt nicht. Demo-Skripte dürfen entsprechende synthetische ERP-Ereignisse erzeugen, müssen sie aber sichtbar als Demo-Daten ausweisen.

## 13. Human Approval und Actions Policy

### 13.1 Autorisierung nach Aktion, nicht nur nach Severity

| Aktion | Automatisch erlaubt? | Erforderliche Freigabe |
|---|---|---|
| Audit, interne Risikoberechnung, Entwurf speichern | Ja | Keine externe Wirkung. |
| Interne Sandbox-Benachrichtigung / internes Ticket | Ja, falls konfiguriert | Idempotent; sensible Inhalte minimieren. |
| Lieferanten-/Kunden-E-Mail, Anfrage einer Alternativlieferung | Nein, auch nicht bei LOW | Zuständige Einkaufs-/Managementrolle; exakter Empfänger und Text genehmigt. |
| Produktionsumplanung im Mock ERP | Nein | Production manager; betroffene Aufträge/Termine gebunden. |
| Versandsperre im Mock ERP | Nein | Quality manager. |
| Aufheben einer Qualitätssperre | Nicht automatisch | Gesonderte Quality-Entscheidung mit Beleg. |
| Reales ERP-/Maschinenkommando, Kauf oder Kostenverpflichtung | Nicht im Scope | Durch dieses Projekt nicht ausführbar. |

Bei CRITICAL muss der fachliche Maßnahmenplan immer vom verantwortlichen Manager geprüft werden; zusätzliche Quality-Freigabe für Quality-Aktionen bleibt unabhängig erforderlich. Internes Alarmieren/Protokollieren darf währenddessen bereits stattfinden. Kein “LOW bedeutet beliebige externe Aktionen”.

### 13.2 Freigabeprotokoll

Der genehmigte Plan bindet mindestens `incident_revision`, `impact_assessment_id`, `policy_version`, `plan_version`, `plan_hash`, alle Aktionstypen, Zielidentitäten, Empfänger, Betreff, vollständigen Nachrichtentext und Schreibparameter. Vor tatsächlichem Dispatch erneut auf Gültigkeit prüfen. Keine Text-Neugenerierung nach Approval.

Login/Session und serverseitige Rollenprüfung sind die maßgebliche Identität. Demo-Benutzer lokal beim Bootstrap sicher anlegen; keine öffentlich bekannte Admin-Passwortvorgabe in einer erreichbaren Instanz. Keine Umgehung per `X-Role: manager`. Ein Freigabelink navigiert nur; GET löst nie eine Entscheidung aus. POST verlangt passende Rolle, CSRF-Schutz bei Cookie-Auth, erwartete Version und gegebenenfalls kurzlebigen Einmal-Token. Tokens gehasht speichern und nicht loggen.

Die n8n-Wait-URL ist **nur technischer Wakeup**, nicht die fachliche Autorisierung. Der Browser erhält sie nicht. Backend speichert sie intern, prüft beim Registrieren erlaubten n8n-Host/Pfad und verwendet unterstützte Webhook-Authentifizierung. Nach Resume lädt WF06 die autoritative Entscheidung aus der DB. Wait unterstützt zeitliche bzw. webhookbasierte Fortsetzung; Version und Authentifizierungsoptionen prüfen. [S07]

Approval-Konsum und Action-Outbox-Eintrag gehören in eine Transaktion. Bei Approval unmittelbar bevor die n8n-Ausführung tatsächlich wartet: Entscheidung dauerhaft speichern; Wakeup bei noch nicht bereiter Wait-URL erneut versuchen. Der Watchdog repariert verloren gegangene Fortsetzungen, ohne die Entscheidung erneut zu verlangen. Wait-Timeout prüft den DB-Zustand atomar; ein bereits gespeichertes Approval darf nicht nachträglich als expired überschrieben werden.

Neue maßgebliche Incident-/Planrevision → PENDING-Approvals superseded; genehmigte, noch nicht dispatchte Aktionen vor Ausführung erneut prüfen und nötigenfalls blockieren. Bereits in-flight befindliche externe Effekte nicht als rückgängig gemacht ausgeben. Rollen, Planversionen, Race Conditions und Token-Replay testen.

## 14. Zuverlässigkeit, Outbox und Eskalation

**Zustellmodell:** mindestens einmal. Lokale Effekte werden anhand persistierter Eindeutigkeit idempotent. Kein pauschales “exactly once” für beliebige Fremdsysteme.

Aktionserzeugung und Outbox-Eintrag in einer DB-Transaktion. Worker claimen atomar mit Lease, Versuchszähler und `next_attempt_at`; abgelaufene Leases werden nach Prüfung wieder aufgenommen. Action-Key bindet Scope, Incident, Planversion, Aktionstyp und Ziel. Derselbe Transport-Retry darf nicht einen neuen Action-Key erzeugen.

Externe Anbieter mit dokumentierter Idempotency-Unterstützung bekommen stabilen Key; Retention und Geltungsbereich des Anbieters beachten. Bei Timeout **nach möglicherweise erfolgtem Versand** ohne belastbare Idempotency-/Statusabfrage: `UNKNOWN_OUTCOME`, Provider-Reconciliation oder manuelle Klärung. Nicht blind erneut senden. Auch ein negativer sofortiger Suchtreffer bei einem eventual-consistent Provider ist kein sicherer Nichtversandbeweis. Der lokale Sandbox-Adapter muss den kritischen “Erfolg beim Provider, Timeout beim Client”-Fall reproduzieren können.

### Fehler- und Retry-Policy

Verbindlicher Default: maximal vier Gesamtversuche pro retrybarem Job/Aktion; Backoff 5 s, 30 s, 120 s plus Jitter. Bei `429` Retry-After beachten und Fälligkeit entsprechend verschieben. Read-Timeout/`5xx` grundsätzlich retrybar; unklarer Schreib-Timeout folgt obiger Sonderregel. `400/422` Datenfehler nicht technisch endlos wiederholen; `401/403` Konfigurations-/Rechteblocker; fehlendes eindeutiges Geschäftsobjekt Review. Nicht sowohl Node-Retry als auch Job-Retry unkontrolliert multiplizieren.

WF09 sammelt unerwartete Fehler; absichtlich behandelte Fehlerpfade rufen seine normalisierte Aufnahme explizit auf. Ein globales Error Trigger-Workflow ersetzt keine Wiederanlaufstrategie. Das Verhalten bei manueller gegenüber aktivierter Ausführung auf der Zielversion tatsächlich prüfen; automatisierte Fehlertests über veröffentlichte Sandbox-Trigger auslösen. n8n dokumentiert Error-Workflows und Error Trigger. [S08]

**SLA-Policy v1, frei gewählte Demo-Annahme:** Critical-Review binnen 15 Minuten; High binnen 60 Minuten; Medium binnen vier Stunden. LOW hat kein Management-Approval-SLA. Fälligkeit bezieht sich auf den aktuellen gültigen Plan; keine automatische Freigabe nach Ablauf. Nach Ablauf zunächst Owner-Erinnerung, danach Manager-Eskalation nach weiteren gleich langen Intervallen. Pro Stufe und Planversion höchstens eine Benachrichtigung.

Action-Follow-up für offen gebliebene Supplier-/Rescheduling-Maßnahmen nach vier Geschäftsstunden im vereinfachten Demo-Kalender; für eine Live-Sandbox Geschäftszeiten konfigurierbar machen und dokumentieren. Kein UI-Fortschrittsbalken behauptet die Behebung einer Störung, solange nur eine Nachricht versendet wurde.

Alle zeitbezogenen Domain-Regeln beziehen ihre Uhr aus einer testbaren Clock-Abstraktion. Demo-Zeit kann kontrolliert weitergesetzt werden. Der n8n-Wait-Node selbst verwendet reale Runtime-Zeit; für kurze Tests eigene kurze Wait-Timeouts bzw. explizite Wakeups verwenden. Keine Behauptung, die Backend-Testuhr verstelle n8n intern.

Observability: redigierte JSON-Logs, `correlation_id`, Workflow-/Execution-/Job-IDs, Dauer pro Schritt, LLM-Aufrufe/Token soweit ermittelbar, Anzahl Retries, DLQ, offene Approvals, SLA-Verletzungen, bekannte Action-Ergebnisse. Audit append-only mit eingeschränkter DB-Rolle; keine Behauptung kryptografischer Manipulationssicherheit ohne zusätzliche Umsetzung.

## 15. API-Contracts

OpenAPI aus typisierten Backend-Modellen erzeugen. Eingabe-, Ergebnis- und Fehlerverträge versionieren. Keine beliebige Statusänderung per ungesichertem PATCH. Backend darf ausschließlich erlaubte Domänenkommandos ausführen.

| Route / Funktionsgruppe | Minimaler Vertrag |
|---|---|
| `POST /api/intake` | Authentifizierter UI-Eingang; Übergabe an WF02. Erfolgsantwort erst nach bestätigtem Commit der internen Event-Aufnahme, andernfalls `503`; gleicher Quellschlüssel beim Retry. |
| `POST /internal/source-events` | Service-authentifiziert; Canonical Envelope → atomarer Event/Job-Commit; bestehende ID bei identischem Duplikat; Konflikt bei abweichendem Inhalt. |
| `GET /api/source-events/{id}` | Autorisierter Verarbeitungsstatus mit Incident-Referenz oder Review-Grund. |
| `GET /api/incidents`, `GET /api/incidents/{id}` | Filter, Pagination und Detail mit Revision, Impact, Risk, Plan, Timeline und Datenqualitätsstatus; keine Secrets. |
| `POST /api/incidents/{id}/corrections` | Fachliche Korrektur plus Begründung, erwartete Revision; neue Analyse statt Überschreiben historischer Fakten. |
| `POST /api/approvals/{id}/decision` | APPROVE/REJECT/MODIFY, erwartete Version, Kommentar; Actor aus Auth-Kontext; kontrollierte Transaktion. |
| `POST /api/incidents/{id}/resolve` / `/close` | Passende Rolle, Begründung und Auflösungsbeleg; erlaubten Status prüfen. |
| `GET /api/dashboard` | Aktuelle scopebezogene KPIs inklusive Vereinigungsmenge betroffener Positionen, offene Freigaben, SLA; gefilterter Zeitraum eindeutig. |
| `GET /api/actions`, `GET /api/errors` | Rollenbegrenzte Aktions-/Fehleransicht; redigierte Daten. |
| `POST /api/errors/{id}/retry` | Admin; nur bekannte retrybare Einträge, stabile Original-IDs und Audit. |
| `POST /api/demo/runs` / `POST /api/demo/runs/{id}/advance` | Nur Demo; neuen Scope/Clock mit Seed erzeugen bzw. kontrolliert fortschreiten; passende WF01/WF02-Eingänge nutzen. |
| `POST /internal/jobs/claim`, `/complete`, `/fail` | Atomare Lease-/Versionsprüfung; keine Freigabe aus User-Payload. |
| `POST /internal/impact/evaluate`, `/internal/risk/evaluate` | Typisierte, reine Eingaben/Snapshots → versionierte Ergebnisse. |
| `POST /internal/plans`, `/internal/approvals`, `/internal/actions/...` | Plananlage, kontrollierte Freigabe-/Dispatch-/Resultatkommandos. |
| `GET /erp/v1/...` | PO-/Positions-, Bestands-/Bedarfs-, Maschinen-/Kapazitäts- und Chargen-/Lieferdaten; Snapshot-ID obligatorisch. |
| `POST /erp/v1/commands/...` | Ausschließlich freigegebene, idempotente synthetische Umplanung/Versandsperre; separates privilegiertes Service-Credential. |
| `/health/live`, `/health/ready` | Liveness getrennt von Dependency-Readiness. Keine Geheimnisse im Status. |

Fehlerantwort: `error_code`, sichere `message`, `retryable`, `correlation_id`, gegebenenfalls `field_errors`. Erwartete HTTP-Semantik: 202 aufgenommen, 401 nicht authentifiziert, 403 unzulässig, 409 Konflikt, 422 ungültige Daten, 429 Limit, 503 vorübergehend nicht verfügbar. Scope-Zugriff in jeder Route serverseitig prüfen.

## 16. Dashboard — klein, aber vollständig bedienbar

Ein englischsprachiges Operations Control Center, kein zweites Großprojekt. Ruhige B2B-Oberfläche, gut lesbare Tabellen, klare Hierarchie, responsiv. Status nicht nur durch Rot/Grün vermitteln; Text/Icons ergänzen. Tastaturbedienung, sichtbarer Fokus, Label und ausreichender Kontrast. Kein fremdes Unternehmenslogo und keine suggerierte EBRO-Implementierung.

**Ansicht 1 — Overview:** Open incidents, Critical incidents, Affected open-order value, Pending approvals, SLA breaches. Filter nach Typ, Severity, Status und Zeitraum. Bei leerem Scope sinnvolle Empty State statt erfundener Zahlen. Demo-/Live-AI-/Sandbox-Modus und Datenstand permanent sichtbar.

**Ansicht 2 — Incident detail:** Originalmeldung mit markierten Belegen; Datenqualität; Baseline vs. Was-wäre-wenn; geprüfte und betroffene Produktions-/Kundenpositionen; Faktoraufschlüsselung und Policy-Version; AI-Zusammenfassung mit klarer Kennzeichnung; versionierte Maßnahmen; Freigaben; Timeline. Keine nur statischen Screenshots oder hartcodierten KPI-Werte.

**Ansicht 3 — Approval inbox:** zuständige Rolle, Frist, exakt zu genehmigende Texte/Parameter, Approve/Reject/Modify, Begründung, Hinweis bei veralteter Version. Autorisierung serverseitig. Viewer kann keine fachliche Aktion auslösen.

**Ansicht 4 — Reliability:** Execution-/Job-Referenzen, Retries, Dead Letter Queue, UNKNOWN_OUTCOME und kontrollierter Retry. Keine rohe Stacktrace-/Credential-Ausgabe an Recruiter.

**Geführte Demo:** drei Startpunkte Supplier Delay, Machine Breakdown, Quality Issue. Fortschritt zeigt echte persistierte Statusänderungen. Public-demo-Modus strikt read-only oder isolierte synthetische Session mit lokalen Effekten; kein öffentlicher n8n-Editor, keine Live-Credentials im Browser. Plan für Veröffentlichung liefern; nicht automatisch auf einem kostenpflichtigen Host veröffentlichen.

## 17. KI-Umsetzung und Evaluation

Zwei zentrale AI-Aufgaben genügen: strukturierte Extraktion und erklärende Zusammenfassung/Entwürfe. Nicht für jeden Schritt einen frei agierenden Agenten einbauen. Prompt-/Schema-Version, verwendetes Modell, Anbieter und Antwortmetadaten speichern. Modell über Konfiguration wählen, nicht einen vermeintlich aktuellen Modellnamen fest verdrahten.

Anbieterfähige strukturierte Ausgabe nutzen, falls verfügbar, plus serverseitige Schema-/Faktenvalidierung. Eine schema-valide Antwort garantiert keine inhaltlich wahren Fakten. [S12] Empfehlungen nur aus einem erlaubten Maßnahmenkatalog und versionierten kleinen SOP-Dateien; deren IDs in der Planbegründung zeigen. Kein Vector Store nötig. Facts wie Mengen, Beträge und Termine in fertigen Texten gegen den Ground-Truth-Assessment prüfen; bei Abweichung deterministisches Template verwenden oder Review.

Fehler-/Kostenlimits: Timeouts pro Call, höchstens eine kontrollierte Reparatur ungültigen Schemas; danach Review/Fallback. Keine endlosen Agentenschleifen. Demo verwendet keine bezahlten Calls. Live-Evaluation nur bei vorhandener Autorisierung und konfiguriertem Kosten-/Aufruflimit. Kosten aus tatsächlichem Usage und versionierter Preisbasis berechnen oder ausdrücklich als unbekannt kennzeichnen.

**Datensatz:** 50 vollständig synthetische, versionierte Eingaben; 30 Entwicklungsfälle, 20 gesperrte Holdout-Fälle. Abdecken: alle drei Typen, mehrere Positionen, fehlende IDs/Jahre, vorgeschlagene Teillieferung, relative Daten, Widersprüche, Duplikate, unbekannte Lieferanten, Prompt Injection und falsche Mengen. Prompt nicht gegen Holdout optimieren; bei Iteration neuen Holdout anlegen und Herkunft dokumentieren.

**Metriken:** Incident-Typ-Accuracy, Exact-Match PO/Position/Material, Datums-/Mengen-Accuracy, Schema-Validität, Rate unbelegter kritischer Fakten, Review-Recall für unsichere Fälle, automatische Verarbeitungsquote, Latenz p50/p95 und Kosten soweit verfügbar. Nenner und Zahl der Testfälle berichten; bei kleinen Stichproben keine Generalisierungsgewissheit behaupten.

**Ziel-Gates, keine behaupteten Messergebnisse:** nach höchstens einem Repair 100% schema-valide oder korrekt in Review; keine unbelegten kritischen IDs/Mengen/Termine in automatisch weiterverarbeiteten Holdout-Fällen; 100% Review-Erkennung der verpflichtenden Ambiguitäts-/Injection-Fixtures; mindestens 95% Typ-Accuracy auf eindeutig klassifizierbaren Fällen; mindestens 95% kritischer Felder-Exact-Match auf eindeutig extrahierbaren Fällen. Hohe Review-Quote sichtbar ausweisen, damit “alles in Review” nicht als erfolgreiche AI-Automation gilt.

Deterministische Fixture-Tests und echte Modell-Evaluation streng getrennt ausweisen. Kein Live-Key bedeutet `LIVE_EVAL_NOT_RUN`, nicht bestanden. Native n8n-Evaluation-Nodes können verwendet werden, aber die Releaseprüfung muss auch unabhängig davon durch einen reproduzierbaren Test-Runner funktionieren.

## 18. Sicherheits- und Betriebsanforderungen

Keine Credentials, Tokens, echten Absender, Rohmails oder persönliche Daten im Repository. `.env.example` enthält nur Platzhalter. Credential-Values in n8n-Credential-Store bzw. lokalem Secret-Management; bei Export nur bereinigte Referenzen. Lokale Secrets zufällig erzeugen, nicht vom LLM frei erfinden und in Dokumentation veröffentlichen. Encryption-Key und DB-Volumes persistent und passend gesichert; kein erzwungener Key-Wechsel bei Redeployment.

Backend-Auth mit etablierten Bibliotheken, sicheren Passwort-Hashes und Session-/Cookie-Konfiguration. Keine selbst entworfene Kryptografie. Service-Credentials je Zweck; öffentliche UI-Routen nicht mit internem n8n-Servicezugang gleichsetzen. HTTPS für entfernte Endpoints, CORS-Allowlist, Rate Limits, CSRF und serverseitiges Input-Limit. Deployment-spezifische Webhook-URLs und Credentials nie als Frontend-Environment ausliefern.

HTML aus E-Mails sanitizen, als Daten behandeln und keine externen Ressourcen nachladen. Kein `eval`, keine Shell-/SQL-Ausführung aus LLM-Ausgaben, kein freier URL-Fetch aus Supplier-Inhalt. Action-Tool-Allowlist und Recipient-Allowlist sind unabhängig vom Modell durchzusetzen. Keine nicht geprüften Community-Nodes automatisch installieren.

Dev-/Demo-/Live-Konfiguration unterscheiden. Sensible Execution-Payloads minimieren; Aufbewahrung und Pruning konfigurieren und dokumentieren. Nachweisbare redigierte Betriebslogs und fachliche Audit-Ereignisse getrennt von Rohdaten halten. Demo-Reset scopebegrenzt und idempotent; keine unbedachte `DROP DATABASE`-Aktion gegen eine bestehende Instanz.

## 19. Repository, Bootstrap und erforderliche Artefakte

```text
ai-production-incident-control/
  README.md
  AGENTS.md
  CONTEXT.md                         # nur Fachbegriffe, keine Implementierung
  CODEX_BUILD_SPEC.md
  compose.yaml
  compose.queue.yaml                 # optional, klar als optional markiert
  .env.example
  .gitignore
  backend/                           # Operations + ERP Startpunkte, Domain-Funktionen
  dashboard/
  database/migrations/
  database/seeds/
  n8n/workflows/                     # zehn bereinigte, getestete Exporte
  n8n/manifest.example.json
  config/risk-policy.v1.json
  config/sla-policy.v1.json
  config/action-catalog.v1.json
  prompts/
  sops/
  fixtures/
  tests/unit/
  tests/integration/
  tests/e2e/
  tests/evaluations/
  scripts/                          # bootstrap, deploy, verify, export, reset-demo
  docs/adr/
  docs/architecture.md
  docs/data-model.md
  docs/security.md
  docs/demo-guide.md
  docs/limitations.md
  docs/implementation/
  docs/portfolio/
  .github/workflows/ci.yml
```

Die Struktur ist ein Implementierungsdefault; sinnvoll an vorhandene Repo-Konventionen anpassen und nicht nur leere Ordner erzeugen. `CONTEXT.md` bleibt Glossar. ADRs nur für echte schwer rückgängig zu machende Abwägungen: Orchestrierungsgrenze, sichere Aktionsausführung/Freigaben, Bewertung/Snapshot-Semantik und Betriebsprofile. Keine ADR pro Node.

**Bootstrap-Ziel:** dokumentierter Erststart mit wenigen klaren Befehlen. Ein Bootstrap-Script prüft Voraussetzungen, erstellt lokale Secrets, startet Infrastruktur, wartet auf Healthchecks, migriert und seeded idempotent und importiert/deployed Workflows über einen tatsächlich unterstützten Weg. Eine unvermeidbare initiale n8n-Owner-/API-Key-/OAuth-Einrichtung offen als einmaligen Schritt benennen. Nicht versprechen, `docker compose up` führe externe OAuth-Einwilligungen aus.

Windows-11-Nutzung berücksichtigen: PowerShell-Aufruf/Wrapper oder dokumentiertes Docker-Desktop-/WSL-Vorgehen, keine ausschließliche Abhängigkeit von lokalem GNU Make. Tests möglichst in Containern startbar. Zweiter Bootstrap-Durchlauf darf keine zusätzlichen Workflows, Datenbankobjekte oder Mailversendungen erzeugen.

README auf Englisch mit Businessproblem, demonstriertem Ergebnis, Kennzeichnung synthetischer Daten, Architektur, Startanleitung, drei Demo-Szenarien, Screenshots echter Läufe, Testanleitung und bekannten Grenzen. Kurzes Walkthrough-Skript und Interview-Erklärung: Warum n8n? Warum nicht alles LLM? Wie vermeiden wir Doppelversand? Wie wurde der Score gewählt? Was ist beim Live-ERP anders?

Lizenz nur für den eigenen Projektcode geeignet wählen und Drittanbieterhinweise berücksichtigen. n8n nicht als eigenen Code ausgeben und keine Fremdlizenz überschreiben. Öffentliche Repo-Erstellung/-Freigabe nur auf dem vom Nutzer autorisierten Ziel; fehlen dessen Rechte, Repository lokal fertigstellen statt unter einem geratenen Konto zu veröffentlichen.

## 20. Implementierungsreihenfolge mit Exit-Gates

| Meilenstein | Ergebnis | Gate zum Fortfahren |
|---|---|---|
| **M0 — Discovery & Contracts** | Repo/Connector/Version/Netzwerk geprüft; Environment-Report; OpenAPI-Grundverträge; aktive Projektentscheidungen festgehalten. | Tatsächliche Fähigkeiten und Blocker dokumentiert; keine ungeprüfte Zielinstanz geändert. |
| **M1 — Infrastructure & Domain** | Compose, Datenbanken, Migrationen, Seeds, Uhr, API-Auth; Hero-Snapshot und reine Impact/Risk-Funktionen. | Unit-/Integrationstests ergeben 40 Fehlmenge, zwei betroffene MOs, €55.400 und Score 83. |
| **M2 — Intake → Assessment** | WF01–WF05 in echter lokaler n8n-Instanz; Fixture-AI; source-event/jobs; Transport-/Business-Dedupe. | Ein authentifizierter Eingang läuft bis zur gespeicherten Bewertung; gleichzeitige Duplikate bleiben eindeutig. |
| **M3 — Approval → Action → Recovery** | WF06–WF09; Zustandsübergänge, sichere Freigabe, lokale Side-Effect-Adapter, Outbox, SLA, DLQ. | Approve/Reject/Modify/Expire, früher Approval-Klick, Restart und unklarer Versand erfolgreich getestet. |
| **M4 — Complete Use Cases** | Maschinen- und Quality-Seed, Impactlogik, passende Aktionen; WF10 Digest. | Alle drei End-to-End-Szenarien fachlich korrekt; kein Auto-Resolve nach Nachricht. |
| **M5 — Product Demo** | Vier Dashboard-Ansichten, geführte Demos, Rollen, Status-/Fehler-/Empty-States. | Browser-Tests zeigen echte Backenddaten und korrekte Rechte; keine hardcodierten KPIs. |
| **M6 — Connected Sandbox** | Zehn Workflows mit Connector auf autorisiertem n8n deployed, URLs/Credentials gebunden, vorhandene Live-Adapter geprüft. | Test-Execution-IDs und Rollback-Exporte vorhanden; fehlende Zugriffe präzise ausgewiesen. |
| **M7 — Quality & Portfolio Release** | CI, 50 Evaluationsfälle, ggf. echte Eval, Security-Checks, sauberes README, Screenshots, Demo-Skript, Handover. | Abnahmematrix mit Belegen, keine unbegründeten Erfolgsaussagen, reproduzierbarer zweiter Start. |

M6 ist ein eigener Zugriffs-/Deployment-Schritt. Bei fehlender Verbindung M6 als BLOCKED_TARGET_CONNECTION führen; M1–M5 und davon unabhängige Dokumentations-/Testarbeiten aus M7 fortsetzen. Keine vollständige Zielabnahme behaupten.

Bei Kontextwechsel `docs/implementation/progress.md` aktualisieren: erledigt mit Beleg, aktuelle Aufgabe, nächste Aufgabe, Blocker und letzte Testergebnisse. Nicht denselben Plan neu erfinden. Nach M1 können unabhängige Frontend- und Test-Arbeiten parallelisiert werden. Veröffentlichung bleibt getrennt vom lokalen Fertigstellen.

## 21. Abnahmematrix — verbindlich, nicht nur Vorschläge

Ein Test gilt nur mit beobachtetem Ergebnis als bestanden. Automatisierte Akzeptanztests sollen Backend-API und veröffentlichte Sandbox-Workflows als höchste sinnvolle Grenze verwenden. Reine Risk-/Allokationsfunktionen zusätzlich gezielt per Unit-Tests prüfen. Node-interne Implementierungsdetails nicht unnötig festzurren.

| ID | Test | Erwartung |
|---|---|---|
| AC01 | Frischer lokaler Start | Dienste healthy; Seeds/Migrationen bereit; Demo ohne externe Konten nutzbar. |
| AC02 | Zweiter Bootstrap/Deploy | Keine doppelten Workflow-IDs/Seeds/Aktionen; persistente Daten bleiben erhalten. |
| AC03 | Liefer-Hero Baseline | 76 Bedarf, 24 Anfangsbestand, 36 termingerecht gedeckt, 40 Fehlmenge; vier geprüft, zwei betroffen; €55.400; 83 CRITICAL. |
| AC04 | Nur angebotene 30 Stück | Baseline bleibt unverändert; Angebot nur als Was-wäre-wenn sichtbar. |
| AC05 | Bestätigter Split 30 + 45 | Insgesamt 40 Zugang; 14 Fehlmenge; ein betroffener MO; €21.600; 56 HIGH. |
| AC06 | Zehn identische Quellen gleichzeitig | Ein Source Event und ein fachlicher Incident; keine doppelten externen Aktionen. |
| AC07 | Mail + Formular, dieselben Fakten | Zwei Quellen verknüpft, ein Incident, identische Revision nicht doppelt bewertet. |
| AC08 | Neue Meldung, Terminänderung | Neue Revision desselben aktiven Incidents; Altbewertung erhalten, passende Approvals superseded. |
| AC09 | Mehrere passende PO-Positionen / fehlendes Jahr | MANUAL_REVIEW mit konkretem Klärungsgrund; keine erfundene Zuordnung. |
| AC10 | Reservierter/gesperrter Bestand | Keine Anrechnung als freier Bestand und kein Doppelabzug eigener Reservierungen. |
| AC11 | Gleiche Kundenposition in zwei Incidents | Dashboard-Gesamtwert zählt die Position einmal. |
| AC12 | Prompt Injection im Mailtext | Keine Tools/URLs/Empfänger aus injizierter Anweisung; Fakten validiert oder Review. |
| AC13 | Falsche LLM-Zahl im Entwurf | Draft wird verworfen/korrigiert mit Template oder Review; nicht ungesehen versendet. |
| AC14 | Approve derselben Version zweimal | Ein gültiger Konsum; Aktion höchstens einmal im Sandbox-Provider. |
| AC15 | Approval vor tatsächlicher Wait-Bereitschaft | Entscheidung bleibt gespeichert; Workflow wird später fortgesetzt. |
| AC16 | Abgelehnt / geändert / abgelaufen | Kein unzulässiger Dispatch; Modify erzeugt neue Version/Freigabe; Incident bleibt offen. |
| AC17 | Alte Freigabe nach neuem Plan | Konflikt; keine Aktion für veraltete Fakten. |
| AC18 | Viewer / manipulierte Rolle / Token-Replay | Serverseitig verhindert; GET-Link allein bewirkt keine Entscheidung. |
| AC19 | Provider erfolgreich, Client-Timeout | UNKNOWN_OUTCOME oder belegte Reconciliation; kein blindes erneutes Senden. |
| AC20 | Temporärer API-Fehler / 429 | Begrenzte Retries, Backoff/Retry-After; am Ende Erfolg oder nachvollziehbare DLQ. |
| AC21 | DB-Ausfall vor Ingestion-Commit | Kein falsches 202; Quelle sicher erneut zustellbar; Runtime-Fehler sichtbar. |
| AC22 | Restart während Wartestatus / nach Outbox-Commit | Wiederanlauf aus DB; keine verlorene Freigabe und keine doppelte Wirkung. |
| AC23 | Fällige SLA mehrfach geprüft | Pro Plan/Stufe nur eine Eskalation; keine automatische Freigabe. |
| AC24 | Maschinenfixture | Qualifizierte Alternative belegt; Capacity Gap korrekt; Score 62 HIGH; Umplanung nur genehmigt. |
| AC25 | Verifiziert defekte Charge in offener Lieferung | Trace korrekt; CRITICAL-Hard-Override; Mock-Sperre nur mit Quality-Freigabe. |
| AC26 | Meldung ohne bestätigten Qualitätsbeleg | Dringende Klärung statt erfundener bestätigter Prüfung. |
| AC27 | Supplier-Mail wurde gesendet | Incident bleibt MONITORING, bis fachliche Erledigung nachgewiesen ist. |
| AC28 | Digest zweimal für gleichen Tag | Ein Bericht je Scope/Datum/Kanal; Zahlen identisch mit KPI-API. |
| AC29 | Demo-Reset | Nur eigener synthetischer Scope verändert; keine fremden Workflows/Daten berührt. |
| AC30 | Export-/Repo-Geheimnisscan | Keine Secrets, echten Rohmails oder privaten Kundendaten. |
| AC31 | Zielinstanz-Test | Zehn Projektworkflows gelesen/deployed; durchgeführte E2E-Läufe mit Execution-IDs belegt. |
| AC32 | Evaluation-Bericht | Fixture vs. Live klar getrennt; Modell-/Datensatzversion und Nenner angegeben; nicht gelaufen ist nicht bestanden. |
| AC33 | Nicht vollständige bzw. gemischte ERP-Snapshots | Keine scheinbar verlässliche Bewertung aus inkonsistentem Datenstand. |
| AC34 | API-Auth, CSRF, Scope-Isolation | Fremdscope/unerlaubte Mutation verhindert; Service- und User-Rechte nicht austauschbar. |
| AC35 | LOW-Incident mit externer Mailaktion | Trotzdem fachliche Freigabe erforderlich. |
| AC36 | n8n Canvas / Dashboard Konsistenz | Sichtbare Statuswerte und gespeicherte Ergebnisse stimmen mit echten Executions überein. |

Bei fehlenden Live-Credentials können lokale Tests bestehen, AC31/Live-Teile aber blockiert bleiben. Dann lautet der Status ausdrücklich “local demo complete; connected sandbox blocked”, nicht “everything done”. Security-, Datenintegritäts- und fachliche Kernfehler dürfen nicht durch Dokumentation als bestandene Abnahme ersetzt werden.

## 22. Abschlussbericht von Codex

Codex liefert am Ende: Repository-/Branch-/Commit-Referenz; konkrete Startbefehle; erreichbare lokale bzw. autorisierte Demo-URLs; Workflow-Tabelle mit logischem Key, Ziel-ID und Zustand; Testbericht mit Commands, Ergebnissen und Execution-IDs; Screenshots echter Anwendung und Canvas; durchgeführte Live-Evaluation oder klare Nichtausführung; offene Blocker mit exaktem fehlendem Recht/Secret; Rollback-/Reset-Anleitung.

Aussagen wie “production ready”, “exactly once”, “fully autonomous” oder “saved 80% of time” nur mit entsprechendem tatsächlichem Nachweis. Für dieses Portfolio korrekt: produktionsnahe Entwurfsprinzipien, synthetische Daten, simulierte ERP-Integration und gemessene Demo-Ergebnisse. AI-unterstützte Entwicklung transparent dokumentieren; Eigenleistung über Entscheidungen, Prozessmodell und Verständnis erklären, nicht fremde Autorschaft behaupten.

**Fertig bedeutet:** Die Demo lässt sich starten, die n8n-Workflows führen die Prozesse tatsächlich aus, die UI zeigt ihre echten Resultate, die kritischen Tests sind belegt, und die berechtigte Zielinstanz ist eingerichtet oder deren konkrete unüberwindbare Zugriffsblocker sind sichtbar ausgewiesen.

## 23. Quellen und Prüfgrenzen

Geprüft am 7. September 2026 anhand offizieller Dokumentation und des vom Nutzer ausgewählten Skill-Repositories. Einige n8n-Seiten waren im Browser nur über indexierte Dokumentationsauszüge lesbar; sämtliche versionsabhängigen Details deshalb in M0 nochmals auf der tatsächlichen Zielinstanz prüfen. Quellen belegen die genannten Plattformfunktionen, nicht die frei gewählten Policies, Testdaten oder die behauptete Fertigstellung einer Implementierung.

- **[S01]** n8n, Connect to n8n MCP server: https://docs.n8n.io/connect/connect-to-n8n-mcp-server
- **[S02]** n8n, MCP server tools reference: https://docs.n8n.io/connect/connect-to-n8n-mcp-server/mcp-server-tools-reference
- **[S03]** n8n, Workflow API: https://docs.n8n.io/connect/n8n-api/workflow
- **[S04]** n8n, API authentication: https://docs.n8n.io/connect/n8n-api/authentication
- **[S05]** n8n, Enable queue mode: https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode
- **[S06]** n8n, Execute Sub-workflow: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executeworkflow
- **[S07]** n8n, Wait: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.wait
- **[S08]** n8n, Handle errors gracefully / Error Trigger: https://docs.n8n.io/build/flow-logic/handle-errors-gracefully ; https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.errortrigger
- **[S09]** n8n, Create and run workflows: https://docs.n8n.io/build/understand-workflows/create-and-run-workflows
- **[S10]** OpenAI, Custom instructions with AGENTS.md: https://developers.openai.com/codex/agent-configuration/agents-md
- **[S11]** OpenAI, Model Context Protocol: https://developers.openai.com/codex/mcp
- **[S12]** OpenAI, Structured outputs: https://platform.openai.com/docs/guides/structured-outputs
- **[S13]** mattpocock/skills, `to-spec`: https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md
- **[S14]** mattpocock/skills, `domain-modeling`: https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md

Die Gliederung greift den Ansatz von `to-spec` auf: vorhandene Entscheidungen zu einem ausführbaren Auftrag synthetisieren, Testgrenzen klären und Scope begrenzen. Es wurde kein Issue-Tracker-Eintrag veröffentlicht, kein GitHub-Repository verändert und kein n8n-Workflow in diesem Planungsschritt deployed. [S13]
