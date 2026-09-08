import { ArrowRight, Factory, Mail, ShieldCheck, Truck } from "lucide-react";
import { incidentTitle, scoped, type Incident, type Kpis } from "./api";
import { Badge, Empty, ErrorBox, Loading, useQuery } from "./ui";
import type { ViewProps } from "./App";

export const caseCopy: Record<
  string,
  { topic: string; intro: string; question: string; icon: typeof Truck }
> = {
  SUPPLIER_DELAY: {
    topic: "Material fehlt",
    intro:
      "Stahlstangen kommen später. Die Werkstatt braucht sie für bestellte Metallrahmen.",
    question: "Welche Aufträge geraten dadurch in Verzug?",
    icon: Truck,
  },
  MACHINE_BREAKDOWN: {
    topic: "Maschine steht",
    intro:
      "Eine Bandsäge fällt aus. Die geplanten Schneidearbeiten müssen neu verteilt werden.",
    question: "Kann eine zweite Säge einen Auftrag übernehmen?",
    icon: Factory,
  },
  QUALITY_ISSUE: {
    topic: "Qualität stimmt nicht",
    intro:
      "Bohrungen in Montageplatten sind zu groß. Die Platten sind für anstehende Lieferungen vorgesehen.",
    question: "Welche Lieferungen müssen zurückgehalten werden?",
    icon: ShieldCheck,
  },
};

export function CaseOverview({
  scopeId,
  refresh,
  kpis,
  onRefresh,
}: ViewProps & { kpis: ReturnType<typeof useQuery<Kpis>> }) {
  const query = useQuery<{ items: Incident[]; total: number }>(
    scoped("/api/incidents", scopeId, { limit: 100 }),
    refresh,
  );
  const incidents = [...(query.data?.items || [])].sort(
    (a, b) =>
      Object.keys(caseCopy).indexOf(a.incident_type) -
      Object.keys(caseCopy).indexOf(b.incident_type),
  );
  return (
    <div className="case-home">
      <section className="purpose-hero">
        <div>
          <span className="eyebrow">
            PRODUKTIONSPLANUNG VERSTÄNDLICH MACHEN
          </span>
          <h1>Eine Störung. Welche Aufträge sind betroffen?</h1>
          <p>
            In einer Metallwerkstatt fehlt Material, eine Maschine steht still
            oder Teile sind fehlerhaft. Dieses Projekt zeigt, was das für die
            Aufträge bedeutet — und bereitet den nächsten Schritt zur
            Entscheidung vor.
          </p>
          <a className="text-link" href="#/about">
            Was macht die KI dabei? <ArrowRight size={17} />
          </a>
        </div>
        <div className="purpose-flow" aria-label="Ablauf">
          {[
            ["01", "Meldung verstehen", "Was ist passiert?"],
            ["02", "Auswirkung prüfen", "Was ist betroffen?"],
            ["03", "Reaktion vorbereiten", "Was können wir tun?"],
            ["04", "Mensch entscheidet", "Was wird freigegeben?"],
          ].map(([n, title, sub]) => (
            <div key={n}>
              <span>{n}</span>
              <p>
                <strong>{title}</strong>
                <small>{sub}</small>
              </p>
            </div>
          ))}
        </div>
      </section>
      <div className="case-section-heading">
        <div>
          <h2>Einen Fall Schritt für Schritt ansehen</h2>
          <p>
            Drei erfundene Situationen aus einer Metallwerkstatt. Jeder Fall
            erklärt Meldung, Folgen und Entscheidung.
          </p>
        </div>
        <span className="quiet-tag">Gespeicherte Beispielfälle</span>
      </div>
      {query.error && <ErrorBox error={query.error} retry={onRefresh} />}
      {query.loading && !query.data ? (
        <Loading />
      ) : !incidents.length ? (
        <Empty title="Noch kein Fall vorhanden">
          Eine neue Meldung kann über die Team-Funktionen angelegt werden.
        </Empty>
      ) : (
        <div className="case-grid">
          {incidents.map((item, index) => {
            const copy = caseCopy[item.incident_type];
            const Icon = copy?.icon || Factory;
            return (
              <article
                className={`case-card case-${item.incident_type.toLowerCase()}`}
                key={item.id}
              >
                <div className="case-card-top">
                  <span className="case-icon">
                    <Icon size={25} />
                  </span>
                  <small>FALL {String(index + 1).padStart(2, "0")}</small>
                </div>
                <span className="eyebrow">{copy?.topic || "Neue Meldung"}</span>
                <h3>{incidentTitle(item)}</h3>
                <p>
                  {copy?.intro ||
                    "Die Meldung wurde mit den vorhandenen Auftragsdaten abgeglichen."}
                </p>
                <div className="case-question">
                  {copy?.question || "Welche Reaktion ist jetzt sinnvoll?"}
                </div>
                <div className="case-card-bottom">
                  <Badge value={item.status} />
                  <a className="button primary" href={`#/incidents/${item.id}`}>
                    Fall ansehen <ArrowRight size={16} />
                  </a>
                </div>
              </article>
            );
          })}
        </div>
      )}
      {query.data && query.data.total > incidents.length && (
        <p className="muted">
          Die ersten {incidents.length} von {query.data.total} Fällen werden
          angezeigt. Alle Fälle stehen im <a href="#/register">Fallregister</a>.
        </p>
      )}
      <section className="next-entry">
        <Mail size={25} />
        <div>
          <h2>Und wo kommt Gemini ins Spiel?</h2>
          <p>
            Bei einer frei formulierten Lieferanten-Mail: Die KI liest die
            gemeldeten Änderungen heraus. Die Auftragsfolgen berechnet
            anschließend das System aus den Betriebsdaten.
          </p>
        </div>
        <a className="button subtle" href="#/mail">
          Mail-Auswertung ansehen <ArrowRight size={16} />
        </a>
      </section>
      <div className="home-foot">
        <span>
          {kpis.data
            ? `${kpis.data.pending_approvals} Entscheidungen offen`
            : "Entscheidungen werden geladen"}{" "}
          · Alle Daten sind erfunden.
        </span>
        <a href="#/register">Fallregister mit Kennzahlen</a>
      </div>
    </div>
  );
}
