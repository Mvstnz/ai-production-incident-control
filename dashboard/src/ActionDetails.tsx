import { label, type Action } from "./api";
import { actionDescription } from "./presentation";
import { Fields, Json } from "./ui";

export function ActionDetails({ action }: { action: Action }) {
  const { incident_id, incident_revision, ...content } = action.payload;
  return (
    <div className="action-explanation">
      <p className="action-description">{actionDescription(action)}</p>
      {!!(content.body || content.subject) && (
        <p className="explanation-note">
          Genauer gespeicherter Nachrichtentext (Originalsprache). Die Freigabe
          bezieht sich auf diesen Inhalt.
        </p>
      )}
      <Fields data={content} />
      <Json
        title="Technische Referenz"
        value={{ action: action.action_type, incident_id, incident_revision }}
      />
    </div>
  );
}

export const actionName = (action: Action) =>
  ({
    INTERNAL_TICKET: "Produktionsplanung informieren",
    SUPPLIER_EMAIL: "Liefertermin bestätigen lassen",
    RESCHEDULE: "Schneideauftrag auf zweite Säge verlegen",
    QUALITY_BLOCK: "Betroffene Platten zurückhalten",
    QUALITY_RELEASE: "Geprüfte Platten freigeben",
  })[action.action_type] || label(action.action_type);
