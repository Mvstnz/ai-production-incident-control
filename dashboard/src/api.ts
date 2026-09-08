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
export interface Action {
  id?: string;
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
export const label = (value: unknown): string =>
  string(value)
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase()) || "Unknown";
export function money(value: unknown, currency = "EUR") {
  return value === null ||
    value === undefined ||
    !Number.isFinite(Number(value))
    ? "—"
    : new Intl.NumberFormat("en-GB", {
        style: "currency",
        currency,
        maximumFractionDigits: 0,
      }).format(Number(value) / 100);
}
export function date(value: unknown) {
  if (!value || !Number.isFinite(Date.parse(string(value)))) return "—";
  return new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Bangkok",
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(string(value)));
}
export const canDecide = (role: Role, required: string) =>
  role === "admin" || role === required;
