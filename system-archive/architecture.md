# System Archive Epistemic Architecture

System Archive has five layers: immutable SHA-256/Zstandard objects; typed and
versioned records; append-only events; neutral typed provenance relationships;
and reproducible views. SQLite stores indexed typed edges while preserving a
future graph-export boundary.

`world_valid_from` and `world_valid_to` describe when material applies;
`observed_at` records when the archive possessed it; `transaction_time` records
catalog insertion. Epistemic `--as-of` reconstruction uses `observed_at`.

Generated artifacts identify inputs, transformation, producer, determinism,
configuration or prompt digest, output digest, and evaluations. V1 creates
deterministic context packs and external-only replay plans, invokes no model,
and never retains hidden reasoning.

```text
episode -> outcome -> evaluation -> lesson candidate -> controlled comparison
        -> policy or skill candidate -> operator promotion -> versioned behavior
```

Experiments remain noncanonical until promotion and cannot automatically alter
instructions, skills, belief, authority, or Mira identity. Later stages add
external replay adapters, multimodal derivations, governed learning experiments,
and federated portable memory.
