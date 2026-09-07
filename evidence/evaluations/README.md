# Fixture evaluation evidence

Run `python tests/evaluations/run_fixture_eval.py` from the repository root.
The checked-in dataset contains 50 synthetic cases, with 30 development and 20
holdout cases frozen by SHA-256 before the first run. The creation tool refuses
to overwrite it; future prompt tuning requires a new dataset/holdout version.

The observed fixture run made zero model calls. All 50 expected processing or
review decisions matched. Mandatory review recall was 20/20 development and
12/12 holdout. Critical facts matched in 10/10 eligible development and 8/8
eligible holdout cases; none of the 18 automatically processed cases invented
critical facts. Automatic processing was 33.3% development and 40% holdout.

Incident-type accuracy was 26/30 development and 18/20 holdout. Unknown messages,
injections and unsupported attachments may be reviewed before classification.
The 95% live-model type-accuracy target is therefore **not demonstrated** by
these fixture results. Exact known-email mapping and typed API/form validation
are not evidence of free-text model quality. The JSON report records the actual
latency distribution, field-level numerators/denominators and every case result.

**LIVE_EVAL_NOT_RUN.** No authorized configured live-model credential, model and
call/cost budget were available for this run. No live-adapter success or live
quality gate is claimed. Duplicate inputs here check deterministic normalization;
durable deduplication, provider effects and workflow execution belong to separate
integration evidence.
