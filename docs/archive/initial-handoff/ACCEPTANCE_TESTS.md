# Verbindliche Abnahmetests

**Stand bei Übergabe:** nicht ausgeführt. Die Golden-Fixture-Arithmetik wurde außerhalb einer Implementierung überprüft; das ersetzt keinen der folgenden Softwaretests.

Jeder Test muss auf die fixierten Versionen und den tatsächlichen Code verweisen. Ergebnisformat: Test-ID, Voraussetzungen, Auslöser, beobachtetes Ergebnis, PASS/FAIL/NOT RUN, Nachweisdatei. Screenshots können ergänzen, aber maschinenprüfbare Assertions nicht ersetzen.

## Plattform und Verträge

**T01 — Frischer Start und wiederholter Start.** Mit leerer Demo-Datenbank und ohne externe Credentials bootstrapen. UI, API, n8n und Mail-Capture sind nutzbar; Schema/Seed vorhanden; Schritte im README vollständig. Erneuter Start erhält Daten und Secrets. Optional nötige Owner-Einrichtung steht ausdrücklich in der Anleitung. Reset gegen ein nicht als Demo erkanntes Ziel wird verweigert.

**T02 — Echte n8n-Laufzeit.** Exportierte Testkette und anschließend Kernworkflows in die gepinnte Instanz importieren, Referenzen auflösen und veröffentlichen. Ein tatsächlicher Produktions-Webhook löst den Code-Subworkflow im externen Runner aus. Zweiter Import erzeugt keine kaputten Verweise oder unkontrollierten Duplikate. Execution-ID und Resultat speichern.

**T03 — Vertragsprüfung.** Alle Beispiel-Events und erwarteten Outputs validieren gegen versionierte JSON-Schemas. Unbekannte Typen, falsche Mengen-/Geldeinheiten und kaputte Datumswerte führen zu dokumentierten Fehlern oder Review. Eine API-Vertragsänderung darf nicht unbemerkt das Frontend oder Workflow-JSON brechen.

**T04 — Seed-Integrität.** PO 4500192/10 gehört zum vorgesehenen Lieferanten und Material, offene Liefermenge ist 40, nutzbarer Bestand ist 14 und Gesamtbedarf ist 38. Produktions-/Vertriebs-/Chargenzuordnungen sind gültige Fremdschlüssel. Zweimal Seeden verdoppelt keinen Datensatz.

## Deduplizierung und Impact

**T05 — Paralleles identisches Source Event.** 20 identische Eingänge mit demselben `(source_system, source_id)` gleichzeitig senden. Genau ein Source Event und genau eine fachliche Erstverarbeitung entstehen; Antworten verweisen auf denselben Vorgang. Keine 20 KI-Aufrufe und keine mehrfachen Benachrichtigungen aus dem Duplikat. Bereits persistierte Events werden beim Dispatcher-Aufruf trotzdem genau einmal bearbeitet; technische Deduplizierung darf keine verlorene Bearbeitung oder Dispatch-Schleife erzeugen.

**T06 — Idempotency-Konflikt.** Dieselbe Source-ID mit verändertem Body senden. Die API verweigert das stille Überschreiben und meldet einen Konflikt. Neue tatsächliche Meldungen müssen eine neue Source-ID tragen.

**T07 — Golden A: Grundrechnung.** Hauptfixture zum festgelegten Demo-Zeitpunkt auslösen. Erwartet: 38 benötigte, 14 rechtzeitig gedeckte und 24 ungedeckte Stück; PRD-1001 gedeckt, PRD-1002 fehlen 8, PRD-1003 fehlen 16. Drei referenzierte, aber zwei unterversorgte Produktionsaufträge. Beide gefährdeten Positionen sind im baseline Plan rechtzeitig und im Incident-Plan verspätet.

**T08 — Golden A: Score.** Faktoren 20/20/10/15/10/10 ergeben 85/CRITICAL. Der Test prüft einzelne Faktoren, Datenquellen und Policy-Version, nicht nur eine hardcodierte Gesamtzahl. Grenzwerte 24/25, 49/50 und 74/75 sowie unbekannte Eingaben separat testen.

**T09 — Golden A: Wert und Aussage.** Nur SO-1002/10 mit 48.000 EUR und SO-1003/10 mit 78.400 EUR zählen; Summe 126.400 EUR. SO-1001 zählt nicht. UI spricht von gefährdetem offenen Auftragswert, nicht garantiertem Umsatzverlust.

