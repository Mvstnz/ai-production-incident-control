# AI Production Incident Control — Bauplan für Codex und PM

**Version:** 1.0 · **Stand:** 7. September 2026  
**Status:** Umsetzungsspezifikation, noch keine implementierte Anwendung  
**Projektverzeichnis:** `ai-production-incident-control`  
**Auftraggeber:** Ole · **Zweck:** öffentlich vorzeigbares Bewerbungs- und Referenzprojekt  
**Adressaten:** Codex als Implementierer; der vom Nutzer eingesetzte PM von Netra als Koordinator

## 0. Auftrag, Lesereihenfolge und Entscheidungsbefugnis

Baut ein nachvollziehbares, lokal startbares Operations-System mit n8n als sichtbarer Automatisierungszentrale. Ein Lieferantenhinweis soll über echte n8n-Ausführungen zu einer belegbaren Auswirkungsanalyse, einer menschlich freigegebenen Maßnahme und einem vollständigen Verlauf führen. Anschließend dieselbe Architektur auf Maschinenausfall und Qualitätsmangel erweitern.

Dieses Dokument ersetzt widersprüchliche Details aus der vorangegangenen Ideenfindung. Es setzt keine Kenntnis des Chats voraus. Eine bestimmte Netra-API, Plugin-Installation oder Agentenfunktion wird nicht vorausgesetzt; „PM“ bezeichnet eine Rolle. Die technische Netra-Anbindung ist nicht Bestandteil der Anwendung.

Lesereihenfolge: `AGENTS.md`, dieses Dokument, `BACKLOG.md`, `ACCEPTANCE_TESTS.md`, `CONTEXT.md`, die vier ADRs. Der PM zerlegt die Arbeit entlang der vorgegebenen Meilensteine, verwaltet Abhängigkeiten und prüft Nachweise. Codex implementiert, führt Tests aus und dokumentiert tatsächliche Ergebnisse. Bereits entschiedene Produktfragen werden nicht erneut abgefragt. Kleine technische Lücken durch begründete, dokumentierte Annahmen schließen. Für zusätzliche Kosten, Veröffentlichung, Zugriff auf echte Unternehmensdaten oder reale externe Aktionen ist eine ausdrückliche Freigabe erforderlich.

Alle folgenden Mengen, Unternehmen, Fristen, Schwellen und Termine sind **synthetische Projektvorgaben**, keine realen Betriebsdaten und keine wissenschaftlich validierten Risikogrenzen. Externe Produktinformationen sind über Quellenkennungen im Dokument `SOURCES.md` belegt.

## 1. Produkt und überprüfbarer Nutzen

**Produktbeschreibung:** Ein n8n-basiertes Incident-System liest Produktions- und Lieferkettenmeldungen, verknüpft sie mit einem synthetischen ERP, berechnet Termin- und Materialauswirkungen, bereitet Gegenmaßnahmen vor und führt genehmigte Aktionen nachvollziehbar aus.

Eine Person soll in der Demo Folgendes sehen: ursprüngliche Nachricht → erkannter Geschäftsvorfall → zugrunde liegende ERP-Fakten → transparent berechnetes Risiko → vorgeschlagene und tatsächlich genehmigte Maßnahmen → Ausführung → Verlauf und Nachverfolgung. n8n darf dabei nicht lediglich ein einzelner HTTP-Aufruf vor einer großen Backend-Anwendung sein.

Das Projekt soll Prozessverständnis, API-Integration, Datenmodellierung, Umgang mit unzuverlässigen Eingaben, Freigaben, Fehlerbehandlung und Testbarkeit zeigen. Keine Behauptung, das System sei industriell produktionsreif, erfülle regulatorische Vorgaben oder habe bereits echte Einsparungen erzielt.

**V1 umfasst:** drei Incident-Typen, zehn logisch gegliederte Kernworkflows, synthetisches ERP, kleine Bedienoberfläche, sicherer Offline-Demomodus, optionaler Live-LLM-Modus, Freigaben, Audit-Verlauf, Fehlerwiederholung, Evaluationsdaten und reproduzierbare Projektunterlagen.

**Erster Lieferumfang:** Supplier Delay vollständig durch die gesamte Kette, einschließlich Freigabe, Ausführung im Sandbox-Modus und Fehlerfall. Maschinenausfall und Qualitätsproblem bleiben verpflichtend für V1, werden aber erst nach diesem funktionierenden Schnitt umgesetzt.

**Nicht Bestandteil von V1:** echtes SAP-/CEE-Schreiben, Einkaufsauslösung, echte autonome Lieferantenkommunikation, automatische reale Maschinensteuerung, universelle Produktionsoptimierung, Mehrmandantenbetrieb, Kubernetes, zwingendes Redis, MCP, Multi-Agent-Systeme oder eine Vektordatenbank. Keine vollständige ERP-Nachbildung. RAG und zusätzliche Anbieterintegrationen sind Erweiterungen, nicht Startvoraussetzungen.

## 2. Korrekturen gegenüber der Ideenfindung

| Bisherige Unschärfe | Verbindliche Korrektur |
|---|---|
| 87 bzw. 88 als vorgegebener Demo-Score | Score ausschließlich aus versionierten Regeln berechnen. Die unten definierte neue Fixture ergibt 85; keine Anpassung der Rechenlogik an eine gewünschte Zahl. |
| 38 Bedarf minus 14 Bestand ohne Terminkette | Zeitabhängige Versorgung und Zuordnung berechnen. Eine angebotene Teillieferung ist nicht automatisch zugesagt. |
| Drei Produktionsaufträge automatisch alle verspätet | Drei verwenden das Material; in der Hauptfixture sind nur zwei tatsächlich unterversorgt. |
| „Revenue at risk“ als vermeintlicher Verlust | Kennzahl heißt `At-risk order value`. Sie beschreibt offene, terminlich gefährdete Auftragspositionen, keine Verlustwahrscheinlichkeit und keinen erwarteten Schaden. |
| LLM meldet `confidence: 0.97` | Keine selbstberichtete Konfidenz als Freigabekriterium. Schema, Quellenbelege, ERP-Abgleich und fachliche Regeln entscheiden über automatische Verarbeitung. |
| Geänderter Liefertermin erzeugt neuen Hash und neuen Incident | Quell-Deduplizierung und fachliche Fortschreibung trennen. Eine neue Zusage zur selben offenen PO-Position ist grundsätzlich eine Revision, kein zweiter Fall. |
| Erst Approval, dann neuer KI-Mailentwurf | Der tatsächlich zu sendende Empfänger, Betreff und Text gehören zur genehmigten Planversion. Nachträgliche Änderungen erfordern neue Freigabe. |
| Ein Idempotency-Key verhindert garantiert jede doppelte E-Mail | Keine pauschale Exactly-once-Garantie. Bei unklarem Sendeergebnis `DELIVERY_UNKNOWN`, Abgleich oder menschliche Prüfung statt blindem Neuversand. |
| Ein einziger Incident-Status beschreibt alles | Fachlichen Incident-Lebenszyklus, Analyse, einzelne Aktionen und Freigaben separat abbilden. Abgelehnte Aktion bedeutet nicht erledigter Incident. |
| Jeder kritische Fall wartet mit allem auf Freigabe | Interne Warnung und sichere protokollierende Maßnahmen dürfen sofort laufen. Externe Kommunikation und Änderungen benötigen eine passende Freigabe. |
| Redis bereits im Standard-Compose | Standard zunächst n8n Single-Instance. Queue-Modus mit Redis erst nach einem belegten Bedarf; n8n dokumentiert Redis im Queue-Kontext. [S1] |
| JSON-Datei vorhanden = n8n-Workflow fertig | Reale Import-, Publish-, Webhook- und Laufzeittests auf einer konkret fixierten n8n-Version sind Pflicht. [S2][S3] |

