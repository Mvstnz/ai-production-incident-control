import { useEffect, useState, type FormEvent } from "react";
import { ArrowRight, MailSearch } from "lucide-react";
import { api, type Run } from "./api";
import { ErrorBox, Loading, useQuery } from "./ui";
import type { ViewProps } from "./App";

export function MailAnalysis({
  session,
  onRun,
}: ViewProps & { onRun: (run: Run) => Promise<void> }) {
  const query = useQuery<{
    live_ai_enabled: boolean;
    source_email: { subject: string; content_text: string };
  }>("/api/demo/catalog", 0, 0);
  const [subject, setSubject] = useState(""),
    [content, setContent] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<Error | null>(null);
  useEffect(() => {
    if (query.data) {
      setSubject(query.data.source_email.subject);
      setContent(query.data.source_email.content_text);
    }
  }, [query.data]);
  const viewer = session.user.role === "viewer";
  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onRun(
        await api<Run>("/api/demo/custom-email", {
          subject,
          content_text: content,
        }),
      );
    } catch (err) {
      setError(err as Error);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="mail-page">
      <section className="plain-panel">
        <span className="case-icon">
          <MailSearch size={26} />
        </span>
        <h1>Eine Lieferanten-Mail auswerten</h1>
        <p className="guide-lead">
          Hier beginnt der tatsächliche KI-Schritt: Gemini liest eine neu
          eingereichte Mail und gibt die gemeldeten Änderungen zur Prüfung
          weiter.
        </p>
        {query.error && <ErrorBox error={query.error} />}
        {!query.data && query.loading && <Loading />}
        {query.data && (
          <>
            <div className="conditional-note">
              <h2>
                {query.data.live_ai_enabled
                  ? "Gemini-Auswertung ist aktiviert"
                  : "Gemini-Auswertung ist hier noch ausgeschaltet"}
              </h2>
              <p>
                {query.data.live_ai_enabled
                  ? viewer
                    ? "Du nutzt den Besucherzugang. Das Einreichen einer neuen Mail erfordert einen Team-Zugang; die vorhandenen Fälle kannst du ohne Anmeldung ansehen."
                    : "Die eingereichte Mail wird an Gemini übertragen. Verwende ausschließlich erfundene Daten aus dem Beispielbetrieb."
                  : "Der Workflow für die KI-Auswertung ist vorhanden, in dieser Umgebung aber nicht für Aufrufe freigeschaltet. Die gespeicherten Fälle lassen sich trotzdem Schritt für Schritt nachvollziehen."}
              </p>
            </div>
            <form onSubmit={submit} className="mail-form">
              <label>
                Betreff
                <input
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  required
                  maxLength={500}
                  readOnly={viewer || !query.data.live_ai_enabled}
                  disabled={busy}
                />
              </label>
              <label>
                Beispiel einer Lieferanten-Mail
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  required
                  rows={11}
                  maxLength={50000}
                  readOnly={viewer || !query.data.live_ai_enabled}
                  disabled={busy}
                />
              </label>
              {error && <ErrorBox error={error} />}
              {!viewer && query.data.live_ai_enabled && (
                <button className="button primary" disabled={busy}>
                  {busy ? "Mail wird eingereicht …" : "Mit Gemini auswerten"}
                  <ArrowRight size={16} />
                </button>
              )}
            </form>
          </>
        )}
        <p className="explanation-note">
          Nach der Auswertung werden die Angaben mit den Betriebsdaten geprüft.
          Fehlmengen und betroffene Aufträge berechnet das System. Die KI
          erteilt keine Freigaben.
        </p>
        <a className="text-link" href="#/overview">
          Gespeicherte Fälle ansehen <ArrowRight size={16} />
        </a>
      </section>
    </div>
  );
}
