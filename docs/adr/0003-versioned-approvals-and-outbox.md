# ADR 0003 — Versionierte Freigaben und transaktionale Arbeitswarteschlange

**Status:** Vorgabe des Bauplans · **Datum:** 7. September 2026

## Kontext

Liefertermine können sich ändern, während eine Person eine alte Freigabeseite offen hat. Dienste können zwischen Persistierung und Versand ausfallen. Ein einfacher Button oder ein Idempotency-Key allein löst diese Probleme nicht.

## Entscheidung

PostgreSQL ist die verbindliche Quelle für Incident-Revisionen, konkrete Action-Pläne, Freigaben und Work Items. Zustandsänderung und nächster Arbeitsauftrag werden atomar gespeichert. Claims besitzen Leases und Tokens. Jede Ausführung prüft aktuelle Revision, genehmigten Payload-Hash und Rolle erneut.

Freigaben warten nicht in einem synchron blockierten Parent-Workflow. Eine Entscheidung erzeugt ein neues persistiertes Ereignis. Ein vorhandener n8n-Wait-Mechanismus kann technische Abläufe erleichtern, ist aber nicht alleiniger Besitzer der fachlichen Freigabe.

## Alternativen

Nur in n8n-Execution-Daten gespeicherte Entscheidungen koppeln die Fachlichkeit zu stark an einzelne Läufe. Ein vollständiger Event-Streaming-Stack wäre leistungsfähiger, ist für die lokale Demo aber unnötig.

## Konsequenzen

At-least-once-Verarbeitung muss durch Eindeutigkeiten und Versionsprüfung beherrscht werden. Eine Outbox garantiert keine atomare externe Mailzustellung. Unklare Ergebnisse werden vor einem erneuten Versuch abgeglichen oder menschlich geprüft. Der Status `DELIVERY_UNKNOWN` ist fachlich notwendig und kein allgemeiner Fehlerstatus.
