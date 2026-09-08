import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  AlertCircle,
  ChevronRight,
  Inbox,
  LoaderCircle,
  X,
} from "lucide-react";
import { api, ApiError, label, text, type RecordData } from "./api";
import { fieldValue, technicalField } from "./presentation";

export function useQuery<T>(
  path: string | null,
  refresh = 0,
  interval = 5000,
  identity = "",
) {
  const [state, setState] = useState<{
    path: string | null;
    identity: string;
    data: T | null;
    error: Error | null;
    loading: boolean;
    loadedAt: Date | null;
  }>({
    path: null,
    identity,
    data: null,
    error: null,
    loading: true,
    loadedAt: null,
  });
  useEffect(() => {
    if (!path) {
      setState({
        path,
        identity,
        data: null,
        error: null,
        loading: false,
        loadedAt: null,
      });
      return;
    }
    let active = true;
    const controller = new AbortController();
    let pending = false;
    setState((prev) => ({
      path,
      identity,
      data: prev.path === path && prev.identity === identity ? prev.data : null,
      error: null,
      loading: true,
      loadedAt:
        prev.path === path && prev.identity === identity ? prev.loadedAt : null,
    }));
    async function load() {
      if (pending) return;
      pending = true;
      try {
        const data = await api<T>(path!, undefined, controller.signal);
        if (active)
          setState({
            path,
            identity,
            data,
            error: null,
            loading: false,
            loadedAt: new Date(),
          });
      } catch (error) {
        if (
          active &&
          !(error instanceof DOMException && error.name === "AbortError")
        )
          setState((prev) => ({
            ...prev,
            error: error as Error,
            loading: false,
          }));
      } finally {
        pending = false;
      }
    }
    void load();
    const timer = interval
      ? window.setInterval(() => {
          if (document.visibilityState === "visible") void load();
        }, interval)
      : undefined;
    return () => {
      active = false;
      controller.abort();
      window.clearInterval(timer);
    };
  }, [path, refresh, interval, identity]);
  if (state.path !== path || state.identity !== identity)
    return { ...state, data: null, error: null, loading: !!path };
  return state;
}
export function Badge({
  value,
  className = "",
}: {
  value: unknown;
  className?: string;
}) {
  return (
    <span
      className={`badge ${String(value || "unknown").toLowerCase()} ${className}`}
    >
      {label(value)}
    </span>
  );
}
export function ErrorBox({
  error,
  retry,
}: {
  error: Error;
  retry?: () => void;
}) {
  return (
    <div className="notice danger" role="alert">
      <AlertCircle size={18} />
      <div>
        <strong>
          {error instanceof ApiError && error.status === 403
            ? "Zugang eingeschränkt"
            : error instanceof ApiError && error.status === 409
              ? "Diese Version ist nicht mehr aktuell"
              : "Anfrage konnte nicht abgeschlossen werden"}
        </strong>
        <p>{error.message}</p>
        {error instanceof ApiError && error.correlationId && (
          <small>Technische Referenz: {error.correlationId}</small>
        )}
        {retry && (
          <button className="text-button" onClick={retry}>
            Daten neu laden <ChevronRight size={14} />
          </button>
        )}
      </div>
    </div>
  );
}
export function Loading({
  children = "Daten werden geladen …",
}: {
  children?: ReactNode;
}) {
  return (
    <div className="empty loading" role="status">
      <LoaderCircle className="spin" size={24} />
      <p>{children}</p>
    </div>
  );
}
export function Empty({
  title,
  children,
  action,
}: {
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="empty">
      <span className="empty-icon">
        <Inbox size={24} />
      </span>
      <h3>{title}</h3>
      <p>{children}</p>
      {action}
    </div>
  );
}
export function Json({
  value,
  title = "View stored data",
}: {
  value: unknown;
  title?: string;
}) {
  return (
    <details className="json-details">
      <summary>{title}</summary>
      <pre>{JSON.stringify(value, null, 2)}</pre>
    </details>
  );
}
export function Fields({ data }: { data: RecordData }) {
  const order = [
    "recipient",
    "subject",
    "title",
    "body",
    "production_order",
    "operation_id",
    "machine_id",
    "site",
    "start_at",
    "end_at",
    "required_hours",
    "capability",
    "lot_id",
    "quantity",
    "inspection_id",
    "shipment_item_ids",
  ];
  const visible = Object.entries(data)
    .filter(([key, value]) => !technicalField(key, value))
    .sort(
      ([a], [b]) =>
        (order.indexOf(a) < 0 ? 99 : order.indexOf(a)) -
        (order.indexOf(b) < 0 ? 99 : order.indexOf(b)),
    );
  const technical = Object.fromEntries(
    Object.entries(data).filter(([key, value]) => technicalField(key, value)),
  );
  return (
    <>
      <dl className="fields">
        {visible.map(([key, value]) => (
          <div key={key}>
            <dt>{label(key)}</dt>
            <dd>
              {key === "body" || key === "subject" || key === "title"
                ? text(value)
                : fieldValue(value, key)}
            </dd>
          </div>
        ))}
      </dl>
      {Object.keys(technical).length > 0 && (
        <Json title="Technical details" value={technical} />
      )}
    </>
  );
}
export function Section({
  title,
  subtitle,
  children,
  action,
  className = "",
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel ${className}`}>
      <header className="panel-head">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        {action}
      </header>
      {children}
    </section>
  );
}
export function Modal({
  title,
  children,
  onClose,
  wide = false,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  wide?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dialog = ref.current;
    const previous = document.activeElement as HTMLElement | null;
    dialog?.showModal();
    return () => {
      dialog?.close();
      previous?.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      className={wide ? "modal wide" : "modal"}
      aria-label={title}
      onCancel={onClose}
      onClick={(event) => {
        if (event.target === ref.current) onClose();
      }}
    >
      <header>
        <h2>{title}</h2>
        <button
          className="icon-button"
          aria-label="Close dialog"
          onClick={onClose}
        >
          <X size={20} />
        </button>
      </header>
      {children}
    </dialog>
  );
}
export function useRoute() {
  const [route, setRoute] = useState(location.hash.slice(1) || "/overview");
  useEffect(() => {
    const change = () => {
      setRoute(location.hash.slice(1) || "/overview");
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", change);
    return () => window.removeEventListener("hashchange", change);
  }, []);
  return route;
}