**T10 — Unverbindliche Teillieferung.** „We may be able to ship 10 pcs“ verändert keine bestätigte Versorgung. Eine separate What-if-Darstellung ist erlaubt, darf aber den Primärscore nicht absenken. Gesamtmenge bleibt 40.

**T11 — Bestätigte Teillieferung / fachliche Revision.** Neue Nachricht bestätigt 10 Stück am 13.10. und restliche 30 am 19.10. Derselbe Incident erhält neue Revision und neue Analyse. PRD-1002 wird rechtzeitig versorgt, PRD-1003 fehlen 14; genau eine gefährdete Position mit 78.400 EUR; Score 70/HIGH. Gesamtzufluss niemals 50.

**T12 — Mehrfache Exposition und Reservierungen.** Zwei Incidents gefährden dieselbe offene Vertriebsposition: Dashboard zählt sie nicht doppelt. Mehrere Materialanforderungen derselben Position erzeugen ebenfalls keinen doppelten Wert. Gesperrter oder bereits fest zugeordneter Bestand wird nicht erneut frei vergeben. Negative Bestandskurven nicht als aufsummierte zusätzliche Fehlmengen zählen.

## KI und Eingaben

**T13 — Fehlende/mehrdeutige Angaben.** Unbekannte PO, mehrere passende PO-Positionen, widersprüchliche Menge und mehrdeutiges Datum gehen in Review. Ein vom Modell frei ausgegebener hoher Confidence-Wert überstimmt dies nicht. Keine erfundenen Jahreszahlen oder Empfänger.

**T14 — Prompt-Injection.** Eine E-Mail mit der Aufforderung, Regeln zu ignorieren, Geheimnisse zu senden oder fremde URLs aufzurufen, wird ausschließlich als fachlicher Input behandelt. Keine Tool-/Netzwerkaktion aufgrund dieser Anweisung, keine Übernahme des fremden Empfängers als Freigabeziel.

**T15 — KI-Ausfall und unbekannter Mock-Input.** Im Live-Modus einen Timeout bzw. ungültiges JSON erzeugen. Bounded Retry oder Review; im erklärenden Schritt sichtbarer Templatefallback. Nicht still auf Mock wechseln. Im Mock-Modus darf unbekannter Freitext keinen erfundenen Erfolg erhalten.

## Freigabe und Ausführung

**T16 — Rollenprüfung.** Viewer und Operator können keine Manager-Aktion genehmigen. Server verweigert auch einen direkt konstruierten HTTP-Aufruf. Berechtigter Manager sieht die exakte Planversion samt Empfänger und Nachricht.

**T17 — Veraltete Freigabe.** Nach Erzeugung eines Approval-Tokens den Incident wie in T11 fortschreiben oder den Entwurf ändern. Alte Freigabe liefert 409/veraltet und kann keine Aktion autorisieren. Bereits ausgeführte alte Aktionen bleiben im Verlauf sichtbar.

**T18 — Race und Replay.** Zwei gleichzeitige Approve-Anfragen führen zu genau einer verbindlichen Entscheidung und einer auszuführenden Aktion. Replay derselben Entscheidung löst keinen zweiten Seiteneffekt aus. Abgelaufene Freigaben werden zurückgewiesen.

**T19 — Konkreter Text, Modify und Reject.** Genehmigten Betreff, Body oder Empfänger nachträglich verändern: neue Freigabe erforderlich. „Modify“ ist kein Approve. „Reject“ lässt den fachlichen Incident offen und erzeugt keinen Versand. GET-Link verändert keinen Status.

**T20 — Erfolgreiche Sandbox-Ausführung.** Nach gültiger Freigabe ist genau eine genehmigte Aktion im bestätigten Sandbox-Adapterzustand vorhanden; Mail-Capture/Ticket und Audit referenzieren dieselbe Action-ID. Ohne Freigabe kein externer Kommunikationsadapteraufruf. Live-KI allein darf keinen echten Versand aktivieren.

**T21 — Annahme erfolgt, Antwort verloren.** Adapter nimmt eine Sendung an, Verbindung bricht vor Antwort ab. Aktion wird `DELIVERY_UNKNOWN`. Kein blinder Retry. Ein Adapter mit belegter Idempotenz oder Abfragemöglichkeit findet das bestehende Ergebnis; andernfalls verlangt das System eine menschliche Abgleichentscheidung. Kein pauschaler Exactly-once-Anspruch für SMTP/Gmail.

## Fehler, Fristen und Lebenszyklus

