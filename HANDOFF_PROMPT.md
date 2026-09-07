# Arbeitsauftrag

Baut das Projekt „AI Production Incident Control“ aus diesem Paket vollständig als vorzeigbares n8n-Bewerbungsprojekt.

Der PM von Netra übernimmt die Koordination, Abhängigkeiten und Abnahme. Codex übernimmt Implementierung, Tests und technische Dokumentation. Setzt keine spezielle Netra-API voraus; verwendet die tatsächlich verfügbare Arbeitsumgebung.

Lest zuerst `AGENTS.md`, danach `docs/BUILD_PLAN.md`, `docs/BACKLOG.md` und `docs/ACCEPTANCE_TESTS.md`. Der Bauplan ersetzt widersprüchliche Details aus früheren Chats. Startet keine neue allgemeine Ideenfindung. Beginnt mit M0 und arbeitet die Lieferphasen mit überprüfbaren Nachweisen ab.

Baut zuerst den Supplier-Delay-Fall komplett durch: persistierter Eingang, KI-Mock/validierte Extraktion, zeitabhängige ERP-Analyse, deterministischer Score, konkreter Aktionsentwurf, echte rollenbasierte Freigabe, Sandbox-Ausführung und Audit-Verlauf. Erst danach Maschine und Qualität ausbauen. n8n muss die sichtbare Orchestrierung übernehmen und tatsächlich lauffähige, importierte Workflows enthalten.

Der Standardmodus muss ohne bezahlte APIs oder fremde Konten funktionieren. Keine echten Unternehmensdaten verwenden. Kein realer Versand, produktiver ERP-Eingriff, kostenpflichtiger Dienst oder öffentliches Deployment ohne separate Zustimmung. Fehlende Live-Credentials dürfen den Offline-Build nicht blockieren.

Beachtet besonders: bestätigte versus vorgeschlagene Teillieferungen, fachliche Revisionen statt falscher Duplikate, keine doppelte Zählung gefährdeter Positionen, Freigabe der exakten Nachricht vor Versand, sichere Behandlung unklarer Zustellung und Wiederanlauf nach Absturz.

Pflegt das Backlog und dokumentiert je Paket die ausgeführten Tests mit Ergebnis. Schreibt nicht „fertig“, solange nur Code, JSON oder ein UI-Mockup vorhanden ist. Nicht ausführbare Tests als `NOT RUN` kennzeichnen. Bei kleineren offenen technischen Fragen trefft eine begründete Entscheidung und dokumentiert sie. Für echte Berechtigungs- oder Kostenfragen bleibt die Zustimmung des Nutzers erforderlich.

Die Abschlussübergabe muss enthalten: lauffähiges Repository, Startanleitung, alle drei Demos, echte n8n-Ausführungsnachweise, Testergebnisse, Screenshots aus der laufenden Anwendung, englisches Portfolio-README und ausdrücklich benannte Grenzen. Beginnt jetzt mit dem Versions-/Import-/Runner-Smoke-Test aus M0.
