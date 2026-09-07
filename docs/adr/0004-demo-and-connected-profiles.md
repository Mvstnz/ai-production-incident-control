# ADR 0004 — reproduzierbare lokale Demo und getrennte Connected Sandbox

**Status:** Vorgabe des Bauplans v1.0 · **Datum:** 2026-09-07

## Kontext

Ein öffentliches Portfolio soll ohne persönliche Konten ausprobierbar sein. Gleichzeitig soll der bereitgestellte n8n-Connector tatsächliche Workflows auf der autorisierten Instanz einrichten. Externe OAuth-Rechte, Netzwerkrouten und bezahlte LLM-Zugriffe lassen sich nicht durch einen Docker-Befehl ersetzen.

## Entscheidung

DEMO_LOCAL verwendet echtes lokales n8n und echte Anwendungslogik, aber klar gekennzeichnete Fixture-AI und lokale externe Effekte. CONNECTED_SANDBOX verwendet dieselben fachlichen Verträge mit vorhandenen berechtigten Live-Adaptern. Alle ERP-Daten bleiben synthetisch. Externe Aktionen bleiben standardmäßig deaktiviert.

Die Basis läuft als Single-Instance-n8n ohne Redis. Ein Queue-Profil mit Redis/Worker/gegebenenfalls Runnern ist optional und getrennt dokumentiert. Keine pauschale Behauptung, jede Version oder Verbindung könne jede Administrationsoperation ausführen.

## Alternativen und Abwägung

Nur Live-Cloud würde Demo und Tests an Konten und Kosten binden. Nur Fixtures würden keine echten Integrationsfähigkeiten nachweisen. Beide Profile geben ein reproduzierbares Ergebnis und erlauben zusätzliche belegte Live-Tests, ohne sie zu erfinden. Redis von Beginn an würde Betriebsaufwand ohne erforderlichen Nutzen erzeugen.

## Konsequenzen

Simulation ist in UI und Reports sichtbar. Initiale Einrichtungsschritte werden ehrlich benannt. Fehlende Live-Rechte blockieren nur entsprechende Tests. Lokale und Zielinstanz-Erfolge werden getrennt dokumentiert. Öffentliche Freigabe ist ein eigener autorisierter Schritt.
