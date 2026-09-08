# ADR 0005 — Administrator inherits application roles

**Status:** Accepted user override · **Date:** 8 September 2026

## Context

The original build specification separated the administrator's reliability
duties from business approvals. During the live-demo review, the user explicitly
requested that the authenticated admin account be able to perform every action
available to Purchasing, Production and Quality roles.

## Decision

`admin` is the application superuser. A role gate accepts an authenticated admin
wherever it accepts another application role. The UI uses the same hierarchy for
approval controls and Quality release proposals. The audit actor remains the
actual admin user; the system does not impersonate or rewrite the actor's role.

This override changes role authorization only. Authentication, allowed Origin,
CSRF, scope membership, immutable plan version and hash, current-state checks,
action claims, recipient allowlists and external-action restrictions remain in
force.

## Consequences

An admin can approve, reject or modify any pending business-role request and can
invoke every other role-restricted application command within an assigned scope.
Compromise of an admin account therefore has greater impact, so generated admin
credentials must remain private and public demos should use the read-only viewer
account. Existing specialist roles retain least-privilege behavior.
