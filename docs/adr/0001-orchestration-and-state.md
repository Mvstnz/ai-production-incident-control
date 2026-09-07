# ADR 0001 — n8n orchestriert; fachlicher Zustand bleibt in PostgreSQL

**Status:** Vorgabe des Bauplans v1.0 · **Datum:** 2026-09-07

## Kontext

Das Portfolio soll echte n8n-Prozessautomatisierung zeigen und zugleich reproduzierbar mit konkurrierenden Meldungen, Wartezuständen und Wiederanlauf umgehen. Weder ein einziger Python-Endpunkt hinter einem n8n-Node noch verstreuter fachlicher Zustand in einzelnen Executions erfüllt beide Ziele gut.

## Entscheidung

Zehn n8n-Workflows übernehmen Trigger, Orchestrierung, Verzweigungen, Freigabe-Warten und Integrationen. Eine Operations API kapselt atomare Zustandskommandos und einmal implementierte testbare Domain-Funktionen. PostgreSQL hält den fachlichen Zustand. Ein gesondertes synthetisches ERP ist per REST abgegrenzt. n8n-interne Tabellen werden nicht direkt bearbeitet.

## Alternativen und Abwägung

Alles in Code-Nodes: einfache erste Demo, aber schwer prüfbare Transaktions- und Parallelitätslogik. Alles im Backend: gute Code-Testbarkeit, aber n8n wird zur Kulisse. Die gewählte Grenze verlangt API-Contracts, lässt dafür sichtbare Orchestrierung mit überprüfbarer Konsistenz zusammenwirken.

## Konsequenzen

Mehrere Trigger nutzen dieselben Domänenkommandos. SQL-Constraints schützen Invarianten unabhängig vom Workflow. API-/Workflow-Grenzen und reine Rechenfunktionen werden separat getestet. Eine API pro Workflow wird ausdrücklich nicht verlangt.