## 3. Architektur und Verantwortlichkeiten

```text
E-Mail-Fixture / optional Gmail     API / Incident-Formular
                \                     /
                 authentifizierter Eingang
                            |
              persistiertes Source Event + Work Item
                            |
                         n8n
      Normalisieren -> Extrahieren -> ERP-Snapshot laden
                            |
           Impact-Berechnung -> Risk Score -> Aktionsplan
                            |
                persistierte Freigabeanforderung
                            |
        Dashboard: ansehen / genehmigen / ändern / ablehnen
                            |
                  neues Ausführungsereignis
                            |
                  n8n Action Execution
                            |
            Sandbox-Mail / Ticket / ERP-Vorschlag
                            |
               SLA, Wiederanlauf und Audit-Verlauf
```

| Bestandteil | Festlegung und Verantwortlichkeit |
|---|---|
| n8n | Routing, Adapteraufrufe, Sub-Workflows, sichtbare Regel- und KI-Schritte, Aktionsausführung, Zeitsteuerung und Fehlerzweige. |
| TypeScript-Kern | Reine, separat testbare Funktionen für zeitabhängige Impact- und Risk-Berechnung. Als selbstständiges JavaScript in die zugehörigen n8n-Code-Nodes bündeln. Kein zweiter, abweichender Rechenkern in Python. |
| FastAPI | Mock-ERP-REST-Schnittstelle, Operations-API, Authentifizierung, Vertragsprüfung, atomare Zustandswechsel, Versionskontrolle und Datenhaltung. Nicht die vollständige Orchestrierung verstecken. |
| PostgreSQL | Eine Instanz im Demo-Stack; getrennte n8n-Datenbank sowie Geschäftsdatenbank mit `erp`- und `ops`-Schemas und getrennten Zugriffsrollen. |
| React + TypeScript + Vite | Kleine Dashboard-Anwendung. Komponentenbibliothek und Layout schlicht halten; keine zusätzliche Frontend-Plattform. |
| n8n task runner | Externer Runner für Code-Nodes; Container-Version muss zur n8n-Version passen. [S4] |
| Mailpit | Lokales Auffangpostfach für ausgehende Demo-E-Mails. Keinen öffentlichen SMTP-Relay konfigurieren. Einsatz vor Umsetzung anhand der offiziellen Dokumentation prüfen. |
| KI-Adapter | `mock` als Standard; ein konfigurierbarer, tatsächlich getesteter Live-Anbieter. Provider und Modell-ID explizit protokollieren. Keine Modellnamen erfinden. |

Standard-Compose: `postgres`, `api`, `n8n`, `n8n-runners`, `dashboard`, `mailpit`. Ein kurzlebiger Bootstrap-/Migrationsdienst ist zulässig. Datenbank und Runner nicht öffentlich veröffentlichen; lokale UI-/Editor-Ports an Loopback binden.

Der TypeScript-Kern erhält vollständig serialisierbare Snapshots. Er macht weder Netzaufrufe noch Datenbankänderungen und verwendet keine implizite Systemuhr. Das Workflow-Buildskript bindet den getesteten Code ein; Hash und Versionskennung des Bundles werden mit exportiert. So sind Unit-Test und n8n-Ausführung dieselbe Implementierung.

**Versionierungsregel:** In M0 eine stabile verfügbare Version wählen, Container und Abhängigkeiten exakt fixieren, Kompatibilität prüfen und in `versions.lock` dokumentieren. Keine produktiven `latest`-Tags. Das ist eine Umsetzungsaufgabe, keine behauptete bereits getestete Versionskombination.

## 4. Betriebsmodi und reproduzierbarer Start

### 4.1 Demo, standardmäßig aktiv

Ohne API-Key, Gmail-Konto, Slack, Jira oder Microsoft-Tenant startbar. Alle Daten synthetisch. Der KI-Mock liefert reproduzierbare Antworten für dokumentierte Fixtures; unbekannte freie Texte dürfen nicht als erfolgreich verstandene Fälle vorgetäuscht werden. Sie gehen in die manuelle Prüfung oder verlangen explizit den Live-Modus.

E-Mail-Eingänge kommen als `.eml`-Fixture über einen geschützten Demo-Eingang in denselben normalisierten Email-Pfad. Mailpit zeigt ausgehende Sandbox-Nachrichten; es ist nicht der Gmail-Eingang. Tickets und Benachrichtigungen besitzen echte persistierte Sandbox-Datensätze mit Referenznummern.

Die Demo verwendet eine explizite fachliche Uhr: `2026-10-12T08:00:00+07:00`, Plant-Zeitzone `Asia/Bangkok`. Die Uhr ist im Dashboard sichtbar und durch einen geschützten Demo-Befehl vorstellbar. Technische Ausführungszeit bleibt zusätzlich als tatsächlicher UTC-Zeitstempel erhalten. Keinen wechselnden Tagesbezug für Golden Tests verwenden.

### 4.2 Live-KI, optional

Gleiche Workflows, Regeln und Daten, aber echter LLM-Aufruf. API-Key nur serverseitig über lokale Secrets. Live-Aufrufe erfordern ausdrückliches Einschalten, ein Token-/Kostenlimit und eine konfigurierte Modell-ID. Ein fehlender Key darf den Demo-Start nicht blockieren. Ein Modellfehler darf nicht unbemerkt in Mock-Ausgaben umgewandelt werden.

### 4.3 Live-Connectoren, getrennt von Live-KI

Gmail als optionaler Eingang, höchstens ein zusätzlicher Benachrichtigungskanal als Adapter. Live-KI aktiviert **keinen** externen Versand. Reale Empfänger und ERP-Änderungen bleiben standardmäßig gesperrt. Benutzerdefinierte Credentials nicht über private, undokumentierte n8n-Endpunkte oder direkten Eingriff in n8n-Tabellen anlegen.

### 4.4 Startvertrag

Der spätere Repository-Stand muss einen dokumentierten Bootstrap für PowerShell und eine POSIX-Shell anbieten. Er erzeugt lokale Secrets, führt Migrationen aus, seedet Daten idempotent, importiert/verknüpft Workflows und prüft deren veröffentlichte Trigger. `docker compose up` alleine darf nicht als vollautomatischer Erststart beworben werden, solange dieser Ablauf nicht nachgewiesen wurde. Falls die gewählte n8n-Version eine initiale Owner-Einrichtung benötigt, genau diesen kleinen manuellen Schritt ehrlich dokumentieren.

