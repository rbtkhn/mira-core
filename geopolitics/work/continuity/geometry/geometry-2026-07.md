# Narrative Geometry

## Decision Summary

- Range: 2026-07-01 through 2026-07-31; nodes: 206; edges: 346; counter-pressure gaps: 47
- Graph quality: {'node_counts': {'source': 122, 'host': 19, 'voice': 31, 'object': 7, 'forecast': 20, 'reality': 7}, 'edge_counts': {'routed_through': 122, 'appeared_in': 122, 'addressed': 59, 'shared_object': 32, 'linked_to': 8, 'forecasted': 3}, 'edges_with_source_ids': 338, 'edges_with_lineage_basis': 0, 'unsupported_candidates': 0, 'generic_only_rejections': 0, 'unmapped_voice_count': 15, 'unresolved_object_count': 0, 'counter_pressure_gap_count': 47, 'shared_host_edges': 5, 'shared_lineage_edges': 0, 'confidence_distribution': {'bounded': 346}}

## Graph Coverage

- Audited dates: 2026-07-01, 2026-07-02, 2026-07-03, 2026-07-04, 2026-07-05, 2026-07-06, 2026-07-07, 2026-07-08, 2026-07-09, 2026-07-10, 2026-07-11, 2026-07-12, 2026-07-13, 2026-07-14, 2026-07-15, 2026-07-16, 2026-07-17, 2026-07-18, 2026-07-19, 2026-07-20
- Skipped dates: 2026-07-21, 2026-07-22, 2026-07-23, 2026-07-24, 2026-07-25, 2026-07-26, 2026-07-27, 2026-07-28, 2026-07-29, 2026-07-30, 2026-07-31

## Crisis-Object Geometry

- `bab-el-mandab`: first appearance from 2026-07-20 to 2026-07-20 (1 dates)
- `basing`: persistent from 2026-07-08 to 2026-07-14 (3 dates)
- `gulf-access`: persistent from 2026-07-13 to 2026-07-20 (5 dates)
- `hormuz`: persistent from 2026-07-03 to 2026-07-16 (7 dates)
- `maritime-access`: first appearance from 2026-07-20 to 2026-07-20 (1 dates)
- `red-sea`: first appearance from 2026-07-16 to 2026-07-16 (1 dates)
- `russia-nato`: persistent from 2026-07-01 to 2026-07-20 (18 dates)
- `saudi-access`: first appearance from 2026-07-13 to 2026-07-13 (1 dates)

## Voice-Host Conditioning

- voice:aguilar -> voice:barnes; hosts=unhosted; basis=manifest_cooccurrence
- voice:davis -> voice:escobar; hosts=unhosted; basis=manifest_cooccurrence
- voice:davis -> voice:sachs; hosts=glenn-diesen; basis=shared_host
- voice:davis -> voice:weichert; hosts=unhosted; basis=manifest_cooccurrence
- voice:escobar -> voice:weichert; hosts=moral-resistance; basis=shared_host
- voice:helmer -> voice:ritter; hosts=unhosted; basis=manifest_cooccurrence
- voice:jermy -> voice:davis; hosts=unhosted; basis=manifest_cooccurrence
- voice:jermy -> voice:krapivnik; hosts=unhosted; basis=manifest_cooccurrence
- voice:jermy -> voice:sachs; hosts=unhosted; basis=manifest_cooccurrence
- voice:johnson -> voice:escobar; hosts=unhosted; basis=manifest_cooccurrence
- voice:johnson -> voice:marandi; hosts=dialogue-works; basis=shared_host
- voice:krapivnik -> voice:sachs; hosts=glenn-diesen; basis=shared_host
- voice:macgregor -> voice:mercouris; hosts=unhosted; basis=manifest_cooccurrence
- voice:marandi -> voice:johnson; hosts=unhosted; basis=manifest_cooccurrence
- voice:marandi -> voice:parsi; hosts=unhosted; basis=manifest_cooccurrence
- voice:mearsheimer -> voice:helmer; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:davis; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:helmer; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:helmer; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:helmer; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:jermy; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:krapivnik; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:krapivnik; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:krapivnik; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:matlock; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:mearsheimer; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:mearsheimer; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:ritter; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:sachs; hosts=unhosted; basis=manifest_cooccurrence
- voice:mercouris -> voice:sachs; hosts=unhosted; basis=manifest_cooccurrence
- voice:pape -> voice:johnson; hosts=unhosted; basis=manifest_cooccurrence
- voice:pape -> voice:marandi; hosts=mario-nawfal; basis=shared_host

## Convergence and Orthogonal Pressure

