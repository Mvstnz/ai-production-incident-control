import { useState, type FormEvent, type ReactNode } from "react";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  FileText,
  GitBranch,
  ShieldAlert,
} from "lucide-react";
import {
  api,
  canDecide,
  date,
  label,
  money,
  record,
  rows,
  scoped,
  string,
  text,
  type Detail,
  type RecordData,
  type Run,
} from "./api";
import {
  Badge,
  Empty,
  ErrorBox,
  Fields,
  Json,
  Loading,
  Modal,
  Section,
  useQuery,
} from "./ui";
import type { ViewProps } from "./App";

function count(value: unknown) {
  return Array.isArray(value) ? value.length : "—";
}
const riskFactorLabels: Record<string, string> = {
  disruption: "Disruption",
  value: "Affected open-order value",
  urgency: "Time to first demand",
  resource_gap: "Resource gap",
  alternative: "Qualified alternative",
  strategic_customer: "Strategic customer affected",
};
function riskFactorValue(key: string, value: unknown): string {
  if (value === null || value === undefined) return "Not established";
  if (key === "alternative" || key === "strategic_customer") {
    return value === true ? "Yes" : value === false ? "No" : "Not established";
  }
  if (!["disruption", "value", "urgency", "resource_gap"].includes(key))
    return text(value);
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "Not established";
  const number = (quantity: number) =>
    new Intl.NumberFormat("en-GB", { maximumFractionDigits: 1 }).format(
      quantity,
    );
  if (key === "value")
    return new Intl.NumberFormat("en-GB", {
      style: "currency",
      currency: "EUR",
      currencyDisplay: "code",
      maximumFractionDigits: 0,
    }).format(numeric / 100);
  if (key === "resource_gap") return `${number(numeric * 100)}%`;
  if (key === "urgency") return `${number(numeric)} h`;
  return `${number(numeric)} ${numeric === 1 ? "day" : "days"}`;
}
function QualityRelease({
  incident,
  scopeId,
  onRefresh,
}: {
  incident: Detail;
  scopeId: string;
  onRefresh: () => void;
}) {
  const [open, setOpen] = useState(false),
    [evidence, setEvidence] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<Error | null>(null),
    [notice, setNotice] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const result = await api<RecordData>(
        `/api/incidents/${incident.id}/quality-release-plan`,
        {
          scope_id: scopeId,
          expected_revision: incident.revision,
          disposition_evidence: evidence,
        },
      );
      setNotice(
        `Release plan version ${text(result.plan_version)} recorded. Review and approve the separate Quality request in the inbox before any release can execute.`,
      );
      setOpen(false);
      setEvidence("");
      onRefresh();
    } catch (err) {
      setError(err as Error);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Section
      title="Separate Quality disposition"
      subtitle="A succeeded block does not authorize its release"
    >
      <div className="panel-padding">
        {notice && (
          <div className="notice success" role="status">
            {notice}
          </div>
        )}
        <p className="muted">
          Record the verified synthetic disposition evidence to propose a
          separate release plan. The release requires its own Quality approval
          and provider receipt.
        </p>
        <button
          className="button subtle"
          onClick={() => {
            setOpen(true);
            setError(null);
          }}
        >
          Propose Quality release
        </button>
      </div>
      {open && (
        <Modal
          title="Propose a separate Quality release"
          onClose={() => setOpen(false)}
        >
          <form onSubmit={submit}>
            <div className="modal-content">
              <div className="notice">
                <ShieldAlert size={18} />
                <p>
                  This creates a release proposal. It does not approve the
                  release, change shipment status or resolve the incident.
                </p>
              </div>
              <Fields
                data={{
                  incident: incident.number,
                  incident_revision: incident.revision,
                }}
              />
              <label>
                Verified disposition evidence
                <textarea
                  required
                  minLength={10}
                  maxLength={2000}
                  rows={5}
                  value={evidence}
                  onChange={(event) => setEvidence(event.target.value)}
                  placeholder="Document the synthetic inspection or disposition reference and why this lot may be released."
                />
              </label>
              {error && <ErrorBox error={error} />}
            </div>
            <footer className="modal-footer">
              <button
                type="button"
                className="button subtle"
                disabled={busy}
                onClick={() => setOpen(false)}
              >
                Cancel
              </button>
              <button
                className="button primary"
                disabled={busy || evidence.trim().length < 10}
              >
                {busy ? "Recording proposal…" : "Create release proposal"}
              </button>
            </footer>
          </form>
        </Modal>
      )}
    </Section>
  );
}
function EvidenceText({
  content,
  evidence,
}: {
  content: string;
  evidence: RecordData;
}) {
  const ranges = Object.values(evidence)
    .map(record)
    .map((item) => record(item.evidence))
    .filter(
      (item) =>
        item.source === "content_text" &&
        Number.isInteger(item.start) &&
        Number.isInteger(item.end) &&
        Number(item.start) >= 0 &&
        Number(item.end) <= content.length &&
        Number(item.end) > Number(item.start),
    )
    .map((item) => ({ start: Number(item.start), end: Number(item.end) }))
    .sort((a, b) => a.start - b.start);
  const merged: { start: number; end: number }[] = [];
  ranges.forEach((range) => {
    const previous = merged.at(-1);
    if (previous && range.start <= previous.end)
      previous.end = Math.max(previous.end, range.end);
    else merged.push({ ...range });
  });
  const pieces: ReactNode[] = [];
  let position = 0;
  merged.forEach((range, index) => {
    pieces.push(content.slice(position, range.start));
    pieces.push(
      <mark key={index}>{content.slice(range.start, range.end)}</mark>,
    );
    position = range.end;
  });
  pieces.push(content.slice(position));
  return <div className="source-text">{pieces}</div>;
}
export function IncidentDetail({
  scopeId,
  refresh,
  session,
  incidentId,
  onRefresh,
  onRun,
}: ViewProps & { incidentId: string; onRun: (run: Run) => Promise<void> }) {
  const query = useQuery<Detail>(
    scoped(`/api/incidents/${encodeURIComponent(incidentId)}`, scopeId),
    refresh,
  );
  const [tab, setTab] = useState("assessment"),
    [splitBusy, setSplitBusy] = useState(false),
    [error, setError] = useState<Error | null>(null);
  if (query.loading && !query.data)
    return <Loading>Loading the incident and its evidence…</Loading>;
  if (!query.data)
    return query.error ? (
      <ErrorBox error={query.error} retry={onRefresh} />
    ) : (
      <Empty title="Incident unavailable">
        This incident is not available in your current scope.
      </Empty>
    );
  const incident = query.data,
    impact = record(incident.impact),
    risk = record(incident.risk),
    whatIf = record(impact.what_if),
    hypothetical = record(whatIf.impact),
    hypotheticalRisk = record(whatIf.risk);
  const latest = incident.plans[0];
  async function confirmSplit() {
    setSplitBusy(true);
    setError(null);
    try {
      await onRun(
        await api<Run>("/api/demo/runs", {
          scope_id: scopeId,
          scenario: "supplier-split",
        }),
      );
    } catch (err) {
      setError(err as Error);
    } finally {
      setSplitBusy(false);
    }
  }
  return (
    <>
      <a className="back-link" href="#/overview">
        <ArrowLeft size={15} />
        Back to overview
      </a>
      {query.error && <ErrorBox error={query.error} retry={onRefresh} />}
      <div className="incident-heading">
        <div>
          <div className="incident-ref">
            <span>{incident.number}</span>
            <span>Revision {incident.revision}</span>
            <Badge value={incident.incident_type} />
          </div>
          <h2>{incident.title}</h2>
          <p>
            Updated {date(incident.updated_at)} Bangkok · Incident{" "}
            <code>{incident.id}</code>
          </p>
        </div>
        <div className="incident-heading-status">
          <Badge value={incident.status} />
          <a className="button primary" href="#/approvals">
            Review approvals
            <ArrowRight size={16} />
          </a>
        </div>
      </div>
      <div className="tabs" aria-label="Incident sections">
        {[
          ["assessment", "Assessment"],
          ["evidence", "Sources & revisions"],
          ["response", "Response & actions"],
          ["timeline", "Audit trail"],
        ].map(([key, title]) => (
          <button
            key={key}
            className={tab === key ? "active" : ""}
            aria-pressed={tab === key}
            onClick={() => setTab(key)}
          >
            {title}
          </button>
        ))}
      </div>
      {tab === "assessment" && (
        <>
          <div
            className={`data-quality ${impact.data_complete === true ? "verified" : "review"}`}
          >
            <span>
              {impact.data_complete === true ? (
                <CheckCircle2 size={19} />
              ) : (
                <ShieldAlert size={19} />
              )}
            </span>
            <div>
              <strong>
                {impact.data_complete === true
                  ? "Verified assessment"
                  : "Manual review / assessment pending"}
              </strong>
              <p>
                {impact.data_complete === true
                  ? `Consistent ERP snapshot · Revision ${text(impact.erp_revision)} · Method ${text(impact.method_version)}`
                  : Array.isArray(impact.review_reasons)
                    ? impact.review_reasons.map(string).join(" · ") ||
                      "Awaiting a complete, verified assessment."
                    : "Awaiting a complete, verified assessment."}
              </p>
            </div>
            <small>As of {date(impact.analysis_time)} Bangkok</small>
          </div>
          <div className="detail-grid">
            <div className="detail-main">
              <Section
                title="Operational impact"
                subtitle="Current confirmed plan after the incident"
              >
                <div className="impact-metrics">
                  <div>
                    <small>Required</small>
                    <strong>{text(impact.total_required)}</strong>
                  </div>
                  <div>
                    <small>Covered at need</small>
                    <strong>{text(impact.total_available)}</strong>
                  </div>
                  <div className="impact-shortage">
                    <small>Shortage at need</small>
                    <strong>{text(impact.total_shortage)}</strong>
                  </div>
                  <div>
                    <small>Affected open-order value</small>
                    <strong>
                      {money(impact.affected_open_order_value_cents)}
                    </strong>
                  </div>
                </div>
                <div className="impact-counts">
                  <span>
                    <b>{count(impact.reviewed_production_orders)}</b> production
                    orders reviewed
                  </span>
                  <span>
                    <b>{count(impact.affected_production_orders)}</b> affected
                    by this incident
                  </span>
                  <span>
                    <b>{count(impact.affected_sales_lines)}</b> at-risk sales
                    positions
                  </span>
                </div>
                <div className="panel-padding">
                  <p className="footnote">
                    {incident.incident_type === "MACHINE_BREAKDOWN"
                      ? "Resource quantities are capacity hours. An alternative is a proposal until a permitted rescheduling action succeeds."
                      : incident.incident_type === "QUALITY_ISSUE"
                        ? "The lot trace and verified inspection govern this assessment. A shipment block requires a separate Quality approval."
                        : "Resource quantities are material units. Proposed supply is excluded from the confirmed plan."}
                  </p>
                  <Fields
                    data={{
                      reviewed_production_orders:
                        impact.reviewed_production_orders,
                      affected_production_orders:
                        impact.affected_production_orders,
                      affected_sales_lines: impact.affected_sales_lines,
                    }}
                  />
                </div>
              </Section>
              <Section
                title="Before / after the incident"
                subtitle="The same ERP snapshot under the original and revised facts"
              >
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Production order</th>
                        <th>Need / operation</th>
                        <th className="numeric">Covered / required</th>
                        <th className="numeric">Gap</th>
                        <th>Original completion</th>
                        <th>Revised completion</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows(impact.projected).map((row, index) => {
                        const before = rows(impact.baseline)[index] || {};
                        return (
                          <tr
                            key={string(
                              row.requirement_id || row.operation_id || index,
                            )}
                          >
                            <td>
                              <strong>{text(row.production_order)}</strong>
                              <small className="block">
                                {row.affected === true
                                  ? "Affected"
                                  : "Reviewed"}
                                {row.already_late_in_baseline === true
                                  ? " · Already late before incident"
                                  : ""}
                              </small>
                            </td>
                            <td>
                              {row.need_at
                                ? date(row.need_at)
                                : text(row.operation_id)}
                            </td>
                            <td className="numeric">
                              {text(row.covered_at_need)} /{" "}
                              {text(
                                row.required_quantity ?? before.required_hours,
                              )}
                            </td>
                            <td className="numeric">
                              {text(
                                row.shortage_at_need ?? row.capacity_gap_hours,
                              )}
                            </td>
                            <td>{date(before.completion_at)}</td>
                            <td>{date(row.completion_at)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                {!rows(impact.projected).length && (
                  <div className="panel-padding">
                    <p className="muted">
                      No production allocation rows are stored for this
                      assessment.
                    </p>
                  </div>
                )}
                {impact.trace ? (
                  <div className="panel-padding">
                    <Json
                      title="Verified lot and shipment trace"
                      value={impact.trace}
                    />
                  </div>
                ) : null}
              </Section>
              {impact.what_if ? (
                <Section
                  title="Unconfirmed split scenario"
                  subtitle="Hypothetical only — excluded from current KPIs"
                >
                  <div className="comparison-grid">
                    <div>
                      <span className="eyebrow">CURRENT CONFIRMED PLAN</span>
                      <strong>
                        {text(impact.total_shortage)} <small>shortage</small>
                      </strong>
                      <p>
                        {count(impact.affected_production_orders)} affected
                        production orders
                      </p>
                      <b>{money(impact.affected_open_order_value_cents)}</b>
                      <span>
                        <Badge value={risk.severity} /> {text(risk.risk_score)}{" "}
                        / 100
                      </span>
                    </div>
                    <div className="hypothetical">
                      <span className="eyebrow">IF THE OFFER IS CONFIRMED</span>
                      <strong>
                        {text(hypothetical.total_shortage)}{" "}
                        <small>shortage</small>
                      </strong>
                      <p>
                        {count(hypothetical.affected_production_orders)}{" "}
                        affected production orders
                      </p>
                      <b>
                        {money(hypothetical.affected_open_order_value_cents)}
                      </b>
                      <span>
                        <Badge value={hypotheticalRisk.severity} />{" "}
                        {text(hypotheticalRisk.risk_score)} / 100
                      </span>
                    </div>
                  </div>
                  <div className="panel-padding">
                    <Json
                      title="Proposed quantities and availability"
                      value={impact.proposals}
                    />
                    <p className="footnote">
                      Confirming this synthetic scenario submits new facts
                      through n8n. It creates a revision and may supersede
                      existing approvals; it does not dispatch an action.
                    </p>
                    {error && <ErrorBox error={error} />}
                    <button
                      className="button subtle"
                      disabled={splitBusy || session.user.role === "viewer"}
                      onClick={() => void confirmSplit()}
                    >
                      <GitBranch size={16} />
                      {splitBusy
                        ? "Submitting revision…"
                        : "Run confirmed split revision"}
                    </button>
                    {session.user.role === "viewer" && (
                      <small className="block">
                        An operational role is required to revise this scope.
                      </small>
                    )}
                  </div>
                </Section>
              ) : null}
              {Array.isArray(impact.proposals) &&
              impact.proposals.length > 0 &&
              !impact.what_if ? (
                <Section title="Verified alternatives / proposals">
                  <div className="panel-padding">
                    <Json
                      value={impact.proposals}
                      title="Review proposal evidence and parameters"
                    />
                  </div>
                </Section>
              ) : null}
            </div>
            <aside className="detail-aside">
              <Section
                title="Risk assessment"
                subtitle={`Demo policy ${text(risk.policy_version)}`}
              >
                <div className="risk-score">
                  <strong>
                    {text(risk.risk_score)}
                    <small>/ 100</small>
                  </strong>
                  <Badge value={risk.severity} />
                </div>
                {risk.override_reason ? (
                  <div className="override-note">
                    <ShieldAlert size={17} />
                    <span>Hard override: {label(risk.override_reason)}</span>
                  </div>
                ) : null}
                <div className="risk-factors">
                  {Object.entries(record(risk.factor_details)).map(
                    ([key, value]) => {
                      const factor = record(value);
                      return (
                        <div key={key}>
                          <span>
                            <strong>
                              {riskFactorLabels[key] || label(key)}
                            </strong>
                            <small className="risk-value">
                              {riskFactorValue(key, factor.value)}
                            </small>
                            <details className="risk-provenance">
                              <summary>Source</summary>
                              <small>{text(factor.source)}</small>
                            </details>
                          </span>
                          <b>+{text(factor.points)}</b>
                        </div>
                      );
                    },
                  )}
                </div>
                <div className="panel-padding">
                  <p className="footnote">{text(risk.explanation)}</p>
                  {Array.isArray(risk.missing_factors) &&
                    risk.missing_factors.length > 0 && (
                      <p className="notice danger">
                        Missing: {risk.missing_factors.map(string).join(", ")}
                      </p>
                    )}
                </div>
              </Section>
              <Section
                title="Response summary"
                subtitle={
                  latest
                    ? label(latest.body.summary_mode)
                    : "Awaiting a stored plan"
                }
              >
                <div className="panel-padding">
                  <span className="badge simulated">
                    Simulated AI / template
                  </span>
                  <p className="summary-text">
                    {latest?.body.summary ||
                      "No response plan has been persisted yet."}
                  </p>
                  {latest && (
                    <>
                      <p className="footnote">
                        SOP references: {latest.body.sop_ids.join(", ")}
                      </p>
                      <small>
                        Plan version {latest.plan_version} · Incident revision{" "}
                        {latest.revision}
                      </small>
                    </>
                  )}
                </div>
              </Section>
              <div className="control-note">
                <ShieldAlert size={20} />
                <p>
                  A completed action moves the incident into monitoring.
                  Resolution still needs evidence that the operational issue is
                  addressed.
                </p>
              </div>
            </aside>
          </div>
        </>
      )}
      {tab === "evidence" && (
        <div className="detail-grid">
          <div className="detail-main">
            {incident.sources.map((source, index) => {
              const envelope = record(source.envelope),
                revision = incident.revisions.find(
                  (item) => item.revision === source.revision,
                ),
                evidence = record(revision?.evidence);
              return (
                <Section
                  key={string(source.id) || index}
                  title={string(envelope.subject) || `Source ${index + 1}`}
                  subtitle={`${label(source.source)} · Revision ${text(source.revision)}`}
                  action={<Badge value={source.status} />}
                >
                  <div className="panel-padding">
                    <Fields
                      data={{
                        from: envelope.sender,
                        received_at: date(source.received_at),
                        source_id: source.id,
                      }}
                    />
                    {envelope.content_text ? (
                      <EvidenceText
                        content={string(envelope.content_text)}
                        evidence={evidence}
                      />
                    ) : (
                      <Json
                        title="Structured intake payload"
                        value={envelope.payload}
                      />
                    )}
                    <p className="footnote">
                      Highlighted text is the recorded source evidence. Source
                      content is rendered as text and cannot execute
                      instructions.
                    </p>
                    <Json
                      title="Extracted fields and provenance"
                      value={evidence}
                    />
                  </div>
                </Section>
              );
            })}
            {!incident.sources.length && (
              <Empty title="No linked sources">
                Source records will appear after the incident is correlated.
              </Empty>
            )}
          </div>
          <aside className="detail-aside">
            <Section
              title="Revision history"
              subtitle="Immutable facts retained for audit"
            >
              <div className="panel-padding">
                {incident.revisions.map((revision, index) => (
                  <details
                    className="revision"
                    key={string(revision.revision) || index}
                    open={revision.revision === incident.revision}
                  >
                    <summary>
                      <GitBranch size={16} />
                      <strong>Revision {text(revision.revision)}</strong>
                      <small>{date(revision.created_at)}</small>
                    </summary>
                    <Fields data={record(revision.facts)} />
                    <Json
                      title="Stored evidence references"
                      value={revision.evidence}
                    />
                  </details>
                ))}
              </div>
            </Section>
            <Section title="Assessment provenance">
              <div className="panel-padding">
                <Fields
                  data={{
                    snapshot_id: impact.snapshot_id,
                    erp_revision: impact.erp_revision,
                    method_version: impact.method_version,
                    policy_version: risk.policy_version,
                    analysis_time: date(impact.analysis_time),
                    source_refs: impact.source_refs,
                  }}
                />
              </div>
            </Section>
          </aside>
        </div>
      )}
      {tab === "response" && (
        <>
          {incident.incident_type === "QUALITY_ISSUE" &&
            canDecide(session.user.role, "quality_manager") &&
            incident.actions.some(
              (action) =>
                action.action_type === "QUALITY_BLOCK" &&
                action.status === "SUCCEEDED",
            ) && (
              <QualityRelease
                incident={incident}
                scopeId={scopeId}
                onRefresh={onRefresh}
              />
            )}
          <Section
            title="Versioned response plans"
            subtitle="Exact stored content and parameters; history is retained"
          >
            <div className="panel-padding">
              {incident.plans.map((plan) => (
                <details
                  className="plan-history"
                  key={plan.id}
                  open={plan.id === latest?.id}
                >
                  <summary>
                    <FileText size={17} />
                    <strong>Plan version {plan.plan_version}</strong>
                    <Badge value={plan.status} />
                    <span>Incident revision {plan.revision}</span>
                  </summary>
                  <p>{plan.body.summary}</p>
                  <small className="hash">Hash {plan.plan_hash}</small>
                  {plan.body.actions.map((action, index) => (
                    <div className="payload-card" key={index}>
                      <h3>{label(action.action_type)}</h3>
                      <small>
                        {action.required_role
                          ? `Required role: ${label(action.required_role)}`
                          : action.action_type === "INTERNAL_TICKET"
                            ? "Internal action · no separate role approval"
                            : "Role not specified"}
                      </small>
                      <Fields data={action.payload} />
                    </div>
                  ))}
                </details>
              ))}
            </div>
            {!incident.plans.length && (
              <Empty title="No plan yet">
                A response plan appears after verification and impact
                assessment.
              </Empty>
            )}
          </Section>
          <Section
            title="Action outcomes"
            subtitle="Provider and workflow evidence from persisted action records"
          >
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Action</th>
                    <th>Status</th>
                    <th>Attempts</th>
                    <th>Provider reference</th>
                    <th>Workflow / execution</th>
                  </tr>
                </thead>
                <tbody>
                  {incident.actions.map((action, index) => (
                    <tr key={action.id || index}>
                      <td>{label(action.action_type)}</td>
                      <td>
                        <Badge value={action.status} />
                      </td>
                      <td>{text(action.attempts)}</td>
                      <td>
                        <code>{text(action.provider_id)}</code>
                      </td>
                      <td>
                        <code>
                          {text(action.workflow_id)} /{" "}
                          {text(action.execution_id)}
                        </code>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>
        </>
      )}
      {tab === "timeline" && (
        <Section
          title="Audit trail"
          subtitle="Append-only recorded events; no synthetic progress steps"
        >
          <ol className="timeline">
            {incident.timeline.map((item, index) => (
              <li key={string(item.id) || index}>
                <span className="timeline-dot" />
                <div>
                  <div className="timeline-title">
                    <strong>{label(item.event)}</strong>
                    <time>{date(item.created_at)} Bangkok</time>
                  </div>
                  <p>
                    Actor {text(item.actor)} · Object{" "}
                    <code>{text(item.object_id)}</code>
                  </p>
                  <Json title="Event details" value={item.data} />
                </div>
              </li>
            ))}
          </ol>
          {!incident.timeline.length && (
            <Empty title="No audit events yet">
              Persisted events will appear here as the workflow proceeds.
            </Empty>
          )}
        </Section>
      )}
    </>
  );
}
