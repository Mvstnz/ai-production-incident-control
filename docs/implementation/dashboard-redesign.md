# Guided dashboard — 2026-09-08

The user requested a German interface that explains the manufacturing use case before exposing operational evidence. The public entry now foregrounds browsing without an account; team sign-in is secondary. The overview introduces three ordinary cases and the sequence report → impact → proposal → decision.

Each case reads the existing incident API. Quantities, affected orders, dates, proposals, roles and approval states come from persisted results. Quality impact uses affected sales positions rather than the empty production-order list. The simple decision view shows the current plan; earlier plans remain in the expandable evidence/history. Step navigation is read-only. Actual decisions still use the existing role, CSRF, exact-version and hash checks.

Gemini has a dedicated mail page and an explanation of its role. The runtime catalog controls whether submission is available. Only authorized team members can submit; public visitors can inspect the stored cases. Existing message bodies stay in their original language so the displayed approval content remains exact. n8n orchestration, database calculations and human authorization are described separately.

Local verification for this change: TypeScript/Vite production build passed; 112 unit tests passed; all 34 PostgreSQL/API integration tests passed, including AI budget and authorization boundaries. Browser checks verified all three guided cases: supplier 40 pieces / two orders / €55,400; saw 10 hours / two orders / €41,200; quality 48 pieces / two positions / €26,400. Responsive checks at 390×844 verified no document overflow and working mobile navigation. Technical inspection remains available in the secondary view, including English original evidence.

Hosted Gemini configuration uses the already attached credential and `models/gemini-3.1-flash-lite`, verified through the cloud node's live model resource listing. The configured total reservation limit is 20 provider calls. Re-running hosting preparation preserves this explicit configuration; fresh environments still default to provider calls disabled. Execution evidence is recorded separately after a real hosted mail run.

LinkedIn: the earlier post was deleted at the user's request. No new post may be published before the user approves its final draft.
