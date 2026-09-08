# Portfolio narrative

This project demonstrates how a manufacturing incident becomes a controlled operational decision. The examples use familiar items: delayed steel rods, a broken band saw and mounting plates with oversized holes.

The interesting engineering work is the boundary between source claims, verified ERP facts, calculated impact and approved actions. An early supplier offer cannot silently become confirmed stock. A machine with the wrong capability cannot be treated as spare capacity. A batch-level defect must be traced to specific shipments before a blocking proposal is approved.

Ten n8n workflows make the process visible. Python owns deterministic calculations and transactional state changes. Supabase PostgreSQL stores the evidence, and Vercel hosts the application. A public visitor can inspect the three cases while operational roles can create isolated runs.

The hosted system uses fixture extraction and captures messages in a sandbox. Live language-model accuracy and real ERP integration are separate claims and are not implied by this demonstration. Current evidence is linked from the repository README and deployment report.