- voice:aguilar <-> voice:barnes: shared object; objects=saudi-access
- voice:davis <-> voice:escobar: shared object; objects=bab-el-mandab
- voice:davis <-> voice:sachs: shared-host limitation; objects=russia-nato
- voice:davis <-> voice:weichert: shared object; objects=bab-el-mandab
- voice:escobar <-> voice:weichert: shared-host limitation; objects=bab-el-mandab
- voice:helmer <-> voice:ritter: shared object; objects=russia-nato
- voice:jermy <-> voice:davis: shared object; objects=russia-nato
- voice:jermy <-> voice:krapivnik: shared object; objects=russia-nato
- voice:jermy <-> voice:sachs: shared object; objects=russia-nato
- voice:johnson <-> voice:escobar: shared object; objects=hormuz
- voice:johnson <-> voice:marandi: shared-host limitation; objects=gulf-access
- voice:krapivnik <-> voice:sachs: shared-host limitation; objects=russia-nato
- voice:macgregor <-> voice:mercouris: shared object; objects=russia-nato
- voice:marandi <-> voice:johnson: shared object; objects=hormuz
- voice:marandi <-> voice:parsi: shared object; objects=hormuz
- voice:mearsheimer <-> voice:helmer: shared object; objects=russia-nato
- voice:mercouris <-> voice:davis: shared object; objects=russia-nato
- voice:mercouris <-> voice:helmer: shared object; objects=russia-nato
- voice:mercouris <-> voice:helmer: shared object; objects=russia-nato
- voice:mercouris <-> voice:helmer: shared object; objects=russia-nato
- voice:mercouris <-> voice:jermy: shared object; objects=russia-nato
- voice:mercouris <-> voice:krapivnik: shared object; objects=russia-nato
- voice:mercouris <-> voice:krapivnik: shared object; objects=russia-nato
- voice:mercouris <-> voice:krapivnik: shared object; objects=russia-nato
- voice:mercouris <-> voice:matlock: shared object; objects=russia-nato
- voice:mercouris <-> voice:mearsheimer: shared object; objects=russia-nato
- voice:mercouris <-> voice:mearsheimer: shared object; objects=russia-nato
- voice:mercouris <-> voice:ritter: shared object; objects=russia-nato
- voice:mercouris <-> voice:sachs: shared object; objects=russia-nato
- voice:mercouris <-> voice:sachs: shared object; objects=russia-nato
- voice:pape <-> voice:johnson: shared object; objects=hormuz
- voice:pape <-> voice:marandi: shared-host limitation; objects=hormuz

## Shared-Lineage Limits

- Shared-host edges: 5; shared-lineage edges: 0

## Object Transitions

- bab-el-mandab: first appearance
- basing: persistent
- gulf-access: persistent
- hormuz: persistent
- maritime-access: first appearance
- red-sea: first appearance
- russia-nato: persistent
- saudi-access: first appearance

## Operator Queries

