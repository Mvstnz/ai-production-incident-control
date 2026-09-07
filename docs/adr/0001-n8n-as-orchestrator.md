# ADR 0001 — n8n als Orchestrator, kleine API für Persistenz

**Status:** Vorgabe des Bauplans · **Datum:** 7. September 2026

## Kontext

Das Ziel ist ein n8n-Bewerbungsprojekt. Eine monolithische Backend-Anwendung mit einem vorgeschalteten Webhook würde zwar eine Oberfläche liefern, aber die gewünschte Automatisierungskompetenz kaum sichtbar machen. Andererseits sind konkurrierende Zustandsänderungen und Freigaben in beliebig verteilten Code-Nodes schwer abzusichern.

## Entscheidung

n8n übernimmt nachvollziehbare Orchestrierung, externe Adapter und die sichtbaren Analyse-/Action-Schritte. FastAPI verwaltet Authentifizierung, versionierte Verträge, synthetische ERP-Daten und atomare Persistenz. Reine Impact-/Risk-Funktionen werden in TypeScript separat getestet und identisch in n8n-Code-Nodes gebündelt.

## Alternativen

Alles in n8n mit frei verteiltem SQL würde zentrale Konsistenzregeln schwächen. Alles im Backend würde das Portfolioziel verfehlen. Ein großer Microservice-Stack würde Integrationsaufwand ohne entsprechenden Demonstrationsnutzen erzeugen.

## Konsequenzen

Es gibt zwei technische Ökosysteme, aber nur einen Rechenkern. Gemeinsame JSON-Verträge und ein früher echter n8n-Importtest sind Pflicht. Der Code-Bundle-Prozess muss reproduzierbar sein. Wenn dieser Ansatz auf der fixierten Version nicht tragfähig ist, Problem in M0 belegen und dieses ADR gezielt ändern, nicht heimlich die ganze Lösung in das Backend verlegen.
