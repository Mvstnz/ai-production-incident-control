import {
  date,
  label,
  money,
  string,
  type Action,
  type RecordData,
} from "./api";

const names: Record<string, string> = {
  "DEMO-NORTH-HALL": "Metallwerkstatt Nord",
  "DEMO-SAW-01": "Bandsäge 1",
  "DEMO-SAW-02": "Bandsäge 2",
  "DEMO-DRILL-01": "Bohrmaschine 1",
  "DEMO-ROD-20": "Stahlstange · Ø 20 mm × 2 m",
  "DEMO-PLATE-10": "Montageplatte · vier Bohrungen mit Ø 10 mm",
  "DEMO-SUPPLIER-A": "Metalllieferant",
  "DEMO-LOT-ROD-01": "Stahlstangen-Lieferung",
  "DEMO-LOT-PLATE-01": "Montageplatten · Charge 01",
  "DEMO-LOT-PLATE-02": "Montageplatten · Charge 02",
  "DEMO-QI-PLATE-01": "Prüfung des Bohrungsdurchmessers",
  STEEL_BAR_CUTTING: "Stahlstangen sägen",
  DRILLING: "Bohren",
};
export function businessName(value: unknown): string {
  const raw = string(value);
  if (names[raw]) return names[raw];
  const patterns: [RegExp, string][] = [
    [/^DEMO-MO-FRAME-(\d+)$/, "Metallrahmen · Auftrag $1"],
    [/^DEMO-MO-CUT-(\d+)$/, "Stahlzuschnitt · Auftrag $1"],
    [/^DEMO-OP-CUT-(\d+)$/, "Schneideauftrag $1"],
    [/^DEMO-SO-FRAME-(\d+)\/(\d+)$/, "Rahmenauftrag $1 · Position $2"],
    [/^DEMO-SO-CUT-(\d+)\/(\d+)$/, "Zuschnittauftrag $1 · Position $2"],
    [/^DEMO-SO-PLATE-(\d+)\/(\d+)$/, "Plattenauftrag $1 · Position $2"],
    [/^DEMO-SHIP-PLATE-(\d+)\/(\d+)$/, "Plattenlieferung $1 · Position $2"],
    [/^DEMO-PO-(\d+)$/, "Bestellung $1"],
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
    return "Metallwerkstatt Nord";
  if (/^(Demo|APIC)/i.test(name))
    return index === undefined ? "Werkstatt" : `Arbeitsbereich ${index + 1}`;
  return name;
}
export function fieldValue(value: unknown, key = ""): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "Ja" : "Nein";
  if (Array.isArray(value))
    return value.map((item) => fieldValue(item, key)).join("; ") || "Keine";
  if (typeof value === "object")
    return Object.entries(value as RecordData)
      .map(([k, v]) => `${label(k)}: ${fieldValue(v, k)}`)
      .join(" · ");
  if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}T/.test(value))
    return date(value);
  if (key.endsWith("_cents")) return money(value);
  if (key === "required_hours" || key.endsWith("_hours"))
    return `${value} Stunden`;
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
    return `${businessName(p.operation_id)} auf ${businessName(p.machine_id)} verlegen. Dafür sind ${fieldValue(p.required_hours, "required_hours")} vorgesehen.`;
  if (action.action_type === "QUALITY_BLOCK")
    return `${string(p.quantity)} Montageplatten sperren und die betroffenen Lieferungen bis zur Qualitätsentscheidung zurückhalten.`;
  if (action.action_type === "QUALITY_RELEASE")
    return "Das gesperrte Material nach der Qualitätsentscheidung freigeben.";
  if (action.action_type === "SUPPLIER_EMAIL")
    return "Den Lieferanten um Bestätigung des Liefertermins und der vorgeschlagenen früheren Teillieferung bitten.";
  if (action.action_type === "INTERNAL_TICKET")
    return "Die Produktionsplanung über betroffene Aufträge und den Handlungsbedarf informieren.";
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
