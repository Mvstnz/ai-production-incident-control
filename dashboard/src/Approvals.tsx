import { useEffect, useState, type FormEvent } from "react";
import {
  ArrowRight,
  Check,
  ClipboardCheck,
  Clock3,
  LockKeyhole,
  Pencil,
  ShieldCheck,
  X,
} from "lucide-react";
import {
  api,
  canDecide,
  date,
  incidentTitle,
  label,
  scoped,
  type Approval,
  type Detail,
  type PlanBody,
  type RecordData,
} from "./api";
import {
  Badge,
  Empty,
  ErrorBox,
  Loading,
  Modal,
  Section,
  useQuery,
} from "./ui";
import type { ViewProps } from "./App";
import { ActionDetails, actionName } from "./ActionDetails";
import { readableSummary } from "./presentation";
import { Json } from "./ui";

function PayloadEditor({
  payload,
  onChange,
  index,
}: {
  payload: RecordData;
  onChange: (payload: RecordData) => void;
  index: number;
}) {
  return (
    <div className="payload-editor">
      {Object.entries(payload).map(([key, value]) => (
        <label key={key}>
          <span>{label(key)}</span>
          {typeof value === "boolean" ? (
            <select
              aria-label={`Action ${index + 1} ${label(key)}`}
              value={String(value)}
              onChange={(e) =>
                onChange({ ...payload, [key]: e.target.value === "true" })
              }
            >
              <option value="true">True</option>
              <option value="false">False</option>
            </select>
          ) : typeof value === "number" ? (
            <input
              aria-label={`Action ${index + 1} ${label(key)}`}
              type="number"
              value={value}
              onChange={(e) =>
                onChange({ ...payload, [key]: Number(e.target.value) })
              }
            />
          ) : value !== null && typeof value === "object" ? (
            <textarea
              aria-label={`Action ${index + 1} ${label(key)}`}
              rows={5}
              defaultValue={JSON.stringify(value, null, 2)}
              onBlur={(e) => {
                try {
                  onChange({ ...payload, [key]: JSON.parse(e.target.value) });
                  e.target.setCustomValidity("");
                } catch {
                  e.target.setCustomValidity(
                    "Enter valid structured parameters (JSON).",
                  );
                  e.target.reportValidity();
                }
              }}
            />
          ) : key === "body" || String(value).length > 120 ? (
            <textarea
              aria-label={`Action ${index + 1} ${label(key)}`}
              rows={6}
              value={String(value ?? "")}
              onChange={(e) => onChange({ ...payload, [key]: e.target.value })}
            />
          ) : (
            <input
              aria-label={`Action ${index + 1} ${label(key)}`}
              value={String(value ?? "")}
              onChange={(e) => onChange({ ...payload, [key]: e.target.value })}
            />
          )}
        </label>
      ))}
    </div>
  );
}
function DecisionDialog({
  approval,
  scopeId,
  kind,
  onClose,
  onDone,
}: {
  approval: Approval;
  scopeId: string;
  kind: "APPROVE" | "REJECT" | "MODIFY";
  onClose: () => void;
  onDone: () => void;
}) {
  const query = useQuery<Detail>(
    scoped(`/api/incidents/${approval.incident_id}`, scopeId),
    0,
    0,
  );
  const original = query.data?.plans.find(
    (plan) => plan.id === approval.plan_id,
  );
  const [body, setBody] = useState<PlanBody | null>(null),
    [comment, setComment] = useState(""),
    [confirmed, setConfirmed] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<Error | null>(null);
  useEffect(() => {
    if (original) setBody(structuredClone(original.body));
  }, [original]);
  const stale =
    !!query.data &&
    (!original ||
      original.plan_hash !== approval.plan_hash ||
      query.data.revision !== approval.revision ||
      ["SUPERSEDED", "EXPIRED"].includes(original.status));
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!confirmed || !body || stale) return;
    setBusy(true);
    setError(null);
    try {
      await api(`/api/approvals/${approval.id}/decision`, {
        scope_id: scopeId,
        decision: kind,
        expected_version: approval.plan_version,
        plan_hash: approval.plan_hash,
        comment,
        ...(kind === "MODIFY" ? { payload: body } : {}),
      });
      onDone();
      onClose();
    } catch (err) {
      setError(err as Error);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal
      title={`${kind === "MODIFY" ? "Ändern und erneut zur Freigabe vorlegen" : kind === "APPROVE" ? "Genauen Inhalt freigeben" : "Reaktion ablehnen"} · v${approval.plan_version}`}
      onClose={onClose}
      wide
    >
      {query.loading && !body ? (
        <Loading>Gespeicherter Inhalt wird geladen …</Loading>
      ) : (
        <form onSubmit={submit}>
          <div className="modal-content">
            {query.error && <ErrorBox error={query.error} />}{" "}
            {stale && (
              <div className="notice danger" role="alert">
                <LockKeyhole size={18} />
                <p>
                  Der Fall oder die Reaktion hat sich geändert. Schließe diese
                  Prüfung und lade die Entscheidungen neu.
                </p>
              </div>
            )}
            <div className="approval-binding">
              <span>
                Bewertungsstand <b>{approval.revision}</b>
              </span>
              <span>
                Version der Reaktion <b>{approval.plan_version}</b>
              </span>
              <span>
                Zuständig <b>{label(approval.required_role)}</b>
              </span>
              <span>
                Gültig bis <b>{date(approval.expires_at)} Berlin</b>
              </span>
              <Json
                title="Technische Referenz"
                value={{ plan_hash: approval.plan_hash }}
              />
            </div>
            {body && (
              <>
                {kind === "MODIFY" ? (
                  <label>
                    Zusammenfassung
                    <textarea
                      rows={3}
                      value={body.summary}
                      onChange={(event) =>
                        setBody({ ...body, summary: event.target.value })
                      }
                    />
                  </label>
                ) : (
                  <p className="summary-text">
                    {readableSummary(body.summary)}
                  </p>
                )}
                {body.actions.map((action, index) => (
                  <section className="payload-card" key={index}>
                    <header>
                      <h3>{actionName(action)}</h3>
                      <small>
                        {action.required_role
                          ? label(action.required_role)
                          : action.action_type === "INTERNAL_TICKET"
                            ? "Interne Information · keine gesonderte Rollenfreigabe"
                            : "Zuständigkeit fehlt"}
                      </small>
                    </header>
                    {kind === "MODIFY" ? (
                      <PayloadEditor
                        payload={action.payload}
                        index={index}
                        onChange={(payload) =>
                          setBody({
                            ...body,
                            actions: body.actions.map((item, i) =>
                              i === index ? { ...item, payload } : item,
                            ),
                          })
                        }
                      />
                    ) : (
                      <ActionDetails action={action} />
                    )}
                  </section>
                ))}
              </>
            )}
            {kind === "MODIFY" && (
              <div className="notice">
                <Pencil size={18} />
                <p>
                  Änderungen erzeugen eine neue Version mit neuen
                  Freigabeanfragen. Das Speichern führt die geänderte Reaktion
                  noch nicht aus.
                </p>
              </div>
            )}
            <label>
              Begründung <span className="required">Pflichtfeld</span>
              <textarea
                rows={3}
                required
                minLength={1}
                maxLength={2000}
                value={comment}
                onChange={(event) => setComment(event.target.value)}
                placeholder="Warum ist diese Entscheidung fachlich sinnvoll?"
              />
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                required
                checked={confirmed}
                onChange={(event) => setConfirmed(event.target.checked)}
              />
              <span>
                {kind === "APPROVE"
                  ? "Ich habe Empfänger, genauen Nachrichtentext und Aktionsparameter dieser Version geprüft."
                  : kind === "MODIFY"
                    ? "Ich habe den geänderten Inhalt geprüft. Eine neue Freigabe ist erforderlich."
                    : "Ich lehne diese Reaktion ab. Der Fall bleibt offen."}
              </span>
            </label>
            {error && <ErrorBox error={error} />}
          </div>
          <footer className="modal-footer">
            <button
              type="button"
              className="button subtle"
              disabled={busy}
              onClick={onClose}
            >
              Abbrechen
            </button>
            <button
              className={`button ${kind === "REJECT" ? "destructive" : "primary"}`}
              disabled={
                busy ||
                !body ||
                stale ||
                !confirmed ||
                !comment.trim() ||
                (kind === "MODIFY" &&
                  JSON.stringify(body) === JSON.stringify(original?.body))
              }
            >
              {busy
                ? "Entscheidung wird gespeichert …"
                : kind === "APPROVE"
                  ? "Diese Version freigeben"
                  : kind === "MODIFY"
                    ? "Geänderte Version speichern"
                    : "Diese Reaktion ablehnen"}
            </button>
          </footer>
        </form>
      )}
    </Modal>
  );
}
export function Approvals({
  scopeId,
  refresh,
  session,
  onRefresh,
  incidentId,
}: ViewProps & { incidentId?: string }) {
  const query = useQuery<{ items: Approval[] }>(
    scoped("/api/approvals", scopeId),
    refresh,
  );
  const [showHistory, setShowHistory] = useState(false),
    [selected, setSelected] = useState<{
      approval: Approval;
      kind: "APPROVE" | "REJECT" | "MODIFY";
    } | null>(null),
    [notice, setNotice] = useState("");
  const latestVersion = Math.max(
    0,
    ...(query.data?.items
      .filter((item) => item.incident_id === incidentId)
      .map((item) => item.plan_version) || []),
  );
  const approvals =
    query.data?.items.filter(
      (item) =>
        (!incidentId || item.incident_id === incidentId) &&
        (showHistory ||
          (incidentId
            ? item.plan_version === latestVersion
            : item.status === "PENDING")),
    ) || [];
  return (
    <>
      {incidentId && (
        <a className="text-link back-link" href={`#/incidents/${incidentId}`}>
          Zur Erklärung dieses Falls
        </a>
      )}
      <div className="notice">
        <ShieldCheck size={19} />
        <p>
          Prüfe Aktion, Zeitpunkt und genauen Nachrichtentext vor der Freigabe.
          Änderungen brauchen eine neue Entscheidung.
        </p>
      </div>
      {notice && (
        <div className="notice success" role="status">
          <Check size={18} />
          <p>{notice}</p>
        </div>
      )}
      {session.user.role === "viewer" && (
        <div className="access-note">
          <LockKeyhole size={16} />
          <span>
            Du bist als Besucher hier. Du kannst die vorgeschlagenen Aktionen
            ansehen. Freigeben, ändern oder ablehnen kann das zuständige Team.
          </span>
        </div>
      )}
      <Section
        title="Vorbereitete Entscheidungen"
        subtitle="Aktionen zur Prüfung durch die zuständige Person"
        action={
          <label className="checkbox-label compact">
            <input
              type="checkbox"
              checked={showHistory}
              onChange={(e) => setShowHistory(e.target.checked)}
            />
            Bisherige Entscheidungen anzeigen
          </label>
        }
      >
        {query.error && (
          <div className="panel-padding">
            <ErrorBox error={query.error} retry={onRefresh} />
          </div>
        )}
        {query.loading && !query.data ? (
          <Loading />
        ) : !approvals.length ? (
          <Empty
            title={
              showHistory
                ? "Keine Entscheidungen vorhanden"
                : "Keine offenen Entscheidungen"
            }
          >
            Sobald eine geprüfte Reaktion eine Freigabe braucht, erscheint sie
            hier.
          </Empty>
        ) : (
          <div className="approval-list">
            {approvals.map((approval) => (
              <article className="approval-card" key={approval.id}>
                <header>
                  <span className="approval-icon">
                    <ClipboardCheck size={21} />
                  </span>
                  <div>
                    <h3>
                      {incidentTitle({
                        title:
                          approval.incident_title || "Vorbereitete Reaktion",
                      })}
                    </h3>
                    <p>
                      Bewertungsstand {approval.revision} ·{" "}
                      <a href={`#/incidents/${approval.incident_id}`}>
                        Fall verstehen
                        <ArrowRight size={13} />
                      </a>
                    </p>
                  </div>
                  <Badge value={approval.status} />
                </header>
                <div className="approval-meta">
                  <span>
                    <ShieldCheck size={15} />
                    {label(approval.required_role)}
                  </span>
                  <span>
                    <Clock3 size={15} />
                    Frist: {date(approval.expires_at)} Berlin
                  </span>
                </div>
                {approval.actions.map((action, index) => (
                  <details className="approval-payload" key={index}>
                    <summary>{actionName(action)}</summary>
                    <ActionDetails action={action} />
                  </details>
                ))}
                <Json
                  title="Technische Referenz"
                  value={{
                    plan_hash: approval.plan_hash,
                    plan_id: approval.plan_id,
                  }}
                />
                <footer>
                  {approval.status === "PENDING" &&
                  canDecide(session.user.role, approval.required_role) ? (
                    <>
                      <button
                        className="button primary"
                        onClick={() =>
                          setSelected({ approval, kind: "APPROVE" })
                        }
                      >
                        <Check size={16} />
                        Prüfen und freigeben
                      </button>
                      <button
                        className="button subtle"
                        onClick={() =>
                          setSelected({ approval, kind: "MODIFY" })
                        }
                      >
                        <Pencil size={15} />
                        Ändern
                      </button>
                      <button
                        className="button danger-text"
                        onClick={() =>
                          setSelected({ approval, kind: "REJECT" })
                        }
                      >
                        <X size={16} />
                        Ablehnen
                      </button>
                    </>
                  ) : (
                    <span className="muted">
                      {approval.status === "PENDING"
                        ? `Zuständig: ${label(approval.required_role)}. Dein Zugang: ${label(session.user.role)}.`
                        : `Stand: ${label(approval.status)}. Diese Anfrage ist bereits abgeschlossen.`}
                    </span>
                  )}
                </footer>
              </article>
            ))}
          </div>
        )}
      </Section>
      {selected && (
        <DecisionDialog
          key={selected.approval.id + selected.kind}
          approval={selected.approval}
          kind={selected.kind}
          scopeId={scopeId}
          onClose={() => setSelected(null)}
          onDone={() => {
            setNotice(
              selected.kind === "MODIFY"
                ? "Eine neue Version wurde gespeichert. Sie braucht eine neue Freigabe."
                : `${label(selected.kind)} wurde gespeichert. Der Verarbeitungsstand aktualisiert sich automatisch.`,
            );
            onRefresh();
          }}
        />
      )}
    </>
  );
}
