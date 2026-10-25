# Same-assistant surface-to-request review

2026-10-25. Reviewer: Codex, the same assistant preparing the paper/audit. This is a non-blinded inspection of the 30 selected request surfaces against canonical requests, with access to existing labels. It is not independent annotation, inter-annotator agreement or a fresh validation set. Principal is supplied separately and need not be restated in the surface. The separate 600-case rule check tests worlds/canonical requests, not natural-language interpretation.

No explicit surface/canonical field contradiction was identified in this sample. This does not establish that a different annotator would infer every canonical interpretation. In particular, an omitted start being resolvable, a year-only snapshot being unresolved, and a future request being prohibited depend on benchmark conventions. The deliberately explicit “wrong scope” wording is artificial and may make the synthetic task easier than production requests. External review should flag these assumptions rather than merely reproduce labels.

| Scenario ID | Surface/canonical correspondence inspected |
|---|---|
| MB3-0189A9B7B1A448AF | DSO alias, 2025, explicit v1 |
| MB3-04AAB17E9F490952 | Margin alias, 2024; finance principal supplied separately |
| MB3-04C594368D445617 | SLA alias, customer tier, 2025 |
| MB3-079BC6EF4B420C13 | Active subscriptions alias, billing term, end-of-2025 point operation |
| MB3-0BD79128B523277E | Expansion alias, end 2024 and expressly missing start; resolvability is contract-dependent |
| MB3-0D91C82676E9DE34 | Backlog alias, 2023, no explicit point/sum operation; snapshot ambiguity is contract-dependent |
| MB3-1746DCB429BAAED3 | Opened-cases alias, 2027; future prohibition depends on supplied clock and policy |
| MB3-1A29930BF32517E1 | Escalations alias, end-of-2025 point, explicit v99 |
| MB3-1AE21D0C7B7734FC | Seller-count alias, product dimension, end-of-2025 point |
| MB3-1B6E8E948F79595D | Expansion alias, 2025 |
| MB3-227274F14E078DAE | AOV alias, explicitly reversed 2025–2024 interval |
| MB3-2707D4986E805CAD | Refund-rate alias, start 2024 and expressly absent end |
| MB3-2D82B2345F5B87B4 | Margin alias, 2025, no explicit row scope |
| MB3-2E8A3AE25A8A405B | Net-sales alias, seller tier, 2025 |
| MB3-2FD4D18AD4D4DFB8 | Backlog alias, 2025, explicit period-sum operation |
| MB3-3C3FC895A74723C4 | Bookings alias, 2025, explicit invoice-to-legal-entity path |
| MB3-3CD9CDD7BE99CF74 | Backlog alias, year-end-2025 point; vendor principal separately supplied |
| MB3-3D95D98CC07D8FC8 | NRR alias, 2025, explicit v1 |
| MB3-440DAB20CB1AE084 | Response-time alias, fiscal 2024 |
| MB3-4665298BEC0D77E3 | Orders alias, 2025, explicit order-to-order-line path |
| MB3-49F52821E3BD2AA6 | GRR alias, no date or version |
| MB3-51F4694C0390954D | Net-sales alias, explicit 2024–2025 interval |
| MB3-5E74299112CA2D4E | Refund-rate alias, 2024; guest principal separately supplied |
| MB3-66BEEBFDDE9C9C35 | Margin alias, 2024, certified definition explicitly requested |
| MB3-68CF87D6FF06972F | Closed-cases alias, priority dimension, 2025 |
| MB3-70B8A16BBA77F27A | Margin alias, 2025, explicit wrong_scope rendered “wrong scope”; artificial wording flagged |
| MB3-7B63846901B61E06 | Retention reference retained unresolved, 2024 |
| MB3-AD046433212AAA42 | MRR alias, plan family, year-end-2025 point |
| MB3-B53F8D0688139975 | Attributed-sales alias, 2023, explicit EUR target |
| MB3-DE04074C771208F1 | Resolution-rate alias, 2025 |

The unannotated review-packet.json omits canonical fields and labels. An independent reviewer should receive it with REVIEWER-CONTRACT.md, without this file or the result reports until their annotations are frozen.
