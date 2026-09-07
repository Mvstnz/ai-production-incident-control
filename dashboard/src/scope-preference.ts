import type { Scope, Session } from "./api";

// A UI preference only. Memberships from login / auth-me remain authoritative.
const key = (session: Session) =>
  `apic.scope.v1:${session.user.id}:${session.user.role}`;

export function rememberScope(session: Session, scopeId: string): void {
  try {
    if (scopeId) localStorage.setItem(key(session), scopeId);
    else localStorage.removeItem(key(session));
  } catch {
    // Browsers that disallow local storage still support the in-memory selection.
  }
}

export function restoreScope(session: Session, memberships: Scope[]): string {
  let saved = "";
  try {
    saved = localStorage.getItem(key(session)) || "";
  } catch {
    // Use an authorized default when preferences cannot be read.
  }
  const selected = memberships.some((scope) => scope.id === saved)
    ? saved
    : memberships[0]?.id || "";
  rememberScope(session, selected);
  return selected;
}
