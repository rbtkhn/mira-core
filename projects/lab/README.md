# Operational Ideas Lab

Status: working structure; first pilot prepared, no experiment executed

## Working loop

Source passage -> operational hypothesis -> project task -> comparison ->
observed result -> retain, revise, reject, or defer.

Start at the [hypothesis register](hypotheses.md) and [pilot queue](pilot-queue.md).
Use the [experiment template](experiment-template.md) to prepare a comparison
and the [result template](result-template.md) after a run is authorized.
The first [Media Production / Grace Gems pilot](pilots/MP-GG-001.md) is ready
for review but has no run results. The [recording examples](recording-examples.md)
are fictional format checks, not experiments or outcome evidence.

## Operating sequence

1. Name a worthwhile project problem; check the queue before adding work.
2. Read a relevant source passage through the [research connection](../singularity-science/README.md).
   Record attribution, limits, Mira's translation, and a rival explanation.
3. Prepare fixed inputs, comparison, quality floor, effort accounting, reviewer,
   stop conditions, and decision rule before execution.
4. Obtain the exact run scope. Prepared does not mean activated. Live evidence
   access and external activity remain separately governed.
5. Run only that scope; preserve deviations and failed attempts. Use fresh
   contexts where carryover could bias comparison. Do not silently repair an
   output before review or discard inconvenient cases.
6. Record results and link them to the hypothesis. The reviewer chooses retain,
   revise, reject, or defer. Review at completion or a stated stop, not on a
   scheduler. Any local adoption needs an explicit scope and limits.

## Records and evidence states

- Hypotheses use `H-001`, `H-002`, etc.; stable IDs are not reused.
- Experiments use a project prefix and sequence, first `MP-GG-001`. Increment
  the protocol version when the comparison changes. Changes after starting a
  run are deviations, not silent edits to the original protocol.
- Authorized runs use result files under `results/`, named by experiment ID,
  run date, and sequence, linking to the hypothesis and protocol version.
- Evidence states: `source-derived proposal`, `prepared test`, `observed result`,
  `locally adopted practice`. A failure can be an observed result.
- Disposition is separate: `retain` keeps a hypothesis available, not adopted;
  `revise` preserves the old formulation and the change; `reject` retains the
  reason; `defer` names missing evidence/capacity and a return condition.
- Local adoption requires an explicit reviewer decision, supporting result
  links, use context, remaining limits, and revision trigger. It does not
  change another project's controls or enter a recursive-learning ledger.

## What counts as useful

Measure acceptable work and total human effort: task preparation, intervention
construction, supervision, review, correction, and error recovery. Show one-time
setup separately and include it in initial totals; do not assume future volume
will amortize it. Keep per-case results and denominators. Record agent time,
token use, and cost when measured; otherwise write `Missing`. Do not infer
human savings from tokens or zero effort from silence.

Quality and boundary failures cannot be offset by speed. Preserve intentional
human judgment, learning, and authorship; reducing all human participation is
not the objective. Label simulations, replays, and live work separately. A
simulation reveals feasibility and failure modes, not commercial impact,
causal certainty, or general validity of a source's theory.

## Authority and persistence

The implementation request establishes this lab and prepares its pilot only.
No experiment or runtime is activated. Real customer, family, donor, property,
and financial evidence stays in an approved private system. Git records may
contain sanitized conclusions and opaque references only when permitted by the
owning workflow. Transcript bodies remain in their archive.

The [Grace Gems controls](../grace-mar/grace-gems/README.md) remain intact. This lab imports
no Anyang approvals and authorizes no spending, communication, or automatic
adoption. No automated evaluator, database, CLI, or scheduled job is added.
Return to [Projects](../README.md).
