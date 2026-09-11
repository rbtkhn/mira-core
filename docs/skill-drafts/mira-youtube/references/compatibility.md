# Legacy compatibility

The `youtube-capture` command remains the compatibility namespace for existing
queue, route, duplicate, receipt, transcript, and intake-draft operations.
Do not rename existing route identifiers, queue fields, target-note paths, or
archive lane names. Forwarding must preserve exit codes and output semantics.

Neither front door silently admits arbitrary sources or mutates manifests.
When transcript attachments exactly match the immediately preceding Mira
YouTube candidate list, the skill may invoke the governed `archive-intake`
workflow directly for those matches. This is current-bundle intent, not
standing permission for future or unmatched uploads. Use `archive-intake`,
`archive-query`, `archive-repair`, `geo-strategy`, or the appropriate
Singularity workflow for later stages.