Reset ist nur in explizit als Demo erkannten Datenbanken erlaubt. Ein Reset-Skript muss vor fremden/produktiven Zielen abbrechen. Neustart darf keine bestehenden Vorfälle, Freigaben oder Schlüssel verlieren.

## 5. Datenmodell und Integritätsregeln

### 5.1 Mock ERP

| Gruppe | Tabellen und Mindestinhalte |
|---|---|
| Stammdaten | `suppliers`, `customers`, `materials`, `machines`; synthetische IDs, Anzeigenamen, Kundenpriorität und explizite Fähigkeiten. |
| Beschaffung | `purchase_orders`, `purchase_order_items`, `supply_commitments`; PO-Positions-ID, offene Gesamtmenge, Lieferort, bestätigte und nur vorgeschlagene Termine. |
| Lager | `inventory_lots`, `inventory_reservations`; Standort, Material, Charge, physischer Bestand, Sperrbestand, Reservierung und nutzbare Menge. Reservierungen nicht zweimal abziehen. |
| Produktion | `production_orders`, `production_requirements`, `production_operations`; Material-/Chargenbedarf, Bedarfstermin, Maschine, Dauer und Reihenfolge. |
| Vertrieb | `sales_orders`, `sales_order_items`, `production_sales_allocations`; offene Mengen, Netto-Einzelpreis, Währung, Liefertermin, Teillieferungserlaubnis. |
| Qualitätsnachweis | `quality_inspections`, `lot_allocations`, `shipments`, `shipment_items`; Inspektionsstatus und nachvollziehbare Chargenverwendung. |

Für V1 genügen begrenzte Szenarien mit einer kritischen Materialkomponente und expliziten Produktions-/Vertriebszuordnungen. Trotzdem müssen die Tabellen Beziehungen statt bloßer Namensstrings enthalten. Keine vollständige mehrstufige MRP oder Optimierung vortäuschen.

### 5.2 Operations

`source_events`, `incidents`, `incident_revisions`, `incident_source_links`, `analysis_snapshots`, `incident_impacts`, `risk_assessments`, `action_plans`, `incident_actions`, `approvals`, `audit_events`, `work_items`, `workflow_errors`, `ai_runs`, `users`, `sessions`.

`work_items` ist die transaktionale Outbox und persistente Arbeitswarteschlange. Ein Zustand und sein nächster Arbeitsauftrag werden in derselben Datenbanktransaktion geschrieben. Bearbeiter reservieren fällige Einträge über zeitlich begrenzte Leases und einen Claim-Token. Der Queue-Zustand ist nicht die n8n-Ausführung selbst.

Zwingende Eindeutigkeiten: `(source_system, source_id)`; eine laufende Incident-Zuordnung je fachlichem aktiven Korrelationsschlüssel; `(incident_id, revision)`; eindeutiger Action-Idempotency-Key; eindeutiger Ereignis-/Nachrichtenschlüssel je Verarbeitung; eindeutiger SLA-Eskalationsschlüssel.

Alle fachlichen Snapshots speichern `incident_revision`, `erp_snapshot_id`, `analysis_as_of`, `schema_version`, `risk_policy_version`, Code-Bundle-Hash und fachliche Quellen. Geld als Integer-Minor-Units mit Währung, Mengen mit Einheit, Zeitstempel mit Zeitzone speichern. Demo ausschließlich EUR; keine stillen Summen über verschiedene Währungen.

### 5.3 Zustände

| Objekt | Zustände |
|---|---|
| Incident-Lebenszyklus | `OPEN`, `MITIGATING`, `MONITORING`, `RESOLVED`, `CLOSED` |
| Analyse | `RECEIVED`, `NORMALIZING`, `REVIEW_REQUIRED`, `ANALYZING`, `ASSESSED`, `ERROR` |
| Freigabe | `PENDING`, `APPROVED`, `REJECTED`, `EXPIRED`, `SUPERSEDED` |
| Aktion | `DRAFT`, `AWAITING_APPROVAL`, `READY`, `RUNNING`, `SUCCEEDED`, `RETRY_SCHEDULED`, `DELIVERY_UNKNOWN`, `FAILED`, `CANCELLED` |
| Work Item | `PENDING`, `LEASED`, `DONE`, `RETRY_SCHEDULED`, `DEAD_LETTER` |

Das API prüft jede Zustandsänderung mit erwarteter Revision. Eine abgelehnte Freigabe lässt den Incident offen. Eine versendete Eskalation führt höchstens zu `MONITORING`, niemals allein zu `RESOLVED`. Eine fachliche Bestätigung oder dokumentierte Managerentscheidung mit Beleg ist zur Lösung nötig. Ein geschlossener Fall wird nicht still überschrieben; Wiedereröffnung ist ein explizites auditiertes Ereignis.

## 6. Eingang, Extraktion und fachliche Fortschreibung

Der kanonische Eingang enthält mindestens `schema_version`, `event_id`, `source_system`, `source_id`, `received_at`, `correlation_id`, `sender`, `subject`, `body_text` und Referenzen auf Originaldaten. Webhook-Eingänge haben Größenlimits und Authentifizierung. Öffentliche Anfragen bekommen erst nach erfolgreicher dauerhafter Annahme eine `202`-Antwort mit Event-ID und Statusadresse. Gleicher Schlüssel und anderer Inhalt ergibt Konflikt statt stiller Überschreibung.

Die KI extrahiert einen diskriminierten Incident-Typ mit typabhängigen Feldern, Unsicherheiten und Quellenbelegen. Ein Lieferfall benötigt eine eindeutig zugeordnete PO-Position, Material/Standort, Menge/Einheit und interpretierbare Terminaussage. Fehlende Angaben dürfen `null` sein. Eine fehlende Jahreszahl wird nicht blind ergänzt; eindeutige Auflösung anhand der PO und des Empfangszeitpunkts muss als Ableitung markiert werden, sonst Prüfung.

Die Quell-E-Mail wird als nicht vertrauenswürdiger Inhalt behandelt, nicht als Systemanweisung. Enthaltene URLs nicht automatisch besuchen, keine Anhänge ausführen, keine vom LLM erfundenen Empfänger oder Tools verwenden. Die tatsächlichen Geschäftspartner und Empfänger kommen aus freigegebenen Stammdaten.

**Technische Deduplizierung:** atomarer Insert anhand Source-System und Source-ID vor teurer Extraktion. Wiederholung liefert denselben Verarbeitungsbezug. Kein bloßes „SELECT, danach INSERT“ ohne Datenbankconstraint.

**Fachliche Korrelation:** Für Lieferfälle vorzugsweise Incident-Typ + Lieferant + PO-Positions-ID + Standort auf einen offenen Fall abbilden. Der neue Liefertermin ist **kein** Teil dieser Identität. Identische Fakten über einen anderen Kanal werden verlinkt. Veränderte bestätigte Fakten erzeugen eine neue Revision. Mehrere plausible Zuordnungen gehen in die Prüfung.

Eine Revision macht eine ältere Analyse und noch offene Freigaben ungültig. Nicht gestartete alte Aktionen abbrechen oder neu planen. Bereits ausgeführte Aktionen bleiben historisch erhalten. Für bereits laufende externe Vorgänge ist ein Stop nicht garantiert; Ergebnis zuerst abgleichen und nur explizite Folgemaßnahmen erzeugen.

