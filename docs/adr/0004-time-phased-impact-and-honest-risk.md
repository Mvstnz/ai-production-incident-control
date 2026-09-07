# ADR 0004 — Zeitabhängige Versorgung und ehrliche Risikokennzahlen

**Status:** Vorgabe des Bauplans · **Datum:** 7. September 2026

## Kontext

Eine einfache Rechnung aus Gesamtbedarf und Lagerbestand ignoriert Bedarfstermine, Sperrbestände und Teilzusagen. Referenzierte Aufträge sind nicht automatisch verspätet; eine gefährdete offene Position ist nicht automatisch verlorener Umsatz.

## Entscheidung

Impact wird deterministisch aus einem konsistenten Snapshot mit bestätigten termingebundenen Zuflüssen und Bedarfen berechnet. Vorgeschlagene Teillieferungen gehören zunächst nur in ein What-if. Die Gesamtmenge einer Bestellung wird durch Aufteilung nicht erhöht. Gefährdeter Auftragswert bezieht sich auf offen gebliebene, verspätete Mengen unter Berücksichtigung erlaubter Teillieferung und wird nicht doppelt gezählt.

Risk Score und Schwellen sind versionierte Portfolio-Regeln, keine statistische Wahrscheinlichkeit. Ein Sicherheits-Override wird separat begründet, nicht als erfundener höherer Rohscore dargestellt. Die KI erklärt und formuliert Vorschläge; Zahlen und Freigaberegeln stammen nicht aus ihrem freien Urteil.

## Alternativen

Ein LLM als alleiniger Risikorechner wäre leichter zu demonstrieren, aber schlecht reproduzierbar und nicht zuverlässig prüfbar. Eine vollständige MRP-/Kapazitätsoptimierung überschreitet den sinnvollen Umfang dieses Projekts.

## Konsequenzen

Golden Tests definieren konkrete Datums-, Mengen- und Wertannahmen. Der vereinfachte durchlaufende Demo-Kalender sowie Grenzen bei Wechselwirkungen mehrerer Incidents müssen in der Anwendung und Dokumentation erkennbar bleiben. Eine neue Bestätigung erzeugt eine neue Analyse und macht veraltete Freigaben ungültig.
