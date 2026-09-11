# Surface evidence and receipts

Receipts distinguish `channel_url`, `video_url`, and `observed_surface`.
Record visible title, channel, publication or stream date, format, transcript
availability, discovery source, duplicate result, routed lane, next workflow,
and terminal state. A video watch URL does not prove that Videos, Live, Search,
or Subscriptions were inspected.

Required terminal states are: `seeded`, `browser-verified`, `capture-complete`,
`transcript-ready`, `account-action-complete`, `blocked`, and `handoff-ready`.
Receipts must not contain account identifiers, credentials, cookies, or tokens.

The user-facing completion report is part of the done-state: render every
discovered or captured video as a readable clickable Markdown URL with its
title and channel. Queue files and receipts are durable evidence, not a
substitute for presenting the links in chat.