## 7. Zeitabhängige Impact Engine

### 7.1 Lieferfall

Aus einem konsistenten ERP-Snapshot zwei Projektionen bilden: bestätigter Ausgangsplan und Plan mit dem aktuellen Incident. Für V1 den einzelnen Incident gegen denselben Snapshot rechnen. Bei mehreren Incidents zeigt das Dashboard eine deduplizierte Gesamtexposition, **keine** kausale Gesamtsimulation aller Wechselwirkungen.

Je Material und Standort: nutzbaren Bestand bestimmen; feste Reservierungen respektieren; bestätigte Zuflüsse und Bedarfe chronologisch verarbeiten; bei gleicher Zeit zuerst nutzbaren Wareneingang, danach feste Reservierungen, danach übrige Bedarfe nach Bedarfstermin, Kundenpriorität und stabiler Positions-ID. Nicht belegte zukünftige Zuflüsse nicht zählen. Bereits verplanten Bestand nicht erneut vergeben.

Zu jedem Bedarf ausgeben: benötigt, rechtzeitig gedeckt, ungedeckt, erster Fehltermin, frühester Termin vollständiger Versorgung und Begründung. Wiederkehrende kumulierte Fehlbestände nicht mehrfach aufsummieren. Die `shortage_qty` der Fixture ist die Summe der noch nicht rechtzeitig gedeckten Bedarfsmengen, keine Summe negativer Lagerkurven.

Produktionsabschluss für die eingeschränkte Demo = vollständige Materialverfügbarkeit + hinterlegte Bearbeitungsdauer. Der Demo-Kalender ist ausdrücklich ein durchlaufender 7-Tage-Kalender. Keine versteckten Feiertags-, Schicht-, Rüst- oder Kapazitätsannahmen; eine erweiterte Kalender-/Kapazitätsplanung ist nicht implementiert, solange es keine Tests dafür gibt.

### 7.2 Auftragswert

Nur offene Vertriebspositionen zählen, deren prognostizierter Termin den zugesagten Termin überschreitet. Bei verbotener Teillieferung kann eine teilweise Materialunterversorgung die gesamte offene Position gefährden. Bei erlaubter Teillieferung nur den nach dem beschriebenen Modell tatsächlich verspäteten offenen Teil bewerten. Die Fixture verbietet Teillieferungen auf den beiden gefährdeten Vertriebspositionen.

Dashboard-Gesamtwert = Vereinigungsmenge der betroffenen offenen Positionen mit ihrer jeweils berechneten gefährdeten Menge, begrenzt auf die offene Positionsmenge. Bei mehreren Incidents dieselbe Position nicht mehrfach aufaddieren; für V1 maximale gefährdete Menge je Position verwenden und diese nicht-additive Aggregation kennzeichnen. Netto-Auftragswert ist weder Gewinn noch Schaden noch prognostizierter Umsatzverlust.

### 7.3 Maschinenausfall

Explizite Operationen mit Maschinenkalender und geplanter Dauer auswerten. Alternative Maschine nur vorschlagen, wenn Material-/Prozessfähigkeit und ein ausreichend großer freier Slot vorhanden sind. V1 wählt unter vorgegebenen kompatiblen Slots deterministisch den frühesten; kein allgemeiner Scheduling-Optimierer.

Eine lediglich vorgeschlagene Umplanung reduziert das aktuelle Risiko nicht. Nach genehmigter und im Mock-ERP bestätigter Planänderung neu rechnen. Ursprüngliche Exposition und verbleibende Exposition separat zeigen.

### 7.4 Qualitätsproblem

Bestätigten Prüfstatus an einer existierenden Charge prüfen, nutzbaren Bestand korrigieren und über Chargenzuordnung die betroffenen Produktions- und Lieferpositionen bestimmen. Bei einem authentifizierten, bestätigten Fehler darf die Regelengine **im Mock-ERP** eine sichere Auslieferungssperre setzen und sofort intern warnen. Ein bloß unklarer KI-Text genügt dafür nicht.

Freigabe einer gesperrten Charge nur durch Quality Manager und mit Begründung. Bereits versandte Mengen als Ausnahme/Eskalation behandeln; eine existierende Auslieferung lässt sich nicht rückwirkend blockieren. Kein automatisches reales Recall- oder Compliance-Verfahren behaupten.

## 8. Golden Scenario A — Supplier Delay

Alle Uhrzeiten Plant-Zeit `Asia/Bangkok`. Fachlicher Start: 12. Oktober 2026, 08:00 Uhr.

**E-Mail:** Asia Precision Components meldet für PO `4500192`, Position `10`, Material `SHAFT-DN300`, eine offene Gesamtmenge von 40 Stück. Bisher zugesagt: 12. Oktober 2026, 08:00 Uhr. Neue bestätigte Gesamtlieferung: 19. Oktober 2026, 08:00 Uhr. Zusätzlich heißt es ausdrücklich: „We may be able to ship 10 pcs on 13 October 2026.“ Diese 10 Stück sind zunächst nur ein Vorschlag und wären Teil der 40, niemals zusätzlich 10.

**Bestand:** 18 physisch, 4 qualitätsgesperrt, 0 weitere Reservierungen = 14 nutzbar. Keine weiteren rechtzeitigen Zugänge und keine rechtzeitig verfügbare freigegebene Alternative.

| Produktionsauftrag | Bedarf | Bedarfstermin | Zugeordnete offene Vertriebsposition | Zugesagter Liefertermin |
|---|---:|---|---|---|
| PRD-1001 | 10 Stück | 12.10.2026, 09:00 | SO-1001/10; nicht gefährdet | 15.10.2026 |
| PRD-1002 | 12 Stück | 14.10.2026, 08:00 | SO-1002/10; 12 × 4.000 EUR = 48.000 EUR | 17.10.2026 |
| PRD-1003 | 16 Stück | 16.10.2026, 08:00 | SO-1003/10; 16 × 4.900 EUR = 78.400 EUR | 19.10.2026 |

Eine kritische Komponente pro Einheit; Produktionsdauer jeweils 48 Stunden nach vollständiger Materialversorgung. SO-1002 und SO-1003 gehören verschiedenen Kunden; der zweite ist strategisch. Ihre offenen Positionen erlauben keine Teillieferung.

**Erwartung ohne bestätigte Teillieferung:** Bedarf 38; davon 14 rechtzeitig gedeckt. PRD-1001 ist voll versorgt; PRD-1002 fehlen 8, PRD-1003 fehlen 16. Insgesamt 24 Stück ungedeckt, zwei unterversorgte Produktionsaufträge, zwei verspätete Vertriebspositionen, zwei gefährdete Kunden, `12_640_000` EUR-Cent Auftragswert. Materialbezug besteht zu drei Produktionsaufträgen; das ist nicht dieselbe Kennzahl wie zwei unterversorgte Aufträge. Beide verspäteten Aufträge werden nach Materialverfügbarkeit am 19.10. frühestens am 21.10. fertig.