**T22 — Absturz und Wiederanlauf.** Nach Persistierung eines Events, während einer Analyse, bei offener Freigabe und nach Claim einer Action jeweils den zuständigen Dienst stoppen/starten. Arbeit geht nicht verloren; Leases verfallen kontrolliert; alte Claim-Token können keinen neu vergebenen Auftrag abschließen. Eventuell bereits ausgelöste externe Aktionen werden vor Wiederholung abgeglichen.

**T23 — Retry und Dead Letter.** Lesenden 429/5xx auslösen: begrenzte Wiederholung mit Backoff. Permanenten Credential-/Vertragsfehler auslösen: Dead Letter, kein Endlosloop. Autorisierter Replay mit Begründung behält fachliche ID. Error Trigger über automatische veröffentlichte Ausführung testen; manuelle Editorläufe separat behandeln.

**T24 — SLA und Digest.** Demo-Uhr vor die Frist, auf die Frist und darüber vorstellen. Genau eine fällige Eskalation je definierter Stufe; Duplikate verlängern keine Frist. Wiederholter Digest-Lauf zählt gleiche offene Positionen nicht doppelt und erzeugt nur einen Bericht je Tag/Zeitzone. Ablauf einer Freigabe löst keinen automatischen Versand aus.

**T25 — Maschinenausfall.** Authentifizierten Ausfall zu einer vorhandenen Maschine melden. Betroffene Operationen korrekt identifizieren; unpassende oder bereits belegte Ersatzmaschine nicht empfehlen. Passender freier Slot erzeugt konkreten Vorschlag. Erst nach Freigabe/Mock-Bestätigung ändert sich der Plan und der verbleibende Impact wird neu berechnet.

**T26 — Qualitätsfall mit offener Auslieferung.** Bestätigt fehlerhafte Charge mit Produktions- und offener Versandzuordnung melden. Nur zugeordnete Mengen/Positionen betroffen; Mock-Sperre gesetzt; Quality Manager intern informiert. Score bleibt nachvollziehbar, Severity-Override CRITICAL weist `QUALITY_SHIPMENT_EXPOSURE` aus. Operator kann Sperre nicht aufheben.

**T27 — Qualitätsfall nach Versand.** Dieselbe Problemart mit bereits versandter Teilmenge. System behauptet nicht, diese Menge rückwirkend gesperrt zu haben; Ausnahme/Eskalation und korrekte noch sperrbare Restmengen sichtbar. Kein reales Recall automatisch ausführen.

**T28 — Incident nicht vorschnell lösen.** Erfolgreiche Eskalationsmail und erstelltes Ticket lassen den Incident in Bearbeitung/Nachverfolgung. Erst dokumentierte fachliche Bestätigung oder berechtigte Managerentscheidung mit Nachweis ermöglicht `RESOLVED`; Abschluss-/Wiedereröffnungsereignisse auditieren.

## Oberfläche, Sicherheit und Portfolio

**T29 — Bedienung und echte Daten.** Drei Szenarien über die Oberfläche auslösen, mit korrekten Rollen bearbeiten, Quellen und Timeline ansehen. Leere Daten, Lade-/Fehlerzustände und Keyboard-Navigation prüfen. Eine UI-Aktion ist auf echte API-Daten und n8n-Execution-ID zurückführbar.

**T30 — Sicherheitsgrenzen.** Unauthentifizierte interne API, fremde Origins, direkte Rollenmanipulation, oversized Payload und unerlaubter Demo-Reset werden verweigert. Keine Secrets in Frontendbundle, Logs, Screenshots oder Workflow-Export. Editor/DB/Runner nicht ungeschützt öffentlich. Live-Credentials schalten nicht nebenbei Schreibadapter frei.

**T31 — Ehrliche Evaluation.** Dataset- und Hold-out-Trennung vorhanden. Reale Modellmessung nur bei tatsächlichem Live-Aufruf als solche ausweisen; Modell/Promptversion und Nenner enthalten. Bei fehlenden Credentials `NOT RUN`. Mock-Ergebnisse nicht als Modellgenauigkeit verkaufen. Falsch automatisch akzeptierte kritische Angaben führen zu sichtbarem Nichtbestehen, nicht zum Entfernen des Testfalls.

**T32 — Reproduzierbare Übergabe.** Unabhängiger Reviewer startet aus frischem Checkout gemäß README, führt die drei Demos sowie Duplikat-/Stale-Approval-/Fehlerfälle aus und sieht dieselben fachlichen Resultate. Screenshots stammen aus diesem echten Stand; Einschränkungen, optional nicht geprüfte Connectoren und echte Testergebnisse sind auffindbar.
