---
name: mira-face
description: "Deprecated compatibility redirect for explicit mira-face requests only. Route to Mira Mind and the requested artifact workflow; ordinary public-facing work does not invoke this skill."
metadata:
  status: deprecated
---

# Mira Face â€” compatibility redirect

Mira Face no longer owns an independent workflow. Preserve the caller's
artifact, audience, scope, and action boundary while routing:

- Wording, biography, and identity claims: [Mira Mind](../mira-mind/SKILL.md).
- Websites and interactive surfaces: Mind plus the appropriate website workflow.
- Generated images or audio: Mind plus the appropriate media workflow.
- Recipient-specific correspondence: [Mira Letters](../mira-letters/SKILL.md).

For Mira's public-facing artifacts and local candidates intended for public
audiences, load Mind's [public-interface reference](../mira-mind/references/public-interface.md).
Ordinary private dashboards and conversation do not require it. If an explicit
request names no artifact or purpose, ask only for that missing scope.

The existing landing-page implementation remains available through the reference.
This redirect grants no retention, sending, publication, deployment, account,
or representation authority. Keep it repository-local; do not synchronize it.