**Fortschreibung:** Der Lieferant bestätigt später verbindlich 10 Stück für 13.10., 08:00, und die übrigen 30 für 19.10., 08:00. Derselbe Incident erhält eine neue Revision. PRD-1002 kann rechtzeitig versorgt werden; PRD-1003 fehlen noch 14. Nur SO-1003/10 bleibt gefährdet: `7_840_000` EUR-Cent. Gesamtbestellmenge bleibt 40, Score wird 70 statt 85. Vorherige Freigaben sind veraltet.

Die maschinenlesbare Datei `fixtures/supplier-delay-golden.json` definiert diese Rechenprobe. Das ist ein erwartetes Testergebnis, noch kein Nachweis einer laufenden n8n-Implementierung.

## 9. Deterministische Risk Engine

`risk_policy_version = portfolio-v1`. Der Score ist ein transparenter Priorisierungsindex, keine Wahrscheinlichkeit. Folgende Projektschwellen werden in einer versionierten Konfigurationsdatei abgelegt.

| Faktor | Regel | Maximum |
|---|---|---:|
| Zusätzliche Verzögerung | 0 Tage → 0; >0 bis 2 → 5; >2 bis 4 → 10; >4 bis 7 → 20; >7 → 25 | 25 |
| Gefährdeter Netto-Auftragswert | 0 → 0; >0 bis <10.000 EUR → 5; 10.000 bis <50.000 → 10; 50.000 bis <100.000 → 15; ab 100.000 → 20 | 20 |
| Zeit bis erstem ungedeckten/gestörten Bedarf | kein Effekt → 0; >7 Tage → 0; >3 bis 7 → 5; >1 bis 3 → 10; bis 1 Tag oder bereits eingetreten → 20 | 20 |
| Anteil ungedeckten/gestörten Bedarfs | 0 → 0; >0 bis 25 % → 5; >25 bis 50 % → 10; >50 % → 15 | 15 |
| Rechtzeitig wirksame bestätigte Alternative | vorhanden → 0; nicht vorhanden → 10 | 10 |
| Strategischer betroffener Kunde | nein → 0; ja → 10 | 10 |

LOW 0–24, MEDIUM 25–49, HIGH 50–74, CRITICAL 75–100. Bei Lieferfällen sind der Disruptionsanteil ungedeckte Stück / relevanter Stückbedarf und die Verzögerung die Verschiebung der bestätigten Lieferung. Für Maschinen: blockierte geplante Operationsstunden / relevante geplante Stunden; für Qualität: nicht nutzbare zugeordnete Menge / relevanter Mengenbedarf. Nenner, Einheit und Betrachtungshorizont müssen je Typ im Resultat stehen. Unbekannte relevante Eingaben sind nicht automatisch null oder „keine Alternative“: Analyse bleibt unvollständig und erfordert Prüfung.

Wenn keine Material-/Operationsstörung und keine verspätete offene Position vorliegt, lautet das Ergebnis `LOW`, Score 0, Begründung `NO_PROJECTED_IMPACT`. Eine isolierte Lieferterminänderung ohne Folgen wird nicht allein wegen fehlender Alternative hochgestuft.

Golden A: 20 Verzögerung + 20 Wert + 10 Dringlichkeit + 15 Unterversorgung + 10 keine Alternative + 10 strategischer Kunde = **85 / CRITICAL**. Nach bestätigter Teillieferung: 20 + 15 + 5 + 10 + 10 + 10 = **70 / HIGH**.

Explizite Sicherheitsregeln dürfen die **Severity** übersteuern, nicht den errechneten Score fälschen. V1-Regel: bestätigter Qualitätsfehler mit Charge in einer noch offenen, zur Auslieferung zugeordneten Position → mindestens CRITICAL; `override_reason = QUALITY_SHIPMENT_EXPOSURE`. Rohscore und Override sichtbar zeigen.

## 10. KI, Pläne und tatsächliche Freigabe

Zwei KI-Stufen genügen: strukturierte Extraktion sowie Erklärung/Kommunikationsentwurf aus bereits berechneten Fakten. Eine dritte oder vierte Stufe ist nur zulässig, wenn sie einen belegbaren Zweck hat. Keine frei handelnden Agenten und keine autonome Wahl von APIs.

Schema, fachlicher Abgleich und erforderliche Felder entscheiden über `VALIDATED`, `REQUIRES_REVIEW` oder `FAILED`. Die KI erhält keine Credentials. Alle vorgeschlagenen Maßnahmen müssen einem erlaubten Action-Typ mit serverseitig bekannten Zielen entsprechen.

Die Erklärung nennt faktische Quellen und trennt bestätigte Tatsachen, vorgeschlagene Gegenmaßnahmen und Unsicherheiten. Zahlen im Dashboard kommen direkt aus strukturierten Ergebnissen, nicht aus frei generiertem Fließtext. Im Fehlerfall kann ein deterministisches Texttemplate erklären, dass die KI-Zusammenfassung fehlt. Dadurch werden weder Daten noch Modellqualität vorgetäuscht.

| Action-Typ | Freigaberegel |
|---|---|
| Incident protokollieren, interne Warnung, internes Sandbox-Ticket | Automatisch, sofern Empfänger/Projekt auf serverseitiger Allowlist stehen. |
| E-Mail an Lieferanten oder Kunden | Immer vorherige Freigabe der konkreten Empfänger, Betreffzeile und Nachricht; standardmäßig nur Sandbox-Versand. |
| Produktionsumplanung | Manager-Freigabe der konkreten Änderung; V1 verändert nur Mock-ERP oder erzeugt einen eindeutig markierten Vorschlag. |
| Alternative Beschaffung anfragen | Konkreten Kommunikationsentwurf freigeben; keine Bestellung oder finanzielle Zusage auslösen. |
| Bestätigte schadhafte Charge im Mock-ERP sperren | Konservative Regelaktion mit sofortiger Warnung; Entsperren nur Quality Manager. |

Freigabe enthält `approval_id`, `incident_revision`, `plan_revision`, `action_payload_hash`, berechtigte Rolle, Ablaufzeit und Entscheider. API prüft die aktuelle Version atomar. Veränderung von Text, Empfänger, Umfang oder zugrunde liegender Analyse macht die Freigabe ungültig. Nur aktuell passende `APPROVED`-Aktionen dürfen ausgeführt werden. „Modify“ erstellt einen neuen Entwurf; es ist kein stillschweigendes Approve.

Dashboard-Entscheidungen über authentifizierte POST-Anfragen mit CSRF-Schutz. GET-Links ändern keinen Zustand. Benachrichtigungslinks öffnen die geschützte Detailseite; keine nackten n8n-Resume-URLs als öffentliche Genehmigungsbuttons. n8n besitzt Wait-/Resume-Funktionen [S5], aber die verbindliche fachliche Freigabe lebt in PostgreSQL und nicht ausschließlich in einer wartenden Ausführung.

## 11. Die zehn Kernworkflows

