# Handover

Open [the live demo](https://ai-production-incident-control-dash.vercel.app) and select **Explore the workspace**. The current cases are delayed steel rods, a stopped band saw, and mounting plates with oversized holes.

Source: [Mvstnz/ai-production-incident-control](https://github.com/Mvstnz/ai-production-incident-control), branch main. Use `git log -1 --oneline` for the checked-out commit.

Run locally with `python scripts/bootstrap.py`. Local account credentials are generated in ignored `.local/credentials.json`; hosted operational credentials are in ignored `.local/hosted-credentials.json`. Never commit either file.

Workflow IDs, tests, configuration and rollback steps: [deployment report](hosting.md).
