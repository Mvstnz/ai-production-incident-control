# ADR 0003 — zeitbezogene Impact-Analyse und deterministische Risk Policy

**Status:** Vorgabe des Bauplans v1.0 · **Datum:** 2026-09-07

## Kontext

Ein LLM kann überzeugende, aber unbelegte Auftragsfolgen formulieren. Eine reine Gesamtsubtraktion von Bedarf und Bestand übersieht Termine, Reservierungen und die Verbindlichkeit von Teillieferungen. Der offene Auftragswert ist außerdem nicht mit Umsatzverlust gleichzusetzen.

## Entscheidung

Die Analyse vergleicht denselben konsistenten ERP-Snapshot vor und nach der Incident-Änderung. Ressourcen werden zeitbezogen und ohne Doppelvergabe allokiert. Vorgeschlagene Teillieferungen bleiben Was-wäre-wenn; bestätigte Splits ersetzen den Lieferplan. Betroffene Kundenpositionen werden anhand eindeutiger IDs gezählt.

Eine versionierte Demo-Policy berechnet Faktoren, Score, Severity und Hard Overrides. Fehlende Fakten bleiben unbekannt. Das LLM erklärt belegte Ergebnisse und erstellt prüfbare Entwürfe; es bestimmt weder Score noch Geschäftsidentitäten aus Vermutungen.

## Alternativen und Abwägung

LLM-only wäre schneller aufzubauen, aber nicht reproduzierbar. Vollständiges MRP/APS wäre präziser, würde den Portfolio-Scope sprengen. Eine explizit vereinfachte, getestete Allokation mit offengelegten Kalender-/Vollpositionsannahmen liefert ein verteidigbares Mittelfeld.

## Konsequenzen

Hero- und Grenzfall-Fixtures werden rechnerisch geprüft. Bestände, Termine, Geld und KI-Text bleiben nachvollziehbar. Die Policy ist keine Verlustwahrscheinlichkeit. Dashboard-Summen bilden die Vereinigungsmenge betroffener offener Kundenpositionen.
