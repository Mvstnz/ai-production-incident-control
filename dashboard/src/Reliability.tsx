import { useState, type FormEvent } from "react";
import {
  Activity,
  AlertTriangle,
  Clock3,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import {
  api,
  date,
  label,
  record,
  rows,
  scoped,
  string,
  text,
  type Action,
  type RecordData,
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

export function Reliability({
  scopeId,
  refresh,
  session,
  onRefresh,
}: ViewProps) {
  const system = useQuery<RecordData>(scoped("/api/system", scopeId), refresh),
    errors = useQuery<{ items: RecordData[] }>(
      scoped("/api/errors", scopeId),
      refresh,
    ),
    actions = useQuery<{ items: Action[] }>(
      scoped("/api/actions", scopeId),
      refresh,
    );
  const [retry, setRetry] = useState<RecordData | null>(null),
    [reason, setReason] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<Error | null>(null),
    [notice, setNotice] = useState("");
  const jobs = rows(system.data?.jobs),
    outbox = rows(system.data?.outbox),
    waits = rows(system.data?.wait_registrations),
    notifications = rows(system.data?.notifications),
    unknown =
      actions.data?.items.filter((item) => item.status === "UNKNOWN_OUTCOME") ||
      [];
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!retry) return;
    setBusy(true);
    setError(null);
    try {
      await api(`/api/errors/${string(retry.id)}/retry`, {
        scope_id: scopeId,
        reason,
      });
      setRetry(null);
      setReason("");
      setNotice(
        "The controlled retry was recorded with its original identifiers. Check the persisted job state below.",
      );
      onRefresh();
    } catch (err) {
      setError(err as Error);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      {system.error && <ErrorBox error={system.error} retry={onRefresh} />}
      <div className="reliability-strip">
        <span>
          <ShieldCheck size={18} />
          <b>Database</b>
          <Badge value={record(system.data?.health).database} />
        </span>
        <span>
          <Activity size={18} />
          <b>AI mode</b>
          {text(system.data?.ai_mode)}
        </span>
        <span>
          <Clock3 size={18} />
          <b>External actions</b>
          {system.data?.external_actions_enabled === false
            ? "Disabled"
            : system.data?.external_actions_enabled === true
              ? "Enabled"
              : "Unknown"}
        </span>
      </div>
      {unknown.length > 0 && (
        <div className="notice danger">
          <AlertTriangle size={19} />
          <div>
            <strong>
              {unknown.length} action outcome{unknown.length === 1 ? "" : "s"}{" "}
              require reconciliation
            </strong>
            <p>
              A provider may have accepted the action. Blind dispatch retries
              are disabled for unknown outcomes.
            </p>
            {unknown.map((action, index) => (
              <p key={action.id || index}>
                {label(action.action_type)} ·{" "}
                <code>{action.provider_id || action.id}</code>
              </p>
            ))}
          </div>
        </div>
      )}
      {notice && (
        <div className="notice success" role="status">
          {notice}
        </div>
      )}
      <Section
        title="Analysis jobs"
        subtitle="Actual n8n workflow and execution references are recorded by the workers"
        action={
          <span className="count-label">
            {system.data ? jobs.length : "—"} jobs
          </span>
        }
      >
        {system.loading && !system.data ? (
          <Loading />
        ) : !jobs.length ? (
          <Empty title="No analysis jobs">
            Start a scenario to observe a real workflow execution.
          </Empty>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Job / source</th>
                  <th>Status / step</th>
                  <th>Attempts</th>
                  <th>Next attempt</th>
                  <th>Workflow / execution</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job, index) => (
                  <tr key={string(job.id) || index}>
                    <td>
                      <code className="block">{text(job.id)}</code>
                      <small>Source {text(job.source_event_id)}</small>
                    </td>
                    <td>
                      <Badge value={job.status} />
                      <small className="block">{text(job.step)}</small>
                    </td>
                    <td>{text(job.attempts)}</td>
                    <td>{date(job.next_attempt_at)}</td>
                    <td>
                      <code className="block">{text(job.workflow_id)}</code>
                      <code>{text(job.execution_id)}</code>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Section>
      <div className="detail-grid">
        <div className="detail-main">
          <Section
            title="Waiting workflows"
            subtitle="Registered execution references; a wakeup is not an approval"
          >
            {waits.length ? (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Plan</th>
                      <th>Workflow / execution</th>
                      <th>Registered</th>
                    </tr>
                  </thead>
                  <tbody>
                    {waits.map((wait, index) => (
                      <tr key={string(wait.plan_id) || index}>
                        <td>
                          <code>{text(wait.plan_id)}</code>
                        </td>
                        <td>
                          <code>
                            {text(wait.workflow_id)} / {text(wait.execution_id)}
                          </code>
                        </td>
                        <td>{date(wait.registered_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="panel-padding">
                <p className="muted">
                  No workflow wait registrations are currently stored in this
                  scope.
                </p>
              </div>
            )}
          </Section>
          <Section
            title="Errors & dead letter queue"
            subtitle="Redacted errors, retry eligibility and preserved references"
          >
            {errors.error && (
              <div className="panel-padding">
                <ErrorBox error={errors.error} retry={onRefresh} />
              </div>
            )}
            {errors.loading && !errors.data ? (
              <Loading />
            ) : !errors.data?.items.length ? (
              <Empty title="No recorded errors">
                No workflow errors are stored for this scope.
              </Empty>
            ) : (
              <div className="error-list">
                {errors.data.items.map((item, index) => (
                  <article
                    className="error-card"
                    key={string(item.id) || index}
                  >
                    <header>
                      <Badge value={item.error_class} />
                      {item.dead_letter === true && (
                        <Badge value="DEAD_LETTER" />
                      )}
                      <time>{date(item.created_at)}</time>
                    </header>
                    <p>{text(item.message)}</p>
                    <Fields
                      data={{
                        job_id: item.job_id,
                        workflow_id: item.workflow_id,
                        execution_id: item.execution_id,
                        next_attempt_at: date(item.next_attempt_at),
                      }}
                    />
                    {session.user.role === "admin" &&
                    item.retryable === true &&
                    item.error_class !== "UNKNOWN_OUTCOME" ? (
                      <button
                        className="button subtle small"
                        onClick={() => {
                          setRetry(item);
                          setError(null);
                          setReason("");
                        }}
                      >
                        <RefreshCw size={14} />
                        Controlled retry
                      </button>
                    ) : (
                      <small>
                        {item.error_class === "UNKNOWN_OUTCOME"
                          ? "Reconcile the outcome before another dispatch."
                          : item.retryable === true
                            ? "An administrator can request a controlled retry."
                            : "This error is not eligible for an automatic retry."}
                      </small>
                    )}
                  </article>
                ))}
              </div>
            )}
          </Section>
        </div>
        <aside className="detail-aside">
          <Section
            title="Local sandbox notifications"
            subtitle="Recorded notices and escalations"
          >
            <div className="panel-padding">
              {notifications.length ? (
                notifications.map((notice, index) => (
                  <details className="receipt" key={string(notice.id) || index}>
                    <summary>{date(notice.created_at)} Bangkok</summary>
                    <Fields data={record(notice.body)} />
                  </details>
                ))
              ) : (
                <p className="muted">
                  No sandbox notifications have been recorded.
                </p>
              )}
            </div>
          </Section>
          <Section
            title="Transactional outbox"
            subtitle="Persisted delivery and wakeup work"
          >
            <div className="panel-padding">
              {outbox.length ? (
                <ul className="outbox-list">
                  {outbox.map((item, index) => (
                    <li key={index}>
                      <span>
                        {label(item.kind)}
                        <Badge value={item.status} />
                      </span>
                      <strong>{text(item.count)}</strong>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">No outbox records for this scope.</p>
              )}
            </div>
          </Section>
          <div className="control-note">
            <RefreshCw size={20} />
            <div>
              <strong>Controlled recovery</strong>
              <p>
                Retries retain the original job and action identities. Unknown
                write outcomes require evidence before another dispatch.
              </p>
              <p>The demo business clock and n8n runtime clock are separate.</p>
            </div>
          </div>
        </aside>
      </div>
      <Section
        title="Action receipts"
        subtitle="Recorded provider outcomes; a receipt does not establish incident resolution"
      >
        {actions.error && (
          <div className="panel-padding">
            <ErrorBox error={actions.error} retry={onRefresh} />
          </div>
        )}
        {actions.data?.items.length ? (
          <div className="panel-padding">
            {actions.data.items.map((action, index) => (
              <details className="receipt" key={action.id || index}>
                <summary>
                  <strong>{label(action.action_type)}</strong>
                  <Badge value={action.status} />
                  <span>Attempts {text(action.attempts)}</span>
                </summary>
                <Fields
                  data={{
                    action_id: action.id,
                    provider_id: action.provider_id,
                    workflow_id: action.workflow_id,
                    execution_id: action.execution_id,
                  }}
                />
                <Json title="Persisted result" value={action.result} />
              </details>
            ))}
          </div>
        ) : actions.loading ? (
          <Loading />
        ) : (
          <Empty title="No actions recorded">
            Action receipts appear after plans are created and executed.
          </Empty>
        )}
      </Section>
      {retry && (
        <Modal
          title="Request a controlled retry"
          onClose={() => setRetry(null)}
        >
          <form onSubmit={submit}>
            <div className="modal-content">
              <p>
                The server will check that this error is retryable. The existing
                job identity and attempt policy are retained.
              </p>
              <Fields
                data={{
                  error_id: retry.id,
                  job_id: retry.job_id,
                  error_class: retry.error_class,
                }}
              />
              <label>
                Reason for retry
                <textarea
                  required
                  rows={3}
                  maxLength={2000}
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                  placeholder="Describe what has changed or why a retry is appropriate."
                />
              </label>
              {error && <ErrorBox error={error} />}
            </div>
            <footer className="modal-footer">
              <button
                type="button"
                className="button subtle"
                disabled={busy}
                onClick={() => setRetry(null)}
              >
                Cancel
              </button>
              <button
                className="button primary"
                disabled={busy || !reason.trim()}
              >
                {busy ? "Recording retry…" : "Request retry"}
              </button>
            </footer>
          </form>
        </Modal>
      )}
    </>
  );
}
