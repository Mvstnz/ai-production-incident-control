# ADR 0002 — Sicherer Offline-Demomodus zuerst

**Status:** Vorgabe des Bauplans · **Datum:** 7. September 2026

## Kontext

Ein Reviewer soll das Projekt ohne Firmenkonto, Gmail-OAuth, kostenpflichtige KI und fremde Cloud-Systeme ansehen können. Gleichzeitig darf die Demo nicht behaupten, ein deterministischer Mock beweise reale KI-Qualität.

## Entscheidung

Der Standardstack nutzt synthetische ERP-Daten, bekannte E-Mail-Fixtures, explizite Mock-KI, lokale Mail-Capture und persistierte Sandbox-Tickets. Live-KI und Live-Connectoren sind getrennte Schalter. Die Demo besitzt eine explizite fachliche Uhr. Keine realen Sendungen oder produktiven ERP-Eingriffe sind standardmäßig möglich.

## Alternativen

Ein zwingender Live-Stack ist realistischer, erschwert aber Einrichtung, sichere Veröffentlichung und deterministische Tests. Ein reiner klickbarer UI-Prototyp wäre einfacher, beweist aber keine n8n-Ausführung.

## Konsequenzen

Alle zentralen Zustandswechsel und Workflows müssen im Demomodus echt ausgeführt werden. Mock-Ausgaben sind nur für bekannte Testfälle zulässig und sichtbar zu kennzeichnen. Reale KI-Metriken werden separat gemessen oder ehrlich als nicht ausgeführt ausgewiesen. Öffentliche Bereitstellung ist eine spätere explizite Entscheidung.
