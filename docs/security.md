# Security boundaries and current controls

The release is a synthetic local demonstration. It does not connect to a real
production ERP, control machinery, buy goods or send to real recipients. The
Compose profile sets external actions off and exposes application ports only on
loopback. A cloud deployment needs a separately authorized network route,
credentials and validation before it can execute application workflows.

## Authentication and authorization

Browser users authenticate with generated local credentials. Argon2 stores
password hashes; sessions persist token hashes server-side. Roles are loaded from
the database rather than caller-supplied headers. Browser mutations validate the
allowed Origin and a session-bound CSRF token; navigation GETs do not approve
anything. Users must also have membership in the requested scope. Login and user
requests have process-local rate limits. The authenticated admin role is a
deliberate application superuser and inherits every business-role permission.
This does not bypass authentication, CSRF, scope membership, plan-version or
payload-hash checks. This user-authorized override is recorded in
[ADR 0005](adr/0005-admin-superuser.md).

Internal n8n routes require `X-Service-Token`. ERP reads and writes use separate
`X-ERP-Token` credentials. Constant-time comparison checks service credentials.
User sessions cannot substitute for a service credential, and knowing a service
credential does not create a browser identity or an approval role. The internal
service remains a privileged trust boundary, not a tenant-isolated public API.

The API buffers and bounds incoming streamed bodies at 128 KiB before parsing.
Canonical envelopes have typed fields, aware timestamps and bounded strings.
Free-form domain facts undergo separate schema, evidence, identity and
plausibility checks. Invalid requests receive safe messages; redaction removes
common secret patterns and URLs from stored error text.

## Approval and permitted effects

The action catalogue allows internal sandbox tickets, synthetic supplier email,
mock rescheduling and quality block/release. Supplier email always needs an
appropriate purchasing or manager approval, including LOW incidents. Mock
rescheduling requires a production manager. Quality block and release require a
quality manager; release additionally requires separate disposition evidence.
CRITICAL plans require responsible-manager review.

The plan hash binds its incident revision, impact assessment, policy version,
plan version and full body. That body includes recipients, subject, message and
write parameters. The backend verifies current plan/hash, approval status and
claim before dispatch. Changes create a new version and supersede unexecuted
work; already executed effects are retained in the audit trail.

n8n Wait URLs are internal wakeup references. Registration limits the origin and
`/webhook-waiting/` path and rejects query strings, fragments and userinfo. A
resumed workflow reloads the database approval; the wakeup payload is not an
authorization. The browser does not receive a Wait URL.

The mail adapter permits `supplier@example.test` and only local Mailpit hosts.
There is no general-purpose SMTP/API destination taken from a message or model.
ERP commands require a matching current action claim, exact payload and approved
plan; a boolean `approved` supplied by a caller is insufficient. Receipts bind
action IDs to payload hashes.

## Untrusted AI and source data

The runtime fixture provider recognizes only the supplied synthetic email and
verified structured inputs. Unknown text, missing years/IDs, inconsistent
amounts, unsupported attachments and instruction-like content route to manual
review. No source text can enable tools, issue SQL/shell commands, change
recipients or cause a URL fetch. The fixture mode is labeled simulated AI.

Risk and severity come from versioned deterministic functions. Generated text is
accepted only through the grounding gate; the current implementation replaces
unverified prose with a deterministic template. No self-reported confidence
threshold grants authority. Live-model evaluation has not run.

## Secrets, storage and operations

Local bootstrap stores generated secrets only in ignored local files and binds
them through environment variables or n8n credentials. `.env.example` contains
placeholders. Workflow exports must be redacted; execution payloads, credentials
and instance-specific private configuration are not public sample data. Secret
scan evidence, rather than this document, determines the export acceptance gate.

PostgreSQL separates application, ERP, migration and n8n roles. The application
runtime role cannot update/delete audit records. Immutable-record triggers add
protection against accidental history modification; this is not cryptographic
tamper evidence against a database administrator. n8n execution pruning is
configured, while application retention and backup exercises remain separate
operational work.

Unknown write outcomes are retained for reconciliation. The scheduler does not
blindly replay them. Scope reset requires the owner and rejects in-flight or
unknown actions. Reset and deployment are limited to project-owned resources;
foreign workflows are outside the task's mutation boundary.

## Verification limits

These controls describe reviewed source behavior. They do not establish a
completed penetration test, production readiness, or passage of every security
acceptance criterion. Read the current acceptance evidence for tested cases.
Loopback HTTP configuration and development cookie settings must not be reused
for a public deployment without HTTPS/session configuration and another review.
Rate-limit counters are per-process and are not a distributed abuse-control
service. Secrets present on the host remain accessible to a host administrator.
