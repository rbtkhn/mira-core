# Voice Continuity

Voice continuity is remembered interpretive pattern across sources and time.

It helps Narrative Geopolitics avoid treating every quote, essay, interview, or social post as isolated. A source-person's current claim often matters because it extends, revises, contradicts, or sharpens a longer pattern.

## Terms

- `voice`: a recurring source-person whose claims, frames, forecasts, contradictions, and source modalities matter across time.
- `voice record`: the durable continuity object for one voice.
- `voice surface`: any file that helps retrieve, interpret, or route a voice.
- `source modality`: the form through which the source entered the system, such as transcript, interview, essay, article, social post, stream, report, or mixed.

Use `voice`, not `speaker`, as the umbrella term. Use `speaker` only when the source is specifically a spoken appearance.

## Workflow Role

Voice continuity sits between source grounding and public judgment:

```text
source manifest
-> voice continuity check
-> channel conditioning check when host context matters
-> synthesis
-> daily brief
-> forecast / review hook
```

It can also support a dialogical path:

```text
bounded question + as-of date
-> source floor
-> voice continuity and channel conditioning
-> reconstructed response
-> disagreement / cross-examination
-> separate moderator synthesis
```

During a daily run, ask:

- Is this claim new for this voice?
- Is it part of a recurring claim family?
- Does it contradict an earlier claim or forecast?
- Is the claim shaped by its source modality?
- Does the voice have a relevant forecast history?
- Does the claim need direct quotation, paraphrase, or exclusion?

## Voice Records

Voice records live in `narrative-geopolitics/voices/`.

They are internal first. Public summaries should come later only when the record is stable, useful, and safe to expose as part of the public model.

Use `narrative-geopolitics/voices/_template.md` when adding a new voice.

## Boundary

Voice continuity is not source truth. It interprets recurring patterns after the source floor is identified.

Voice continuity is also not final judgment. It informs synthesis and briefs, but the daily run still has to name the crisis object, actor incentives, uncertainty, and forecast/review hook.

Voice continuity is not a persona specification. It must not license stylistic
impersonation, invented present opinion, or an inference presented as a quote.
Dialogical use is governed by [dialogue-contract.md](dialogue-contract.md).

Voice continuity is not channel conditioning. Use [../channels/](../channels/README.md) when the key question is how a host, show, or channel reshaped a guest's claims.