| ID | Zweck und Mindestverhalten |
|---|---|
| WF01 Email Intake | Demo-EML bzw. optional Gmail in Source Event überführen; Quellnachweis, technische Deduplizierung und persistierte Annahme. Keine unverifizierten Sender als autorisierte Entscheider behandeln. |
| WF02 API / Form Intake | Authentifizierter Webhook und Formularadapter; kanonischer Eventvertrag; persistierte Annahme und eindeutige Rückgabe. |
| WF03 Normalize / Extract / Correlate | Extraktion, Vertragsprüfung, ERP-Zuordnung, Incident neu anlegen oder fortschreiben; Konflikte in Review; WF04 und WF05 für aktuelle Revision ausführen. |
| WF04 ERP Impact Analysis | Konsistenten Snapshot über ERP-API abrufen, typabhängige Projektion im gebündelten Code ausführen, Ergebnis mit Quellen speichern. |
| WF05 Risk / Explanation / Plan | Versionierten Score berechnen, Override anwenden, Erklärung und konkrete Action-Entwürfe vorbereiten; automatisierbare Aktionen und Freigabeanforderungen getrennt einstellen. |
| WF06 Human Approval | Freigabeanforderung zustellen, danach Lauf beenden. Ein späteres persistiertes Entscheidungsereignis revalidiert Revision und Rolle und stellt erlaubte Aktionen zur Ausführung bereit. Kein synchron blockierter Parent-Workflow. |
| WF07 Action Execution | Aktion leasen, Berechtigung/Planversion erneut prüfen, erlaubten Adapter aufrufen, Ergebnis/unklare Zustellung persistieren und Nachverfolgung einplanen. |
| WF08 SLA / Dispatch / Recovery | Zeitgesteuert fällige Work Items atomar claimen und nach Typ dispatchen; offene Fristen, abgelaufene Leases und veraltete Analysen prüfen. Nicht jeden historischen Incident vollständig neu rechnen. |
| WF09 Error Handler / Dead Letter | Automatische n8n-Ausführungsfehler normalisieren; Retry nur nach Policy; dauerhaft fehlerhafte Arbeitsaufträge quarantänisieren; manuell autorisierten Replay unterstützen. |
| WF10 Management Digest | Fälligen Tagesbericht aus deduplizierten Kennzahlen und aktuellen Incidents erzeugen, in der Sandbox zustellen und pro Berichtsdatum/Zeitzone nur einmal buchen. |

Für sofortige Berechnungen Sub-Workflow-Aufrufe verwenden; für Freigaben und andere langlebige Arbeit persistierte Ereignisse. Übergaben referenzieren IDs, Revisionen und Snapshot-IDs statt beliebig großer kopierter Payloads. Alle Workflows sind sinnvoll benannt und mit kurzen Sticky Notes versehen.

### 11.1 Empfang ist nicht erneute Bearbeitung

Die dauerhafte Annahme eines Source Events und seine spätere Bearbeitung sind verschiedene Operationen. Ein vom Dispatcher referenziertes bereits gespeichertes Event ist kein neu eingegangenes Duplikat und darf deshalb nicht einfach verworfen werden. Jeder Aufruf kennzeichnet, ob er einen neuen Eingang registriert oder einen geclaimten Auftrag zu einer vorhandenen Event-ID bearbeitet. Quell-Eindeutigkeit verhindert doppelte Annahme; Work-Item-Identität und Claim-Token steuern Wiederholung der Bearbeitung.

Zielrouting: `source.email.received` → WF01, `source.structured.received` → WF02, `analysis.requested` → WF03, `approval.requested` und `approval.decided` → die getrennten Zweige von WF06, `action.ready` → WF07, `digest.due` → WF10. WF01/WF02 normalisieren akzeptierte Events und stellen genau einmal `analysis.requested` ein. Ein nativer Gmail-Trigger nutzt denselben Annahmevertrag und beendet den Eingang nach dauerhaftem Speichern; er darf nicht zusätzlich eine zweite Analyse starten. WF03 ruft WF04/WF05 für sofortige Resultate auf. Statusabschluss und nächster Arbeitsauftrag werden gemeinsam über die Operations-API verbucht. Bei einem schon abgeschlossenen Work Item denselben gespeicherten Ergebnisbezug zurückgeben.

Diese Zustellverträge als Integrationstest festhalten: ein nativer Eingang, ein direkter API-Eingang, Dispatcher-Wiederholung und Retry dürfen weder eine Endlosschleife noch eine verlorene Bearbeitung erzeugen.

Die Zahl zehn ist keine Qualitätsmetrik. Wird WF08 durch technische Dispatch-Aufgaben unübersichtlich, darf ein zusätzlicher klar benannter Infrastrukturworkflow abgetrennt werden; im ADR begründen. Keine künstliche Node-Zahl anstreben.

Der n8n Error Trigger reagiert auf fehlgeschlagene automatische Ausführungen, nicht auf manuelle Editorläufe. Deshalb über veröffentlichte Trigger testen und WF09 zusätzlich mit einem Test-Harness speisen. [S6] Bei vollständigem Ausfall von n8n und/oder Datenbank kann derselbe Stack nicht seine sofortige Alarmierung garantieren; Container-Logs und Healthchecks bleiben der lokale Nachweis, nach Wiederanlauf greift Lease-Recovery.

## 12. API-Verträge und atomare Operationen

Alle öffentlichen Verträge in OpenAPI und JSON Schema versionieren. Die folgenden Routen sind Zielverträge für die Implementierung, nicht bereits vorhandene Endpunkte.

| Route | Zweck |
|---|---|
| `POST /v1/intake/events` | Eingang mit Idempotency-Key speichern; 202 und Event-ID oder bestehender Bezug. |
| `GET /v1/events/{id}` | Annahme-/Verarbeitungsstand abfragen. |
| `GET /v1/erp/snapshots/{id}` | Unveränderlichen Analyse-Snapshot lesen; Erstellung über erlaubten internen Auftrag. |
| `GET /v1/incidents` und `GET /v1/incidents/{id}` | Gefilterte Übersicht und revisionsbezogene Detaildaten. |
| `POST /v1/incidents/{id}/review` | Autorisierte Korrektur als neue Revision; Originaldaten behalten. |
| `POST /v1/approvals/{id}/decision` | Entscheidung mit erwarteter Plan-/Incident-Revision; abgelaufen/veraltet → 409. |
| `POST /v1/incidents/{id}/resolve` | Fachliche Lösung mit Nachweis; keine bloße Button-Abkürzung um Pflichtmaßnahmen herum. |
| `GET /v1/metrics` | Deduplizierte Kennzahlen mit Währung, Zeitbezug und Modellannahmen. |
| `POST /internal/work-items/claim` | Fällige Arbeit atomar reservieren, Lease und Claim-Token zurückgeben. |
| `POST /internal/work-items/{id}/complete` | Nur durch aktuellen Claim-Besitzer abschließen; Folgezustand und nächste Arbeit atomar. |
| `POST /internal/work-items/{id}/fail` | Bekannter Fehler, Retry oder Dead Letter nach Fehlerklasse. |
| `POST /v1/admin/work-items/{id}/replay` | Autorisierter Replay mit Begründung, gleichbleibender fachlicher Identität. |
| `POST /v1/demo/scenarios/{key}/run` | Lokale Demo-Fixture als echte Eingabe einstellen. |
| `POST /v1/demo/clock/advance` | Nur im Demo-Modus fachliche Uhr vorstellen; auditieren. |

