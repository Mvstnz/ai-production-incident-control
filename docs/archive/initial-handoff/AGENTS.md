# Arbeitsregeln für Codex und den koordinierenden PM

## Auftrag

Implementiert `AI Production Incident Control` gemäß `docs/BUILD_PLAN.md`. Dies ist ein Bewerbungsprojekt mit synthetischen Daten, nicht ein produktives ERP. Das vorliegende Paket enthält eine Spezifikation, noch keine lauffähige Implementierung.

Lest zuerst `docs/BUILD_PLAN.md`, dann `docs/BACKLOG.md` und die für die Aufgabe relevanten Tests in `docs/ACCEPTANCE_TESTS.md`. `CONTEXT.md` enthält ausschließlich Begriffsdefinitionen. Architekturentscheidungen stehen unter `docs/adr/`.

## Arbeitsweise

Der PM verwaltet Abhängigkeiten, Arbeitspakete, Risiken und Nachweise. Codex implementiert und testet. Eine konkrete Netra-API oder ein bestimmter Agentenmodus ist keine Voraussetzung. Bei verfügbarer Delegation nur unabhängige, klar abgegrenzte Pakete parallel bearbeiten; andernfalls dieselben Pakete sequenziell erledigen.

Mit M0 beginnen: Versionen prüfen und fixieren, eine kleine echte n8n-Kette importieren/veröffentlichen/ausführen. Erst danach weitere Workflow-Dateien erstellen. Die vorhandene Spezifikation ist die Entscheidungsvorlage; keine neue allgemeine Ideen- oder Interviewrunde starten. Kleine Implementierungsentscheidungen selbst treffen und dokumentieren.

Nach jedem Arbeitspaket dokumentieren: Dateien, ausgeführte Testbefehle, Ergebnisse, offene Probleme und nächstes freies Paket. `docs/BACKLOG.md` aktuell halten. Eine nicht ausgeführte Prüfung als `NOT RUN` kennzeichnen. Keine pauschalen Erfolgsbehauptungen und keine simulierten Testlogs.

## Nicht verhandelbare Anforderungen

- n8n bleibt die sichtbare Automatisierungszentrale. Nicht alle Workflows in eine Backend-Blackbox verschieben.
- Der Standardmodus benötigt weder fremde Konten noch bezahlte API-Aufrufe. Mock-KI sichtbar kennzeichnen; unbekannte Eingaben nicht als verstanden ausgeben.
- Goldene Ergebnisse: Supplier Delay 24 fehlende Stück, zwei gefährdete Vertriebspositionen, 126.400 EUR, Score 85; bestätigte Teillieferung 14 fehlende Stück, eine gefährdete Position, 78.400 EUR, Score 70. Regeln nicht manipulieren, um diese Werte zu erzwingen.
- Technische Duplikate, neue fachliche Revisionen und veraltete Freigaben unterschiedlich behandeln.
- Freigabe bindet exakten Empfänger, Text, Action-Payload und Planversion. Ein neuer KI-Entwurf nach Freigabe ist nicht automatisch autorisiert.
- Kein autonomer realer Versand, Einkauf, produktiver ERP-Eingriff oder unautorisierter Cloud-Deploy.
- Keine Exactly-once-Garantie für fremde E-Mail-Anbieter ohne belegtes Protokoll. Unklares Ergebnis wird `DELIVERY_UNKNOWN`, nicht blind wiederholt.
- Keine echten Unternehmensdaten, Credentials, Tokens oder sensitiven Workflow-Exports veröffentlichen.
- Rechenlogik als reine, getestete TypeScript-Funktionen; derselbe gebündelte Code läuft in n8n. API übernimmt Persistenz und atomare Verträge, nicht eine zweite Rechenimplementierung.
- Fehlerfälle und reale n8n-Laufzeittests gehören zum Lieferumfang. Vorhandenes JSON oder UI-Mockup bedeutet nicht „fertig“.
- Ein gesendetes Eskalationsschreiben bedeutet nicht, dass ein Incident gelöst ist.

## Änderungs- und Sicherheitsgrenzen

Vor zusätzlichem Geldverbrauch, Zugriff auf echte Konten, Veröffentlichung oder realen externen Aktionen Zustimmung einholen. Fehlende Live-Credentials sind kein Grund, den Offline-Demopfad nicht fertigzustellen. Bestehende fremde Dateien und insbesondere bestehende `AGENTS.md`-Regeln nicht blind überschreiben.

Das Ziel-README, die UI und Codebezeichner sind englisch. Deutsche Übergabedokumente dürfen erhalten bleiben. Gemeinsame Verträge vor parallelen Änderungen stabilisieren. Wichtige schwer rückgängig zu machende Entscheidungen als kurzes ADR dokumentieren, nicht im Glossar.

## Tests und Abschluss

Die konkreten Testbefehle sind in M0/M1 einzurichten und anschließend hier oder im README einzutragen. Vorher keine nicht vorhandenen Befehle als ausgeführt darstellen. Tests laufen gegen die fixierten Versionen und enthalten einen frischen Bootstrap-/Importtest.

Fertig bedeutet: alle Pflichtkriterien in `docs/ACCEPTANCE_TESTS.md` mit überprüfbaren Nachweisen bestanden. Optionale Live-Tests dürfen mit ehrlichem Grund `NOT RUN` bleiben, dürfen aber nicht als funktionsgeprüfte Live-Integration beworben werden. Abschlussbericht unterscheidet implementiert, getestet, nicht getestet und bekannte Grenzen.
