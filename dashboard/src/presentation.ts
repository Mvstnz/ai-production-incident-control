import {
  date,
  label,
  money,
  string,
  type Action,
  type RecordData,
} from "./api";

const names: Record<string, string> = {
  "DEMO-NORTH-HALL": "North workshop",
  "DEMO-SAW-01": "Band saw S-01",
  "DEMO-SAW-02": "Band saw S-02",
  "DEMO-DRILL-01": "Drill press B-01",
  "DEMO-ROD-20": "Steel rod · Ø20 mm × 2 m",
  "DEMO-PLATE-10": "Mounting plate · four 10 mm holes",
  "DEMO-SUPPLIER-A": "Metal supplier",
  "DEMO-LOT-ROD-01": "Steel-rod delivery batch",
  "DEMO-LOT-PLATE-01": "Mounting plates · batch 01",
  "DEMO-LOT-PLATE-02": "Mounting plates · batch 02",
  "DEMO-QI-PLATE-01": "Hole-diameter inspection",
  STEEL_BAR_CUTTING: "Cutting steel bars",
  DRILLING: "Drilling",
};
export function businessName(value: unknown): string {
  const raw = string(value);
  if (names[raw]) return names[raw];
  const patterns: [RegExp, string][] = [
    [/^DEMO-MO-FRAME-(\d+)$/, "Mounting frames · order $1"],
    [/^DEMO-MO-CUT-(\d+)$/, "Steel sections · order $1"],
    [/^DEMO-OP-CUT-(\d+)$/, "Cutting job $1"],
    [/^DEMO-SO-FRAME-(\d+)\/(\d+)$/, "Frame order $1 · item $2"],
    [/^DEMO-SO-CUT-(\d+)\/(\d+)$/, "Steel-section order $1 · item $2"],
    [/^DEMO-SO-PLATE-(\d+)\/(\d+)$/, "Plate order $1 · item $2"],
    [/^DEMO-SHIP-PLATE-(\d+)\/(\d+)$/, "Plate shipment $1 · item $2"],
    [/^DEMO-PO-(\d+)$/, "Purchase order $1"],
  ];
  for (const [pattern, replacement] of patterns)
    if (pattern.test(raw)) return raw.replace(pattern, replacement);
  return raw || "—";
}
export function workspaceName(
  name: string | undefined,
  index?: number,
): string {
  if (!name || name.includes("Invented manufacturing world"))
    return "North workshop";
  if (/^(Demo|APIC)/i.test(name))
    return index === undefined
      ? "Manufacturing workspace"
      : `Workspace ${index + 1}`;
  return name;
}
export function fieldValue(value: unknown, key = ""): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value))
    return value.map((item) => fieldValue(item, key)).join("; ") || "None";
  if (typeof value === "object")
    return Object.entries(value as RecordData)
      .map(([k, v]) => `${label(k)}: ${fieldValue(v, k)}`)
      .join(" · ");
  if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}T/.test(value))
    return date(value);
  if (key.endsWith("_cents")) return money(value);
  if (key === "required_hours" || key.endsWith("_hours"))
    return `${value} hours`;
  return businessName(value);
}
export function technicalField(key: string, value: unknown): boolean {
  return (
    /^(id|scope_id|incident_id|source_id|source_event_id|job_id|plan_id|action_id|snapshot_id|workflow_id|execution_id|provider_id|correlation_id|object_id|plan_hash|hash|source_refs|method_version|policy_version|erp_revision|incident_revision)$/.test(
      key,
    ) ||
    (typeof value === "string" && /^[0-9a-f]{8}-[0-9a-f-]{27,}$/i.test(value))
  );
}
export function actionDescription(action: Action): string {
  const p = action.payload;
  if (action.action_type === "RESCHEDULE")
    return `Move ${businessName(p.operation_id).toLowerCase()} to ${businessName(p.machine_id)} for ${fieldValue(p.required_hours, "required_hours")}.`;
  if (action.action_type === "QUALITY_BLOCK")
    return `Hold ${string(p.quantity)} mounting plates and stop the affected shipments pending a quality decision.`;
  if (action.action_type === "QUALITY_RELEASE")
    return "Release the held material after the quality decision.";
  if (action.action_type === "SUPPLIER_EMAIL")
    return "Ask the supplier to confirm the delivery date and the proposed early shipment.";
  if (action.action_type === "INTERNAL_TICKET")
    return "Notify production planning of the affected orders and required follow-up.";
  return label(action.action_type);
}
export function readableSummary(summary: string): string {
  return summary
    .replace(/^SUPPLIER_DELAY:/, "Delayed delivery.")
    .replace(/^MACHINE_BREAKDOWN:/, "Machine outage.")
    .replace(/^QUALITY_ISSUE:/, "Quality issue.")
    .replace("Resource shortage:", "Shortage:")
    .replace(
      "Synthetic ERP assessment; affected value is not a forecast revenue loss.",
      "The order value shows exposure, not a predicted loss.",
    );
}
