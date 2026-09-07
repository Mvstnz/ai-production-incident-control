# ADR 0002 — versionierte Freigaben und ehrliche Zustellgarantien

**Status:** Vorgabe des Bauplans v1.0 · **Datum:** 2026-09-07

## Kontext

Ein Freigabelink oder ein Hash allein verhindert weder die Ausführung einer veralteten Maßnahme noch Doppelversand nach unklarem Provider-Timeout. Der frühere Entwurf hat diese Risiken nicht ausreichend unterschieden.

## Entscheidung

Freigaben binden den exakten versionierten Maßnahmenplan einschließlich Empfänger, vollständigem Text und Parametern. Serverseitige Identität, Rolle, Frist und Zustand bestimmen die Gültigkeit. Ein n8n-Wait-Resume ist nur ein Wakeup. Freigabekonsum und Action-Outbox werden atomar gespeichert.

Jobs werden mindestens einmal zugestellt. Persistente eindeutige Schlüssel und providerseitige Idempotenz schützen bekannte Wiederholungen. Bei unklarem externem Schreibresultat ohne verlässliche Idempotenz/Abfrage gilt UNKNOWN_OUTCOME mit Reconciliation oder Review, nicht blindes Retry.

## Alternativen und Abwägung

Ein einfacher Approve-Link ist kürzer zu bauen, aber bindet ohne zusätzliche Kontrollen weder Identität noch Planversion. Pauschales Retry verbessert scheinbare Verfügbarkeit, riskiert aber unerwünschte Nebenwirkungen. Die gewählte Lösung benötigt mehr Zustände, macht Grenzen dafür nachvollziehbar und testbar.

## Konsequenzen

Entwürfe entstehen vor Freigabe. Änderungen können Freigaben superseden. GET löst nichts aus. Jeder Provideradapter dokumentiert seine Garantien. Die Demo testet ausdrücklich Provider-Erfolg mit Client-Timeout. Kein pauschales Exactly-once-Versprechen.