Interne API-Routen benötigen einen separaten Service-Token und sind nicht direkt über die öffentliche Dashboard-Proxyroute erreichbar. n8n darf nicht direkt Geschäfts-/n8n-Systemtabellen verändern. Ein zentrales n8n-Datenbankpasswort berechtigt nicht automatisch zur Geschäfts-API.

Work Items tragen `kind`, `aggregate_id`, `revision`, `available_at`, `attempt_count`, `lease_owner`, `lease_expires_at`, `claim_token`, `correlation_id` und eine kompakte versionierte Payload. Der Dispatcher verarbeitet begrenzte Batches. Ablaufen einer Lease führt nicht automatisch zu sicherem Neuversand einer möglicherweise bereits versendeten Nachricht; unklare externe Aktionen zuerst abgleichen.

## 13. Fehler, Wiederholung und Fristen

**Erwartete Fachfehler:** fehlende Zuordnung, unklare Jahreszahl, widersprüchliche Mengen → Review, kein endloser technischer Retry. **Vorübergehende Fehler:** 429, klar nicht ausgeführte Anfrage, lesender 5xx → begrenzter Retry mit Backoff. **Permanente Fehler:** ungültige Credentials/Verträge → Dead Letter und Adminhinweis. **Unklare externe Wirkung:** Timeout nach möglicher Annahme → `DELIVERY_UNKNOWN`.

Standard: höchstens fünf Gesamtversuche für sicher wiederholbare Arbeit; Backoff-Basis nach Fehlschlag 5, 30, 120, 600 Sekunden mit Jitter, gültiges `Retry-After` respektieren. Diese Werte sind Projektkonfiguration, keine Herstellerempfehlung. Restart bewahrt Versuchszähler. Replay erzeugt keine neue fachliche Action-ID.

Eine Datenbank-Outbox sichert die gemeinsame Speicherung von Zustand und Arbeitsauftrag, nicht die atomare Transaktion mit einem fremden Mailanbieter. Adapter verwenden dessen Idempotenzmechanismus nur, sofern tatsächlich dokumentiert und getestet. Ohne solchen Mechanismus bei unklarem Ergebnis zunächst Provider-Abgleich oder menschliche Entscheidung. Diese Einschränkung muss im README stehen.

Default-SLA für erste interne Reaktion: CRITICAL 15 Minuten, HIGH 60 Minuten, MEDIUM 4 Stunden, LOW 24 Stunden; ab fachlichem Eingang, als verstrichene Zeit, nicht als Arbeitszeit. Managerentscheidung oder explizite qualifizierte Bestätigung kann Reaktion dokumentieren. Eine automatische Benachrichtigung allein zählt nicht als menschliche Reaktion.

SLA-Eskalation einmal pro `(incident, revision, policy, deadline, level)`. Duplikate dürfen Fristen nicht verlängern. Bei verschärfter Lage gilt die frühere von bestehender Frist und neuer verschärfter Frist. Bereits eskalierte Frist darf durch Revision nicht unbeabsichtigt erneut spammen. Freigabeablauf und SLA sind unterschiedliche Fristen; abgelaufene Freigabe autorisiert keine Aktion.

## 14. Dashboard und minimale Bedienung

Fünf Ansichten genügen: Übersicht, Incident-Detail, Freigaben, Systemzustand/Fehler, Demo-Labor. UI und öffentliche Repository-Dokumentation auf Englisch. Dieses Übergabedokument kann deutsch bleiben.

Übersicht: offene Incidents, CRITICAL, offene Freigaben, eindeutig definierter gefährdeter Auftragswert; Filter nach Typ, Status und Schweregrad. Detail: Originalmeldung, geprüfte Extraktion, Bestand-/Terminprojektion, direkt belegte betroffene Positionen, Score je Faktor, Unsicherheiten, genehmigter Aktionsinhalt, Timeline und Quellen-/Versionsangaben.

Freigabeseite zeigt Rollenberechtigung, Ablauf und veralteten Zustand. „Approve“, „Modify“, „Reject“ nur für Berechtigte, mit Bestätigungsansicht des tatsächlichen Inhalts. Die Oberfläche muss auf Fehler, leere Daten und Ladezustände reagieren und per Tastatur bedienbar sein. Status nicht ausschließlich durch Farbe kennzeichnen.

Demo-Labor: Scenario A, verbindliche Teillieferungs-Revision, Scenario B, Scenario C, Duplikat, API-Ausfall, unklare E-Mail-Zustellung, veraltete Freigabe. Technische Failure-Injection nur hinter lokalem Demo-/Adminschutz. Deutlicher Banner `Synthetic data · Mock AI` beziehungsweise `Synthetic data · Live AI`.

Kein Frontend-Fakeflow: jede angezeigte Aktion muss anhand ihrer gespeicherten Daten und n8n-Execution-ID nachvollziehbar sein. Ein optional öffentliches Deployment ist erst nach separater Freigabe zulässig; der n8n-Editor gehört nicht in eine ungeschützte Recruiter-Demo.

## 15. Sicherheit, Nachvollziehbarkeit und Grenzen

Rollen: Viewer liest; Operator erfasst und korrigiert; Production Manager genehmigt operative Maßnahmen; Quality Manager kontrolliert Qualitätsfreigaben; Admin verwaltet technische Fehler und Demo-Reset. Lokale Demo-Nutzer mit dokumentierter Anmeldung sind zulässig, aber nicht als offenes Rollenauswahlfeld in öffentlich bereitgestellten Systemen.

Session-Authentifizierung mit einer etablierten Bibliothek, sichere Cookie-Einstellungen für den jeweiligen Modus, CSRF-/Origin-Prüfung bei Schreibzugriffen, serverseitige Rollenprüfung, Request-Größenlimits und Rate Limits. Secret-Keys nie im Frontend, nie im Workflow-JSON und nie in Beispieldaten. E-Mail-Originaldaten und LLM-Eingaben aus normalen Logs entfernen oder redigieren.

Workflow-Exporte vor Veröffentlichung auf Credential-Namen, IDs, manuelle Header, E-Mail-Adressen, URLs und gespeicherte Testdaten prüfen. n8n weist ausdrücklich darauf hin, dass Exporte Credential-Namen/-IDs und andere sensible Konfiguration enthalten können. [S2]

Audit speichert Actor, Aktion, Revision, Status vorher/nachher, Correlation-ID, Workflow-/Execution-ID, fachliche Zeit und technische UTC-Zeit. Schreibpfade append-only für den Anwendungsnutzer gestalten. Dies ist ein nachvollziehbarer Verlauf, **kein** manipulationssicheres oder regulatorisch zertifiziertes Audit-System.

Keine echten EBRO-/Kunden-/Lieferantendaten, Logos, internen Formulierungen oder Credentials übernehmen. Synthetische Firma, Materialbezeichnungen und Vorgänge dürfen den Fertigungskontext plausibel darstellen, ohne interne Daten zu kopieren.

## 16. Tests und Nachweise

