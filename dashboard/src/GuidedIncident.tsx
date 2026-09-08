import { useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  ChevronDown,
  FileText,
  ShieldCheck,
} from "lucide-react";
import {
  date,
  incidentTitle,
  label,
  money,
  record,
  rows,
  scoped,
  string,
  type Detail,
  type Run,
} from "./api";
import { businessName, actionDescription } from "./presentation";
import { Badge, ErrorBox, Loading, useQuery } from "./ui";
import { IncidentDetail } from "./IncidentDetail";
import { actionName } from "./ActionDetails";
import type { ViewProps } from "./App";

const steps = ["Meldung", "Auswirkung", "Vorschlag", "Entscheidung"];
const quantity = (value: unknown) =>
  typeof value === "number" && Number.isFinite(value)
    ? value.toLocaleString("de-DE")
    : "—";

export function GuidedIncident(
  props: ViewProps & { incidentId: string; onRun: (run: Run) => Promise<void> },
) {
  const { scopeId, refresh, incidentId, onRefresh } = props;
  const query = useQuery<Detail>(
    scoped(`/api/incidents/${incidentId}`, scopeId),
    refresh,
  );
  const [step, setStep] = useState(0),
    [advanced, setAdvanced] = useState(false);
  if (query.error) return <ErrorBox error={query.error} retry={onRefresh} />;
  if (!query.data) return <Loading />;
  const d = query.data;
  const revision = d.revisions.find((r) => Number(r.revision) === d.revision);
  const facts = record(revision?.facts),
    impact = d.impact || {};
  const machine = d.incident_type === "MACHINE_BREAKDOWN",
    quality = d.incident_type === "QUALITY_ISSUE";
  const currentPlan = [...d.plans]
    .filter(
      (p) =>
        p.revision === d.revision &&
        !["SUPERSEDED", "EXPIRED"].includes(p.status),
    )
    .sort((a, b) => b.plan_version - a.plan_version)[0];
  const proposedActions =
    currentPlan?.body.actions.filter(
      (a) => a.action_type !== "INTERNAL_TICKET",
    ) || [];
  const approvals = d.approvals.filter((a) => a.plan_id === currentPlan?.id);
  const responsible =
    [...new Set(approvals.map((a) => label(a.required_role)))].join(", ") ||
    "Das zuständige Team";
  const currentActions = d.actions.filter(
    (a) => a.plan_id === currentPlan?.id && a.action_type !== "INTERNAL_TICKET",
  );
  const source = record(d.sources[0]?.envelope);
  const live =
    record(revision?.extraction_metadata).provider === "google-gemini";
  const projection = rows(impact.projected),
    trace = rows(impact.trace);
  const affected = Array.isArray(
    quality ? impact.affected_sales_lines : impact.affected_production_orders,
  )
    ? ((quality
        ? impact.affected_sales_lines
        : impact.affected_production_orders) as unknown[])
    : null;
  const complete = impact.data_complete === true;
  const emailFacts = rows(facts.confirmed_supply_schedule);
  function go(next: number) {
    setStep(next);
    document
      .getElementById("case-step-heading")
      ?.focus({ preventScroll: true });
    window.scrollTo(0, 0);
  }
  return (
    <>
      <a className="text-link back-link" href="#/overview">
        <ArrowLeft size={15} /> Alle Fälle
      </a>
      <header className="guided-heading">
        <div>
          <span className="eyebrow">{label(d.incident_type)}</span>
          <h1>{incidentTitle(d)}</h1>
        </div>
        <Badge value={d.status} />
      </header>
      <nav className="step-nav" aria-label="Schritte des Falls">
        {steps.map((name, i) => (
          <button
            key={name}
            aria-current={step === i ? "step" : undefined}
            className={step === i ? "current" : ""}
            onClick={() => go(i)}
          >
            <span>{i + 1}</span>
            {name}
            <ArrowRight size={15} />
          </button>
        ))}
      </nav>
      <section className="guide-panel" aria-labelledby="case-step-heading">
        <div className="guide-step-label">SCHRITT {step + 1} VON 4</div>
        <h2 id="case-step-heading" tabIndex={-1}>
          {
            [
              "Was ist passiert?",
              "Was bedeutet das für die Aufträge?",
              "Was können wir jetzt tun?",
              "Wer entscheidet — und was passiert danach?",
            ][step]
          }
        </h2>
        {step === 0 && (
          <>
            <p className="guide-lead">
              {machine
                ? `${businessName(facts.machine_id)} wurde als ausgefallen gemeldet. In dieser Zeit können die dafür eingeplanten Arbeiten nicht regulär stattfinden.`
                : quality
                  ? `Bei ${businessName(facts.material)} wurde ein Qualitätsmangel gemeldet. Vor der Auslieferung muss die betroffene Ware geprüft werden.`
                  : `Der Liefertermin für ${businessName(facts.material)} hat sich geändert. Jetzt muss geprüft werden, ob das Material für die anstehenden Aufträge reicht.`}
            </p>
            <div className="fact-sheet">
              <div>
                <FileText size={21} />
                <h3>Aus der Meldung übernommen</h3>
              </div>
              <dl className="simple-facts">
                {machine ? (
                  <>
                    <div>
                      <dt>Maschine</dt>
                      <dd>{businessName(facts.machine_id)}</dd>
                    </div>
                    <div>
                      <dt>Ausfall ab</dt>
                      <dd>{date(facts.outage_start_at)}</dd>
                    </div>
                    <div>
                      <dt>Voraussichtlich wieder verfügbar</dt>
                      <dd>{date(facts.outage_end_at)}</dd>
                    </div>
                  </>
                ) : quality ? (
                  <>
                    <div>
                      <dt>Betroffene Ware</dt>
                      <dd>{businessName(facts.lot_id)}</dd>
                    </div>
                    <div>
                      <dt>Gemeldete Menge</dt>
                      <dd>{quantity(facts.reported_quantity)} Stück</dd>
                    </div>
                    <div>
                      <dt>Prüfergebnis</dt>
                      <dd>
                        {facts.defect_type ===
                        "Mounting-plate holes measure 11 mm instead of the specified 10 mm"
                          ? "Bohrungen: 11 mm statt geforderter 10 mm"
                          : string(facts.defect_type)}
                      </dd>
                    </div>
                  </>
                ) : (
                  <>
                    <div>
                      <dt>Material</dt>
                      <dd>{businessName(facts.material)}</dd>
                    </div>
                    {emailFacts.map((s, i) => (
                      <div key={i}>
                        <dt>
                          Bestätigter Liefertermin
                          {emailFacts.length > 1 ? ` ${i + 1}` : ""}
                        </dt>
                        <dd>
                          {quantity(s.quantity)} Stück · {date(s.available_at)}
                        </dd>
                      </div>
                    ))}
                    {facts.proposed_partial && (
                      <div>
                        <dt>Zusätzlicher Vorschlag des Lieferanten</dt>
                        <dd>
                          {quantity(record(facts.proposed_partial).quantity)}{" "}
                          Stück früher · noch nicht bestätigt
                        </dd>
                      </div>
                    )}
                  </>
                )}
              </dl>
            </div>
            <p className="explanation-note">
              {live
                ? "Diese Mail wurde mit Gemini ausgewertet. Die übernommenen Angaben wurden anschließend gegen Textbelege und Betriebsdaten geprüft."
                : "Dieser gespeicherte Beispielfall verwendet vorbereitete Angaben. Beim Ansehen wird kein KI-Aufruf ausgelöst."}
            </p>
            <details className="original-message">
              <summary>Originalmeldung ansehen</summary>
              <pre>
                {string(source.content_text) ||
                  string(facts.reason) ||
                  "Die Meldung enthält strukturierte Betriebsdaten."}
              </pre>
            </details>
          </>
        )}
        {step === 1 && (
          <>
            <p className="guide-lead">
              {quality
                ? "Die Prüfung verfolgt die fehlerhafte Charge bis zu den geplanten Lieferungen."
                : machine
                  ? "Die Prüfung vergleicht die geplanten Schneidearbeiten mit dem Ausfall und den verfügbaren Maschinenzeiten."
                  : "Die Prüfung vergleicht Materialbedarf, Lagerbestand und bestätigte Lieferungen für jeden Auftrag zum benötigten Termin."}
            </p>
            {!complete ? (
              <div className="notice">
                <p>
                  Die Berechnung ist noch nicht vollständig. Fehlende Werte sind
                  kein Beleg dafür, dass keine Aufträge betroffen sind.
                </p>
              </div>
            ) : null}
            <div className="impact-trio">
              <div>
                <strong>{affected === null ? "—" : affected.length}</strong>
                <span>
                  {quality
                    ? "betroffene Lieferpositionen"
                    : "betroffene Produktionsaufträge"}
                </span>
              </div>
              <div>
                <strong>
                  {quantity(impact.total_shortage)}
                  <small> {machine ? "Std." : "Stück"}</small>
                </strong>
                <span>
                  {machine
                    ? "ungedeckte Maschinenzeit"
                    : quality
                      ? "fehlerhafte Teile"
                      : "Material fehlt zum Bedarfstermin"}
                </span>
              </div>
              <div>
                <strong>{money(d.affected_open_order_value_cents)}</strong>
                <span>Wert betroffener offener Aufträge</span>
              </div>
            </div>
            <p className="explanation-note">
              Der Auftragswert zeigt, welche Bestellungen betroffen sind. Er ist
              keine Prognose für einen Umsatzverlust.
            </p>
            <div className="readable-table">
              <table>
                <caption>
                  {quality
                    ? "Betroffene Lieferungen"
                    : "Geprüfte Produktionsaufträge"}
                </caption>
                <thead>
                  <tr>
                    <th>{quality ? "Lieferung" : "Auftrag"}</th>
                    <th>{quality ? "Fehlerhafte Menge" : "Ergebnis"}</th>
                    <th>
                      {quality
                        ? "Lieferstatus"
                        : machine
                          ? "Ungedeckte Zeit"
                          : "Fehlmenge"}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {quality
                    ? trace.map((r, i) => (
                        <tr key={i}>
                          <td>{businessName(r.sales_line)}</td>
                          <td>{quantity(r.quantity)} Stück</td>
                          <td>
                            {r.shipment_status === "PENDING"
                              ? "Noch nicht versendet"
                              : label(r.shipment_status)}
                          </td>
                        </tr>
                      ))
                    : projection.map((r, i) => {
                        const isAffected = affected?.includes(
                          r.production_order,
                        );
                        return (
                          <tr key={i}>
                            <td>{businessName(r.production_order)}</td>
                            <td>
                              <span
                                className={
                                  isAffected ? "impact-affected" : "impact-ok"
                                }
                              >
                                {isAffected
                                  ? "Betroffen"
                                  : complete
                                    ? "Nicht betroffen"
                                    : "Noch offen"}
                              </span>
                            </td>
                            <td>
                              {quantity(
                                machine
                                  ? r.capacity_gap_hours
                                  : r.shortage_at_need,
                              )}{" "}
                              {machine ? "Std." : "Stück"}
                            </td>
                          </tr>
                        );
                      })}
                </tbody>
              </table>
            </div>
            <div className="explanation-note">
              <ShieldCheck size={17} /> Diese Ergebnisse stammen aus der
              gespeicherten Auftragsberechnung. Gemini berechnet diese Zahlen
              nicht.
            </div>
          </>
        )}
        {step === 2 && (
          <>
            <p className="guide-lead">
              {proposedActions.length
                ? "Aus der Prüfung wurde die folgende Reaktion vorbereitet. Ein Vorschlag allein verändert noch keinen Auftrag und keine Lieferung."
                : "Für den aktuellen Stand liegt noch keine ausführbare Reaktion vor. Die Meldung muss zunächst vollständig geprüft werden."}
            </p>
            {proposedActions.map((a, i) => (
              <article className="proposal-explained" key={i}>
                <span className="case-icon">
                  <Check size={23} />
                </span>
                <div>
                  <span className="eyebrow">VORBEREITETE REAKTION</span>
                  <h3>{actionName(a)}</h3>
                  <p>{actionDescription(a)}</p>
                  {a.action_type === "RESCHEDULE" && (
                    <p>
                      <b>Zeitraum:</b> {date(a.payload.start_at)} bis{" "}
                      {date(a.payload.end_at)}
                    </p>
                  )}
                  <p className="muted">
                    Zuständig:{" "}
                    {label(a.required_role || approvals[0]?.required_role)}
                  </p>
                </div>
              </article>
            ))}
            {!machine && !quality && record(impact.what_if).impact && (
              <div className="conditional-note">
                <h3>Wenn die vorgeschlagene Teillieferung bestätigt wird</h3>
                <p>
                  Die Fehlmenge würde laut gespeicherter Vergleichsrechnung auf{" "}
                  <b>
                    {quantity(
                      record(record(impact.what_if).impact).total_shortage,
                    )}{" "}
                    Stück
                  </b>{" "}
                  sinken. Die frühere Lieferung ist bislang ein Vorschlag und
                  wird in der aktuellen Berechnung noch nicht als verfügbar
                  gezählt.
                </p>
              </div>
            )}
            {machine &&
              proposedActions.some((a) => a.action_type === "RESCHEDULE") && (
                <p className="explanation-note">
                  Die Umplanung gilt für den genannten Schneideauftrag. Weitere
                  Kapazitätslücken brauchen eine eigene Lösung. Der
                  vorgeschlagene Zeitraum ist noch keine Reservierung.
                </p>
              )}
          </>
        )}
        {step === 3 && (
          <>
            <p className="guide-lead">
              Die zuständige Person prüft den genauen Inhalt und entscheidet:
              freigeben, ändern oder ablehnen. Erst eine gültige Freigabe
              erlaubt die zugehörige Aktion.
            </p>
            <div className="decision-sequence">
              <div>
                <span>1</span>
                <h3>Prüfen</h3>
                <p>
                  <b>{responsible}:</b>{" "}
                  {quality
                    ? "Die betroffene Ware und die Lieferungen prüfen."
                    : machine
                      ? "Maschine, Auftrag und Zeitraum prüfen."
                      : "Empfänger und genauen Nachrichtentext prüfen."}
                </p>
              </div>
              <div>
                <span>2</span>
                <h3>Entscheiden</h3>
                <p>
                  Eine Freigabe gilt genau für die geprüfte Version. Änderungen
                  brauchen eine neue Entscheidung.
                </p>
              </div>
              <div>
                <span>3</span>
                <h3>Ergebnis nachverfolgen</h3>
                <p>
                  n8n stößt die freigegebene Aktion an. Das System speichert, ob
                  sie erfolgreich war oder geprüft werden muss.
                </p>
              </div>
            </div>
            <div className="decision-status">
              <div>
                <h3>Gespeicherter Stand</h3>
                {approvals.length ? (
                  approvals.map((a) => (
                    <p key={a.id}>
                      {label(a.required_role)} <Badge value={a.status} />
                    </p>
                  ))
                ) : (
                  <p>Aktuell liegt keine passende Freigabeanfrage vor.</p>
                )}
                {currentActions.map((a, i) => (
                  <p key={a.id || i}>
                    {actionName(a)} <Badge value={a.status} />
                  </p>
                ))}
              </div>
              <a className="button primary" href={`#/approvals/${d.id}`}>
                Entscheidung ansehen <ArrowRight size={17} />
              </a>
            </div>
            <p className="explanation-note">
              {props.session.user.role === "viewer"
                ? "Du bist als Besucher hier und kannst den Ablauf ansehen. Entscheidungen erfordern einen Team-Zugang. "
                : ""}
              Dieses Portfolio arbeitet mit erfundenen Betriebsdaten.
              Lieferanten-Mails werden als Ergebnis gespeichert und nicht an
              echte Empfänger verschickt.
            </p>
          </>
        )}
        <footer className="guide-controls">
          <button
            className="button subtle"
            disabled={step === 0}
            onClick={() => go(step - 1)}
          >
            <ArrowLeft size={16} /> Zurück
          </button>
          <span>Schritt {step + 1} / 4 · reine Ansicht</span>
          {step < 3 ? (
            <button className="button primary" onClick={() => go(step + 1)}>
              Weiter: {steps[step + 1]} <ArrowRight size={16} />
            </button>
          ) : (
            <a className="button subtle" href="#/overview">
              Anderen Fall ansehen <ArrowRight size={16} />
            </a>
          )}
        </footer>
      </section>
      <button
        className="advanced-toggle"
        aria-expanded={advanced}
        onClick={() => setAdvanced(!advanced)}
      >
        <ChevronDown size={17} /> Details für Fachprüfung und Technik{" "}
        {advanced ? "schließen" : "öffnen"}
      </button>
      {advanced && (
        <div className="advanced-area">
          <p className="explanation-note">
            Vollständige gespeicherte Berechnungen, Revisionen und technische
            Nachweise. Originalinhalte können auf Englisch vorliegen.
          </p>
          <IncidentDetail {...props} />
        </div>
      )}
    </>
  );
}
