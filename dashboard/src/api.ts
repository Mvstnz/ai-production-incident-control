export type RecordData = Record<string, unknown>;
export type Role =
  | "viewer"
  | "operator"
  | "purchasing"
  | "production_manager"
  | "quality_manager"
  | "admin";
export interface Session {
  user: { id: string; username: string; role: Role };
  csrf_token: string;
  scopes?: Scope[];
}
export interface Scope {
  id: string;
  name: string;
  clock?: string;
  synthetic?: boolean;
}
export interface Incident {
  id: string;
  number: string;
  title: string;
  incident_type: string;
  status: string;
  revision: number;
  risk_score: number | null;
  severity: string | null;
  affected_open_order_value_cents: number | null;
  updated_at: string;
}
export function incidentTitle(incident: Pick<Incident, "title">): string {
  const examples: [string, string][] = [
    ["SUPPLIER_DELAY:DEMO-PO-8264:20", "Stahlstangen kommen zu spät"],
    ["MACHINE_BREAKDOWN:DEMO-SAW-01", "Bandsäge 1 steht still"],
    [
      "QUALITY_ISSUE:DEMO-LOT-PLATE-01:DEMO-QI-PLATE-01",
      "Montageplatten mit zu großen Bohrungen",
    ],
  ];
  return (
    examples.find(([key]) => incident.title.endsWith(key))?.[1] ??
    incident.title
  );
}
export interface Action {
  id?: string;
  plan_id?: string;
  action_type: string;
  payload: RecordData;
  required_role?: string;
  status?: string;
  attempts?: number;
  provider_id?: string;
  execution_id?: string;
  workflow_id?: string;
  result?: RecordData;
}
export interface PlanBody {
  policy_version?: string;
  summary: string;
  summary_mode: string;
  sop_ids: string[];
  actions: Action[];
}
export interface Plan {
  id: string;
  plan_version: number;
  plan_hash: string;
  revision: number;
  status: string;
  body: PlanBody;
  created_at: string;
}
export interface Approval {
  id: string;
  incident_id: string;
  incident_title?: string;
  revision: number;
  plan_id: string;
  plan_version: number;
  plan_hash: string;
  status: string;
  required_role: string;
  expires_at: string;
  actions: Action[];
}
export interface Detail extends Incident {
  sources: RecordData[];
  revisions: RecordData[];
  impact: RecordData | null;
  risk: RecordData | null;
  plans: Plan[];
  actions: Action[];
  approvals: Approval[];
  timeline: RecordData[];
}
export interface Kpis {
  open_incidents: number;
  critical_incidents: number;
  affected_open_order_value_cents: number;
  pending_approvals: number;
  sla_breaches: number;
  currency: string;
  clock: string;
  timezone: string;
  ai_mode: string;
  profile: string;
  aggregation: string;
}
export interface Run {
  scope_id: string;
  source_event_id: string;
  job_id: string;
  status_url: string;
}
export type Scenario =
  | "supplier-delay"
  | "supplier-split"
  | "machine-breakdown"
  | "quality-issue"
  | "quality-shipped"
  | "unknown-input";
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public correlationId?: string,
  ) {
    super(message);
  }
}
let csrf = "";
export function setCsrf(value: string) {
  csrf = value;
}
export function scoped(
  path: string,
  scopeId: string,
  params: Record<string, string | number> = {},
) {
  const query = new URLSearchParams({ scope_id: scopeId });
  Object.entries(params).forEach(([k, v]) => {
    if (v !== "") query.set(k, String(v));
  });
  return `${path}?${query}`;
}
export async function api<T>(
  path: string,
  body?: unknown,
  signal?: AbortSignal,
): Promise<T> {
  // Browser requests can reach only the explicitly public API namespace.
  if (!path.startsWith("/api/")) throw new ApiError("Invalid API path", 400);
  let response: Response;
  try {
    response = await fetch(path, {
      method: body === undefined ? "GET" : "POST",
      credentials: "same-origin",
      signal,
      headers:
        body === undefined
          ? { Accept: "application/json" }
          : {
              Accept: "application/json",
              "Content-Type": "application/json",
              "X-CSRF-Token": csrf,
            },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError")
      throw error;
    throw new ApiError(
      "The Operations API could not be reached. Check the local services and try again.",
      0,
    );
  }
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const result = record(data);
    const detail = record(result.detail);
    const message =
      string(result.message) ||
      string(detail.message) ||
      (typeof result.detail === "string" ? result.detail : "") ||
      `Request failed (${response.status}).`;
    throw new ApiError(
      message,
      response.status,
      string(result.correlation_id) || undefined,
    );
  }
  return data as T;
}
export const record = (value: unknown): RecordData =>
  value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as RecordData)
    : {};