- Hosts creating apparent convergence: ['dialogue-works', 'glenn-diesen', 'mario-nawfal', 'moral-resistance']
- Objects lacking counter-pressure: ['basing', 'maritime-access', 'russia-nato', 'unresolved-object']
- Distinct voices present: aguilar, barnes, baud, blumenthal, crooke, davis, escobar, freeman, helmer, henningsen, hoh, jermy, jiang, johnson, kent, krainer, krapivnik, macgregor, marandi, martyanov, matlock, mcgovern, mearsheimer, mercouris, pape, parsi, postol, ritter, sachs, weichert, wilkerson
- Changed since prior date: {'from_date': '2026-07-19', 'to_date': '2026-07-20', 'nodes_added': ['host:breaking-points', 'host:daniel-davis', 'host:judging-freedom', 'host:tucker-carlson', 'object:bab-el-mandab', 'source:SRC-20260720-01', 'source:SRC-20260720-02', 'source:SRC-20260720-03', 'source:SRC-20260720-04', 'source:SRC-20260720-05', 'source:SRC-20260720-06', 'source:SRC-20260720-07', 'source:SRC-20260720-08', 'source:SRC-20260720-09', 'source:SRC-20260720-10', 'source:SRC-20260720-11', 'source:SRC-20260720-12', 'source:SRC-20260720-13', 'voice:barnes', 'voice:baud', 'voice:blumenthal', 'voice:crooke', 'voice:davis', 'voice:escobar', 'voice:jermy', 'voice:mearsheimer', 'voice:ritter', 'voice:weichert'], 'nodes_removed': ['host:glenn-diesen', 'source:SRC-20260719-01', 'source:SRC-20260719-02', 'source:SRC-20260719-03', 'source:SRC-20260719-04', 'source:SRC-20260719-05', 'source:SRC-20260719-06', 'voice:krapivnik', 'voice:marandi', 'voice:mcgovern', 'voice:sachs'], 'edges_added': [('source:SRC-20260720-01', 'host:alexander-mercouris', 'routed_through'), ('source:SRC-20260720-02', 'host:judging-freedom', 'routed_through'), ('source:SRC-20260720-03', 'host:dialogue-works', 'routed_through'), ('source:SRC-20260720-04', 'host:judging-freedom', 'routed_through'), ('source:SRC-20260720-05', 'host:dialogue-works', 'routed_through'), ('source:SRC-20260720-06', 'host:tucker-carlson', 'routed_through'), ('source:SRC-20260720-07', 'host:breaking-points', 'routed_through'), ('source:SRC-20260720-08', 'host:judging-freedom', 'routed_through'), ('source:SRC-20260720-09', 'host:daniel-davis', 'routed_through'), ('source:SRC-20260720-10', 'host:judging-freedom', 'routed_through'), ('source:SRC-20260720-11', 'host:moral-resistance', 'routed_through'), ('source:SRC-20260720-12', 'host:daniel-davis', 'routed_through'), ('source:SRC-20260720-13', 'host:moral-resistance', 'routed_through'), ('voice:barnes', 'source:SRC-20260720-12', 'appeared_in'), ('voice:baud', 'object:gulf-access', 'addressed'), ('voice:baud', 'source:SRC-20260720-03', 'appeared_in'), ('voice:blumenthal', 'source:SRC-20260720-10', 'appeared_in'), ('voice:crooke', 'source:SRC-20260720-02', 'appeared_in'), ('voice:davis', 'object:bab-el-mandab', 'addressed'), ('voice:davis', 'source:SRC-20260720-09', 'appeared_in'), ('voice:escobar', 'object:bab-el-mandab', 'addressed'), ('voice:escobar', 'source:SRC-20260720-11', 'appeared_in'), ('voice:jermy', 'source:SRC-20260720-06', 'appeared_in'), ('voice:johnson', 'source:SRC-20260720-04', 'appeared_in'), ('voice:mearsheimer', 'source:SRC-20260720-05', 'appeared_in'), ('voice:mearsheimer', 'source:SRC-20260720-07', 'appeared_in'), ('voice:mercouris', 'source:SRC-20260720-01', 'appeared_in'), ('voice:ritter', 'source:SRC-20260720-08', 'appeared_in'), ('voice:weichert', 'object:bab-el-mandab', 'addressed'), ('voice:weichert', 'source:SRC-20260720-13', 'appeared_in')], 'edges_removed': [('source:SRC-20260719-01', 'host:alexander-mercouris', 'routed_through'), ('source:SRC-20260719-02', 'host:moral-resistance', 'routed_through'), ('source:SRC-20260719-03', 'host:glenn-diesen', 'routed_through'), ('source:SRC-20260719-04', 'host:glenn-diesen', 'routed_through'), ('source:SRC-20260719-05', 'host:moral-resistance', 'routed_through'), ('source:SRC-20260719-06', 'host:dialogue-works', 'routed_through'), ('voice:johnson', 'source:SRC-20260719-05', 'appeared_in'), ('voice:krapivnik', 'object:russia-nato', 'addressed'), ('voice:krapivnik', 'source:SRC-20260719-03', 'appeared_in'), ('voice:marandi', 'source:SRC-20260719-02', 'appeared_in'), ('voice:mcgovern', 'object:gulf-access', 'addressed'), ('voice:mcgovern', 'source:SRC-20260719-06', 'appeared_in'), ('voice:mercouris', 'source:SRC-20260719-01', 'appeared_in'), ('voice:sachs', 'object:russia-nato', 'addressed'), ('voice:sachs', 'source:SRC-20260719-04', 'appeared_in')]}

## Prioritized Review Queue

1. **P1** voice:davis × voice:sachs: shared-host limitation Action: confirm distinct mechanisms or recover independent lineage
2. **P1** voice:pape × voice:marandi: shared-host limitation Action: confirm distinct mechanisms or recover independent lineage
3. **P1** voice:johnson × voice:marandi: shared-host limitation Action: confirm distinct mechanisms or recover independent lineage
4. **P1** voice:krapivnik × voice:sachs: shared-host limitation Action: confirm distinct mechanisms or recover independent lineage
5. **P1** voice:escobar × voice:weichert: shared-host limitation Action: confirm distinct mechanisms or recover independent lineage

## Limitations and Non-Evidence Notice

- Generated: `2026-07-21T18:40:32.833498+00:00`
- Content hash: `2a763b2ef8ff163c`
- This is advisory generated state, not research evidence.
- Different voices are not independent evidence unless lineage independence has been established.
- Graph density and degree do not indicate authority, correctness, or evidentiary strength.
