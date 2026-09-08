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
import { GuidedIncident } from "./GuidedIncident";
import { CaseOverview } from "./CaseOverview";
import { About } from "./About";
import { MailAnalysis } from "./MailAnalysis";
import { Approvals } from "./Approvals";
import { Reliability } from "./Reliability";
import { rememberScope, restoreScope } from "./scope-preference";
import { workspaceName } from "./presentation";

function Brand() {
  return (
    <a className="brand" href="#/overview" aria-label="Zur Fallübersicht">
      <span className="brand-symbol">
        <Activity size={24} />
      </span>
      <span>
        <b>APIC</b>
        <small>Produktionsplanung</small>
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
            Material fehlt.
            <br />
            Was nun?
          </h1>
          <p>
            Dieses Portfolio zeigt, welche Aufträge von einer Störung betroffen
            sind und welche Reaktion ein Mensch freigeben kann.
          </p>
          <div className="login-principles">
            <span>
              <CheckCheck size={18} /> Meldung mit Betriebsdaten prüfen
            </span>
            <span>
              <ClipboardCheck size={18} /> Reaktion durch Menschen freigeben
            </span>
            <span>
              <Activity size={18} /> Ergebnisse nachvollziehen
            </span>
          </div>
        </div>
        <small>
          Portfolio-Projekt mit vollständig erfundenen Betriebsdaten
        </small>
      </aside>
      <main className="login-main">
        <div className="login-form">
          <span className="eyebrow">METALLWERKSTATT NORD</span>
          <h2>Was passiert, wenn Material fehlt?</h2>
          <p>
            Sieh dir an, wie aus einer Störungsmeldung eine konkrete
            Entscheidung wird.
          </p>
          {catalog.data?.public_demo_enabled && (
            <button
              className="button primary full"
              disabled={busy}
              onClick={() => void explore()}
            >
              Beispiele ohne Anmeldung ansehen <ArrowRight size={17} />
            </button>
          )}
          <details className="team-login">
            <summary>Team-Zugang: anmelden</summary>
            <form onSubmit={submit}>
              {error && <ErrorBox error={error} />}
              <label>
                Benutzername
                <input
                  name="username"
                  autoComplete="username"
                  required
                  maxLength={100}
                  placeholder="Dein Benutzername"
                />
              </label>
              <label>
                Passwort
                <input
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  maxLength={500}
                  placeholder="Dein Passwort"
                />
              </label>
              <button className="button primary full" disabled={busy}>
                {busy ? "Anmeldung läuft …" : "Als Team-Mitglied anmelden"}
                <ArrowRight size={17} />
              </button>
            </form>
          </details>
          <div className="login-note">
            <ShieldCheck size={20} />
            <p>
              Du kannst alle Beispiele als Besucher ansehen. Team-Mitglieder
              können zusätzlich Meldungen einreichen und Aktionen freigeben.
            </p>
          </div>
          <small>Es werden keine echten Lieferanten kontaktiert.</small>
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
    title: "Stahlstangen kommen zu spät",
    icon: Truck,
    description:
      "Ein Lieferwagen fällt aus. Stahlstangen kommen später und fehlen für bestellte Metallrahmen.",
    journey: "Meldung → betroffene Aufträge → Lieferant kontaktieren",
  },
  {
    id: "machine-breakdown",
    title: "Bandsäge 1 steht still",
    icon: Factory,
    description:
      "Ein gerissener Antriebsriemen stoppt die Bandsäge. Eine zweite Säge könnte einen Schneideauftrag übernehmen.",
    journey: "Ausfall → verfügbare Zeiten → Umplanung prüfen",
  },
  {
    id: "quality-issue",
    title: "Montageplatten mit zu großen Bohrungen",
    icon: ShieldCheck,
    description:
      "Montageplatten haben Bohrungen mit 11 statt 10 mm Durchmesser. Die Qualität muss vor der Lieferung geklärt werden.",
    journey: "Prüfung → betroffene Lieferungen → Qualität entscheiden lassen",
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
      title={readOnly ? "Einen Fall auswählen" : "Neuen Beispielfall starten"}
      onClose={onClose}
      wide
    >
      <div className="modal-content">
        {readOnly && (
          <div className="notice">
            <ShieldCheck size={18} />
            <p>
              Jeder Fall erklärt die Meldung, ihre Folgen und eine mögliche
              Reaktion.
            </p>
          </div>
        )}
        <p className="muted">
          {readOnly
            ? "Wähle eine Situation aus der Werkstatt."
            : "Jeder neue Fall erhält einen eigenen Arbeitsbereich und wird durch die Workflows geprüft."}
        </p>
        <div className="notice">
          <ShieldCheck size={18} />
          <p>Material, Maschine und Qualität</p>
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
                  <small>FALL 0{i + 1}</small>
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
            ? "Als Besucher kannst du den Ablauf ansehen. Freigaben erfolgen durch die zuständige Person."
            : "Die Prüfung bereitet eine Reaktion vor. Anschließend entscheidet das zuständige Team."}
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
        <strong>Neue Meldung</strong>
        <p>
          {event ? (
            <>
              <Badge value={event.status} />
              <span className="inline-label">Prüfung</span>
              <Badge value={event.job_status} />
            </>
          ) : (
            "Meldung wird geprüft …"
          )}
        </p>
        <Json
          title="Technische Details"
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
          Fall ansehen
          <ArrowRight size={16} />
        </a>
      ) : null}
      <button
        className="icon-button"
        aria-label="Meldungsstatus schließen"
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
        <Loading>Zugang wird geprüft …</Loading>
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
    : route.startsWith("/approvals")
      ? "approvals"
      : route === "/reliability"
        ? "reliability"
        : route === "/about"
          ? "about"
          : route === "/mail"
            ? "mail"
            : route === "/register"
              ? "register"
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
        Zum Inhalt
      </a>
      <aside className={`sidebar ${mobile ? "open" : ""}`}>
        <Brand />
        <button
          ref={navigationClose}
          className="icon-button mobile-nav-close"
          aria-label="Navigation schließen"
          onClick={closeNavigation}
        >
          <X size={18} />
        </button>
        <div className="sidebar-kicker">DIE WERKSTATT</div>
        <nav
          id="workspace-navigation"
          aria-label="Hauptnavigation"
          onClick={() => {
            if (mobile) closeNavigation();
          }}
        >
          <a
            href="#/overview"
            className={page === "overview" || page === "detail" ? "active" : ""}
          >
            <LayoutDashboard size={19} />
            <span>Fälle ansehen</span>
          </a>
          <a
            href="#/approvals"
            className={page === "approvals" ? "active" : ""}
          >
            <ClipboardCheck size={19} />
            <span>Entscheidungen</span>
            {kpis.data && kpis.data.pending_approvals > 0 && (
              <span className="nav-count">{kpis.data.pending_approvals}</span>
            )}
          </a>
          <a href="#/mail" className={page === "mail" ? "active" : ""}>
            <MailSearch size={19} />
            <span>Mail auswerten</span>
          </a>
          <a href="#/about" className={page === "about" ? "active" : ""}>
            <Activity size={19} />
            <span>So funktioniert es</span>
          </a>
        </nav>
        <div className="sidebar-bottom">
          <div className="environment-label">
            <span className="status-dot" />
            <b>Portfolio-Projekt</b>
            <p>Metallwerkstatt Nord</p>
          </div>
          <div className="sidebar-user">
            <span className="avatar">
              {session.user.username.slice(0, 2).toUpperCase()}
            </span>
            <div>
              <strong>
                {session.user.username === "public_viewer"
                  ? "Besucher"
                  : session.user.username}
              </strong>
              <small>{label(session.user.role)}</small>
            </div>
            <button
              className="icon-button"
              aria-label="Abmelden / Team-Zugang"
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
          aria-label="Navigation schließen"
          onClick={closeNavigation}
        />
      )}
      <div className="workspace">
        <header className="topbar">
          <div className="topbar-start">
            <button
              ref={navigationToggle}
              className="icon-button mobile-menu"
              aria-label="Navigation umschalten"
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
              Werkstatt <ChevronRight size={14} />
              <b>
                {page === "detail"
                  ? "Fall verstehen"
                  : page === "approvals"
                    ? "Entscheidungen"
                    : label(page)}
              </b>
            </span>
          </div>
          <div className="topbar-actions">
            <label className="scope-select">
              <span>Arbeitsbereich</span>
              <select
                value={scopeId}
                onChange={(e) => changeScope(e.target.value)}
                aria-label="Arbeitsbereich"
              >
                {!scopes.length && (
                  <option value="">Noch kein Arbeitsbereich</option>
                )}
                {scopes.map((item, index) => (
                  <option key={item.id} value={item.id}>
                    {workspaceName(item.name, index)}
                  </option>
                ))}
              </select>
            </label>
            <button className="button primary" onClick={() => setDemo(true)}>
              <Play size={15} />
              Fall auswählen
            </button>
          </div>
        </header>
        <div className="mode-strip">
          <span>
            <ShieldCheck size={14} />
            <b>Metallwerkstatt Nord</b>
          </span>
          <span>
            {kpis.data
              ? `Planungsstand · ${date(kpis.data.clock)} · ${kpis.data.timezone}`
              : "Planungsstand wird geladen"}
          </span>
        </div>
        <main id="main-content" tabIndex={-1}>
          <div
            className={`page-heading ${["overview", "detail", "about", "mail"].includes(page) ? "compact-heading" : ""}`}
          >
            <div>
              <span className="eyebrow">{workspaceName(scope?.name)}</span>
              <h1>
                {page === "detail"
                  ? "Fall verstehen"
                  : page === "approvals"
                    ? "Entscheidungen"
                    : page === "reliability"
                      ? "Verarbeitungsverlauf"
                      : "Fallübersicht"}
              </h1>
              <p>
                {page === "detail"
                  ? "Die Meldung, ihre Folgen und der nächste Schritt."
                  : page === "approvals"
                    ? "Hier prüft die zuständige Person den genauen Inhalt und entscheidet über die vorbereitete Reaktion."
                    : page === "reliability"
                      ? "Gespeicherte Verarbeitungsschritte und technische Nachweise."
                      : "Meldungen, Auswirkungen und Entscheidungen auf einen Blick."}
              </p>
            </div>
            <button
              className="button subtle"
              onClick={() => setRefresh((n) => n + 1)}
            >
              <RefreshCw size={16} />
              Aktualisieren
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
                title="Dein Arbeitsbereich ist bereit"
                action={
                  <button
                    className="button primary"
                    onClick={() => setDemo(true)}
                  >
                    <Play size={16} />
                    Neuen Fall starten
                  </button>
                }
              >
                Einen Fall auswählen to create a workspace. Follow its
                assessment and the actions that need review.
              </Empty>
            )
          ) : page === "overview" ? (
            <CaseOverview {...common} kpis={kpis} />
          ) : page === "about" ? (
            <About />
          ) : page === "mail" ? (
            <MailAnalysis {...common} onRun={onRun} />
          ) : page === "register" ? (
            <Overview {...common} kpis={kpis} onDemo={() => setDemo(true)} />
          ) : page === "detail" ? (
            <GuidedIncident
              key={scopeId + route}
              {...common}
              incidentId={route.slice("/incidents/".length)}
              onRun={onRun}
            />
          ) : page === "approvals" ? (
            <Approvals
              key={route}
              {...common}
              incidentId={
                route.startsWith("/approvals/")
                  ? route.slice("/approvals/".length)
                  : undefined
              }
            />
          ) : (
            <Reliability {...common} />
          )}
          <footer className="page-footer">
            <span>AI Production Incident Control</span>
            <span>Erfundene Betriebsdaten · Entscheidungen durch Menschen</span>
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
