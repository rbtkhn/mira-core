# Grok Claim Ledgers

This directory is the pre-synthesis intake layer for external Grok research.

Grok output enters here as `grok-reported-unverified` claims with report provenance,
source URLs, and source-independence notes. It is not archive truth, a reality-lattice
claim, or a publication-ready finding. Claims may be promoted only after a bounded
verification packet establishes the required evidence standard.

Workflow:

```text
Grok report -> claim ledger -> duplicate/source-chain review -> VER packet
-> human assessment -> optional reality-lattice promotion -> synthesis
```

Rules:

- Preserve the original Grok wording or a faithful short paraphrase.
- Keep event date and publication date separate.
- Treat repeated URLs or reports derived from one originating report as one evidence chain.
- Never convert `confirmed` in a Grok report into repository-confirmed fact automatically.
- Link every promoted claim to its completed `VER-*` packet.

