import { useState } from "react";
import {
  ArrowDownRight,
  ArrowRight,
  CircleAlert,
  Clock3,
  Euro,
  Filter,
  Layers,
  Play,
  Search,
  ShieldAlert,
} from "lucide-react";
import {
  date,
  incidentTitle,
  label,
  money,
  scoped,
  type Incident,
  type Kpis,
} from "./api";
import { Badge, Empty, ErrorBox, Loading, Section, useQuery } from "./ui";
import type { ViewProps } from "./App";

export function Overview({
  scopeId,
  refresh,
  kpis,
  onRefresh,
  onDemo,
}: ViewProps & {
  kpis: ReturnType<typeof useQuery<Kpis>>;
  onDemo: () => void;
}) {
  const [filters, setFilters] = useState({
      type: "",
      severity: "",
      status: "",
      updated_after: "",
      updated_before: "",
    }),
    [offset, setOffset] = useState(0),
    [search, setSearch] = useState("");
  const query = useQuery<{ items: Incident[]; total: number }>(
    scoped("/api/incidents", scopeId, {
      ...filters,
      updated_after: filters.updated_after
        ? `${filters.updated_after}+07:00`
        : "",
      updated_before: filters.updated_before
        ? `${filters.updated_before}+07:00`
        : "",
      offset,
      limit: 25,
    }),
    refresh,
  );
  const list =
    query.data?.items.filter((item) =>
      `${item.number} ${item.title} ${incidentTitle(item)}`
        .toLowerCase()
        .includes(search.toLowerCase()),
    ) || [];
  function filter(key: keyof typeof filters, value: string) {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setOffset(0);
  }
  const stats = [
    {
      key: "open_incidents",
      title: "Open incidents",
      icon: Layers,
      note: "Current unresolved episodes",
    },
    {
      key: "critical_incidents",
      title: "Critical incidents",
      icon: ShieldAlert,
      note: "Highest review priority",
    },
    {
      key: "affected_open_order_value_cents",
      title: "Affected open-order value",
      icon: Euro,
      note: "Unique open customer positions",
    },
    {
      key: "pending_approvals",
      title: "Pending approvals",
      icon: CircleAlert,
      note: "Awaiting a human decision",
    },
    {
      key: "sla_breaches",
      title: "SLA breaches",
      icon: Clock3,
      note: "Persisted escalation records",
    },
  ] as const;
  return (
    <>
      {kpis.error && <ErrorBox error={kpis.error} retry={onRefresh} />}
      <div className="kpi-grid" aria-label="Current scope metrics">
        {stats.map(({ key, title, icon: Icon, note }) => (
          <section
            className={`kpi ${key === "affected_open_order_value_cents" ? "money-kpi" : ""}`}
            key={key}
          >
            <div className="kpi-label">
              <span>{title}</span>
              <Icon size={17} />
            </div>
            <strong aria-busy={!kpis.data}>
              {!kpis.data
                ? "—"
                : key === "affected_open_order_value_cents"
                  ? money(kpis.data[key])
                  : kpis.data[key]}
            </strong>
            <small>{note}</small>
          </section>
        ))}
      </div>
      <div className="metric-note">
        <ArrowDownRight size={15} />
        <span>
          Value uses the union of affected open sales positions. It is not
          predicted revenue loss.
        </span>
        {kpis.loadedAt && (
          <span className="last-read">
            Last read{" "}
            {kpis.loadedAt.toLocaleTimeString("en-GB", {
              timeZone: "Europe/Berlin",
            })}{" "}
            Berlin
          </span>
        )}
      </div>
      <Section
        title="Incident register"
        subtitle="Current problems, business impact and next steps"
        action={
          <span className="count-label">
            {query.data?.total ?? "—"} incidents
          </span>
        }
      >
        <div className="filters">
          <label className="search">
            <Search size={16} />
            <input
              aria-label="Search this page"
              placeholder="Search this page…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>
          <label>
            <span>Incident type</span>
            <select
              value={filters.type}
              onChange={(e) => filter("type", e.target.value)}
            >
              <option value="">All types</option>
              {["SUPPLIER_DELAY", "MACHINE_BREAKDOWN", "QUALITY_ISSUE"].map(
                (v) => (
                  <option key={v} value={v}>
                    {label(v)}
                  </option>
                ),
              )}
            </select>
          </label>
          <label>
            <span>Severity</span>
            <select
              value={filters.severity}
              onChange={(e) => filter("severity", e.target.value)}
            >
              <option value="">All severities</option>
              {["CRITICAL", "HIGH", "MEDIUM", "LOW"].map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Status</span>
            <select
              value={filters.status}
              onChange={(e) => filter("status", e.target.value)}
            >
              <option value="">All states</option>
              {[
                "NEW",
                "ANALYZING",
                "ASSESSED",
                "WAITING_APPROVAL",
                "ACTION_IN_PROGRESS",
                "MONITORING",
                "MANUAL_REVIEW",
                "RESOLVED",
                "CLOSED",
              ].map((v) => (
                <option value={v} key={v}>
                  {label(v)}
                </option>
              ))}
            </select>
          </label>
          <details className="date-filter">
            <summary>
              <Filter size={15} />
              Period
            </summary>
            <div>
              <label>
                Updated after (Berlin)
                <input
                  type="datetime-local"
                  value={filters.updated_after}
                  onChange={(e) => filter("updated_after", e.target.value)}
                />
              </label>
              <label>
                Updated before (Berlin)
                <input
                  type="datetime-local"
                  value={filters.updated_before}
                  onChange={(e) => filter("updated_before", e.target.value)}
                />
              </label>
              <button
                className="text-button"
                onClick={() => {
                  filter("updated_after", "");
                  filter("updated_before", "");
                }}
              >
                Clear period
              </button>
            </div>
          </details>
        </div>
        {query.error && (
          <div className="panel-padding">
            <ErrorBox error={query.error} retry={onRefresh} />
          </div>
        )}
        {query.loading && !query.data ? (
          <Loading />
        ) : !list.length ? (
          <Empty
            title={
              Object.values(filters).some(Boolean) || search
                ? "No matching incidents"
                : "No incidents in this scope"
            }
            action={
              <button className="button subtle" onClick={onDemo}>
                <Play size={15} />
                Browse examples
              </button>
            }
          >
            {Object.values(filters).some(Boolean) || search
              ? "Adjust the filters to see other incidents."
              : "Choose an example to follow its assessment and proposed response."}
          </Empty>
        ) : (
          <div className="table-scroll">
            <table className="incidents-table">
              <thead>
                <tr>
                  <th>Incident / operational object</th>
                  <th>Severity</th>
                  <th>Response state</th>
                  <th className="numeric">Open-order value</th>
                  <th>Last updated</th>
                  <th>
                    <span className="sr-only">Open</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {list.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <a
                        className="incident-link"
                        href={`#/incidents/${item.id}`}
                      >
                        <small>Assessment version {item.revision}</small>
                        <strong>{incidentTitle(item)}</strong>
                        <span>{label(item.incident_type)}</span>
                      </a>
                    </td>
                    <td>
                      <Badge value={item.severity} />
                      <span className="score-mini">
                        {item.risk_score === null
                          ? "Unscored"
                          : `${item.risk_score} / 100`}
                      </span>
                    </td>
                    <td>
                      <Badge value={item.status} />
                    </td>
                    <td className="numeric value">
                      {money(item.affected_open_order_value_cents)}
                    </td>
                    <td className="date-cell">{date(item.updated_at)}</td>
                    <td>
                      <a
                        className="icon-button"
                        href={`#/incidents/${item.id}`}
                        aria-label={`Open ${incidentTitle(item)}`}
                      >
                        <ArrowRight size={18} />
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="table-footer">
          <span>
            Filters apply to the register. KPIs show the whole selected scope.
          </span>
          <div>
            <button
              className="button subtle small"
              disabled={offset === 0}
              onClick={() => setOffset(Math.max(0, offset - 25))}
            >
              Previous
            </button>
            <span>Page {Math.floor(offset / 25) + 1}</span>
            <button
              className="button subtle small"
              disabled={!query.data || offset + 25 >= query.data.total}
              onClick={() => setOffset(offset + 25)}
            >
              Next
            </button>
          </div>
        </div>
      </Section>
      <div className="overview-explainer">
        <div>
          <span className="eyebrow">THE CONTROL LOOP</span>
          <h2>Facts first. People in control.</h2>
        </div>
        <p>
          Source evidence and a consistent ERP snapshot determine impact.
          Versioned rules set priority. The exact response is reviewed before a
          consequential action runs.
        </p>
        <a href="#/approvals">
          Review approval inbox
          <ArrowRight size={16} />
        </a>
      </div>
    </>
  );
}
