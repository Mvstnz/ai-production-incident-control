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
  Fields,
  Loading,
  Modal,
  Section,
  useQuery,
} from "./ui";
import type { ViewProps } from "./App";

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
      title={`${kind === "MODIFY" ? "Modify and request new approval" : kind === "APPROVE" ? "Approve exact response" : "Reject response"} · v${approval.plan_version}`}
      onClose={onClose}
      wide
    >
      {query.loading && !body ? (
        <Loading>Loading the exact stored response…</Loading>
      ) : (
        <form onSubmit={submit}>
          <div className="modal-content">
            {query.error && <ErrorBox error={query.error} />}{" "}
            {stale && (
              <div className="notice danger" role="alert">
                <LockKeyhole size={18} />
                <p>
                  This incident or plan has changed. Close this review and
                  refresh the inbox.
                </p>
              </div>
            )}
            <div className="approval-binding">
              <span>
                Incident revision <b>{approval.revision}</b>
              </span>
              <span>
                Plan version <b>{approval.plan_version}</b>
              </span>
              <span>
                Required role <b>{label(approval.required_role)}</b>
              </span>
              <span>
                Expires <b>{date(approval.expires_at)} Bangkok</b>
              </span>
              <code>{approval.plan_hash}</code>
            </div>
            {body && (
              <>
                {kind === "MODIFY" ? (
                  <label>
                    Response summary
                    <textarea
                      rows={3}
                      value={body.summary}
                      onChange={(event) =>
                        setBody({ ...body, summary: event.target.value })
                      }
                    />
                  </label>
                ) : (
                  <p className="summary-text">{body.summary}</p>
                )}
                {body.actions.map((action, index) => (
                  <section className="payload-card" key={index}>
                    <header>
                      <h3>{label(action.action_type)}</h3>
                      <small>
                        {action.required_role
                          ? label(action.required_role)
                          : action.action_type === "INTERNAL_TICKET"
                            ? "Internal action · no separate role approval"
                            : "Role not specified"}
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
                      <Fields data={action.payload} />
                    )}
                  </section>
                ))}
              </>
            )}
            {kind === "MODIFY" && (
              <div className="notice">
                <Pencil size={18} />
                <p>
                  Changes create a new immutable plan version and fresh approval
                  requests. This submission does not approve or dispatch the
                  revised response.
                </p>
              </div>
            )}
            <label>
              Decision rationale <span className="required">Required</span>
              <textarea
                rows={3}
                required
                minLength={1}
                maxLength={2000}
                value={comment}
                onChange={(event) => setComment(event.target.value)}
                placeholder="Record the business reason for this decision."
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
                  ? "I have reviewed the exact recipients, message content and action parameters above for this plan version."
                  : kind === "MODIFY"
                    ? "I have reviewed the revised content and understand that a new approval is required."
                    : "I reject this response plan. The operational incident will remain open."}
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
              Cancel
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
                ? "Recording decision…"
                : kind === "APPROVE"
                  ? "Approve this exact version"
                  : kind === "MODIFY"
                    ? "Create revised plan"
                    : "Reject this response"}
            </button>
          </footer>
        </form>
      )}
    </Modal>
  );
}
export function Approvals({ scopeId, refresh, session, onRefresh }: ViewProps) {
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
  const approvals =
    query.data?.items.filter(
      (item) => showHistory || item.status === "PENDING",
    ) || [];
  return (
    <>
      <div className="notice">
        <ShieldCheck size={19} />
        <p>
          Each decision binds a plan version and hash. The server rechecks your
          role, expiry and current incident revision before accepting it.
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
            Viewer access: inspect evidence and exact action content. A
            responsible operational role must submit decisions.
          </span>
        </div>
      )}
      <Section
        title="Requests for review"
        subtitle="All requests in the selected scope; role restrictions are shown on each request"
        action={
          <label className="checkbox-label compact">
            <input
              type="checkbox"
              checked={showHistory}
              onChange={(e) => setShowHistory(e.target.checked)}
            />
            Include history
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
              showHistory ? "No approval requests" : "No pending approvals"
            }
          >
            Approval requests appear here when a verified action plan requires a
            human decision.
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
                    <h3>Response plan · Version {approval.plan_version}</h3>
                    <p>
                      Incident revision {approval.revision} ·{" "}
                      <a href={`#/incidents/${approval.incident_id}`}>
                        Open incident
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
                    Due {date(approval.expires_at)} Bangkok
                  </span>
                </div>
                {approval.actions.map((action, index) => (
                  <details
                    className="approval-payload"
                    key={index}
                    open={approval.status === "PENDING"}
                  >
                    <summary>{label(action.action_type)}</summary>
                    <Fields data={action.payload} />
                  </details>
                ))}
                <p className="hash">
                  Plan hash <code>{approval.plan_hash}</code>
                </p>
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
                        Review & approve
                      </button>
                      <button
                        className="button subtle"
                        onClick={() =>
                          setSelected({ approval, kind: "MODIFY" })
                        }
                      >
                        <Pencil size={15} />
                        Modify
                      </button>
                      <button
                        className="button danger-text"
                        onClick={() =>
                          setSelected({ approval, kind: "REJECT" })
                        }
                      >
                        <X size={16} />
                        Reject
                      </button>
                    </>
                  ) : (
                    <span className="muted">
                      {approval.status === "PENDING"
                        ? `Requires ${label(approval.required_role)}. Your role: ${label(session.user.role)}.`
                        : `This request is ${label(approval.status).toLowerCase()} and cannot accept another decision.`}
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
                ? "A revised plan was recorded. Fresh approval is required."
                : `${label(selected.kind)} decision recorded. The persisted workflow state will refresh automatically.`,
            );
            onRefresh();
          }}
        />
      )}
    </>
  );
}