export const rows = (value: unknown): RecordData[] =>
  Array.isArray(value) ? value.map(record) : [];
export const string = (value: unknown): string =>
  value === null || value === undefined
    ? ""
    : typeof value === "object"
      ? JSON.stringify(value)
      : String(value);
export const text = (value: unknown): string => string(value) || "—";
const readableLabels: Record<string, string> = {
  CANCELLED: "Abgebrochen",
  NEW: "Neu",
  RUNNING: "In Bearbeitung",
  OVERVIEW: "Fälle ansehen",
  ABOUT: "So funktioniert es",
  MAIL: "Mail auswerten",
  REGISTER: "Fallregister",
  APPROVE: "Freigabe",
  REJECT: "Ablehnung",
  MODIFY: "Änderung",
  PRODUCTION_MANAGER: "Produktionsleitung",
  QUALITY_MANAGER: "Qualitätsmanagement",
  PURCHASING: "Einkauf",
  OPERATOR: "Sachbearbeitung",
  ADMIN: "Administration",
  APPROVED: "Freigegeben",
  REJECTED: "Abgelehnt",
  EXPIRED: "Abgelaufen",
  SUPERSEDED: "Durch neuere Version ersetzt",
  MONITORING: "In Nachverfolgung",
  RESOLVED: "Gelöst",
  OPEN: "Offen",
  ANALYZING: "Wird geprüft",
  CRITICAL: "Kritisch",
  HIGH: "Hoch",
  MEDIUM: "Mittel",
  LOW: "Niedrig",
  PROPOSED: "Vorgeschlagen",
  CONFIRMED: "Bestätigt",
  VERIFIED: "Geprüft",
  QUEUED: "Eingeplant",
  FAILED: "Fehlgeschlagen",
  IN_PROGRESS: "In Bearbeitung",
  PRODUCTION_ORDER: "Produktionsauftrag",
  QUANTITY: "Menge",
  SUBJECT: "Betreff",
  TITLE: "Titel",
  STATUS: "Stand",
  INTERNAL_TICKET: "Info an die Produktionsplanung",
  SUPPLIER_EMAIL: "Lieferanten-Nachricht",
  RESCHEDULE: "Schneideauftrag umplanen",
  QUALITY_BLOCK: "Lieferung sperren",
  QUALITY_RELEASE: "Qualitätsfreigabe",
  SUPPLIER_DELAY: "Lieferverzug",
  MACHINE_BREAKDOWN: "Maschinenausfall",
  QUALITY_ISSUE: "Qualitätsmangel",
  SUCCEEDED: "Abgeschlossen",
  WAITING_APPROVAL: "Freigabe ausstehend",
  MANUAL_REVIEW: "Prüfung erforderlich",
  DEAD_LETTER: "Eingriff erforderlich",
  UNKNOWN_OUTCOME: "Ergebnis prüfen",
  RETRY_SCHEDULED: "Erneuter Versuch geplant",
  NORMALIZE: "Meldung wird geprüft",
  PENDING: "Entscheidung offen",
  VIEWER: "Besucherzugang",
  RELIABILITY: "Verarbeitungsverlauf",
  MACHINE_ID: "Maschine",
  OPERATION_ID: "Schneideauftrag",
  SITE: "Standort",
  REQUIRED_HOURS: "Benötigte Zeit",
  START_AT: "Start",
  END_AT: "Ende",
  LOT_ID: "Charge",
  INSPECTION_ID: "Prüfung",
  SHIPMENT_ITEM_IDS: "Betroffene Lieferungen",
  INCIDENT_REVISION: "Bewertungsstand",
  PURCHASE_ORDER_ITEM: "Bestellposition",
  CAPABILITY: "Bearbeitung",
  RECIPIENT: "Empfänger",
  BODY: "Nachricht",
};
export const label = (value: unknown): string =>
  readableLabels[string(value).toUpperCase()] ||
  string(value)
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase()) ||
  "Unbekannt";
export function money(value: unknown, currency = "EUR") {
  return value === null ||
    value === undefined ||
    !Number.isFinite(Number(value))
    ? "—"
    : new Intl.NumberFormat("de-DE", {
        style: "currency",
        currency,
        maximumFractionDigits: 0,
      }).format(Number(value) / 100);
}
let displayTimezone = "Europe/Berlin";
export function setDisplayTimezone(value: string) {
  try {
    new Intl.DateTimeFormat("de-DE", { timeZone: value });
    displayTimezone = value;
  } catch {
    /* Keep the configured default. */
  }
}
export function date(value: unknown) {
  if (!value || !Number.isFinite(Date.parse(string(value)))) return "—";
  return new Intl.DateTimeFormat("de-DE", {
    timeZone: displayTimezone,
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(string(value)));
}
export const canDecide = (role: Role, required: string) =>
  role === "admin" || role === required;
