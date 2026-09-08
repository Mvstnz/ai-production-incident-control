import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import {
  Activity,
  ArrowRight,
  CheckCheck,
  ChevronRight,
  ClipboardCheck,
  Factory,
  LayoutDashboard,
  LogOut,
  MailSearch,
  Menu,
  Play,
  RefreshCw,
  ShieldCheck,
  Truck,
  X,
} from "lucide-react";
import {
  api,
  date,
  label,
  scoped,
  setCsrf,
  setDisplayTimezone,
  string,
  type Kpis,
  type RecordData,
  type Run,
  type Scenario,
  type Scope,
  type Session,
} from "./api";
import {
  Badge,
  Empty,
  ErrorBox,
  Loading,
  Json,
  Modal,
  useQuery,
  useRoute,
} from "./ui";
import { Overview } from "./Overview";
import { IncidentDetail } from "./IncidentDetail";
import { Approvals } from "./Approvals";
import { Reliability } from "./Reliability";
import { rememberScope, restoreScope } from "./scope-preference";
import { workspaceName } from "./presentation";

function Brand() {
  return (
    <a className="brand" href="#/overview" aria-label="APIC overview">
      <span className="brand-symbol">
        <Activity size={24} />
      </span>
      <span>
        <b>APIC</b>
        <small>Incident control</small>
      </span>
    </a>
  );
}
function Login({ onLogin }: { onLogin: (session: Session) => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const catalog = useQuery<{ public_demo_enabled: boolean }>(
    "/api/demo/catalog",
    0,
  );
  async function explore() {
    setBusy(true);
    setError(null);
    try {
      const session = await api<Session>("/api/auth/demo", {});
      setCsrf(session.csrf_token);
      onLogin(session);
    } catch (err) {
      setError(err as Error);
    } finally {
      setBusy(false);
    }
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true);
    setError(null);
    try {
      const session = await api<Session>("/api/auth/login", {
        username: form.get("username"),
        password: form.get("password"),
      });
      setCsrf(session.csrf_token);
      onLogin(session);
    } catch (err) {
      setError(err as Error);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="login-layout">
      <aside className="login-story">
        <Brand />
        <div>
          <span className="eyebrow">AI PRODUCTION INCIDENT CONTROL</span>
          <h1>
            Clarity when
            <br />
            operations change.
          </h1>
          <p>
            From an unstructured incident to a verified impact assessment, a
            human-approved response and an auditable action trail.
          </p>
          <div className="login-principles">
            <span>
              <CheckCheck size={18} /> Verified operational facts
            </span>
            <span>
              <ClipboardCheck size={18} /> Human-approved response
            </span>
            <span>
              <Activity size={18} /> Persisted execution evidence
            </span>
          </div>
        </div>
        <small>Portfolio examples using fictional business records</small>
      </aside>
      <main className="login-main">
        <div className="login-form">
          <span className="eyebrow">OPERATIONS WORKSPACE</span>
          <h2>Sign in to incident control</h2>
          <p>
            Follow a delayed delivery, a stopped saw and a quality inspection.
          </p>
          {catalog.data?.public_demo_enabled && (
            <button
              className="button primary full"
              disabled={busy}
              onClick={() => void explore()}
            >
              Explore the workspace <ArrowRight size={17} />
            </button>
          )}
          <form onSubmit={submit}>
            {error && <ErrorBox error={error} />}
            <label>
              Username
              <input
                name="username"
                autoComplete="username"
                required
                autoFocus
                maxLength={100}
                placeholder="Your username"
              />
            </label>
            <label>
              Password
              <input
                name="password"
                type="password"
                autoComplete="current-password"
                required
                maxLength={500}
                placeholder="Your generated password"
              />
            </label>
            <button className="button primary full" disabled={busy}>
              {busy ? "Signing in…" : "Open workspace"}
              <ArrowRight size={17} />
            </button>
          </form>
          <div className="login-note">
            <ShieldCheck size={20} />
            <p>
              Visitors can inspect the examples. Authorized team members can
              review and approve actions.
            </p>
          </div>
          <small>
            Public visitors can inspect the cases. Operational decisions require
            an authorized account.
          </small>
        </div>
      </main>
    </div>
  );
}

const scenarios: {
  id: Scenario;
  title: string;
  icon: typeof Truck;
  description: string;
  journey: string;
}[] = [
  {
    id: "supplier-delay",
    title: "Steel rods delayed",
    icon: Truck,
    description:
      "A delivery truck breaks down. Seventy-five steel rods arrive late. They are needed for four orders for welded mounting frames.",
    journey:
      "Verify the message → compare impact → review the supplier response",
  },
  {
    id: "machine-breakdown",
    title: "Band saw S-01 stops",
    icon: Factory,
    description:
      "A broken drive belt stops the band saw for two days. The second saw has six free hours and can take over one cutting job.",
    journey:
      "Verify the outage → inspect capacity → review the new cutting schedule",
  },
  {
    id: "quality-issue",
    title: "Mounting plates: holes too large",
    icon: ShieldCheck,
    description:
      "Forty-eight mounting plates have 11 mm holes instead of 10 mm. Two shipments are waiting; the affected batch needs a quality decision.",
    journey: "Verify the inspection → trace the lot → request Quality approval",
  },
];
function DemoDialog({
  onClose,
  onRun,
  readOnly,
  scopeId,
}: {
  onClose: () => void;
  onRun: (run: Run) => Promise<void>;
  readOnly: boolean;
  scopeId: string;
}) {
  const [busy, setBusy] = useState<Scenario | "custom-email" | null>(null),
    [error, setError] = useState<Error | null>(null),
    [subject, setSubject] = useState(""),
    [content, setContent] = useState(""),
    [liveEnabled, setLiveEnabled] = useState(false);
  useEffect(() => {
    const abort = new AbortController();
    void api<{
      live_ai_enabled: boolean;
      source_email: { subject: string; content_text: string };
    }>("/api/demo/catalog", undefined, abort.signal)
      .then((data) => {
        setSubject(data.source_email.subject);
        setContent(data.source_email.content_text);
        setLiveEnabled(data.live_ai_enabled);
      })
      .catch((err) => {
        if (!abort.signal.aborted) setError(err as Error);
      });
    return () => abort.abort();
  }, []);
  async function start(scenario: Scenario) {
    setBusy(scenario);
    setError(null);
    try {
      if (readOnly) {
        const kind = {
          "supplier-delay": "SUPPLIER_DELAY",
          "machine-breakdown": "MACHINE_BREAKDOWN",
          "quality-issue": "QUALITY_ISSUE",
        }[scenario as "supplier-delay" | "machine-breakdown" | "quality-issue"];
        const data = await api<{
          items: { id: string; incident_type: string }[];
        }>(scoped("/api/incidents", scopeId));
        const incident = data.items.find((item) => item.incident_type === kind);
        if (!incident)
          throw new Error(
            "This example is being prepared. Please try again shortly.",
          );
        window.location.hash = "/incidents/" + incident.id;
        onClose();
        return;
      }
      const run = await api<Run>("/api/demo/runs", { scenario });
      await onRun(run);
      onClose();
    } catch (err) {
      setError(err as Error);
    } finally {
      setBusy(null);
    }
  }
  async function startCustom(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy("custom-email");
    setError(null);
    try {
      const run = await api<Run>("/api/demo/custom-email", {
        subject,
        content_text: content,
      });
      await onRun(run);
      onClose();
    } catch (err) {
      setError(err as Error);
    } finally {
      setBusy(null);
    }
  }
  return (
    <Modal
      title={readOnly ? "Choose an example" : "Start an example"}
      onClose={onClose}
      wide
    >
      <div className="modal-content">
        {readOnly && (
          <div className="notice">
            <ShieldCheck size={18} />
            <p>
              Select an example to inspect its source, calculation and proposed
              actions.
            </p>
          </div>
        )}
        <p className="muted">
          {readOnly
            ? "Choose a problem to see its impact and proposed response."
            : "Each example opens a separate workspace and prepares an assessment."}
        </p>
        <div className="notice">
          <ShieldCheck size={18} />
          <p>Delivery, production and quality</p>
        </div>
        {error && <ErrorBox error={error} />}
        <div className="demo-options">
          {scenarios.map(
            ({ id, title, icon: Icon, description, journey }, i) => (
              <button
                key={id}
                className="demo-option"
                disabled={!!busy}
                onClick={() => void start(id)}
              >
                <span className="demo-icon">
                  <Icon size={23} />
                </span>
                <span className="demo-copy">
                  <small>SCENARIO 0{i + 1}</small>
                  <strong>{title}</strong>
                  <span>{description}</span>
                  <em>{journey}</em>
                </span>
                <span className="demo-arrow">
                  {busy === id ? (
                    <RefreshCw className="spin" size={19} />
                  ) : (
                    <ArrowRight size={20} />
                  )}
                </span>
              </button>
            ),
          )}
        </div>
        {liveEnabled && !readOnly && (
          <>
            <div className="demo-divider">
              <span>OR CHECK YOUR OWN SAMPLE MAIL</span>
            </div>
            <form className="custom-mail" onSubmit={startCustom}>
              <div className="custom-mail-heading">
                <span className="demo-icon">
                  <MailSearch size={23} />
                </span>
                <div>
                  <strong>Analyze with Gemini</strong>
                  <p>
                    Edit this synthetic supplier email. Gemini extracts a
                    candidate; the backend accepts only exact quoted and
                    ERP-consistent facts.
                  </p>
                </div>
              </div>
              <label>
                Subject
                <input
                  value={subject}
                  onChange={(event) => setSubject(event.target.value)}
                  required
                  maxLength={500}
                  disabled={!!busy || readOnly}
                />
              </label>
              <label>
                Email body
                <textarea
                  value={content}
                  onChange={(event) => setContent(event.target.value)}
                  required
                  maxLength={50000}
                  rows={10}
                  disabled={!!busy || readOnly}
                />
              </label>
              <div className="custom-mail-actions">
                <small>
                  Sender is fixed to supplier@example.test. Nothing is sent to a
                  real mailbox.
                </small>
                <button
                  className="button primary"
                  disabled={!!busy || readOnly}
                >
                  {busy === "custom-email" ? (
                    <RefreshCw className="spin" size={17} />
                  ) : (
                    <MailSearch size={17} />
                  )}
                  Check sample mail
                </button>
              </div>
            </form>
          </>
        )}
        <p className="footnote">
          {readOnly
            ? "Visitors can inspect each assessment. The responsible role must approve the exact plan before an action runs."
            : "The assessment prepares a response. The responsible team reviews it before an action runs."}
        </p>
      </div>
    </Modal>
  );
}
function RunTracker({
  run,
  refresh,
  onDismiss,
}: {
  run: Run;
  refresh: number;
  onDismiss: () => void;
}) {
  const query = useQuery<RecordData>(
    scoped(`/api/source-events/${run.source_event_id}`, run.scope_id),
    refresh,
    2500,
  );
  const event = query.data;
  return (
    <div className="run-tracker" aria-live="polite">
      <span className="tracker-icon">
        <Activity size={20} />
      </span>
      <div>
        <strong>Guided run</strong>
        <p>
          {event ? (
            <>
              <Badge value={event.status} />
              <span className="inline-label">Analysis job</span>
              <Badge value={event.job_status} />
            </>
          ) : (
            "Checking the report…"
          )}
        </p>
        <Json
          title="Technical details"
          value={{ source: run.source_event_id, analysis: run.job_id }}
        />
        {Array.isArray(event?.review_reasons) && (
          <p>{event.review_reasons.map(string).join(" · ")}</p>
        )}
        {query.error && <p role="alert">{query.error.message}</p>}
      </div>
      {event?.incident_id ? (
        <a
          className="button subtle"
          href={`#/incidents/${string(event.incident_id)}`}
        >
          View incident
          <ArrowRight size={16} />
        </a>
      ) : null}
      <button
        className="icon-button"
        aria-label="Dismiss guided run status"
        onClick={onDismiss}
      >
        <X size={18} />
      </button>
    </div>
  );
}
export default function App() {
  const [session, setSession] = useState<Session | null>(null),
    [booting, setBooting] = useState(true),
    [authError, setAuthError] = useState<Error | null>(null);
  const [scopeId, setScopeId] = useState(""),
    [scopeRefresh, setScopeRefresh] = useState(0),
    [refresh, setRefresh] = useState(0),
    [demo, setDemo] = useState(false),
    [mobile, setMobile] = useState(false),
    [run, setRun] = useState<Run | null>(null);
  const navigationToggle = useRef<HTMLButtonElement>(null);
  const navigationClose = useRef<HTMLButtonElement>(null);
  const closeNavigation = useCallback(() => {
    setMobile(false);
    navigationToggle.current?.focus();
  }, []);
  const route = useRoute();
  const sessionIdentity = session
    ? `${session.user.id}:${session.user.role}`
    : "";
  const scopeQuery = useQuery<{ items: Scope[] }>(
    session ? "/api/scopes" : null,
    scopeRefresh,
    10000,
    sessionIdentity,
  );
  const scopes = scopeQuery.data?.items || session?.scopes || [];
  const kpis = useQuery<Kpis>(
    session && scopeId ? scoped("/api/dashboard", scopeId) : null,
    refresh,
    5000,
    sessionIdentity,
  );
  useEffect(() => {
    if (kpis.data?.timezone) setDisplayTimezone(kpis.data.timezone);
  }, [kpis.data?.timezone]);
  useEffect(() => {
    let active = true;
    api<Session>("/api/auth/me")
      .then((value) => {
        if (active) {
          setCsrf(value.csrf_token || "");
          setScopeId(restoreScope(value, value.scopes || []));
          setSession(value);
        }
      })
      .catch((error) => {
        if (active && error.status !== 401) setAuthError(error);
      })
      .finally(() => {
        if (active) setBooting(false);
      });
    return () => {
      active = false;
    };
  }, []);
  useEffect(() => {
    if (session && scopes.length && !scopeId)
      setScopeId(restoreScope(session, scopes));
  }, [scopes, scopeId, session]);
  useEffect(() => {
    setMobile(false);
  }, [route]);
  useEffect(() => {
    if (!mobile) return;
    navigationClose.current?.focus();
    const onEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !event.defaultPrevented) {
        event.preventDefault();
        closeNavigation();
      }
    };
    document.addEventListener("keydown", onEscape);
    return () => document.removeEventListener("keydown", onEscape);
  }, [mobile, closeNavigation]);
  async function logout() {
    try {
      await api("/api/auth/logout", {});
      setCsrf("");
      setSession(null);
      setScopeId("");
      setRun(null);
      location.hash = "/overview";
    } catch (error) {
      setAuthError(error as Error);
    }
  }
  async function onRun(value: Run) {
    setRun(value);
    setScopeRefresh((n) => n + 1);
    setScopeId(value.scope_id);
    if (session) rememberScope(session, value.scope_id);
    setRefresh((n) => n + 1);
    location.hash = "/overview";
  }
  function changeScope(id: string) {
    if (!session || !scopes.some((scope) => scope.id === id)) return;
    setScopeId(id);
    rememberScope(session, id);
    setRun(null);
    location.hash = "/overview";
  }
  if (booting)
    return (
      <div className="boot">
        <Loading>Checking your session…</Loading>
      </div>
    );
  if (!session)
    return (
      <Login
        onLogin={(value) => {
          setScopeId(restoreScope(value, value.scopes || []));
          setSession(value);
          setAuthError(null);
          setScopeRefresh((n) => n + 1);
        }}
      />
    );
  const page = route.startsWith("/incidents/")
    ? "detail"
    : route === "/approvals"
      ? "approvals"
      : route === "/reliability"
        ? "reliability"
        : "overview";
  const scope = scopes.find((item) => item.id === scopeId);
  const common = {
    scopeId,
    refresh,
    session,
    onRefresh: () => setRefresh((n) => n + 1),
  };
  return (
    <div className="app-shell">
      <a
        className="skip-link"
        href="#main-content"
        onClick={(event) => {
          event.preventDefault();
          document.getElementById("main-content")?.focus();
        }}
      >
        Skip to content
      </a>
      <aside className={`sidebar ${mobile ? "open" : ""}`}>
        <Brand />
        <button
          ref={navigationClose}
          className="icon-button mobile-nav-close"
          aria-label="Close navigation"
          onClick={closeNavigation}
        >
          <X size={18} />
        </button>
        <div className="sidebar-kicker">WORKSPACE</div>
        <nav
          id="workspace-navigation"
          aria-label="Main navigation"
          onClick={() => {
            if (mobile) closeNavigation();
          }}
        >
          <a
            href="#/overview"
            className={page === "overview" || page === "detail" ? "active" : ""}
          >
            <LayoutDashboard size={19} />
            <span>Overview</span>
          </a>
          <a
            href="#/approvals"
            className={page === "approvals" ? "active" : ""}
          >
            <ClipboardCheck size={19} />
            <span>Approval inbox</span>
            {kpis.data && kpis.data.pending_approvals > 0 && (
              <span className="nav-count">{kpis.data.pending_approvals}</span>
            )}
          </a>
          <a
            href="#/reliability"
            className={page === "reliability" ? "active" : ""}
          >
            <Activity size={19} />
            <span>Processing history</span>
          </a>
        </nav>
        <div className="sidebar-bottom">
          <div className="environment-label">
            <span className="status-dot" />
            <b>Operations workspace</b>
            <p>Production planning</p>
          </div>
          <div className="sidebar-user">
            <span className="avatar">
              {session.user.username.slice(0, 2).toUpperCase()}
            </span>
            <div>
              <strong>
                {session.user.username === "public_viewer"
                  ? "Visitor"
                  : session.user.username}
              </strong>
              <small>{label(session.user.role)}</small>
            </div>
            <button
              className="icon-button"
              aria-label="Sign out"
              onClick={() => void logout()}
            >
              <LogOut size={17} />
            </button>
          </div>
        </div>
      </aside>
      {mobile && (
        <button
          className="nav-backdrop"
          aria-label="Dismiss navigation"
          onClick={closeNavigation}
        />
      )}
      <div className="workspace">
        <header className="topbar">
          <div className="topbar-start">
            <button
              ref={navigationToggle}
              className="icon-button mobile-menu"
              aria-label="Toggle navigation"
              aria-expanded={mobile}
              aria-controls="workspace-navigation"
              onClick={() => {
                if (mobile) closeNavigation();
                else setMobile(true);
              }}
            >
              <Menu size={21} />
            </button>
            <span className="breadcrumb">
              Operations <ChevronRight size={14} />
              <b>
                {page === "detail"
                  ? "Incident detail"
                  : page === "approvals"
                    ? "Approval inbox"
                    : label(page)}
              </b>
            </span>
          </div>
          <div className="topbar-actions">
            <label className="scope-select">
              <span>Workspace</span>
              <select
                value={scopeId}
                onChange={(e) => changeScope(e.target.value)}
                aria-label="Workspace"
              >
                {!scopes.length && <option value="">No scopes yet</option>}
                {scopes.map((item, index) => (
                  <option key={item.id} value={item.id}>
                    {workspaceName(item.name, index)}
                  </option>
                ))}
              </select>
            </label>
            <button className="button primary" onClick={() => setDemo(true)}>
              <Play size={15} />
              Browse examples
            </button>
          </div>
        </header>
        <div className="mode-strip">
          <span>
            <ShieldCheck size={14} />
            <b>Production planning</b>
          </span>
          <span>
            {kpis.data
              ? `Planning date · ${date(kpis.data.clock)} · ${kpis.data.timezone}`
              : "Waiting for the scope data clock"}
          </span>
        </div>
        <main id="main-content" tabIndex={-1}>
          <div className="page-heading">
            <div>
              <span className="eyebrow">{workspaceName(scope?.name)}</span>
              <h1>
                {page === "detail"
                  ? "Incident detail"
                  : page === "approvals"
                    ? "Approval inbox"
                    : page === "reliability"
                      ? "Processing history"
                      : "Operations overview"}
              </h1>
              <p>
                {page === "detail"
                  ? "Follow the facts, assessment and response in one place."
                  : page === "approvals"
                    ? "Review exactly what will happen before an action is released."
                    : page === "reliability"
                      ? "Follow each assessment, approval and completed action."
                      : "Prioritize operational impact. Keep every decision traceable."}
              </p>
            </div>
            <button
              className="button subtle"
              onClick={() => setRefresh((n) => n + 1)}
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>
          {authError && <ErrorBox error={authError} />}{" "}
          {scopeQuery.error && (
            <ErrorBox
              error={scopeQuery.error}
              retry={() => setScopeRefresh((n) => n + 1)}
            />
          )}{" "}
          {run?.scope_id === scopeId && (
            <RunTracker
              run={run}
              refresh={refresh}
              onDismiss={() => setRun(null)}
            />
          )}{" "}
          {!scopeId ? (
            scopeQuery.loading ? (
              <Loading />
            ) : (
              <Empty
                title="Your workspace is ready"
                action={
                  <button
                    className="button primary"
                    onClick={() => setDemo(true)}
                  >
                    <Play size={16} />
                    Choose a scenario
                  </button>
                }
              >
                Choose an example to create a workspace. Follow its assessment
                and the actions that need review.
              </Empty>
            )
          ) : page === "overview" ? (
            <Overview {...common} kpis={kpis} onDemo={() => setDemo(true)} />
          ) : page === "detail" ? (
            <IncidentDetail
              {...common}
              incidentId={route.slice("/incidents/".length)}
              onRun={onRun}
            />
          ) : page === "approvals" ? (
            <Approvals {...common} />
          ) : (
            <Reliability {...common} />
          )}
          <footer className="page-footer">
            <span>AI Production Incident Control</span>
            <span>
              Sample data · Rule-based assessment · No live supplier delivery
            </span>
          </footer>
        </main>
      </div>
      {demo && (
        <DemoDialog
          onClose={() => setDemo(false)}
          onRun={onRun}
          readOnly={session.user.role === "viewer"}
          scopeId={scopeId}
        />
      )}
    </div>
  );
}

export type ViewProps = {
  scopeId: string;
  refresh: number;
  session: Session;
  onRefresh: () => void;
};
