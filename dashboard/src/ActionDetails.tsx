import { label, type Action } from "./api";
import { actionDescription } from "./presentation";
import { Fields, Json } from "./ui";

export function ActionDetails({ action }: { action: Action }) {
  const { incident_id, incident_revision, ...content } = action.payload;
  return (
    <div className="action-explanation">
      <p className="action-description">{actionDescription(action)}</p>
      <Fields data={content} />
      <Json
        title="Technical reference"
        value={{ action: action.action_type, incident_id, incident_revision }}
      />
    </div>
  );
}

export const actionName = (action: Action) =>
  ({
    INTERNAL_TICKET: "Notify production planning",
    SUPPLIER_EMAIL: "Confirm supplier delivery",
    RESCHEDULE: "Move the cutting job",
    QUALITY_BLOCK: "Hold the affected plates",
    QUALITY_RELEASE: "Release the inspected plates",
  })[action.action_type] || label(action.action_type);