Unit-Tests: zeitabhängige Versorgung, Reservoir-/Reservierungsregeln, Teillieferungen, Geldaggregation, Scoregrenzen, typabhängige Faktoren und Zustandswechsel. Vertragstests: Event-, ERP-Snapshot-, Action-, Approval- und Analyse-JSON. Integrationstests: API + echte PostgreSQL-Transaktionen mit parallelen Anfragen. Workflowtests: echte importierte und veröffentlichte n8n-Flows. UI-End-to-End: vollständiger Weg vom Eingang bis zur sandboxseitigen Maßnahme und Timeline.

Deterministische Tests laufen ohne externe Provider. Ein Mock-LLM-Pass ist nur ein Orchestrierungsnachweis, keine KI-Qualitätsmessung.

Live-Evaluation: mindestens 60 kuratierte Fälle einschließlich unklarer und bösartiger Inhalte; 40 Entwicklung, 20 vorher zurückgehaltene Tests. PO-Zuordnung, Mengen, Datumsinterpretation, Typ, Schema-Validität, Anteil automatisch akzeptierter Fälle, unnötige Review-Fälle, unbelegte Aussagen, Latenz und tatsächlicher Tokenverbrauch messen. Als Ziel mindestens 95 % Typgenauigkeit auf dem kleinen Hold-out; keine falsch zugeordneten kritischen IDs/Daten unter automatisch akzeptierten Hold-out-Fällen. Ein Treffer auf diesem kleinen Testset ist keine allgemeine Fehlerfreiheit.

Ein Report nennt Modell, Promptversion, Datasetversion, Testzeitpunkt, Nenner und nicht bestandene Fälle. Ohne ausgeführte Live-Evaluation ausdrücklich `NOT RUN — credentials/budget required`; keine erfundenen Prozentzahlen oder Kosten. Testfälle dürfen nicht automatisch aus den Antworten des zu prüfenden Modells als richtig übernommen werden.

Die verbindlichen Abnahmetests stehen in `ACCEPTANCE_TESTS.md`. Keinen Meilenstein anhand vorhandener Dateien allein als erledigt markieren.

## 17. Lieferphasen

| Phase | Ergebnis | Abnahme |
|---|---|---|
| M0 — Machbarkeit & Verträge | Versionen, minimaler n8n-Lauf, Runner, Import/Publish, API-/Schema-Verträge, Bootstrap-Grenzen. | Eine importierte Testkette läuft über einen veröffentlichten Trigger; Neustart und zweiter Import funktionieren. |
| M1 — Fundament | Auth, PostgreSQL-Migrationen, synthetisches ERP, Source Events, Zustände, Outbox, feste Demo-Uhr. | Goldene Stammdaten konsistent; doppelte Annahme atomar; State/API-Vertragstests grün. |
| M2 — Erster vollständiger Schnitt | Supplier Delay über WF01/02–07, zunächst minimale UI und Mock-KI. | 85/CRITICAL; echte Freigabe; genau eine bestätigte Sandbox-Aktion; Fall bleibt bis fachlicher Lösung offen. |
| M3 — Robustheit | WF08–10, Revisionen, Dead Letter, Replay, Provider-Unsicherheit, SLA und Restart. | Duplikat-, Teillieferungs-, Stale-Approval-, Neustart- und Fehlerfälle automatisiert belegt. |
| M4 — V1 vervollständigen | Maschine, Qualität, vollständige kleine UI, optionale Live-KI und Adaptervertrag. | Alle drei Szenarien; Qualitäts- und Rollengrenzen; fehlende Live-Credentials sauber angezeigt. |
| M5 — Bewerbungsfähiges Release | Dokumentation, Screenshots aus laufender Anwendung, Video-Skript, CI, Evaluationsreport und frischer Starttest. | Unabhängiger Start anhand README; alle Pflichtabnahmen grün; Grenzen und echte Ergebnisse dokumentiert. |

M0 ist zuerst zu erledigen; Workflow-Dateien nicht massenhaft erfinden, bevor die Laufzeit geprüft ist. Datenmodell/API-Verträge vor paralleler Frontend-/Workflow-Implementierung einfrieren. Der PM hält Backlog, Risiken, Entscheidungen und Testnachweise aktuell. Der Build-Agent bearbeitet die nächste freie Aufgabe ohne neue allgemeine Ideenrunde.

## 18. Zielstruktur des späteren Repositories

```text
ai-production-incident-control/
  README.md
  AGENTS.md
  CONTEXT.md
  compose.yaml
  .env.example
  versions.lock
  apps/
    api/                    # FastAPI, Operations und Mock-ERP
    dashboard/              # React/TypeScript
  packages/
    domain-core/            # reine Impact-/Risk-Funktionen
    contracts/              # JSON Schema / generierte Verträge
  n8n/
    workflows/              # echte, geprüfte JSON-Exporte
    workflow-manifest.json  # stabile IDs, Referenzen, Node-Versionen
    build/                  # reproduzierbarer Code-Bundle-/Exportprozess
  database/
    migrations/
    seed/
  fixtures/
    emails/
    scenarios/
    evaluations/
  tests/
    unit/
    contracts/
    integration/
    workflows/
    e2e/
  scripts/
    bootstrap.ps1
    bootstrap.sh
    verify/
  docs/
    BUILD_PLAN.md
    BACKLOG.md
    ACCEPTANCE_TESTS.md
    architecture.md
    api-contracts.md
    threat-model.md
    demo-guide.md
    evaluation-report.md
    limitations.md
    SOURCES.md
    adr/
  evidence/
    test-results/
    screenshots/
    workflow-runs/
  .github/workflows/
```

Die Übergabe enthält nur die Planungsdateien, nicht bereits diese gesamte Implementierung. Eine vorhandene fremde `AGENTS.md` im Zielprojekt nicht blind überschreiben. Projektspezifische Regeln zusammenführen. Codex unterstützt Repository-Anweisungen über `AGENTS.md`. [S7]

## 19. Definition of Done

V1 ist fertig, wenn ein neuer Nutzer anhand des README einen sicheren synthetischen Stack starten, die drei fachlichen Demos auslösen, Rechenwege prüfen, als berechtigte Person eine konkrete Aktion freigeben, deren echte Sandbox-Ausführung sehen und Fehlerfälle nachvollziehen kann. Alle Kernflows müssen in n8n laufen; Screenshots allein sind kein Funktionsbeleg.

Außerdem: keine geheimen Daten im Export; reproduzierbare Migration/Seed/Import-Schritte; Authentifizierung und Rollen wirksam; neue Termine machen alte Freigaben ungültig; Liefermengen werden nicht verdoppelt; gefährdete Auftragspositionen werden nicht doppelt gezählt; unbekannte Sendewirkung wird nicht als sicher fehlgeschlagen behandelt; Metriken enthalten keine erfundenen Ergebnisse.

Die Abschlussübergabe nennt exakt: umgesetzt, durch welche Tests belegt, nicht umgesetzt, optional mangels Credentials nicht geprüft, bekannte Grenzen, Startanleitung und nächsten konkreten technischen Schritt. Ein guter Portfolio-Stand ist ein nachvollziehbares, begrenztes System — keine unbewiesene Behauptung „enterprise-ready“.
