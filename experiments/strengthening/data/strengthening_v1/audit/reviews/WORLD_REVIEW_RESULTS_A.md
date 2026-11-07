# Dimension-level review results for 60 worlds: A


This review covers 60 worlds, 120 paired questions, and 183 required facts. All 60 overall world judgments and all 240 dimension-level judgments are `pass` (no annotation issues requiring correction were identified).

## World 01: 9ed5c47057168100a21bdc8c7cf7

Question IDs: `7372f8da9bfcc833658a55c809c5`, `0c51c0b4918f467ffb8710fb18fd`.

Collection IDs: `83a3a46112fe1203e5c524c974e9`, `9b365ba139e8eef59a60c0a91ca9`.

Entity: Veloria-9ED5C470; Rendering: list; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: release_code = Permit-R21; review_days = 7 working days.

**D1 Consistency of required facts with the original text: pass**

The question asks for the R3 release code and review interval; Permit-R21 in S01 and 7 working days in S04 match these two required facts, respectively.

Evidence: S01, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each list assertion contains Veloria-9ED5C470, R3, the field, and its value; the 13 release-code assertions (including the original) cannot substitute for the review interval in S04.

Evidence: S01, S04.

**D3 Temporal and revision status: pass**

2035-06-01 falls within the validity period of R3; R2/Permit-R66 in S02 should be obsolete, whereas S05 assigns the old code to R3 and should be contradictory.

Evidence: S01, S02, S05.

**D4 Source policy: pass**

The question restricts sources to 9ed5c4705716.registry.invalid; S01/S04 are allowed, whereas the consortium.invalid source of S05 is not. Source identity and factual contradiction are separate checks.

Evidence: S01, S04, S05.

**Findings for this world**

- Complementary support is distributed across operative-record and operative-part-1; both facts must be retained.
- Identical values for the Annex entity do not concern the subject of this question.

**Original-text evidence index**

- **S01**: chunk `68e6f65479806d015781f377ba65`, claim `ab1b68a6338d0ff1b62573453bad`, Character span `[474, 553)`; Source `https://9ed5c4705716.registry.invalid/replica-2`.
  > - Entity Veloria-9ED5C470; revision R3; release authorization code: Permit-R21.
- **S04**: chunk `cfe34e7b87c7fb197e8cd6ee1695`, claim `d6be94398b0eb51bd7f3ba5fbda4`, Character span `[508, 585)`; Source `https://9ed5c4705716.registry.invalid/operative-part-1`.
  > - Entity Veloria-9ED5C470; revision R3; file review interval: 7 working days.
- **S02**: chunk `465e9892672a58815abd659ecc74`, claim `5496ca0a5e9517532e2251877863`, Character span `[481, 560)`; Source `https://9ed5c4705716.registry.invalid/archive`.
  > - Entity Veloria-9ED5C470; revision R2; release authorization code: Permit-R66.
- **S05**: chunk `8ceed72720ec7ac0de035b69d210`, claim `79164c70aee449350c6ede203682`, Character span `[492, 571)`; Source `https://9ed5c4705716.consortium.invalid/disputed`.
  > - Entity Veloria-9ED5C470; revision R3; release authorization code: Permit-R66.

## World 02: decda79e6f4b61953c78887e7115

Question IDs: `a569c73c973a3e37b95938c1562c`, `4ac8e6080fea8144e72de087c42c`.

Collection IDs: `64069350f4463f534e28bf4105aa`, `f718f3c7322a886c9b3eec1ef8c6`.

Entity: Veloria-DECDA79E; Rendering: list; Support structure: equivalent_support; Required fact count: 4; Overall judgment: **pass**.

Required facts: release_code = Permit-K32; route = Juniper-76; review_days = 21 working days; retention_days = 60 calendar days.

**D1 Consistency of required facts with the original text: pass**

The four requested fields correspond to Permit-K32, Juniper-76, 21 working days, and 60 calendar days; the R3 values in S04/S01/S06/S03 agree with them.

Evidence: S04, S01, S06, S03.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each list span fully binds the subject and R3; support from the four separate chunks and from the complete independent-current chunk forms alternative sets, rather than two sets that must both be present.

Evidence: S01, S03, S04, S06.

**D3 Temporal and revision status: pass**

R3 covers the query date; Permit-M34 under R2 is obsolete, whereas Permit-M34 under R3 conflicts with the current Permit-K32. The distinct negative labels are appropriate.

Evidence: S04, S07, S08.

**D4 Source policy: pass**

The question imposes no source-prefix restriction, so S07 on consortium is an allowed source despite its contradictory content; the designated operative-record page must not replace the allowed-source policy.

Evidence: S07, S04.

**Findings for this world**

- There are alternative support paths for the four fields; complete support sets are related by OR.
- Correct values in Annex do not support the target entity.

**Original-text evidence index**

- **S04**: chunk `5ee2b697efa208f022e21f6f784f`, claim `cbf4c9762c675479b55d63fab664`, Character span `[1864, 1943)`; Source `https://decda79e6f4b.registry.invalid/operative-record`.
  > - Entity Veloria-DECDA79E; revision R3; release authorization code: Permit-K32.
- **S01**: chunk `af0758625c1a88494c5d37147e0f`, claim `7c60a7d0c719d2d933c41e0f378a`, Character span `[1847, 1913)`; Source `https://decda79e6f4b.registry.invalid/operative-part-1`.
  > - Entity Veloria-DECDA79E; revision R3; service route: Juniper-76.
- **S06**: chunk `811186a1dc7593ff0a17ab7eea70`, claim `f9fe70b0aa7f0398d6eb868694c0`, Character span `[2021, 2099)`; Source `https://decda79e6f4b.registry.invalid/independent-current`.
  > - Entity Veloria-DECDA79E; revision R3; file review interval: 21 working days.
- **S03**: chunk `a5a3c6a137a4a7e897851855d722`, claim `cf858feaf23ae0922a5b742a7536`, Character span `[1818, 1902)`; Source `https://decda79e6f4b.registry.invalid/operative-part-3`.
  > - Entity Veloria-DECDA79E; revision R3; archival retention period: 60 calendar days.
- **S07**: chunk `26fa04099ef0a0a45b5b0d3f5bae`, claim `fc00393d1db583e8880c67e6893d`, Character span `[1877, 1956)`; Source `https://decda79e6f4b.consortium.invalid/disputed`.
  > - Entity Veloria-DECDA79E; revision R3; release authorization code: Permit-M34.
- **S08**: chunk `fa2a9930d218a4ce6ce8a30195e9`, claim `e22f49d4b1823255052792e90725`, Character span `[1904, 1983)`; Source `https://decda79e6f4b.registry.invalid/archive`.
  > - Entity Veloria-DECDA79E; revision R2; release authorization code: Permit-M34.

## World 03: 5d003b94793caa20e5577314724d

Question IDs: `a757ec72b9094adb5e0466fabeac`, `c6c9286fc1cc46d62ec29b9756ec`.

Collection IDs: `acb014b1729484430ea927e4e6d6`, `9ef3a15e1b6477e5c90644fbbbe4`.

Entity: Veloria-5D003B94; Rendering: list; Support structure: position; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Aster-50; retention_days = 180 calendar days; review_days = 3 working days.

**D1 Consistency of required facts with the original text: pass**

The R5 question requests the route, retention period, and review interval; S01=Aster-50, S03=180 calendar days, and S05=3 working days agree with the fact table.

Evidence: S01, S03, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

All three list spans contain the subject, revision, predicate, and value; the key assertions occur at approximately characters 3184–3321, and their late position does not invalidate full-text support.

Evidence: S01, S03, S05.

**D3 Temporal and revision status: pass**

R5 applies on the query date; R4/Aster-83 in S06 is obsolete, whereas R5/Aster-83 in S08 is a conflicting value under the same revision and cannot serve as a valid route.

Evidence: S01, S06, S08.

**D4 Source policy: pass**

An empty prefix list means sources are unrestricted; registry and consortium are both allowed, but source permission does not correct the erroneous route in S08.

Evidence: S01, S08.

**Findings for this world**

- The assertion-position scenario requires checking complete spans rather than bare values; all three annotated spans here contain complete assertions.
- The 13 route assertions (including the original) still do not cover the other two fields.

**Original-text evidence index**

- **S01**: chunk `5cc7fbf72e252a6941c8329daa08`, claim `15a2aee067c2959829dcf6324c30`, Character span `[3184, 3248)`; Source `https://5d003b94793c.registry.invalid/replica-7`.
  > - Entity Veloria-5D003B94; revision R5; service route: Aster-50.
- **S03**: chunk `829e9850d8606228da490b275303`, claim `942922f2f08544d621070a17034e`, Character span `[3184, 3269)`; Source `https://5d003b94793c.registry.invalid/operative-record`.
  > - Entity Veloria-5D003B94; revision R5; archival retention period: 180 calendar days.
- **S05**: chunk `7d448d29da933cf3097c2d032f78`, claim `488e321bdaee31fb56d78839c028`, Character span `[3244, 3321)`; Source `https://5d003b94793c.registry.invalid/operative-record`.
  > - Entity Veloria-5D003B94; revision R5; file review interval: 3 working days.
- **S06**: chunk `170b7e9ffd03eefcd49f0e02e942`, claim `d4c6ec6ab62e73c14af10f3141b3`, Character span `[3259, 3323)`; Source `https://5d003b94793c.registry.invalid/archive`.
  > - Entity Veloria-5D003B94; revision R4; service route: Aster-83.
- **S08**: chunk `663d8a899aa167f1baacf24f5c5d`, claim `b16709627d7820ccec8cb1bfdf9c`, Character span `[3266, 3330)`; Source `https://5d003b94793c.consortium.invalid/disputed`.
  > - Entity Veloria-5D003B94; revision R5; service route: Aster-83.

## World 04: dc7967fc8538d480967a553acd64

Question IDs: `576948d42d3ee6b1ea1706f7eb0a`, `b11532af42b737dc6fa0821b83f9`.

Collection IDs: `87750ab16ed3a85e5c2a94b771a4`, `09ad6d545243527ff80e7e1d62fa`.

Entity: Veloria-DC7967FC; Rendering: list; Support structure: same_url_complementary; Required fact count: 4; Overall judgment: **pass**.

Required facts: release_code = Permit-R19; route = Cobalt-56; retention_days = 120 calendar days; review_days = 14 working days.

**D1 Consistency of required facts with the original text: pass**

The four required R6 values—Permit-R19, Cobalt-56, 120 calendar days, and 14 working days—can all be recovered individually from S01/S05/S06/S04.

Evidence: S01, S05, S06, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four short list assertions are individually self-contained; although they share the operative-record URL, they occupy different chunks, so a source hit cannot substitute for coverage of all four facts.

Evidence: S01, S04, S05, S06.

**D3 Temporal and revision status: pass**

R6 is valid on 2035-06-01; Permit-V14 under R5 belongs to the old revision, whereas Permit-V14 presented as R6 contradicts Permit-R19.

Evidence: S01, S02, S08.

**D4 Source policy: pass**

Sources are restricted to dc7967fc8538.registry.invalid; all four positive examples comply, whereas the consortium/disputed source of S08 violates this prefix restriction.

Evidence: S01, S04, S05, S06, S08.

**Findings for this world**

- In the same-URL complementary structure, one page or one code replica cannot count as support for four facts.
- The Annex chunks explicitly change the subject, supporting the irrelevant annotation.

**Original-text evidence index**

- **S01**: chunk `0a90fc0387e9e6dcaa40449c5b8e`, claim `21216d8dd6c7242f9bd6d35277ff`, Character span `[497, 576)`; Source `https://dc7967fc8538.registry.invalid/operative-record`.
  > - Entity Veloria-DC7967FC; revision R6; release authorization code: Permit-R19.
- **S05**: chunk `3560427dc5582121950f71a7084a`, claim `c0a2528f7dee6292df12567a716c`, Character span `[478, 543)`; Source `https://dc7967fc8538.registry.invalid/operative-record`.
  > - Entity Veloria-DC7967FC; revision R6; service route: Cobalt-56.
- **S06**: chunk `d8fe53a0a6dee2ac9a71451e4991`, claim `22f912378b5e5c961a5cc1f1d20d`, Character span `[500, 585)`; Source `https://dc7967fc8538.registry.invalid/operative-record`.
  > - Entity Veloria-DC7967FC; revision R6; archival retention period: 120 calendar days.
- **S04**: chunk `ebd96e153849307361c61e9166c5`, claim `66e5feff2601c1b3e9acdc9cbfc2`, Character span `[477, 555)`; Source `https://dc7967fc8538.registry.invalid/operative-record`.
  > - Entity Veloria-DC7967FC; revision R6; file review interval: 14 working days.
- **S02**: chunk `d9395b6638b7b40c347f86d3b344`, claim `2d964c7bda88639ec75bc1cc33cb`, Character span `[474, 553)`; Source `https://dc7967fc8538.registry.invalid/archive`.
  > - Entity Veloria-DC7967FC; revision R5; release authorization code: Permit-V14.
- **S08**: chunk `d1bc8bb4ec0b54ff92ad7bc45404`, claim `23f933ef90926510afe29177d39b`, Character span `[476, 555)`; Source `https://dc7967fc8538.consortium.invalid/disputed`.
  > - Entity Veloria-DC7967FC; revision R6; release authorization code: Permit-V14.

## World 05: e19e0a9d0cbfd471003d8bb55752

Question IDs: `5b730b7245c7e23a2336f93f49f4`, `31615d2d0955b2ee50f9de521ec3`.

Collection IDs: `cff57ab121d5169a36cb242f7ddd`, `395f42b6d1ee25ce51c0d483fb0a`.

Entity: Veloria-E19E0A9D; Rendering: list; Support structure: single_chunk; Required fact count: 2; Overall judgment: **pass**.

Required facts: retention_days = 60 calendar days; review_days = 3 working days.

**D1 Consistency of required facts with the original text: pass**

The question requests only the R8 retention and review periods; 60 calendar days in S01 and 3 working days in S02 correspond to those fields.

Evidence: S01, S02.

**D2 Complete assertions, complementary support, and alternative support: pass**

S01 and S02 each bind the subject, R8, and field within the same complete chunk; each of the 13 identical-content chunks already supports both facts.

Evidence: S01, S02.

**D3 Temporal and revision status: pass**

R8 applies on 2035-06-01; R7/180 calendar days is obsolete, whereas R8/180 calendar days in S06 conflicts with the current 60 days.

Evidence: S01, S03, S06.

**D4 Source policy: pass**

Only e19e0a9d0cbf.registry.invalid is allowed; the replicas and operative-record containing S01/S02 comply, whereas the consortium source of S06 does not.

Evidence: S01, S02, S06.

**Findings for this world**

- This world has complete support within a single chunk; the two fields must not be merged into one fact merely because they share a chunk.
- The Annex examples have identical values but a different subject and should be excluded.

**Original-text evidence index**

- **S01**: chunk `7863bd021867f20076ef2fb0ad79`, claim `086e606b35f4f092da6e13c9435f`, Character span `[888, 972)`; Source `https://e19e0a9d0cbf.registry.invalid/replica-10`.
  > - Entity Veloria-E19E0A9D; revision R8; archival retention period: 60 calendar days.
- **S02**: chunk `7863bd021867f20076ef2fb0ad79`, claim `978434e0b2a28e9b4340f99f6c1b`, Character span `[974, 1051)`; Source `https://e19e0a9d0cbf.registry.invalid/replica-10`.
  > - Entity Veloria-E19E0A9D; revision R8; file review interval: 3 working days.
- **S03**: chunk `34e9fde839091bffa20f11bd6ee2`, claim `52d0731a1eb9007f52c50260d7a7`, Character span `[884, 969)`; Source `https://e19e0a9d0cbf.registry.invalid/archive`.
  > - Entity Veloria-E19E0A9D; revision R7; archival retention period: 180 calendar days.
- **S06**: chunk `c411abe718f3ea63d1cb79d3bb0a`, claim `947d64b492138eff7b79f2389c57`, Character span `[873, 958)`; Source `https://e19e0a9d0cbf.consortium.invalid/disputed`.
  > - Entity Veloria-E19E0A9D; revision R8; archival retention period: 180 calendar days.

## World 06: dd0a8cf59b4246d424256e158073

Question IDs: `89ee3062096648a839c878dcf7ee`, `4b3f24e0aa5556d656f544280576`.

Collection IDs: `9c6970902861a2a00a88f9369789`, `cf153a50033e5cb406105ffac4e9`.

Entity: Veloria-DD0A8CF5; Rendering: list; Support structure: temporal_conflict; Required fact count: 3; Overall judgment: **pass**.

Required facts: release_code = Permit-M61; route = Cobalt-41; retention_days = 180 calendar days.

**D1 Consistency of required facts with the original text: pass**

Permit-M61, Cobalt-41, and 180 calendar days are supported by S08/S05/S12, respectively, exactly matching the three fields in the R6 question.

Evidence: S08, S05, S12.

**D2 Complete assertions, complementary support, and alternative support: pass**

All three valid spans are complete; even when the three old values occur together in a negative-example chunk, they are not alternative support for the three current facts.

Evidence: S05, S08, S12, S02, S03, S04.

**D3 Temporal and revision status: pass**

The old R5 values Permit-R40/Aster-63/60 days should be obsolete; S02–S04 bind these old values to R6 and should be contradictory rather than obsolete.

Evidence: S02, S03, S04, S09, S10, S11.

**D4 Source policy: pass**

Sources are unrestricted, so the consortium chunk with current-revision contradictions is also allowed; admission does not make its three contradictory assertions valid factual support.

Evidence: S02, S03, S04, S05.

**Findings for this world**

- All three fields have current-revision contradictions and old-revision comparisons; status requires checking both revision and value.
- With unrestricted sources, contradictory content can coexist with valid support; the annotations here distinguish them.

**Original-text evidence index**

- **S08**: chunk `732d2076906e7d6cf00cf7ef68e2`, claim `1840b4e80f4603a138398da8048e`, Character span `[1152, 1231)`; Source `https://dd0a8cf59b42.registry.invalid/operative-record`.
  > - Entity Veloria-DD0A8CF5; revision R6; release authorization code: Permit-M61.
- **S05**: chunk `b0aaa1b6a277151f9bf1ec1be611`, claim `e64d836c22b1c424ad372fc4fec8`, Character span `[1160, 1225)`; Source `https://dd0a8cf59b42.registry.invalid/operative-record`.
  > - Entity Veloria-DD0A8CF5; revision R6; service route: Cobalt-41.
- **S12**: chunk `5f5100bf310c58f1d316dd92006a`, claim `7cadd4cc321e00487ead9bf9aeae`, Character span `[1171, 1256)`; Source `https://dd0a8cf59b42.registry.invalid/operative-record`.
  > - Entity Veloria-DD0A8CF5; revision R6; archival retention period: 180 calendar days.
- **S02**: chunk `de34bd11c0fd111cc5ccf6278c6a`, claim `032890c6502032536242f2240275`, Character span `[1065, 1144)`; Source `https://dd0a8cf59b42.consortium.invalid/disputed`.
  > - Entity Veloria-DD0A8CF5; revision R6; release authorization code: Permit-R40.
- **S03**: chunk `de34bd11c0fd111cc5ccf6278c6a`, claim `3cc9e414383a128215954a5215ab`, Character span `[1146, 1210)`; Source `https://dd0a8cf59b42.consortium.invalid/disputed`.
  > - Entity Veloria-DD0A8CF5; revision R6; service route: Aster-63.
- **S04**: chunk `de34bd11c0fd111cc5ccf6278c6a`, claim `441a47e67fea9457b080acf67d98`, Character span `[1212, 1296)`; Source `https://dd0a8cf59b42.consortium.invalid/disputed`.
  > - Entity Veloria-DD0A8CF5; revision R6; archival retention period: 60 calendar days.
- **S09**: chunk `3bb2c152aa94f5243939351ea1b8`, claim `5102a44952c4df706cc1c0f0e2e3`, Character span `[1154, 1233)`; Source `https://dd0a8cf59b42.registry.invalid/archive`.
  > - Entity Veloria-DD0A8CF5; revision R5; release authorization code: Permit-R40.
- **S10**: chunk `3bb2c152aa94f5243939351ea1b8`, claim `e5e64cd48377dc8cc4c8d8c2ea0e`, Character span `[1235, 1299)`; Source `https://dd0a8cf59b42.registry.invalid/archive`.
  > - Entity Veloria-DD0A8CF5; revision R5; service route: Aster-63.
- **S11**: chunk `3bb2c152aa94f5243939351ea1b8`, claim `4fe20b54bdca654900980176ebe4`, Character span `[1301, 1385)`; Source `https://dd0a8cf59b42.registry.invalid/archive`.
  > - Entity Veloria-DD0A8CF5; revision R5; archival retention period: 60 calendar days.

## World 07: cbca62047199dc997da7715c147f

Question IDs: `c11890800fcc6d0e40a60450eda4`, `0d0eccacc919895b11efeb67a20d`.

Collection IDs: `0f368a8bef13e99edb4c56222be6`, `1bf15f2e1005f18780a9bc9cd27d`.

Entity: Veloria-CBCA6204; Rendering: prose; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: release_code = Permit-R64; review_days = 5 working days.

**D1 Consistency of required facts with the original text: pass**

The question asks for the R5 authorization code and review interval; the text explicitly gives Permit-R64 and 5 working days in S01 and S06, respectively.

Evidence: S01, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The prose sentences bind each field and value using “For entity ... in revision R5”; the code in operative-record and interval in operative-part-1 provide complementary support.

Evidence: S01, S06.

**D3 Temporal and revision status: pass**

R4/Permit-R85 is obsolete on the query date; R5/Permit-R85 contradicts the current Permit-R64. The obsolete and contradictory labels have direct textual support.

Evidence: S01, S03, S04.

**D4 Source policy: pass**

There is no prefix restriction, so S04 remains an allowed source despite being on consortium; its code contradiction is the reason it provides no valid support.

Evidence: S04, S01.

**Findings for this world**

- The 13 code assertions (including the original) do not supply the review interval; S06 remains necessary.
- The Annex subject and target entity have explicitly different names.

**Original-text evidence index**

- **S01**: chunk `03872f31fac3b53ad38618058fd1`, claim `1e0b6468f8304fe71465fc6e593f`, Character span `[1433, 1522)`; Source `https://cbca62047199.registry.invalid/replica-7`.
  > For entity Veloria-CBCA6204 in revision R5, the release authorization code is Permit-R64.
- **S06**: chunk `4c888668350381698560f2761538`, claim `54158188eb13b8b1a36f5b178262`, Character span `[1369, 1456)`; Source `https://cbca62047199.registry.invalid/operative-part-1`.
  > For entity Veloria-CBCA6204 in revision R5, the file review interval is 5 working days.
- **S03**: chunk `72809f40ebe902d355e93cf9caeb`, claim `1ee6b1a5017fab11e4c458f9dcab`, Character span `[1448, 1537)`; Source `https://cbca62047199.registry.invalid/archive`.
  > For entity Veloria-CBCA6204 in revision R4, the release authorization code is Permit-R85.
- **S04**: chunk `95ae61cd0997f1cf52d2a544cd9e`, claim `fbb67f24a1d9b7ba49cf8af5c4f9`, Character span `[1457, 1546)`; Source `https://cbca62047199.consortium.invalid/disputed`.
  > For entity Veloria-CBCA6204 in revision R5, the release authorization code is Permit-R85.

## World 08: 0725e021b81b943c49a35e6af7f2

Question IDs: `ce0e54cefc19c72848df1aba30a6`, `608cf257a248995e682aa2fd4b23`.

Collection IDs: `747c2da3f3941cd5e4afe4db43d2`, `db1fe05780ab685b09d3a3e848cc`.

Entity: Veloria-0725E021; Rendering: prose; Support structure: equivalent_support; Required fact count: 4; Overall judgment: **pass**.

Required facts: route = Cobalt-67; review_days = 5 working days; retention_days = 90 calendar days; release_code = Permit-R84.

**D1 Consistency of required facts with the original text: pass**

The R5 values Cobalt-67, 5 working days, 90 calendar days, and Permit-R84 all have current prose support from allowed sources.

Evidence: S06, S03, S01, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four separate sentences and the complete four-field independent-current chunk form alternative sets; the four sentences in the complete consortium chunk are also semantically complete, but source permission requires a separate check.

Evidence: S01, S03, S04, S06, S08, S09, S10, S11.

**D3 Temporal and revision status: pass**

R4/Cobalt-78 in S07 belongs to the old revision; R5/Cobalt-78 in S12 is a current-revision contradiction. Identical values do not justify merging these statuses.

Evidence: S06, S07, S12.

**D4 Source policy: pass**

Sources are restricted to 0725e021b81b.registry.invalid; S08–S11 give correct current values but come from consortium/complete-current and should be marked semantically valid but source-disallowed.

Evidence: S08, S09, S10, S11, S12.

**Findings for this world**

- Factual correctness and source compliance require separate checks: the complete external-domain chunk is not an acceptable alternative source.
- A complete four-fact support path remains within the allowed domain and does not depend on the external-domain chunk.

**Original-text evidence index**

- **S06**: chunk `8b95a7988a9f6ddde43139cf7459`, claim `0092b83f7079252070c347229cca`, Character span `[674, 749)`; Source `https://0725e021b81b.registry.invalid/operative-record`.
  > For entity Veloria-0725E021 in revision R5, the service route is Cobalt-67.
- **S03**: chunk `b83127afa42713160c72a9da9869`, claim `5a5273d26fd5d77107ecbbd19d3e`, Character span `[692, 779)`; Source `https://0725e021b81b.registry.invalid/operative-part-1`.
  > For entity Veloria-0725E021 in revision R5, the file review interval is 5 working days.
- **S01**: chunk `6cf9cab91e4e4f8f2901d62d853d`, claim `03946032854ec8f9225faf240e2e`, Character span `[686, 780)`; Source `https://0725e021b81b.registry.invalid/operative-part-2`.
  > For entity Veloria-0725E021 in revision R5, the archival retention period is 90 calendar days.
- **S04**: chunk `2f9d051588ff90fdbd290e2b241f`, claim `8733cc7055f40bc0842b76b3c5ac`, Character span `[663, 752)`; Source `https://0725e021b81b.registry.invalid/operative-part-3`.
  > For entity Veloria-0725E021 in revision R5, the release authorization code is Permit-R84.
- **S08**: chunk `44b1495d809dbc6ec0bbe201adc0`, claim `9907f6e8d7669d70a570e17343f7`, Character span `[687, 762)`; Source `https://0725e021b81b.consortium.invalid/complete-current`.
  > For entity Veloria-0725E021 in revision R5, the service route is Cobalt-67.
- **S09**: chunk `44b1495d809dbc6ec0bbe201adc0`, claim `cdc5bb71ba79670feb8b95fefbae`, Character span `[764, 851)`; Source `https://0725e021b81b.consortium.invalid/complete-current`.
  > For entity Veloria-0725E021 in revision R5, the file review interval is 5 working days.
- **S10**: chunk `44b1495d809dbc6ec0bbe201adc0`, claim `1739349f7ab19359f3c8b0f5bc19`, Character span `[853, 947)`; Source `https://0725e021b81b.consortium.invalid/complete-current`.
  > For entity Veloria-0725E021 in revision R5, the archival retention period is 90 calendar days.
- **S11**: chunk `44b1495d809dbc6ec0bbe201adc0`, claim `6e21d3e758de536f65309f789a6b`, Character span `[949, 1038)`; Source `https://0725e021b81b.consortium.invalid/complete-current`.
  > For entity Veloria-0725E021 in revision R5, the release authorization code is Permit-R84.
- **S07**: chunk `429a61c6ab8457c684be10cd852f`, claim `caeb227efffb1a7e7ab0e909e23c`, Character span `[673, 748)`; Source `https://0725e021b81b.registry.invalid/archive`.
  > For entity Veloria-0725E021 in revision R4, the service route is Cobalt-78.
- **S12**: chunk `ae11ac3bcbb0da8cbefe892d3196`, claim `d9caee0ec6ce431f49608cad876b`, Character span `[666, 741)`; Source `https://0725e021b81b.consortium.invalid/disputed`.
  > For entity Veloria-0725E021 in revision R5, the service route is Cobalt-78.

## World 09: ee8731d6c6b1437021f5b3b5e39d

Question IDs: `d1e417f9c5efbeb240448f9bbe78`, `15efdda79a3c271c04753800c37f`.

Collection IDs: `bd802283d69ab456b45cdc6b12ab`, `defaf47f2f07f0ed809e379a921d`.

Entity: Veloria-EE8731D6; Rendering: prose; Support structure: position; Required fact count: 3; Overall judgment: **pass**.

Required facts: review_days = 11 working days; release_code = Permit-R31; retention_days = 90 calendar days.

**D1 Consistency of required facts with the original text: pass**

Under R5, S01=11 working days, S06=Permit-R31, and S05=90 calendar days match the requested review, authorization, and archival fields, respectively.

Evidence: S01, S06, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The prose spans at approximately characters 1133–1261 all contain the entity and R5; late placement affects scoring or delivery visibility but not the completeness of the original assertion bindings.

Evidence: S01, S05, S06.

**D3 Temporal and revision status: pass**

The R4 value of 21 working days is obsolete; S08 still gives 21 days despite specifying R5, contradicting the 11 days in S01. Both status judgments are appropriate.

Evidence: S01, S04, S08.

**D4 Source policy: pass**

There is no source allowlist; the consortium URL of S08 should not be treated as a policy violation. Its problem is the incorrect current review-interval value.

Evidence: S01, S08.

**Findings for this world**

- The review-interval field has 13 valid assertions (including the original), but the other two fields still require independent support.
- The three correct Annex values must not be used to complete support for the target entity.

**Original-text evidence index**

- **S01**: chunk `6d6b54e0bd232a2d483efd3209e3`, claim `ac9bcbaa9daaae76dd728cc5461f`, Character span `[1133, 1221)`; Source `https://ee8731d6c6b1.registry.invalid/replica-4`.
  > For entity Veloria-EE8731D6 in revision R5, the file review interval is 11 working days.
- **S06**: chunk `135921500a4d7c559633926c2d6a`, claim `f51208b75ad2f7e3a69cd92bb53b`, Character span `[1172, 1261)`; Source `https://ee8731d6c6b1.registry.invalid/operative-record`.
  > For entity Veloria-EE8731D6 in revision R5, the release authorization code is Permit-R31.
- **S05**: chunk `74e689f7f19c965fb8c73ffc7e96`, claim `7897baa589ace6a512e1ad885e5c`, Character span `[1160, 1254)`; Source `https://ee8731d6c6b1.registry.invalid/operative-record`.
  > For entity Veloria-EE8731D6 in revision R5, the archival retention period is 90 calendar days.
- **S04**: chunk `e2ac6798c968389187c052f01653`, claim `f04273e4acf458805735b61dc6d2`, Character span `[1088, 1176)`; Source `https://ee8731d6c6b1.registry.invalid/archive`.
  > For entity Veloria-EE8731D6 in revision R4, the file review interval is 21 working days.
- **S08**: chunk `3f224ec98d5124f24ba6eac3ebbd`, claim `51fb25ffda18dcf764a503b272db`, Character span `[1077, 1165)`; Source `https://ee8731d6c6b1.consortium.invalid/disputed`.
  > For entity Veloria-EE8731D6 in revision R5, the file review interval is 21 working days.

## World 10: d9c577be401108f197ec3c98ac0d

Question IDs: `dadbd76b8299290538db4a8c789d`, `0d69814bbb199df6c62eb05c1044`.

Collection IDs: `77e69e15ef1dd373cc94e35efa4f`, `fcd0cc1b24b7bf41a356f254b817`.

Entity: Veloria-D9C577BE; Rendering: prose; Support structure: same_url_complementary; Required fact count: 4; Overall judgment: **pass**.

Required facts: release_code = Permit-K24; review_days = 11 working days; route = Aster-32; retention_days = 180 calendar days.

**D1 Consistency of required facts with the original text: pass**

The four R3 prose assertions give Permit-K24, 11 working days, Aster-32, and 180 calendar days, matching the four requested fields and truth table individually.

Evidence: S09, S04, S07, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four primary supports occur in A79/A64/A73/A69, each with a complete subject–revision–field sentence; four assertions from different chunks are still jointly required despite sharing a URL.

Evidence: S04, S05, S07, S09.

**D3 Temporal and revision status: pass**

The query date falls within R3's validity period; R2/Permit-R32 in S02 is obsolete, whereas R3/Permit-R32 in S01 contradicts the current K24.

Evidence: S09, S02, S01.

**D4 Source policy: pass**

The question leaves sources unrestricted, so consortium/disputed is admissible but does not support the correct code; all positive registry sources are also allowed.

Evidence: S01, S09.

**Findings for this world**

- This same-URL complementary case has no replicas and only four distinct primary support chunks; page identity cannot replace complete fact coverage.
- The Annex subject is not the requested Veloria-D9C577BE.

**Original-text evidence index**

- **S09**: chunk `81ad9c76766c73d4b611f5d8a821`, claim `9f24d341076147701eb2cbf7704e`, Character span `[699, 788)`; Source `https://d9c577be4011.registry.invalid/operative-record`.
  > For entity Veloria-D9C577BE in revision R3, the release authorization code is Permit-K24.
- **S04**: chunk `91118933c9d3eff2798dacde44ac`, claim `6824ff3e43ddc284bf13d65e430f`, Character span `[668, 756)`; Source `https://d9c577be4011.registry.invalid/operative-record`.
  > For entity Veloria-D9C577BE in revision R3, the file review interval is 11 working days.
- **S07**: chunk `1411d67c0e657883e4e5cd9eef5b`, claim `d26ae58331d5ad1e215c969dc1bc`, Character span `[683, 757)`; Source `https://d9c577be4011.registry.invalid/operative-record`.
  > For entity Veloria-D9C577BE in revision R3, the service route is Aster-32.
- **S05**: chunk `68e61f95343f8779fb10bdb44f0f`, claim `ab9e3f4a039160c2e9988825683e`, Character span `[672, 767)`; Source `https://d9c577be4011.registry.invalid/operative-record`.
  > For entity Veloria-D9C577BE in revision R3, the archival retention period is 180 calendar days.
- **S02**: chunk `e284618786ce83517cccf448dee3`, claim `908ef1788fecfc3a18281510ab8a`, Character span `[678, 767)`; Source `https://d9c577be4011.registry.invalid/archive`.
  > For entity Veloria-D9C577BE in revision R2, the release authorization code is Permit-R32.
- **S01**: chunk `c9f4e6a2970a4586f5da28d20475`, claim `7f0341799870675c59bb79d40244`, Character span `[679, 768)`; Source `https://d9c577be4011.consortium.invalid/disputed`.
  > For entity Veloria-D9C577BE in revision R3, the release authorization code is Permit-R32.

## World 11: 3e76e34590e189ccea5f9eed9618

Question IDs: `8a8fa5a3d750fbda1343aa714c9a`, `db53c4c02f91d811c3610c5a5999`.

Collection IDs: `45ee5a714cd97a627670770aeac8`, `b09eedbdc743986853960cd2511f`.

Entity: Veloria-3E76E345; Rendering: prose; Support structure: single_chunk; Required fact count: 4; Overall judgment: **pass**.

Required facts: route = Cobalt-74; review_days = 5 working days; release_code = Permit-V46; retention_days = 30 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R4 route Cobalt-74, review interval of 5 working days, code Permit-V46, and retention period of 30 calendar days are expressed individually in S01–S04.

Evidence: S01, S02, S03, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four prose sentences share one complete support chunk, and each restates the entity and R4; they are not bare values that inherit their subject solely from a page heading.

Evidence: S01, S02, S03, S04.

**D3 Temporal and revision status: pass**

R4 is valid in June 2035; R3/Willow-57 in S05 is obsolete, whereas R4/Willow-57 in S09 conflicts with the current Cobalt-74.

Evidence: S01, S05, S09.

**D4 Source policy: pass**

Unrestricted sources allow both registry and consortium; the source identity of S09 is permitted, but its contradictory status still prevents the route fact from receiving credit.

Evidence: S01, S09.

**Findings for this world**

- Complete four-fact support within one chunk exists; replicas do not increase the number of distinct facts.
- The three Annex examples concern a different entity and cannot complete the target facts.

**Original-text evidence index**

- **S01**: chunk `4c212546778baada4bf656d85fe3`, claim `6af4aab66106c9397eb86f3308e6`, Character span `[1365, 1440)`; Source `https://3e76e34590e1.registry.invalid/replica-0`.
  > For entity Veloria-3E76E345 in revision R4, the service route is Cobalt-74.
- **S02**: chunk `4c212546778baada4bf656d85fe3`, claim `2a314ad491cbf5112e55ad169dcc`, Character span `[1442, 1529)`; Source `https://3e76e34590e1.registry.invalid/replica-0`.
  > For entity Veloria-3E76E345 in revision R4, the file review interval is 5 working days.
- **S03**: chunk `4c212546778baada4bf656d85fe3`, claim `7afca8a394235a1d425b8c93ec7d`, Character span `[1531, 1620)`; Source `https://3e76e34590e1.registry.invalid/replica-0`.
  > For entity Veloria-3E76E345 in revision R4, the release authorization code is Permit-V46.
- **S04**: chunk `4c212546778baada4bf656d85fe3`, claim `049967120df74d050b711a1cf880`, Character span `[1622, 1716)`; Source `https://3e76e34590e1.registry.invalid/replica-0`.
  > For entity Veloria-3E76E345 in revision R4, the archival retention period is 30 calendar days.
- **S05**: chunk `eb18cb429a7d5b12dbf1ea5fd604`, claim `22ebea6a50fb8a7c0b13824bad77`, Character span `[1358, 1433)`; Source `https://3e76e34590e1.registry.invalid/archive`.
  > For entity Veloria-3E76E345 in revision R3, the service route is Willow-57.
- **S09**: chunk `89e82b40c5d50d92955d3a8dc5c8`, claim `f89b8b705d61f41e30385cbc5ff6`, Character span `[1391, 1466)`; Source `https://3e76e34590e1.consortium.invalid/disputed`.
  > For entity Veloria-3E76E345 in revision R4, the service route is Willow-57.

## World 12: 9b7186639521ce344a17114d6ccc

Question IDs: `8a768c3154be02a69b6e4adde8d5`, `f622499f3eacf91f756625385239`.

Collection IDs: `f00d2e51a8d1f3d62a14c713b099`, `db7c1711fc115e54646419bc96bd`.

Entity: Veloria-9B718663; Rendering: prose; Support structure: temporal_conflict; Required fact count: 4; Overall judgment: **pass**.

Required facts: review_days = 11 working days; retention_days = 60 calendar days; release_code = Permit-R80; route = Cobalt-56.

**D1 Consistency of required facts with the original text: pass**

The R6 question requests an 11-working-day review interval, 60-day retention period, Permit-R80, and Cobalt-56; S01/S12/S13/S06 agree with these four truth values.

Evidence: S01, S12, S13, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

All four current prose spans contain Veloria-9B718663 and R6; four conflicting values occurring together in one chunk cannot replace valid support.

Evidence: S01, S06, S12, S13.

**D3 Temporal and revision status: pass**

S02–S05 contain the old R5 combination of 14 days/120 days/R10/Aster-30; S07–S10 present that same combination as R6 and should be current-revision contradictions. The label distinction is correct.

Evidence: S02, S03, S04, S05, S07, S08, S09, S10.

**D4 Source policy: pass**

There is no source restriction, so the consortium chunk containing current contradictions is source-allowed; correctness of all four fields must be judged from values and revisions rather than domain filtering.

Evidence: S07, S08, S09, S10.

**Findings for this world**

- All four fields in this world have both obsolete and current-revision conflicting values; semantic status is not determined by URL host.
- Review-interval replicas cannot substitute for support for the other three fields.

**Original-text evidence index**

- **S01**: chunk `7e665e46acdc6f6fb202393f6e26`, claim `ca8d104beadb4bd9af20fa7adb92`, Character span `[1294, 1382)`; Source `https://9b7186639521.registry.invalid/replica-8`.
  > For entity Veloria-9B718663 in revision R6, the file review interval is 11 working days.
- **S12**: chunk `7015b034a79c5ff308a2d000f35d`, claim `5c8c3c162f6752b45f1f2c815d64`, Character span `[1290, 1384)`; Source `https://9b7186639521.registry.invalid/operative-record`.
  > For entity Veloria-9B718663 in revision R6, the archival retention period is 60 calendar days.
- **S13**: chunk `632baaacdf088bd719e83cbb565f`, claim `1e7893a37099e88b257080fada89`, Character span `[1251, 1340)`; Source `https://9b7186639521.registry.invalid/operative-record`.
  > For entity Veloria-9B718663 in revision R6, the release authorization code is Permit-R80.
- **S06**: chunk `a4374e37532dd3b7438c18dc05ca`, claim `510a0c7de51a03b78f658be43017`, Character span `[1252, 1327)`; Source `https://9b7186639521.registry.invalid/operative-record`.
  > For entity Veloria-9B718663 in revision R6, the service route is Cobalt-56.
- **S02**: chunk `5ddf6bcf3ea642fd67347b7d2440`, claim `aacf402e239b53b29fbf69bac1d0`, Character span `[1278, 1366)`; Source `https://9b7186639521.registry.invalid/archive`.
  > For entity Veloria-9B718663 in revision R5, the file review interval is 14 working days.
- **S03**: chunk `5ddf6bcf3ea642fd67347b7d2440`, claim `9cba102eee8f44c70ac0b6e2c927`, Character span `[1368, 1463)`; Source `https://9b7186639521.registry.invalid/archive`.
  > For entity Veloria-9B718663 in revision R5, the archival retention period is 120 calendar days.
- **S04**: chunk `5ddf6bcf3ea642fd67347b7d2440`, claim `df9fde83495a859c7c9fa63b3b97`, Character span `[1465, 1554)`; Source `https://9b7186639521.registry.invalid/archive`.
  > For entity Veloria-9B718663 in revision R5, the release authorization code is Permit-R10.
- **S05**: chunk `5ddf6bcf3ea642fd67347b7d2440`, claim `73b4288cdcf9f15d8d83343cd7c1`, Character span `[1556, 1630)`; Source `https://9b7186639521.registry.invalid/archive`.
  > For entity Veloria-9B718663 in revision R5, the service route is Aster-30.
- **S07**: chunk `b1704046948c6997e3f9e077de0b`, claim `4a5346ada0a842b7542770cdddf9`, Character span `[1255, 1343)`; Source `https://9b7186639521.consortium.invalid/disputed`.
  > For entity Veloria-9B718663 in revision R6, the file review interval is 14 working days.
- **S08**: chunk `b1704046948c6997e3f9e077de0b`, claim `a26795fdfde299a9f24632af6e70`, Character span `[1345, 1440)`; Source `https://9b7186639521.consortium.invalid/disputed`.
  > For entity Veloria-9B718663 in revision R6, the archival retention period is 120 calendar days.
- **S09**: chunk `b1704046948c6997e3f9e077de0b`, claim `1e3fb1631983f65e0f4df3b696d7`, Character span `[1442, 1531)`; Source `https://9b7186639521.consortium.invalid/disputed`.
  > For entity Veloria-9B718663 in revision R6, the release authorization code is Permit-R10.
- **S10**: chunk `b1704046948c6997e3f9e077de0b`, claim `d5119408ed1f2fff8e7b6c141e84`, Character span `[1533, 1607)`; Source `https://9b7186639521.consortium.invalid/disputed`.
  > For entity Veloria-9B718663 in revision R6, the service route is Aster-30.

## World 13: 17f56219004c52f16e1f251f249d

Question IDs: `8c895ef1bb51630954ce812ddf60`, `70d73e84bb6c75d0eb3b086876b9`.

Collection IDs: `771d43ac2df755b15a940c59d3ed`, `3521977530b6379f0d4cd9b1d9b6`.

Entity: Veloria-17F56219; Rendering: qa; Support structure: cross_url_complementary; Required fact count: 4; Overall judgment: **pass**.

Required facts: retention_days = 180 calendar days; release_code = Permit-V16; route = Willow-84; review_days = 7 working days.

**D1 Consistency of required facts with the original text: pass**

The four R6 question–answer pairs give 180 calendar days, Permit-V16, Willow-84, and 7 working days, covering the four requested fields.

Evidence: S01, S04, S07, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each annotated span includes the entire question and answer: the question supplies the entity, R6, and field, and the answer supplies the value. The pairs on four different URLs are complementary; retaining only the answer line is insufficient.

Evidence: S01, S04, S05, S07.

**D3 Temporal and revision status: pass**

The R5 value of 60 calendar days no longer applies on the query date; an R6 answer of 60 days contradicts the current 180 days. The labels for S09 and S06 are supported.

Evidence: S01, S09, S06.

**D4 Source policy: pass**

The question allows only 17f56219004c.registry.invalid; the four current supports lie within that domain, whereas S06 is excluded because it is on consortium/disputed.

Evidence: S01, S04, S05, S07, S06.

**Findings for this world**

- QA renderings require checking the question and answer jointly; the support spans in this example cover both parts.
- Identical fields and values in Annex question–answer pairs still do not concern the target entity.

**Original-text evidence index**

- **S01**: chunk `45d14b5e0dfd3f4b6bb921c02e06`, claim `c65c2595a67ad4467071534252e3`, Character span `[786, 896)`; Source `https://17f56219004c.registry.invalid/replica-11`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-17F56219? A: 180 calendar days.
- **S04**: chunk `b901db79df8f59a84bb76eaa37f5`, claim `b4790a62d50b80161751e2818eb4`, Character span `[790, 894)`; Source `https://17f56219004c.registry.invalid/operative-part-1`.
  > Q: Under revision R6, what is the release authorization code for entity Veloria-17F56219? A: Permit-V16.
- **S07**: chunk `bb6e24abf98d5e1d17ab00db4ad8`, claim `06fb75c75e436330ed9deb77089b`, Character span `[756, 846)`; Source `https://17f56219004c.registry.invalid/operative-part-2`.
  > Q: Under revision R6, what is the service route for entity Veloria-17F56219? A: Willow-84.
- **S05**: chunk `00b9ad918aa404b1e2acc4cfe670`, claim `6bb4d270e706d3fd01e24d96b130`, Character span `[777, 879)`; Source `https://17f56219004c.registry.invalid/operative-part-3`.
  > Q: Under revision R6, what is the file review interval for entity Veloria-17F56219? A: 7 working days.
- **S09**: chunk `3b002c183ce01f4329394b7a45b1`, claim `1e8478342ccf4cdee1c5b769a639`, Character span `[798, 907)`; Source `https://17f56219004c.registry.invalid/archive`.
  > Q: Under revision R5, what is the archival retention period for entity Veloria-17F56219? A: 60 calendar days.
- **S06**: chunk `00d0dbb973d38647b3aff5713b70`, claim `3e7df42a36cc3c3cbb88f8ada73e`, Character span `[793, 902)`; Source `https://17f56219004c.consortium.invalid/disputed`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-17F56219? A: 60 calendar days.

## World 14: 069ab1d069588c45b5a65a717488

Question IDs: `81cc2a2c444442fbd02b6eb3357c`, `5ad0edeabbae89289c15f47ecd42`.

Collection IDs: `e7ec1c45fc800ba4ac6a11ca545b`, `923d6c1cdf0b361ffb99fc058a51`.

Entity: Veloria-069AB1D0; Rendering: qa; Support structure: equivalent_support; Required fact count: 4; Overall judgment: **pass**.

Required facts: release_code = Permit-M63; review_days = 3 working days; retention_days = 90 calendar days; route = Aster-82.

**D1 Consistency of required facts with the original text: pass**

The R6 question–answer pairs give Permit-M63, 3 working days, 90 calendar days, and Aster-82, corresponding to the requested release, review, retention, and route fields.

Evidence: S02, S03, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each span includes the question containing the subject and R6 plus the complete answer; the independent-current chunk supplies all four facts independently and is an alternative to the distributed support set.

Evidence: S02, S03, S04, S05.

**D3 Temporal and revision status: pass**

R5/Permit-K49 in S08 is obsolete; S01 specifies R6 but still gives K49, contradicting the current M63. Obsolete and contradictory must remain distinct.

Evidence: S02, S08, S01.

**D4 Source policy: pass**

Sources are restricted to 069ab1d06958.registry.invalid; the correct current pairs S10–S13 come from consortium. Semantic validity can hold, but source_allowed=False must be retained.

Evidence: S10, S11, S12, S13, S01.

**Findings for this world**

- Correctness and acceptability of the complete external-domain chunk are separate; it is not an alternative support set from allowed sources.
- The independent-current chunk in the allowed domain still provides complete support, avoiding reliance solely on external-domain assertions to establish coverage.

**Original-text evidence index**

- **S02**: chunk `e043dfde84c7982978cb7c8c04cf`, claim `b7ce2d97230cd82a42ebefc2e6d8`, Character span `[1707, 1811)`; Source `https://069ab1d06958.registry.invalid/replica-2`.
  > Q: Under revision R6, what is the release authorization code for entity Veloria-069AB1D0? A: Permit-M63.
- **S03**: chunk `7068329992d350657628fe8627cb`, claim `c108592790652359f59f356f93d7`, Character span `[1888, 1990)`; Source `https://069ab1d06958.registry.invalid/independent-current`.
  > Q: Under revision R6, what is the file review interval for entity Veloria-069AB1D0? A: 3 working days.
- **S04**: chunk `7068329992d350657628fe8627cb`, claim `01c76b6ad528f6b8f76fed0da07b`, Character span `[1992, 2101)`; Source `https://069ab1d06958.registry.invalid/independent-current`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-069AB1D0? A: 90 calendar days.
- **S05**: chunk `7068329992d350657628fe8627cb`, claim `1a23bf63778e9963b7d3478aa0d6`, Character span `[2103, 2192)`; Source `https://069ab1d06958.registry.invalid/independent-current`.
  > Q: Under revision R6, what is the service route for entity Veloria-069AB1D0? A: Aster-82.
- **S08**: chunk `21a9aa22497a6ebbe83551759d4b`, claim `28bd4f3ab5d32815ad54da1992a5`, Character span `[1794, 1898)`; Source `https://069ab1d06958.registry.invalid/archive`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-069AB1D0? A: Permit-K49.
- **S01**: chunk `adf816e5f02aa4ed6cc115a6e07c`, claim `70577205403059ae95cdffedd7c3`, Character span `[1767, 1871)`; Source `https://069ab1d06958.consortium.invalid/disputed`.
  > Q: Under revision R6, what is the release authorization code for entity Veloria-069AB1D0? A: Permit-K49.
- **S10**: chunk `cff2439d205d70b3021ac8793d2e`, claim `7f3766bfd19b2aadf0ee6da49ecc`, Character span `[1754, 1858)`; Source `https://069ab1d06958.consortium.invalid/complete-current`.
  > Q: Under revision R6, what is the release authorization code for entity Veloria-069AB1D0? A: Permit-M63.
- **S11**: chunk `cff2439d205d70b3021ac8793d2e`, claim `b805fb5f0edfa148938df468bd4d`, Character span `[1860, 1962)`; Source `https://069ab1d06958.consortium.invalid/complete-current`.
  > Q: Under revision R6, what is the file review interval for entity Veloria-069AB1D0? A: 3 working days.
- **S12**: chunk `cff2439d205d70b3021ac8793d2e`, claim `b5e5c53a22bc50d08353ef6e5045`, Character span `[1964, 2073)`; Source `https://069ab1d06958.consortium.invalid/complete-current`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-069AB1D0? A: 90 calendar days.
- **S13**: chunk `cff2439d205d70b3021ac8793d2e`, claim `4730c47eace1af78a39549ff24b2`, Character span `[2075, 2164)`; Source `https://069ab1d06958.consortium.invalid/complete-current`.
  > Q: Under revision R6, what is the service route for entity Veloria-069AB1D0? A: Aster-82.

## World 15: 435622fa3cb24a56eee9e34e19bd

Question IDs: `ac7b54ce6074833e0d225c14beae`, `246371684aaf628fa4835b3c5213`.

Collection IDs: `bb221ba6e5ea1cbf072c84d9e1a2`, `4d512ec429d41e56805b48e3e102`.

Entity: Veloria-435622FA; Rendering: qa; Support structure: position; Required fact count: 3; Overall judgment: **pass**.

Required facts: release_code = Permit-K39; route = Willow-47; review_days = 21 working days.

**D1 Consistency of required facts with the original text: pass**

The question requests the R5 code, route, and review interval; S03=Permit-K39, S06=Willow-47, and S08=21 working days match them individually.

Evidence: S03, S06, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

The QA spans after character 2141 retain the entity/R5/field in the question and the value in the answer; late placement does not make the original spans incomplete.

Evidence: S03, S06, S08.

**D3 Temporal and revision status: pass**

R5 applies on the query date; R4/Permit-K34 is the old code, whereas K34 under R5 is a current negative example that disagrees with K39.

Evidence: S03, S05, S02.

**D4 Source policy: pass**

The 435622fa3cb2.registry.invalid allowlist permits the current pairs and archive; the consortium URL of S02 is excluded. Permission for an old-revision source does not make its content current.

Evidence: S03, S05, S02.

**Findings for this world**

- Although the answer line is short, the scoring span must include the preceding question; the annotation here includes that context.
- K39, Willow-47, and 21 days in Annex should not be used to complete support for the target entity.

**Original-text evidence index**

- **S03**: chunk `165cb6c0ad20a39ad32a52ccf55d`, claim `1be330eef9d6995a465b73b375d8`, Character span `[2141, 2245)`; Source `https://435622fa3cb2.registry.invalid/replica-0`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-435622FA? A: Permit-K39.
- **S06**: chunk `c0ced5cf8e74dc31a741e92599df`, claim `52c2db8a87c96c9183ed44cc7c54`, Character span `[2148, 2238)`; Source `https://435622fa3cb2.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the service route for entity Veloria-435622FA? A: Willow-47.
- **S08**: chunk `2b57eda11cad763b4357ff0126dc`, claim `a24943bf2adc2cbc75d2fbb8e3f8`, Character span `[2219, 2322)`; Source `https://435622fa3cb2.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the file review interval for entity Veloria-435622FA? A: 21 working days.
- **S05**: chunk `803208df2c43f3f4a43231a5acb1`, claim `f0925e543931440713a417a8f302`, Character span `[2184, 2288)`; Source `https://435622fa3cb2.registry.invalid/archive`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-435622FA? A: Permit-K34.
- **S02**: chunk `bc7d78b4e8157fcc6907bb131efa`, claim `b359bc07ad2cb94f239eac6be30b`, Character span `[2152, 2256)`; Source `https://435622fa3cb2.consortium.invalid/disputed`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-435622FA? A: Permit-K34.

## World 16: 1b46f5e19cfbc0387e4a647d3406

Question IDs: `ed7222eb7c3288fc0c68b57a4d45`, `d5e424d2b2b50620ff17534c1e90`.

Collection IDs: `c7464854301d8efcb6b8246eb5f4`, `4ed1224c1e163f749374960bc3e4`.

Entity: Veloria-1B46F5E1; Rendering: qa; Support structure: same_url_complementary; Required fact count: 4; Overall judgment: **pass**.

Required facts: retention_days = 90 calendar days; route = Aster-88; review_days = 3 working days; release_code = Permit-V57.

**D1 Consistency of required facts with the original text: pass**

S01/S06/S02/S09 give 90 calendar days, Aster-88, 3 working days, and Permit-V57, agreeing with the R6 question.

Evidence: S01, S06, S02, S09.

**D2 Complete assertions, complementary support, and alternative support: pass**

In each QA pair, the question specifies the entity and revision and the answer supplies the value; the four same-URL chunks remain complementary, so retaining one chunk does not establish all four fields.

Evidence: S01, S02, S06, S09.

**D3 Temporal and revision status: pass**

R5/60 calendar days is obsolete; S08 specifies R6 but answers 60 days, contradicting the R6 value of 90 days. The status judgment is appropriate.

Evidence: S01, S03, S08.

**D4 Source policy: pass**

Only 1b46f5e19cfb.registry.invalid is allowed; the positive operative-record and replica sources comply, whereas consortium/disputed does not.

Evidence: S01, S02, S06, S09, S08.

**Findings for this world**

- A shared URL does not imply a shared question–answer pair or a complete fact set; all four bindings must be preserved.
- Both current correct and old values appear, but the temporal and revision boundaries are clear.

**Original-text evidence index**

- **S01**: chunk `fb490a299fd0a98f4afecfe487b9`, claim `80b4d2df431ae0cd8b87474b92f5`, Character span `[1369, 1478)`; Source `https://1b46f5e19cfb.registry.invalid/replica-10`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-1B46F5E1? A: 90 calendar days.
- **S06**: chunk `aa1218be4990a4af34ffb539fa4c`, claim `17241d064ac7755e2dab4f07248a`, Character span `[1356, 1445)`; Source `https://1b46f5e19cfb.registry.invalid/operative-record`.
  > Q: Under revision R6, what is the service route for entity Veloria-1B46F5E1? A: Aster-88.
- **S02**: chunk `ae3b18bc17f1afd042952faf9222`, claim `f42d3f11ecce317e2a1ea7685a89`, Character span `[1350, 1452)`; Source `https://1b46f5e19cfb.registry.invalid/operative-record`.
  > Q: Under revision R6, what is the file review interval for entity Veloria-1B46F5E1? A: 3 working days.
- **S09**: chunk `799ff306aebbb28b97c5a0cecd9e`, claim `bdc7da38b18f1a4ca900e1926b93`, Character span `[1375, 1479)`; Source `https://1b46f5e19cfb.registry.invalid/operative-record`.
  > Q: Under revision R6, what is the release authorization code for entity Veloria-1B46F5E1? A: Permit-V57.
- **S03**: chunk `8fe39059c1cd5fdeca9c27c6dc49`, claim `b500668b42605d37929ca052abb2`, Character span `[1374, 1483)`; Source `https://1b46f5e19cfb.registry.invalid/archive`.
  > Q: Under revision R5, what is the archival retention period for entity Veloria-1B46F5E1? A: 60 calendar days.
- **S08**: chunk `11a0b5fff4a1308714914d88e369`, claim `befa790f4d5039e884b07c76f6f5`, Character span `[1358, 1467)`; Source `https://1b46f5e19cfb.consortium.invalid/disputed`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-1B46F5E1? A: 60 calendar days.

## World 17: 5eee3a0bbf1b1c5a502b164a82da

Question IDs: `a8629078648915befb9bc62961ce`, `fdf34f802304b7e280ef847fd826`.

Collection IDs: `e1991e0a3b7782df5c259f793b96`, `b374cfd6b12063b1b82202944129`.

Entity: Veloria-5EEE3A0B; Rendering: qa; Support structure: single_chunk; Required fact count: 2; Overall judgment: **pass**.

Required facts: release_code = Permit-M65; retention_days = 60 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R4 question asks only for the authorization code and retention period; S03/04 provide Permit-M65 and 60 calendar days, respectively.

Evidence: S03, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

Both Q+A pairs occur in one complete chunk and give the entity and R4 before the value; the single-chunk support structure for two facts has direct textual support.

Evidence: S03, S04.

**D3 Temporal and revision status: pass**

R3/Permit-K82 is obsolete by June 2035; S02 still gives K82 under R4 and is a current code contradiction, not a valid alternative.

Evidence: S03, S01, S02.

**D4 Source policy: pass**

The question has no source-prefix constraint, so the consortium source of S02 is allowed; its content is invalid because it conflicts with the current M65.

Evidence: S02, S03.

**Findings for this world**

- The complete chunk for the target entity must be distinguished from the Annex pairs, even when their answers are also M65 or 60 days.
- Unrestricted sources do not mean contradictory content can receive factual-support credit.

**Original-text evidence index**

- **S03**: chunk `1eb57f10ec9c3676f9a868ca6e8f`, claim `b802095879c73d826d62547c5536`, Character span `[294, 398)`; Source `https://5eee3a0bbf1b.registry.invalid/replica-3`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-5EEE3A0B? A: Permit-M65.
- **S04**: chunk `1eb57f10ec9c3676f9a868ca6e8f`, claim `30cfcad639a690786b9114f78255`, Character span `[400, 509)`; Source `https://5eee3a0bbf1b.registry.invalid/replica-3`.
  > Q: Under revision R4, what is the archival retention period for entity Veloria-5EEE3A0B? A: 60 calendar days.
- **S01**: chunk `27342139c23698b914d98443f1fd`, claim `46b3035f1fd836ba9a1819448384`, Character span `[291, 395)`; Source `https://5eee3a0bbf1b.registry.invalid/archive`.
  > Q: Under revision R3, what is the release authorization code for entity Veloria-5EEE3A0B? A: Permit-K82.
- **S02**: chunk `e53c6ef181da145d2ea0c1e1412a`, claim `504f591ee563a5083ce93b9a3450`, Character span `[287, 391)`; Source `https://5eee3a0bbf1b.consortium.invalid/disputed`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-5EEE3A0B? A: Permit-K82.

## World 18: e3b68dc94f4e0e9954c524ef91c7

Question IDs: `9e3f2963ff78c68673731fd8d763`, `332816ff3b572cc2da3c81d53b36`.

Collection IDs: `8d7375b4ab5c2d1e9512ccaae2da`, `d5ef1977974b2315220d0f760d40`.

Entity: Veloria-E3B68DC9; Rendering: qa; Support structure: temporal_conflict; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Aster-58; retention_days = 120 calendar days; review_days = 11 working days.

**D1 Consistency of required facts with the original text: pass**

The three requested R3 fields are supplied by Aster-58 in S11, 120 calendar days in S04, and 11 working days in S06.

Evidence: S11, S04, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

Every valid pair includes the question naming the entity and R3 and its answer; support for the three fields is jointly required and cannot be replaced by three old-value pairs.

Evidence: S04, S06, S11.

**D3 Temporal and revision status: pass**

The R2 combination Cobalt-13/30 days/7 working days is obsolete; S01–S03 repeat it under R3 and should be labeled current-revision contradictions.

Evidence: S01, S02, S03, S07, S08, S09.

**D4 Source policy: pass**

The e3b68dc94f4e.registry.invalid allowlist permits the three positive examples and archive; the full group of contradictory consortium pairs is disallowed.

Evidence: S01, S02, S03, S04, S06, S11.

**Findings for this world**

- This example distinguishes obsolete revisions, current contradictions, allowed sources, and the target subject; the four dimensions cannot substitute for one another.

**Original-text evidence index**

- **S11**: chunk `9803bc3c7a02f4e5d8227f32df4f`, claim `2fac7c2226ed46195eb90036f0a0`, Character span `[675, 764)`; Source `https://e3b68dc94f4e.registry.invalid/operative-record`.
  > Q: Under revision R3, what is the service route for entity Veloria-E3B68DC9? A: Aster-58.
- **S04**: chunk `04e2fbccb404fa038200e09e69b5`, claim `7fbc946fa908c8a2a9b8995b7616`, Character span `[688, 798)`; Source `https://e3b68dc94f4e.registry.invalid/operative-record`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-E3B68DC9? A: 120 calendar days.
- **S06**: chunk `e54796a6066401d50056ad44b3b3`, claim `1e6111e178da357431dc7a3625fa`, Character span `[684, 787)`; Source `https://e3b68dc94f4e.registry.invalid/operative-record`.
  > Q: Under revision R3, what is the file review interval for entity Veloria-E3B68DC9? A: 11 working days.
- **S01**: chunk `3e92de964c8af7e6cc6c7d0b9386`, claim `576acc943f284454954d9b1dac5b`, Character span `[702, 792)`; Source `https://e3b68dc94f4e.consortium.invalid/disputed`.
  > Q: Under revision R3, what is the service route for entity Veloria-E3B68DC9? A: Cobalt-13.
- **S02**: chunk `3e92de964c8af7e6cc6c7d0b9386`, claim `e036a5e217bd9374f5bd7e9d0ac4`, Character span `[794, 903)`; Source `https://e3b68dc94f4e.consortium.invalid/disputed`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-E3B68DC9? A: 30 calendar days.
- **S03**: chunk `3e92de964c8af7e6cc6c7d0b9386`, claim `6e84c7c7242c6d7636a24f6eb369`, Character span `[905, 1007)`; Source `https://e3b68dc94f4e.consortium.invalid/disputed`.
  > Q: Under revision R3, what is the file review interval for entity Veloria-E3B68DC9? A: 7 working days.
- **S07**: chunk `df32b6e8f8f1db3f965ffb3999e2`, claim `d14e64e4ef60961a70e9cedfc3cb`, Character span `[688, 778)`; Source `https://e3b68dc94f4e.registry.invalid/archive`.
  > Q: Under revision R2, what is the service route for entity Veloria-E3B68DC9? A: Cobalt-13.
- **S08**: chunk `df32b6e8f8f1db3f965ffb3999e2`, claim `5493ac8e2ccecb0743737d352e31`, Character span `[780, 889)`; Source `https://e3b68dc94f4e.registry.invalid/archive`.
  > Q: Under revision R2, what is the archival retention period for entity Veloria-E3B68DC9? A: 30 calendar days.
- **S09**: chunk `df32b6e8f8f1db3f965ffb3999e2`, claim `7bb6a5713059ede67c0f47edc813`, Character span `[891, 993)`; Source `https://e3b68dc94f4e.registry.invalid/archive`.
  > Q: Under revision R2, what is the file review interval for entity Veloria-E3B68DC9? A: 7 working days.

## World 19: 05bc08a3df744aaba606274c66ff

Question IDs: `9dda9b7fa634a3fecd7fd8cad18a`, `719d07b72812736e7580e9b655a8`.

Collection IDs: `feffbf75d212c2217c2145d6c3f0`, `f59c409247e328c0843bd58f0d4e`.

Entity: Veloria-05BC08A3; Rendering: list; Support structure: cross_url_complementary; Required fact count: 4; Overall judgment: **pass**.

Required facts: review_days = 3 working days; retention_days = 120 calendar days; release_code = Permit-R19; route = Cobalt-66.

**D1 Consistency of required facts with the original text: pass**

The R8 question requests four fields; S07/S09/S04/S05 supply 3 working days, 120 calendar days, Permit-R19, and Cobalt-66, matching both meaning and value.

Evidence: S07, S09, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each of the four list assertions fully specifies the subject and R8; they are distributed across operative-record and part-1/2/3 and must be combined to cover all four requested facts.

Evidence: S04, S05, S07, S09.

**D3 Temporal and revision status: pass**

The R7 value of 7 working days is obsolete; R8/7 days in S01 conflicts with R8/3 days, supporting the contradictory label.

Evidence: S07, S08, S01.

**D4 Source policy: pass**

Sources are unrestricted, so 05bc08a3df74.consortium.invalid is not policy-prohibited; S01 should be excluded from valid support because of its conflicting review-interval value.

Evidence: S01, S07.

**Findings for this world**

- Four facts distributed across URLs cannot be replaced by one page-hit event.
- The correct review interval, retention period, and code in Annex do not concern the requested subject.

**Original-text evidence index**

- **S07**: chunk `647e1b921d62654e774599605b95`, claim `6d3aed85186bd9c29863848cc0f6`, Character span `[492, 569)`; Source `https://05bc08a3df74.registry.invalid/operative-record`.
  > - Entity Veloria-05BC08A3; revision R8; file review interval: 3 working days.
- **S09**: chunk `bce88af57de9ebde2cc8385cf8aa`, claim `e990dc8e020a3b31d37e15db7ded`, Character span `[485, 570)`; Source `https://05bc08a3df74.registry.invalid/operative-part-1`.
  > - Entity Veloria-05BC08A3; revision R8; archival retention period: 120 calendar days.
- **S04**: chunk `e237ecfe0c3f1df1a43c12f20ccc`, claim `30cedf4ee0ee6f55870cb0aae224`, Character span `[489, 568)`; Source `https://05bc08a3df74.registry.invalid/operative-part-2`.
  > - Entity Veloria-05BC08A3; revision R8; release authorization code: Permit-R19.
- **S05**: chunk `545623d43eccb2c415903390da33`, claim `77021e62ab82e7610dc9a89303a7`, Character span `[504, 569)`; Source `https://05bc08a3df74.registry.invalid/operative-part-3`.
  > - Entity Veloria-05BC08A3; revision R8; service route: Cobalt-66.
- **S08**: chunk `aa49261d015054f8bf8e17cdfeda`, claim `d9d9ce827fc9f07156589bf8fc73`, Character span `[489, 566)`; Source `https://05bc08a3df74.registry.invalid/archive`.
  > - Entity Veloria-05BC08A3; revision R7; file review interval: 7 working days.
- **S01**: chunk `145a2e29fb0a0a797a1f51d4ecf3`, claim `e1074a8238e51841336920e2397e`, Character span `[488, 565)`; Source `https://05bc08a3df74.consortium.invalid/disputed`.
  > - Entity Veloria-05BC08A3; revision R8; file review interval: 7 working days.

## World 20: 9dc35b8464be88ace1e5e7f10d27

Question IDs: `0a1819be4aac8153516bb2b26a83`, `f39acf1c9887aac2f8993179e807`.

Collection IDs: `9af81259ed4fed3ad1f72e9a654c`, `246222dd81c17cce36367f155071`.

Entity: Veloria-9DC35B84; Rendering: list; Support structure: equivalent_support; Required fact count: 4; Overall judgment: **pass**.

Required facts: review_days = 3 working days; route = Cobalt-74; release_code = Permit-V31; retention_days = 120 calendar days.

**D1 Consistency of required facts with the original text: pass**

The requested R7 review interval, route, code, and retention period are 3 working days, Cobalt-74, Permit-V31, and 120 days, corresponding to S03/S01/S06/S05.

Evidence: S03, S01, S06, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The list spans contain the subject, R7, predicate, and value; either the complete independent-current chunk or the four distributed chunks can provide a complete support set.

Evidence: S01, S03, S05, S06.

**D3 Temporal and revision status: pass**

R6/7 working days is obsolete on the query date; R7/7 days in S08 contradicts the current 3 days and must not be treated as current truth based on occurrence order or URL.

Evidence: S03, S02, S08.

**D4 Source policy: pass**

There is no source allowlist, so registry and consortium are both allowed; the designated operative-record is used only for page-hit evaluation and must not be mistaken for the only usable source.

Evidence: S03, S06, S08.

**Findings for this world**

- Equivalent support sets are disjunctive rather than conjunctive; multiple replicas do not create additional required facts.

**Original-text evidence index**

- **S03**: chunk `d78d54544518492794b7e15f0402`, claim `e1ea14a9a214527758b3bb17562c`, Character span `[858, 935)`; Source `https://9dc35b8464be.registry.invalid/operative-record`.
  > - Entity Veloria-9DC35B84; revision R7; file review interval: 3 working days.
- **S01**: chunk `4794ae55a186602b069c57716353`, claim `cb70712090a454252494a5655d33`, Character span `[916, 981)`; Source `https://9dc35b8464be.registry.invalid/operative-part-1`.
  > - Entity Veloria-9DC35B84; revision R7; service route: Cobalt-74.
- **S06**: chunk `fbeb0b3782cd54aaa4a641d8daca`, claim `f469c608e5cfcff87b6c63f60e70`, Character span `[1026, 1105)`; Source `https://9dc35b8464be.registry.invalid/independent-current`.
  > - Entity Veloria-9DC35B84; revision R7; release authorization code: Permit-V31.
- **S05**: chunk `f4e79911234c5001e7db888d57be`, claim `2b5aa8c4eb36cd210617ece24fcd`, Character span `[897, 982)`; Source `https://9dc35b8464be.registry.invalid/operative-part-3`.
  > - Entity Veloria-9DC35B84; revision R7; archival retention period: 120 calendar days.
- **S02**: chunk `7cc2e29ddeb435eae03889cbbe10`, claim `b2f6034b84dc54db7edc054dbcb2`, Character span `[885, 962)`; Source `https://9dc35b8464be.registry.invalid/archive`.
  > - Entity Veloria-9DC35B84; revision R6; file review interval: 7 working days.
- **S08**: chunk `25d6510bf977d3ecae292d1c85be`, claim `15cec993ed29942baad5563f15c7`, Character span `[896, 973)`; Source `https://9dc35b8464be.consortium.invalid/disputed`.
  > - Entity Veloria-9DC35B84; revision R7; file review interval: 7 working days.

## World 21: c201c231abe8aa12a684560d5e82

Question IDs: `8c8fbdeb044fbe9421a7e92d35e2`, `f06db1c2bbb57a19124e63aa02f9`.

Collection IDs: `5cff2de60b2c44a13691fa451166`, `331c4c414fe7b54aecde59111aa6`.

Entity: Veloria-C201C231; Rendering: list; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: review_days = 14 working days; retention_days = 120 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R8 review interval of 14 working days and retention period of 120 calendar days are supported by the list assertions in S01 and S04, respectively, matching the two requested fields.

Evidence: S01, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

S01 and S04 explicitly state the entity, revision, and predicate; their short code-like spans preserve the relationships, and the facts on the two URLs remain complementary.

Evidence: S01, S04.

**D3 Temporal and revision status: pass**

R7/5 days in S03 is obsolete; R8/5 days in S06 conflicts with 14 days. Current status agrees with the temporal boundaries.

Evidence: S01, S03, S06.

**D4 Source policy: pass**

Sources are unrestricted, so c201c231abe8.consortium.invalid/disputed does not violate policy; S06 cannot receive credit because its review-interval value does not match.

Evidence: S06, S01.

**Findings for this world**

- Although the review interval has replicas, the retention period still needs a different support type; repeating one fact does not complete coverage of two facts.

**Original-text evidence index**

- **S01**: chunk `532af9c962ef658200f7564aaabc`, claim `a91a1bf2c53e3f65c28b154c97f5`, Character span `[798, 876)`; Source `https://c201c231abe8.registry.invalid/replica-10`.
  > - Entity Veloria-C201C231; revision R8; file review interval: 14 working days.
- **S04**: chunk `a1697a907fc33f9e27c86471a266`, claim `468b7c11699516d6de5ec8d8b585`, Character span `[779, 864)`; Source `https://c201c231abe8.registry.invalid/operative-part-1`.
  > - Entity Veloria-C201C231; revision R8; archival retention period: 120 calendar days.
- **S03**: chunk `0f06ed742468b70415a460b1e9ea`, claim `d5d6bc2cec4ae21dd63a5bd5175d`, Character span `[700, 777)`; Source `https://c201c231abe8.registry.invalid/archive`.
  > - Entity Veloria-C201C231; revision R7; file review interval: 5 working days.
- **S06**: chunk `8a4099722fba9165e245e88aa5a2`, claim `08d4194213dee163f0f9e23dba27`, Character span `[809, 886)`; Source `https://c201c231abe8.consortium.invalid/disputed`.
  > - Entity Veloria-C201C231; revision R8; file review interval: 5 working days.

## World 22: ae9adbe4331d8b7abf6d5269108d

Question IDs: `51fd6d88e5515535b3af99bf4f24`, `1c93da66bf7aa10964ab7febf5cc`.

Collection IDs: `01e210fefa4ea7b210c5d897362d`, `e5673893412448f6b64a6972fbc6`.

Entity: Veloria-AE9ADBE4; Rendering: list; Support structure: equivalent_support; Required fact count: 4; Overall judgment: **pass**.

Required facts: release_code = Permit-M18; route = Cobalt-20; review_days = 14 working days; retention_days = 120 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R5 values Permit-M18, Cobalt-20, 14 working days, and 120 calendar days occur in the target-entity assertions S05/S04/S12/S10, respectively.

Evidence: S05, S04, S12, S10.

**D2 Complete assertions, complementary support, and alternative support: pass**

All four list spans are complete; the equivalent-support structure should accept either a complete independent set or the distributed four-field set, without requiring all repeated expressions to be present.

Evidence: S04, S05, S10, S12.

**D3 Temporal and revision status: pass**

R4/Permit-R16 is obsolete; S03 binds R16 to R5 and is a current negative example contradicting M18. The classification has textual support.

Evidence: S01, S03, S05.

**D4 Source policy: pass**

Sources are restricted to ae9adbe4331d.registry.invalid; the complete, correct current chunk containing S06–S09 comes from consortium and is disallowed. S03 is also on the prohibited domain.

Evidence: S06, S07, S08, S09, S03.

**Findings for this world**

- A complete four-fact chunk from an external domain can be semantically valid while remaining excluded from allowed-source coverage.
- M18/Cobalt-20/14 days in Annex do not support the target entity.

**Original-text evidence index**

- **S05**: chunk `6d475def1e02fc2417427e613452`, claim `187ba39009d117cdf5e5abf8533f`, Character span `[472, 551)`; Source `https://ae9adbe4331d.registry.invalid/replica-3`.
  > - Entity Veloria-AE9ADBE4; revision R5; release authorization code: Permit-M18.
- **S04**: chunk `543e17ac856ba60fc858bd888460`, claim `eff554c5edc9e43c152a1e83d0c0`, Character span `[488, 553)`; Source `https://ae9adbe4331d.registry.invalid/operative-part-1`.
  > - Entity Veloria-AE9ADBE4; revision R5; service route: Cobalt-20.
- **S12**: chunk `6fb9801044fadd2432fbf043f654`, claim `03176654971efd66158a54c24202`, Character span `[497, 575)`; Source `https://ae9adbe4331d.registry.invalid/operative-part-2`.
  > - Entity Veloria-AE9ADBE4; revision R5; file review interval: 14 working days.
- **S10**: chunk `8d16e1284a4c8fa390099d2d65d9`, claim `21693bbd4fd121215d6460074017`, Character span `[481, 566)`; Source `https://ae9adbe4331d.registry.invalid/operative-part-3`.
  > - Entity Veloria-AE9ADBE4; revision R5; archival retention period: 120 calendar days.
- **S01**: chunk `8a432d53d49b40b85b8f7f976c7a`, claim `6249571d8acf38373c7229d26997`, Character span `[497, 576)`; Source `https://ae9adbe4331d.registry.invalid/archive`.
  > - Entity Veloria-AE9ADBE4; revision R4; release authorization code: Permit-R16.
- **S03**: chunk `916f8324861f30832d2025ce5148`, claim `a67ed046b25fcedbaf8340467e11`, Character span `[490, 569)`; Source `https://ae9adbe4331d.consortium.invalid/disputed`.
  > - Entity Veloria-AE9ADBE4; revision R5; release authorization code: Permit-R16.
- **S06**: chunk `ec757da539edf70cb1dea52484e6`, claim `7213718c8aa55cc1276a97da5b81`, Character span `[500, 579)`; Source `https://ae9adbe4331d.consortium.invalid/complete-current`.
  > - Entity Veloria-AE9ADBE4; revision R5; release authorization code: Permit-M18.
- **S07**: chunk `ec757da539edf70cb1dea52484e6`, claim `f761996bcd0aed29806d4d5b3a7a`, Character span `[581, 646)`; Source `https://ae9adbe4331d.consortium.invalid/complete-current`.
  > - Entity Veloria-AE9ADBE4; revision R5; service route: Cobalt-20.
- **S08**: chunk `ec757da539edf70cb1dea52484e6`, claim `93ff82d8d5d178173aed91a345f4`, Character span `[648, 726)`; Source `https://ae9adbe4331d.consortium.invalid/complete-current`.
  > - Entity Veloria-AE9ADBE4; revision R5; file review interval: 14 working days.
- **S09**: chunk `ec757da539edf70cb1dea52484e6`, claim `c10f7bffbef324e2563d1a5e5d78`, Character span `[728, 813)`; Source `https://ae9adbe4331d.consortium.invalid/complete-current`.
  > - Entity Veloria-AE9ADBE4; revision R5; archival retention period: 120 calendar days.

## World 23: d208d439525a70477d9124aaf205

Question IDs: `84aa02fb1b56ef73aa1bae7028bf`, `d0434050b4d5caea15c0cc41952b`.

Collection IDs: `50f87db591078b3717c5f7edfa5b`, `922e57fa70d4d7e3e3c3047ae17e`.

Entity: Veloria-D208D439; Rendering: list; Support structure: position; Required fact count: 3; Overall judgment: **pass**.

Required facts: retention_days = 30 calendar days; release_code = Permit-M85; review_days = 7 working days.

**D1 Consistency of required facts with the original text: pass**

The question asks for the R3 retention period, authorization code, and review interval; 30 days in S01, Permit-M85 in S07, and 7 working days in S04 agree with the expected values.

Evidence: S01, S07, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

The primary assertions occur after approximately character 3212, but the annotations still retain Entity/R3/field/value; late placement alone does not imply missing semantic support.

Evidence: S01, S04, S07.

**D3 Temporal and revision status: pass**

The R2 retention period of 90 calendar days is obsolete; S08 still gives 90 days under R3, contradicting the current 30 days.

Evidence: S01, S02, S08.

**D4 Source policy: pass**

The allowlist is d208d439525a.registry.invalid; the primary supports comply, whereas S08 on consortium/disputed does not.

Evidence: S01, S04, S07, S08.

**Findings for this world**

- The target entity and Annex must be distinguished independently of their values; the correct M85 or 7 days in Annex should not complete the requested support.
- Complete support at a late position differs from visibility to the scoring model.

**Original-text evidence index**

- **S01**: chunk `852acc775135a6e05d3b40430b97`, claim `6fdc38dd86895ca123b1da258813`, Character span `[3255, 3339)`; Source `https://d208d439525a.registry.invalid/replica-3`.
  > - Entity Veloria-D208D439; revision R3; archival retention period: 30 calendar days.
- **S07**: chunk `d4f3fa27aeae4e975214a3cf6bc1`, claim `65f1047d4cc7be3bafdc0c4bbe42`, Character span `[3212, 3291)`; Source `https://d208d439525a.registry.invalid/operative-record`.
  > - Entity Veloria-D208D439; revision R3; release authorization code: Permit-M85.
- **S04**: chunk `d97786735593c14debc85d16086b`, claim `cd3ec8148ddfa4a9f283ed93789c`, Character span `[3254, 3331)`; Source `https://d208d439525a.registry.invalid/operative-record`.
  > - Entity Veloria-D208D439; revision R3; file review interval: 7 working days.
- **S02**: chunk `0d701c01f22c51c93f46949a9522`, claim `dd0befd85a247bb5a66474099802`, Character span `[3302, 3386)`; Source `https://d208d439525a.registry.invalid/archive`.
  > - Entity Veloria-D208D439; revision R2; archival retention period: 90 calendar days.
- **S08**: chunk `f793a88b6206dfb388a555f2aad9`, claim `e8be248ef6c6dfc0fc5e9db8e045`, Character span `[3238, 3322)`; Source `https://d208d439525a.consortium.invalid/disputed`.
  > - Entity Veloria-D208D439; revision R3; archival retention period: 90 calendar days.

## World 24: 2e4ba86c499edd4bf143aee0c38f

Question IDs: `8d7d949074cd7afa5040c54b12e5`, `1763917050875cc8de49364682f7`.

Collection IDs: `c2a4abcf9b5a71078f9d9b1ce8f5`, `e241d14c5d189c6d51503904355d`.

Entity: Veloria-2E4BA86C; Rendering: list; Support structure: same_url_complementary; Required fact count: 4; Overall judgment: **pass**.

Required facts: release_code = Permit-K28; review_days = 11 working days; retention_days = 60 calendar days; route = Juniper-18.

**D1 Consistency of required facts with the original text: pass**

The four requested R6 values Permit-K28, 11 working days, 60 calendar days, and Juniper-18 are explicitly given in S04/S05/S09/S07.

Evidence: S04, S05, S09, S07.

**D2 Complete assertions, complementary support, and alternative support: pass**

All four same-URL list assertions fully bind the subject and R6; they come from different primary chunks, so all four facts are required rather than merely an operative-record hit.

Evidence: S04, S05, S07, S09.

**D3 Temporal and revision status: pass**

R5/Permit-R19 in S02 does not apply on 2035-06-01; S01 repeats R19 under R6, contradicting K28. The contradictory label is appropriate.

Evidence: S04, S02, S01.

**D4 Source policy: pass**

The question imposes no domain restriction, so S01 on consortium is source-allowed; its failure to support the current code is compatible with that source-permission judgment.

Evidence: S01, S04.

**Findings for this world**

- In this same-URL complementary case, code replicas cannot replace the four fields, and the three Annex assertions cannot join the primary support set.

**Original-text evidence index**

- **S04**: chunk `1635952ff73731f786f24b779f62`, claim `4a1574e468b72374683505070439`, Character span `[1029, 1108)`; Source `https://2e4ba86c499e.registry.invalid/operative-record`.
  > - Entity Veloria-2E4BA86C; revision R6; release authorization code: Permit-K28.
- **S05**: chunk `4cae39ea7a85a46b2612a98e1ffe`, claim `96c362995e28815907c413193eb5`, Character span `[1074, 1152)`; Source `https://2e4ba86c499e.registry.invalid/operative-record`.
  > - Entity Veloria-2E4BA86C; revision R6; file review interval: 11 working days.
- **S09**: chunk `5ec605a89c2c01d741cf13722070`, claim `9deb262b5eed6c9a27c6cbc29856`, Character span `[1075, 1159)`; Source `https://2e4ba86c499e.registry.invalid/operative-record`.
  > - Entity Veloria-2E4BA86C; revision R6; archival retention period: 60 calendar days.
- **S07**: chunk `f0d3719f12e6cd3b9f3158c0b3aa`, claim `828021f75edb88ad76204485377f`, Character span `[955, 1021)`; Source `https://2e4ba86c499e.registry.invalid/operative-record`.
  > - Entity Veloria-2E4BA86C; revision R6; service route: Juniper-18.
- **S02**: chunk `85f67e594647ada177b7cf618e40`, claim `99fbc5f2cd1b98514773808e4fbe`, Character span `[1070, 1149)`; Source `https://2e4ba86c499e.registry.invalid/archive`.
  > - Entity Veloria-2E4BA86C; revision R5; release authorization code: Permit-R19.
- **S01**: chunk `9777a1c52b9945a8859006970d19`, claim `5a2758f06a62c49bf123f937746c`, Character span `[990, 1069)`; Source `https://2e4ba86c499e.consortium.invalid/disputed`.
  > - Entity Veloria-2E4BA86C; revision R6; release authorization code: Permit-R19.

## World 25: 6c8a166e4aaa4ce866c1acc6ba6e

Question IDs: `480c9a5b77a52fa882798f8d9f13`, `1f819fc4d3c84b43625df3af3af7`.

Collection IDs: `571b62697829a2d6cb40e0425546`, `d4dfda99f9d189fb4e7cc04f1ca0`.

Entity: Veloria-6C8A166E; Rendering: list; Support structure: single_chunk; Required fact count: 4; Overall judgment: **pass**.

Required facts: release_code = Permit-R69; route = Aster-59; review_days = 11 working days; retention_days = 90 calendar days.

**D1 Consistency of required facts with the original text: pass**

The required R7 values Permit-R69, Aster-59, 11 working days, and 90 calendar days appear consecutively in S01–S04, matching the requested fields.

Evidence: S01, S02, S03, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

One complete list chunk contains four assertions, each specifying Entity/R7; any complete replica supports all fields, but an isolated value cannot replace that binding.

Evidence: S01, S02, S03, S04.

**D3 Temporal and revision status: pass**

R6/Permit-R68 is the old code; R7/Permit-R68 in S09 differs from the current R69 only in the final character but remains a conflicting value and must not be ignored.

Evidence: S01, S05, S09.

**D4 Source policy: pass**

An empty allowed-prefix list means unrestricted sources; consortium/disputed and registry replicas are all source-allowed, but the content contradiction in S09 still requires checking.

Evidence: S01, S09.

**Findings for this world**

- The single-character difference between R69 and R68 is factually meaningful and must not be normalized away.
- The complete single-chunk set contains four facts, not four pages.

**Original-text evidence index**

- **S01**: chunk `08c845f858bd26b464d206c16a26`, claim `145b7990cc87b88e97749c771319`, Character span `[1642, 1721)`; Source `https://6c8a166e4aaa.registry.invalid/replica-1`.
  > - Entity Veloria-6C8A166E; revision R7; release authorization code: Permit-R69.
- **S02**: chunk `08c845f858bd26b464d206c16a26`, claim `2b1199d79e87625f60f57371c73d`, Character span `[1723, 1787)`; Source `https://6c8a166e4aaa.registry.invalid/replica-1`.
  > - Entity Veloria-6C8A166E; revision R7; service route: Aster-59.
- **S03**: chunk `08c845f858bd26b464d206c16a26`, claim `32b522748a12f58d53bc56d9bfe3`, Character span `[1789, 1867)`; Source `https://6c8a166e4aaa.registry.invalid/replica-1`.
  > - Entity Veloria-6C8A166E; revision R7; file review interval: 11 working days.
- **S04**: chunk `08c845f858bd26b464d206c16a26`, claim `70482a4dc6001fac921b4655f0d6`, Character span `[1869, 1953)`; Source `https://6c8a166e4aaa.registry.invalid/replica-1`.
  > - Entity Veloria-6C8A166E; revision R7; archival retention period: 90 calendar days.
- **S05**: chunk `dac0a018f83b3d63fe19ae34eb48`, claim `4895996718542afeca235ba812ea`, Character span `[1676, 1755)`; Source `https://6c8a166e4aaa.registry.invalid/archive`.
  > - Entity Veloria-6C8A166E; revision R6; release authorization code: Permit-R68.
- **S09**: chunk `e70971ac7dbf391fac5546e29ac9`, claim `bbde3b96a78bce2412fe1a6e925a`, Character span `[1657, 1736)`; Source `https://6c8a166e4aaa.consortium.invalid/disputed`.
  > - Entity Veloria-6C8A166E; revision R7; release authorization code: Permit-R68.

## World 26: 3fe7f2cc3eece0352a55ed329272

Question IDs: `0b9d3f2f9287681882befc63f922`, `4547efb0b4fea0070687a1a66dbb`.

Collection IDs: `3bb6e2d8fb998a0079bbc55cd64a`, `6ffc908f3bffe2934c8f7bc2ef2f`.

Entity: Veloria-3FE7F2CC; Rendering: list; Support structure: temporal_conflict; Required fact count: 2; Overall judgment: **pass**.

Required facts: review_days = 14 working days; route = Aster-10.

**D1 Consistency of required facts with the original text: pass**

R5 requires 14 working days and Aster-10; S04 and S05 support these values in list sentences about the target entity.

Evidence: S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The current interval and route spans both contain the subject and R5; the obsolete and current conflicting combinations also contain both fields, but completeness does not make them valid support.

Evidence: S04, S05, S06, S07.

**D3 Temporal and revision status: pass**

The R4 combination of 5 days/Juniper-64 is obsolete; S06/S07 give that same old combination under R5 and should be current-revision contradictions.

Evidence: S02, S03, S06, S07.

**D4 Source policy: pass**

The question leaves sources unrestricted, so both contradictions in the consortium/disputed chunk should be source-allowed; a contradictory label must not be interpreted as source prohibition.

Evidence: S06, S07.

**Findings for this world**

- Temporal and revision judgments apply to both fields; 14 days and Aster-10 in Annex do not concern the target entity.

**Original-text evidence index**

- **S04**: chunk `08aa2feea13702961d9767123d56`, claim `6566759fb4042a8e6b8e910a0014`, Character span `[889, 967)`; Source `https://3fe7f2cc3eec.registry.invalid/operative-record`.
  > - Entity Veloria-3FE7F2CC; revision R5; file review interval: 14 working days.
- **S05**: chunk `cbded3e5dd6ee8a7fea8f36c07b3`, claim `c7f216b6d6156dc24e884a82a7d4`, Character span `[814, 878)`; Source `https://3fe7f2cc3eec.registry.invalid/operative-record`.
  > - Entity Veloria-3FE7F2CC; revision R5; service route: Aster-10.
- **S06**: chunk `e7183ae1b13b25ae071a2afe7000`, claim `1d7b7f7f2536e33d8ce7b2a97b72`, Character span `[857, 934)`; Source `https://3fe7f2cc3eec.consortium.invalid/disputed`.
  > - Entity Veloria-3FE7F2CC; revision R5; file review interval: 5 working days.
- **S07**: chunk `e7183ae1b13b25ae071a2afe7000`, claim `2575181d97281dba9d12732aa824`, Character span `[936, 1002)`; Source `https://3fe7f2cc3eec.consortium.invalid/disputed`.
  > - Entity Veloria-3FE7F2CC; revision R5; service route: Juniper-64.
- **S02**: chunk `554d3f7ffb13869f9962360e6826`, claim `5a877a047b12944ee2a60ae6731b`, Character span `[901, 978)`; Source `https://3fe7f2cc3eec.registry.invalid/archive`.
  > - Entity Veloria-3FE7F2CC; revision R4; file review interval: 5 working days.
- **S03**: chunk `554d3f7ffb13869f9962360e6826`, claim `686f04f49cde0e85614bed8d1c42`, Character span `[980, 1046)`; Source `https://3fe7f2cc3eec.registry.invalid/archive`.
  > - Entity Veloria-3FE7F2CC; revision R4; service route: Juniper-64.

## World 27: d7d75ad5d3d9f41dbbe4a1506f52

Question IDs: `3b8184d633251e8ecdba3517c6ef`, `687bddd53d61fe9d86b020f99db6`.

Collection IDs: `4f7bf54dd506b7724f3f650239e9`, `8fc7be7c88b282fa025ccde40416`.

Entity: Veloria-D7D75AD5; Rendering: prose; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: review_days = 14 working days; route = Cobalt-36.

**D1 Consistency of required facts with the original text: pass**

The question requests the R8 review interval and route; 14 working days in S02 and Cobalt-36 in S03 directly support both required facts.

Evidence: S02, S03.

**D2 Complete assertions, complementary support, and alternative support: pass**

Both prose sentences fully include “For entity ... in revision R8” plus the field and value; operative-record and operative-part-1 provide complementary support across URLs.

Evidence: S02, S03.

**D3 Temporal and revision status: pass**

R7/3 working days in S01 is obsolete on the query date; R8/3 days in S04 contradicts 14 days and cannot support the current review interval.

Evidence: S02, S01, S04.

**D4 Source policy: pass**

There is no source-prefix restriction; S04 on consortium is allowed but incorrect evidence, and both primary registry supports are also allowed.

Evidence: S02, S03, S04.

**Findings for this world**

- Two complete primary supports are not equivalent to two source-URL hits; omitting either field leaves support incomplete.

**Original-text evidence index**

- **S02**: chunk `6479ec2adf4cd6ed4b3ddbba2d12`, claim `bfbec4132d21c541afdf95cac293`, Character span `[199, 287)`; Source `https://d7d75ad5d3d9.registry.invalid/operative-record`.
  > For entity Veloria-D7D75AD5 in revision R8, the file review interval is 14 working days.
- **S03**: chunk `2b357ac30ffa3e579f3f4237c2c0`, claim `534fe8407b2592fe751dd208407e`, Character span `[196, 271)`; Source `https://d7d75ad5d3d9.registry.invalid/operative-part-1`.
  > For entity Veloria-D7D75AD5 in revision R8, the service route is Cobalt-36.
- **S01**: chunk `887bc660197a859e8ccc93feb229`, claim `147fda0ea9d03a11a4755bec35bb`, Character span `[207, 294)`; Source `https://d7d75ad5d3d9.registry.invalid/archive`.
  > For entity Veloria-D7D75AD5 in revision R7, the file review interval is 3 working days.
- **S04**: chunk `d9ff8ae48907ec0ea4c5f88fdd9b`, claim `dc107ab63bfb1abe735ca609e344`, Character span `[199, 286)`; Source `https://d7d75ad5d3d9.consortium.invalid/disputed`.
  > For entity Veloria-D7D75AD5 in revision R8, the file review interval is 3 working days.

## World 28: edc0e70b068d60e91ed872b4d97e

Question IDs: `4b3b875b5bcfb385d31fc3a1489e`, `27fcf29c74451ed90f5ae8eb1aa4`.

Collection IDs: `f2a5fe4cd8db39fc41ed5712e6dc`, `4a85742986a24851feae6be2afc9`.

Entity: Veloria-EDC0E70B; Rendering: prose; Support structure: equivalent_support; Required fact count: 2; Overall judgment: **pass**.

Required facts: review_days = 21 working days; retention_days = 60 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R9 review interval of 21 working days and retention period of 60 calendar days are supported by S01 and S06, matching the two-field question.

Evidence: S01, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

Both prose spans fully specify the subject/R9/relationship; S03/S04 in the complete external-domain chunk also contain complete assertions. Semantics and source permission should be assessed separately, without calling the spans incomplete merely because of their domain.

Evidence: S01, S06, S03, S04.

**D3 Temporal and revision status: pass**

The R8 value of 14 working days is obsolete; 14 days under R9 in S08 contradicts the current 21 days. The obsolete/contradictory distinction is appropriate.

Evidence: S01, S07, S08.

**D4 Source policy: pass**

Only edc0e70b068d.registry.invalid is allowed; S03/S04 give correct current values but are on consortium and cannot serve as alternative support from allowed sources.

Evidence: S03, S04, S08, S01, S06.

**Findings for this world**

- In the equivalent-support design, complete sets from external and allowed domains must be counted separately.

**Original-text evidence index**

- **S01**: chunk `6105e29bf8d894e8af502ea7a947`, claim `41b714a6a7ca4c34c5fde73dd300`, Character span `[1595, 1683)`; Source `https://edc0e70b068d.registry.invalid/operative-record`.
  > For entity Veloria-EDC0E70B in revision R9, the file review interval is 21 working days.
- **S06**: chunk `78cecc0da92444a1e20201e2d461`, claim `01fdb76d582e4612fc51a2629b55`, Character span `[1521, 1615)`; Source `https://edc0e70b068d.registry.invalid/operative-part-1`.
  > For entity Veloria-EDC0E70B in revision R9, the archival retention period is 60 calendar days.
- **S03**: chunk `f2286d242c022b26025ee800557d`, claim `10881df3ad9e96b030df489171a0`, Character span `[1512, 1600)`; Source `https://edc0e70b068d.consortium.invalid/complete-current`.
  > For entity Veloria-EDC0E70B in revision R9, the file review interval is 21 working days.
- **S04**: chunk `f2286d242c022b26025ee800557d`, claim `97c285ac9445702e7305eb0cd377`, Character span `[1602, 1696)`; Source `https://edc0e70b068d.consortium.invalid/complete-current`.
  > For entity Veloria-EDC0E70B in revision R9, the archival retention period is 60 calendar days.
- **S07**: chunk `c645e285b29cb16f573b495713bd`, claim `71163d435f08fbeca0c4f7beaea0`, Character span `[1561, 1649)`; Source `https://edc0e70b068d.registry.invalid/archive`.
  > For entity Veloria-EDC0E70B in revision R8, the file review interval is 14 working days.
- **S08**: chunk `13afe58bfb99b263b5213ef379bd`, claim `064bd477370a6fadb6788160b37b`, Character span `[1550, 1638)`; Source `https://edc0e70b068d.consortium.invalid/disputed`.
  > For entity Veloria-EDC0E70B in revision R9, the file review interval is 14 working days.

## World 29: 40a25298fb4914fa4245f4622b23

Question IDs: `1908b36d0aea2310d9389354803a`, `4b40f6b39197c6e792eeb1d6ec02`.

Collection IDs: `f75f209367c6878f7f83f7f0145c`, `70e499bc5f43d1ac7a900a7fe9da`.

Entity: Veloria-40A25298; Rendering: prose; Support structure: position; Required fact count: 4; Overall judgment: **pass**.

Required facts: route = Cobalt-73; review_days = 3 working days; release_code = Permit-V31; retention_days = 60 calendar days.

**D1 Consistency of required facts with the original text: pass**

The requested R9 route, review interval, code, and retention period are Cobalt-73, 3 working days, Permit-V31, and 60 days, corresponding individually to S01/S08/S07/S03.

Evidence: S01, S08, S07, S03.

**D2 Complete assertions, complementary support, and alternative support: pass**

All four prose spans fully bind Veloria-40A25298 and R9, beginning around characters 664–702; arbitrary text from the same page cannot replace these assertions.

Evidence: S01, S03, S07, S08.

**D3 Temporal and revision status: pass**

R8/Willow-84 is the obsolete route; S06 gives Willow-84 under R9, contradicting Cobalt-73. Both negative-example judgments are correct.

Evidence: S01, S09, S06.

**D4 Source policy: pass**

The 40a25298fb49.registry.invalid allowlist permits all primary supports and prohibits the consortium domain of S06; Annex is on an allowed domain but still has the wrong subject.

Evidence: S01, S03, S07, S08, S06, S04.

**Findings for this world**

- Both allowed source and target entity must be checked; neither can be established by a correct value alone.

**Original-text evidence index**

- **S01**: chunk `707ab8557c46940468504cf862e2`, claim `6d0f085e174f3be6bc58fa5efcb8`, Character span `[698, 773)`; Source `https://40a25298fb49.registry.invalid/replica-3`.
  > For entity Veloria-40A25298 in revision R9, the service route is Cobalt-73.
- **S08**: chunk `5f7f554510d182f4d2594c224f5b`, claim `929f57123b42cc848c3bd20ad358`, Character span `[676, 763)`; Source `https://40a25298fb49.registry.invalid/operative-record`.
  > For entity Veloria-40A25298 in revision R9, the file review interval is 3 working days.
- **S07**: chunk `ab4e9dc5cd78ef57e148b2f23b36`, claim `eeb7096f300230cef81b330cef6a`, Character span `[702, 791)`; Source `https://40a25298fb49.registry.invalid/operative-record`.
  > For entity Veloria-40A25298 in revision R9, the release authorization code is Permit-V31.
- **S03**: chunk `ddbe8ae2d950c0c903647c3d66fa`, claim `c70dbc3249b7fe2a68491447cd55`, Character span `[664, 758)`; Source `https://40a25298fb49.registry.invalid/operative-record`.
  > For entity Veloria-40A25298 in revision R9, the archival retention period is 60 calendar days.
- **S09**: chunk `bf2ac554dd64d1bf7f0e175807de`, claim `e353e2456727def0ef0647a5bd71`, Character span `[678, 753)`; Source `https://40a25298fb49.registry.invalid/archive`.
  > For entity Veloria-40A25298 in revision R8, the service route is Willow-84.
- **S06**: chunk `9f792895637c5872daaff0532d8f`, claim `93c4699519e7530dd976ac765e18`, Character span `[691, 766)`; Source `https://40a25298fb49.consortium.invalid/disputed`.
  > For entity Veloria-40A25298 in revision R9, the service route is Willow-84.
- **S04**: chunk `8c198b152f3580a94fe61fd64c42`, claim `bf8ffb521aff43537699ff0ec549`, Character span `[700, 781)`; Source `https://40a25298fb49.registry.invalid/annex-0`.
  > For entity Veloria-40A25298-Annex in revision R9, the service route is Cobalt-73.

## World 30: 26e56412928bd49d9b924657b892

Question IDs: `62a08e711fd6b062ab1103360464`, `8b1ac140a5236463595e8272f9f1`.

Collection IDs: `9f4386f750e64f3cd4d73ca81efb`, `a9522f5d4039a76513a6cfc0094a`.

Entity: Veloria-26E56412; Rendering: prose; Support structure: same_url_complementary; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Aster-14; retention_days = 120 calendar days; release_code = Permit-V71.

**D1 Consistency of required facts with the original text: pass**

Aster-14, 120 calendar days, and Permit-V71 requested by the R5 question can be recovered from S02/S04/S06, with no requested field missing.

Evidence: S02, S04, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each prose assertion fully includes the entity and R5; route replicas complement support for the other two fields. The operative-record URL identity cannot replace complete support for all three facts.

Evidence: S02, S04, S06.

**D3 Temporal and revision status: pass**

R4/Juniper-33 is obsolete on the query date; R5/Juniper-33 in S07 disagrees with the current Aster-14 and is a contradictory current assertion.

Evidence: S02, S05, S07.

**D4 Source policy: pass**

The allowlist is 26e56412928b.registry.invalid; primary supports and archive are allowed, whereas S07 on consortium/disputed is prohibited.

Evidence: S02, S04, S06, S07.

**Findings for this world**

- The identical Annex route, retention period, and code should all be excluded because of the subject suffix; none was found to have been included as target-entity support.

**Original-text evidence index**

- **S02**: chunk `d97da26481f342a2d2dba5412c35`, claim `b495522038f82ac2bb2b07f5c74d`, Character span `[607, 681)`; Source `https://26e56412928b.registry.invalid/replica-1`.
  > For entity Veloria-26E56412 in revision R5, the service route is Aster-14.
- **S04**: chunk `c164284c0c1ca96fce1ce67dda30`, claim `c9092ca931b58466d8a70baa477b`, Character span `[587, 682)`; Source `https://26e56412928b.registry.invalid/operative-record`.
  > For entity Veloria-26E56412 in revision R5, the archival retention period is 120 calendar days.
- **S06**: chunk `2c676cbf5cdd411260dfb13a7bd3`, claim `dd950635b5758eb16632b61b6f67`, Character span `[674, 763)`; Source `https://26e56412928b.registry.invalid/operative-record`.
  > For entity Veloria-26E56412 in revision R5, the release authorization code is Permit-V71.
- **S05**: chunk `caa641082a5973649e3c1d89fca3`, claim `d027b5011735c20c5e99a0ad1906`, Character span `[584, 660)`; Source `https://26e56412928b.registry.invalid/archive`.
  > For entity Veloria-26E56412 in revision R4, the service route is Juniper-33.
- **S07**: chunk `0f97542cc5a343b53025ab1c5246`, claim `a4950214d80f9bb559466ca2cf29`, Character span `[599, 675)`; Source `https://26e56412928b.consortium.invalid/disputed`.
  > For entity Veloria-26E56412 in revision R5, the service route is Juniper-33.

## World 31: 5e6b32b22ee4ebe8756516cb78c7

Question IDs: `09ca67105a33ffe72f4f0871f9ad`, `7a794ed52dc2887791d0439a1d0c`.

Collection IDs: `9a6c236e3f43fba2f17b2f01e4e0`, `2dd5171fcbc91cb46cee1e06c571`.

Entity: Veloria-5E6B32B2; Rendering: prose; Support structure: single_chunk; Required fact count: 4; Overall judgment: **pass**.

Required facts: review_days = 14 working days; release_code = Permit-K81; retention_days = 30 calendar days; route = Willow-48.

**D1 Consistency of required facts with the original text: pass**

The R6 values 14 working days, Permit-K81, 30 calendar days, and Willow-48 are explicitly supported by S01–S04; all four fields and values match the question.

Evidence: S01, S02, S03, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four complete prose assertions share one positive chunk, each naming the target entity and R6; the whole chunk supports four facts, but retaining only its first half does not establish complete delivery.

Evidence: S01, S02, S03, S04.

**D3 Temporal and revision status: pass**

R6 applies on 2035-06-01; R5/7 working days is the old review interval, whereas S09 gives 7 days under R6, contradicting the current 14 days.

Evidence: S01, S06, S09.

**D4 Source policy: pass**

Sources are restricted to 5e6b32b22ee4.registry.invalid; all four positive examples are allowed, whereas the current conflicting value on consortium/disputed violates the source prefix.

Evidence: S01, S02, S03, S04, S09.

**Findings for this world**

- Complete single-chunk support starts at character 979 and extends through the end of the route assertion; the presence of the first assertion does not establish delivery of every fact in the chunk.
- Current Annex values do not concern the target entity.

**Original-text evidence index**

- **S01**: chunk `73c448f860287225a78e88109bf8`, claim `4ceb8f632c1300585dff51f63921`, Character span `[979, 1067)`; Source `https://5e6b32b22ee4.registry.invalid/replica-0`.
  > For entity Veloria-5E6B32B2 in revision R6, the file review interval is 14 working days.
- **S02**: chunk `73c448f860287225a78e88109bf8`, claim `b9ae88831a24b2d15c45f793118b`, Character span `[1069, 1158)`; Source `https://5e6b32b22ee4.registry.invalid/replica-0`.
  > For entity Veloria-5E6B32B2 in revision R6, the release authorization code is Permit-K81.
- **S03**: chunk `73c448f860287225a78e88109bf8`, claim `ee77abdcb6e5c24fe89a0097d8b1`, Character span `[1160, 1254)`; Source `https://5e6b32b22ee4.registry.invalid/replica-0`.
  > For entity Veloria-5E6B32B2 in revision R6, the archival retention period is 30 calendar days.
- **S04**: chunk `73c448f860287225a78e88109bf8`, claim `49185794171a41eabc2bab3ad126`, Character span `[1256, 1331)`; Source `https://5e6b32b22ee4.registry.invalid/replica-0`.
  > For entity Veloria-5E6B32B2 in revision R6, the service route is Willow-48.
- **S06**: chunk `be84e6147173e5921fbd465e3eec`, claim `fe1937dc9543eeea4d08bb47244a`, Character span `[976, 1063)`; Source `https://5e6b32b22ee4.registry.invalid/archive`.
  > For entity Veloria-5E6B32B2 in revision R5, the file review interval is 7 working days.
- **S09**: chunk `8e70bed8ad9b087bcb300f0beb08`, claim `eb0581ff035b71ddff26128aa32b`, Character span `[992, 1079)`; Source `https://5e6b32b22ee4.consortium.invalid/disputed`.
  > For entity Veloria-5E6B32B2 in revision R6, the file review interval is 7 working days.

## World 32: 522c7cc27a9f414b6832a5ead858

Question IDs: `a6f7fa0f54d3d90258e7ee10d9b4`, `b23b50f35033eb9669d2e80c07cb`.

Collection IDs: `cd4d71c9312358146751a6052c79`, `b43331bfd56e642717c6c5e4a015`.

Entity: Veloria-522C7CC2; Rendering: prose; Support structure: temporal_conflict; Required fact count: 2; Overall judgment: **pass**.

Required facts: retention_days = 120 calendar days; route = Willow-61.

**D1 Consistency of required facts with the original text: pass**

R4 requires retention of 120 calendar days and route Willow-61; S01 and S06 are complete current statements about this entity.

Evidence: S01, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

Both original spans contain the subject, R4, field, and value; the two conflicting values occurring together in archive or disputed chunks are not alternative expressions of current support.

Evidence: S01, S06, S03, S04, S07, S08.

**D3 Temporal and revision status: pass**

R3/180 days and Willow-11 form the old combination; the same 180 days/Willow-11 under R4 conflict with the current 120 days/Willow-61.

Evidence: S03, S04, S07, S08.

**D4 Source policy: pass**

The question leaves sources unrestricted, so registry and consortium are both allowed; S07/S08 lose credit because of their content rather than source policy.

Evidence: S01, S06, S07, S08.

**Findings for this world**

- The similar route names Willow-61 and Willow-11 cannot be merged; temporal/revision status and values all require checking.

**Original-text evidence index**

- **S01**: chunk `02d0bfeecc9ff28bb960d79e605d`, claim `2346c0d38fc3896b9a04088065a6`, Character span `[294, 389)`; Source `https://522c7cc27a9f.registry.invalid/replica-1`.
  > For entity Veloria-522C7CC2 in revision R4, the archival retention period is 120 calendar days.
- **S06**: chunk `071f9293f5413eb7c65b899133f6`, claim `fe59229aa4f0f0ea96b264cd1c93`, Character span `[302, 377)`; Source `https://522c7cc27a9f.registry.invalid/operative-record`.
  > For entity Veloria-522C7CC2 in revision R4, the service route is Willow-61.
- **S03**: chunk `8dbce1c2cb96f9f94d333c064b91`, claim `0bf7561f47cf128fb8803931502a`, Character span `[291, 386)`; Source `https://522c7cc27a9f.registry.invalid/archive`.
  > For entity Veloria-522C7CC2 in revision R3, the archival retention period is 180 calendar days.
- **S04**: chunk `8dbce1c2cb96f9f94d333c064b91`, claim `17fc5e57e7d6c2682a71ca30f116`, Character span `[388, 463)`; Source `https://522c7cc27a9f.registry.invalid/archive`.
  > For entity Veloria-522C7CC2 in revision R3, the service route is Willow-11.
- **S07**: chunk `ef75ac6117915ea4bbd11e5baff1`, claim `84e46df1d1a9dfa87ffcc2c6372a`, Character span `[299, 394)`; Source `https://522c7cc27a9f.consortium.invalid/disputed`.
  > For entity Veloria-522C7CC2 in revision R4, the archival retention period is 180 calendar days.
- **S08**: chunk `ef75ac6117915ea4bbd11e5baff1`, claim `95aee202df34b780fd445d312b0b`, Character span `[396, 471)`; Source `https://522c7cc27a9f.consortium.invalid/disputed`.
  > For entity Veloria-522C7CC2 in revision R4, the service route is Willow-11.

## World 33: b1af6c74b835e6d857dcce8b3ac7

Question IDs: `097b732f6c272ec76847f06be8da`, `384bfb4850c2a5b5eba376441ce4`.

Collection IDs: `5053b69fda51669d4bed38865f3f`, `e90b1c4659421d6e805d05d9875e`.

Entity: Veloria-B1AF6C74; Rendering: qa; Support structure: cross_url_complementary; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Aster-63; release_code = Permit-K69; retention_days = 60 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R4 question requires Aster-63, Permit-K69, and 60 calendar days, individually supplied by the positive QA examples S06/S08/S04.

Evidence: S06, S08, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

All three annotated spans include a question specifying the entity, R4, and field plus the complete answer; they span operative-record and part-1/2 and are complementary rather than duplicates.

Evidence: S04, S06, S08.

**D3 Temporal and revision status: pass**

R3/Willow-82 is obsolete; S05 answers Willow-82 under R4, contradicting the current Aster-63. The distinction between revision-related negative examples is supported.

Evidence: S06, S03, S05.

**D4 Source policy: pass**

There is no allowed-prefix restriction, so S05 on consortium is source-allowed; the primary registry supports are also allowed, and the designated page must not be treated as the only acceptable source.

Evidence: S04, S06, S08, S05.

**Findings for this world**

- QA support requires treating the question and answer as a joint assertion; correct Annex answers do not complete support for the target entity.

**Original-text evidence index**

- **S06**: chunk `b7170771363e5aa190d3328bfed2`, claim `06fccc721579eb0cd1eb216c6b98`, Character span `[2049, 2138)`; Source `https://b1af6c74b835.registry.invalid/operative-record`.
  > Q: Under revision R4, what is the service route for entity Veloria-B1AF6C74? A: Aster-63.
- **S08**: chunk `78847513c1de47d97d6bae775731`, claim `80bce18eccae4b22d6fabe11b9f4`, Character span `[1950, 2054)`; Source `https://b1af6c74b835.registry.invalid/operative-part-1`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-B1AF6C74? A: Permit-K69.
- **S04**: chunk `78801c1ad2b70d44c20ecd0c27eb`, claim `cfd9dcbd94a744d3edca3ae4eb75`, Character span `[1920, 2029)`; Source `https://b1af6c74b835.registry.invalid/operative-part-2`.
  > Q: Under revision R4, what is the archival retention period for entity Veloria-B1AF6C74? A: 60 calendar days.
- **S03**: chunk `5e914cb2d5a524d76190390358c5`, claim `c0ba50d4f926253c86847c4066f5`, Character span `[2034, 2124)`; Source `https://b1af6c74b835.registry.invalid/archive`.
  > Q: Under revision R3, what is the service route for entity Veloria-B1AF6C74? A: Willow-82.
- **S05**: chunk `d3ea33e14746ee895c27d4b58d97`, claim `a25614f5f9472b05d1000e3ec44d`, Character span `[1998, 2088)`; Source `https://b1af6c74b835.consortium.invalid/disputed`.
  > Q: Under revision R4, what is the service route for entity Veloria-B1AF6C74? A: Willow-82.

## World 34: 39ebf7945377d5463628344bc248

Question IDs: `6718cc8d772193b662a9bf6280db`, `1892bacba0e75ae7b0ac2a680ee7`.

Collection IDs: `6b39ba5326c86d18ad628d0a2b92`, `552c4932a407f2985e4f5866bfd6`.

Entity: Veloria-39EBF794; Rendering: qa; Support structure: equivalent_support; Required fact count: 2; Overall judgment: **pass**.

Required facts: route = Willow-43; review_days = 14 working days.

**D1 Consistency of required facts with the original text: pass**

The requested R6 route and review interval are Willow-43 and 14 working days; the current QA pairs S02/S03 agree with the truth values.

Evidence: S02, S03.

**D2 Complete assertions, complementary support, and alternative support: pass**

The independent-current chunk contains two complete Q+A pairs and independently supplies complete support; the distributed set is an alternative path, and both sets are not required simultaneously.

Evidence: S02, S03.

**D3 Temporal and revision status: pass**

S05 gives the old R5/Aster-81 route, whereas S04 gives the current conflicting R6/Aster-81 value; their statuses should be obsolete and contradictory, respectively. The current positive value remains Willow-43.

Evidence: S02, S05, S04.

**D4 Source policy: pass**

Sources are unrestricted, so consortium/disputed does not violate policy; S04 still cannot establish the correct route. Factual validity and source acceptability remain separate.

Evidence: S02, S03, S04.

**Findings for this world**

- The two Annex QA pairs give the same Willow-43 and 14 days, but the subject suffix makes them irrelevant to the question.

**Original-text evidence index**

- **S02**: chunk `9e4f2e350acfe2bb56e25edbde37`, claim `9c4bafe186e161926981098532ad`, Character span `[809, 899)`; Source `https://39ebf7945377.registry.invalid/independent-current`.
  > Q: Under revision R6, what is the service route for entity Veloria-39EBF794? A: Willow-43.
- **S03**: chunk `9e4f2e350acfe2bb56e25edbde37`, claim `587140a7f2efead7b8552042fd14`, Character span `[901, 1004)`; Source `https://39ebf7945377.registry.invalid/independent-current`.
  > Q: Under revision R6, what is the file review interval for entity Veloria-39EBF794? A: 14 working days.
- **S05**: chunk `f835330500868379c38b74b8e3e0`, claim `99f994a3aebf8d9f4c07e8a60332`, Character span `[770, 859)`; Source `https://39ebf7945377.registry.invalid/archive`.
  > Q: Under revision R5, what is the service route for entity Veloria-39EBF794? A: Aster-81.
- **S04**: chunk `8d573ec00fc70aa9cabcc05322ec`, claim `3e434375f2ccf0eea8fee92671d5`, Character span `[805, 894)`; Source `https://39ebf7945377.consortium.invalid/disputed`.
  > Q: Under revision R6, what is the service route for entity Veloria-39EBF794? A: Aster-81.

## World 35: b4efb019e822cf2464209df9c08b

Question IDs: `ebc1465a1ded3321840519436b79`, `d6543e8063a96bb075615d0261d4`.

Collection IDs: `81e530b8b796d4ba78a68b62a101`, `0672b48a0cb3f682551abb4b9d8c`.

Entity: Veloria-B4EFB019; Rendering: qa; Support structure: position; Required fact count: 3; Overall judgment: **pass**.

Required facts: release_code = Permit-M64; retention_days = 120 calendar days; route = Juniper-87.

**D1 Consistency of required facts with the original text: pass**

Permit-M64, 120 calendar days, and Juniper-87 requested by the R7 question occur in the target-entity QA pairs S04/S07/S06, respectively.

Evidence: S04, S07, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three QA spans fully retain the entity, R7, and field in the question; starting around characters 394–406 does not itself guarantee scoring visibility, but the original semantic bindings are complete.

Evidence: S04, S06, S07.

**D3 Temporal and revision status: pass**

R6/Permit-V61 is the old code; R7/V61 in S05 disagrees with the current M64, so the distinct statuses of the two negative examples are appropriate.

Evidence: S04, S02, S05.

**D4 Source policy: pass**

There is no source allowlist, so the consortium source of S05 is admissible; the code contradiction, rather than domain noncompliance, explains its lack of factual support.

Evidence: S04, S05.

**Findings for this world**

- All three fields have current support from allowed sources; identical-value Annex passages are not alternatives.

**Original-text evidence index**

- **S04**: chunk `d1d490126484ced04482548fc3a9`, claim `17a969c6bf22ad6e688f7c91747f`, Character span `[394, 498)`; Source `https://b4efb019e822.registry.invalid/replica-3`.
  > Q: Under revision R7, what is the release authorization code for entity Veloria-B4EFB019? A: Permit-M64.
- **S07**: chunk `13ba5e7a400602ae84d39fd759cc`, claim `46b7707c0d379449cadb473fe195`, Character span `[406, 516)`; Source `https://b4efb019e822.registry.invalid/operative-record`.
  > Q: Under revision R7, what is the archival retention period for entity Veloria-B4EFB019? A: 120 calendar days.
- **S06**: chunk `b7503f8056a9ad2aa38c510823b2`, claim `98a91da49bb38e1a5f524e70f421`, Character span `[405, 496)`; Source `https://b4efb019e822.registry.invalid/operative-record`.
  > Q: Under revision R7, what is the service route for entity Veloria-B4EFB019? A: Juniper-87.
- **S02**: chunk `0d964200b7f1f7602b12e5cffe83`, claim `8832002b6d9cfa006144915d83d8`, Character span `[409, 513)`; Source `https://b4efb019e822.registry.invalid/archive`.
  > Q: Under revision R6, what is the release authorization code for entity Veloria-B4EFB019? A: Permit-V61.
- **S05**: chunk `7ef397b901df073999d6458fbef0`, claim `226bc7d972acbbbcbd60c22b5084`, Character span `[382, 486)`; Source `https://b4efb019e822.consortium.invalid/disputed`.
  > Q: Under revision R7, what is the release authorization code for entity Veloria-B4EFB019? A: Permit-V61.

## World 36: 29ecbcc62ac8cec0dc44f6ba30cf

Question IDs: `ef57f2a6a1887c42cbdedc5ac6ce`, `cc42ac7e5d75a61e10ec960ea808`.

Collection IDs: `844d3d270fdbdfd33ba6e51eeed3`, `d296c753e229ce14658eded5a7d9`.

Entity: Veloria-29ECBCC6; Rendering: qa; Support structure: same_url_complementary; Required fact count: 4; Overall judgment: **pass**.

Required facts: route = Willow-39; release_code = Permit-V55; retention_days = 60 calendar days; review_days = 5 working days.

**D1 Consistency of required facts with the original text: pass**

R8 requires Willow-39, Permit-V55, 60 calendar days, and 5 working days, corresponding in order to S02/S08/S03/S07 with matching QA meanings.

Evidence: S02, S08, S03, S07.

**D2 Complete assertions, complementary support, and alternative support: pass**

All four Q+A pairs retain the revision and subject; the original supports share one URL but occupy different chunks. Route replicas cannot replace retention, code, and review-interval support.

Evidence: S02, S03, S07, S08.

**D3 Temporal and revision status: pass**

R7/Willow-61 is the old route; Willow-61 under R8 conflicts with Willow-39. The statuses of S09 and S05 have independent textual evidence.

Evidence: S02, S09, S05.

**D4 Source policy: pass**

The 29ecbcc62ac8.registry.invalid allowlist permits positive examples and archive and prohibits consortium/disputed; the source flag for S05 is correct.

Evidence: S02, S03, S07, S08, S05.

**Findings for this world**

- Same-URL complementary support for four fields cannot be judged from page retention alone; field binding in QA comes from the question line.

**Original-text evidence index**

- **S02**: chunk `b57f98b468903399916a21356dab`, claim `8ac5a4cae85afe8e3eeae3d70357`, Character span `[1499, 1589)`; Source `https://29ecbcc62ac8.registry.invalid/replica-9`.
  > Q: Under revision R8, what is the service route for entity Veloria-29ECBCC6? A: Willow-39.
- **S08**: chunk `197ecb0d41c4774e5b5a5c75599d`, claim `be2dea5c58a7dbe792a330469e23`, Character span `[1464, 1568)`; Source `https://29ecbcc62ac8.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the release authorization code for entity Veloria-29ECBCC6? A: Permit-V55.
- **S03**: chunk `d8e631bc569e01352ad60851efad`, claim `168bdd5318e507d6a5353a3390de`, Character span `[1338, 1447)`; Source `https://29ecbcc62ac8.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the archival retention period for entity Veloria-29ECBCC6? A: 60 calendar days.
- **S07**: chunk `426a12803840f4d2ec4d2abefd55`, claim `42976f7591536e5d7539d0305915`, Character span `[1394, 1496)`; Source `https://29ecbcc62ac8.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the file review interval for entity Veloria-29ECBCC6? A: 5 working days.
- **S09**: chunk `7e772b192a7dbaded6e2dbc19a4d`, claim `bf8b5ee746af80fdd100b7cadaad`, Character span `[1350, 1440)`; Source `https://29ecbcc62ac8.registry.invalid/archive`.
  > Q: Under revision R7, what is the service route for entity Veloria-29ECBCC6? A: Willow-61.
- **S05**: chunk `781d674923f795973dc9d76f9c0b`, claim `31174b868f77a10de70723f9e929`, Character span `[1468, 1558)`; Source `https://29ecbcc62ac8.consortium.invalid/disputed`.
  > Q: Under revision R8, what is the service route for entity Veloria-29ECBCC6? A: Willow-61.

## World 37: a14db04fc497b5cf89ea45d7053d

Question IDs: `06e46f2893dea942fb3b12191024`, `e98e2bdcb3f930e8b31d7d186568`.

Collection IDs: `9ec1cdbf58d4a189f1a19cb4339c`, `8adad641aaec0862d5ad544126be`.

Entity: Veloria-A14DB04F; Rendering: qa; Support structure: single_chunk; Required fact count: 4; Overall judgment: **pass**.

Required facts: release_code = Permit-M20; review_days = 7 working days; route = Willow-67; retention_days = 60 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R8 QA pairs give Permit-M20, 7 working days, Willow-67, and 60 calendar days; S02–S05 cover all required fields.

Evidence: S02, S03, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four complete Q+A pairs share one positive chunk, with each question stating the entity, R8, and field; this chunk and its complete replicas support all four facts.

Evidence: S02, S03, S04, S05.

**D3 Temporal and revision status: pass**

R7/Permit-R69 in S01 is obsolete; R8/R69 in S07 contradicts the current M20. A code's historical occurrence does not justify credit.

Evidence: S02, S01, S07.

**D4 Source policy: pass**

Unrestricted sources permit both registry and consortium; the content contradiction in S07 is independent of its allowed-source identity.

Evidence: S02, S07.

**Findings for this world**

- Complete support in one chunk does not mean one answer value suffices; all four QA bindings must be retained individually.
- The three Annex QA pairs concern a different subject and should remain irrelevant.

**Original-text evidence index**

- **S02**: chunk `c6619cc27a01a44c7340c8346a18`, claim `c9b7416e95015e24b60b592f95f1`, Character span `[607, 711)`; Source `https://a14db04fc497.registry.invalid/replica-2`.
  > Q: Under revision R8, what is the release authorization code for entity Veloria-A14DB04F? A: Permit-M20.
- **S03**: chunk `c6619cc27a01a44c7340c8346a18`, claim `59c110d66f3b001aa22b3d6b38d5`, Character span `[713, 815)`; Source `https://a14db04fc497.registry.invalid/replica-2`.
  > Q: Under revision R8, what is the file review interval for entity Veloria-A14DB04F? A: 7 working days.
- **S04**: chunk `c6619cc27a01a44c7340c8346a18`, claim `3ab2bad25eab962f614fa0f882d2`, Character span `[817, 907)`; Source `https://a14db04fc497.registry.invalid/replica-2`.
  > Q: Under revision R8, what is the service route for entity Veloria-A14DB04F? A: Willow-67.
- **S05**: chunk `c6619cc27a01a44c7340c8346a18`, claim `6f3b947c25e49c1b3adc3fce1549`, Character span `[909, 1018)`; Source `https://a14db04fc497.registry.invalid/replica-2`.
  > Q: Under revision R8, what is the archival retention period for entity Veloria-A14DB04F? A: 60 calendar days.
- **S01**: chunk `fad3c8bf4188e4e24592fc656be9`, claim `b6f393331af73a1b42977b803f8d`, Character span `[663, 767)`; Source `https://a14db04fc497.registry.invalid/archive`.
  > Q: Under revision R7, what is the release authorization code for entity Veloria-A14DB04F? A: Permit-R69.
- **S07**: chunk `f3b9eb1f14c91fdf3afad12dbacb`, claim `e6984a028a71a020b096d5e40020`, Character span `[580, 684)`; Source `https://a14db04fc497.consortium.invalid/disputed`.
  > Q: Under revision R8, what is the release authorization code for entity Veloria-A14DB04F? A: Permit-R69.

## World 38: 7695c91d098f4b3d52e2d26188fa

Question IDs: `d5f39d2ea82d21f007ece297472d`, `3e313e98a1f2a06f41e35e3202a1`.

Collection IDs: `a9746ecb9ac9f2769fc3f3b1afed`, `8c7d799af86525f306a84587becd`.

Entity: Veloria-7695C91D; Rendering: qa; Support structure: temporal_conflict; Required fact count: 3; Overall judgment: **pass**.

Required facts: review_days = 14 working days; route = Juniper-64; retention_days = 90 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R7 values 14 working days, Juniper-64, and 90 calendar days are supported by S05/S11/S10, respectively, matching the three requested fields.

Evidence: S05, S11, S10.

**D2 Complete assertions, complementary support, and alternative support: pass**

All three current QA spans include the target entity and R7; the three conflicting values in the complete disputed chunk do not provide alternative support for the three current facts, even when all are present.

Evidence: S05, S10, S11, S07, S08, S09.

**D3 Temporal and revision status: pass**

The old R6 combination is 11 days/Cobalt-79/30 days; S07–S09 repeat it under R7, contradicting the current 14 days/Juniper-64/90 days.

Evidence: S02, S03, S04, S07, S08, S09.

**D4 Source policy: pass**

The question restricts sources to 7695c91d098f.registry.invalid; all three current positive examples are allowed, whereas the full consortium group S07–S09 is prohibited.

Evidence: S05, S10, S11, S07, S08, S09.

**Findings for this world**

- The old-revision and current contradictory three-field groups must not be merged into one temporal status in this world.

**Original-text evidence index**

- **S05**: chunk `8fcca4b3b817a1cf53b4f12b99ad`, claim `58a60b5184865fe3c90c3f7d340f`, Character span `[1069, 1172)`; Source `https://7695c91d098f.registry.invalid/replica-3`.
  > Q: Under revision R7, what is the file review interval for entity Veloria-7695C91D? A: 14 working days.
- **S11**: chunk `234249a8bdde5bf0ec804040f41c`, claim `eb0273bbd422fdab5ea1462907fa`, Character span `[1064, 1155)`; Source `https://7695c91d098f.registry.invalid/operative-record`.
  > Q: Under revision R7, what is the service route for entity Veloria-7695C91D? A: Juniper-64.
- **S10**: chunk `a01091958daab9b1791f150d0fca`, claim `5938e80ffc75166b0b4f593fde3f`, Character span `[1067, 1176)`; Source `https://7695c91d098f.registry.invalid/operative-record`.
  > Q: Under revision R7, what is the archival retention period for entity Veloria-7695C91D? A: 90 calendar days.
- **S07**: chunk `f58c7fa0aba6994ca0154ba7afc3`, claim `a719a712818e4be48e8abad88772`, Character span `[1058, 1161)`; Source `https://7695c91d098f.consortium.invalid/disputed`.
  > Q: Under revision R7, what is the file review interval for entity Veloria-7695C91D? A: 11 working days.
- **S08**: chunk `f58c7fa0aba6994ca0154ba7afc3`, claim `bbb55b04638bf0c89b6ee0debedd`, Character span `[1163, 1253)`; Source `https://7695c91d098f.consortium.invalid/disputed`.
  > Q: Under revision R7, what is the service route for entity Veloria-7695C91D? A: Cobalt-79.
- **S09**: chunk `f58c7fa0aba6994ca0154ba7afc3`, claim `60d526d07ff9f692a2cf45dc9d4e`, Character span `[1255, 1364)`; Source `https://7695c91d098f.consortium.invalid/disputed`.
  > Q: Under revision R7, what is the archival retention period for entity Veloria-7695C91D? A: 30 calendar days.
- **S02**: chunk `d895f4846f2bfc9f80375c5eb4ae`, claim `202a6fd79b70d20fb2ce09b1328d`, Character span `[1083, 1186)`; Source `https://7695c91d098f.registry.invalid/archive`.
  > Q: Under revision R6, what is the file review interval for entity Veloria-7695C91D? A: 11 working days.
- **S03**: chunk `d895f4846f2bfc9f80375c5eb4ae`, claim `8311dff9cfe415dcac70d44cff27`, Character span `[1188, 1278)`; Source `https://7695c91d098f.registry.invalid/archive`.
  > Q: Under revision R6, what is the service route for entity Veloria-7695C91D? A: Cobalt-79.
- **S04**: chunk `d895f4846f2bfc9f80375c5eb4ae`, claim `c7818655b7ac4a1af81b2b5eeb7f`, Character span `[1280, 1389)`; Source `https://7695c91d098f.registry.invalid/archive`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-7695C91D? A: 30 calendar days.

## World 39: 5d8ec042a5715e6a76377096cc38

Question IDs: `54e16d66e8b8f833a0b8bb11ee4b`, `d9ac1de5416c74f0c045e727b0f8`.

Collection IDs: `a444d2512bc49f667878084c9b95`, `0db9c3caab8df659e7b01a4e7d5f`.

Entity: Veloria-5D8EC042; Rendering: list; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: retention_days = 90 calendar days; route = Aster-24.

**D1 Consistency of required facts with the original text: pass**

The R9 archival period of 90 calendar days and route Aster-24 are supported by the list sentences in S04 and S01, respectively.

Evidence: S04, S01.

**D2 Complete assertions, complementary support, and alternative support: pass**

The retention period in operative-record and route in operative-part-1 each have an independent, complete Entity/R9 binding, providing complementary support across two chunks.

Evidence: S01, S04.

**D3 Temporal and revision status: pass**

R8/30 calendar days in S05 is obsolete; R9/30 days in S03 contradicts the current 90 days. The two labels must not be merged.

Evidence: S04, S05, S03.

**D4 Source policy: pass**

5d8ec042a571.registry.invalid is the allowed prefix; both primary supports comply, whereas consortium/disputed in S03 violates the prefix restriction.

Evidence: S01, S04, S03.

**Findings for this world**

- The 90 days and Aster-24 in Annex do not concern the requested subject and cannot complete support, even from an allowed source.

**Original-text evidence index**

- **S04**: chunk `b4256ca7b68ab0aeb1304aa767da`, claim `b5944231364d7e96b4aa84291e0e`, Character span `[1065, 1149)`; Source `https://5d8ec042a571.registry.invalid/operative-record`.
  > - Entity Veloria-5D8EC042; revision R9; archival retention period: 90 calendar days.
- **S01**: chunk `15319045e694c6c808a0e2996192`, claim `c04c9a1b8755c1b92dc05eae0a33`, Character span `[1075, 1139)`; Source `https://5d8ec042a571.registry.invalid/operative-part-1`.
  > - Entity Veloria-5D8EC042; revision R9; service route: Aster-24.
- **S05**: chunk `bd78ea957a5a60b3689719ea8c6a`, claim `6c866042e11e354accf0ef122c7d`, Character span `[1052, 1136)`; Source `https://5d8ec042a571.registry.invalid/archive`.
  > - Entity Veloria-5D8EC042; revision R8; archival retention period: 30 calendar days.
- **S03**: chunk `66d71be5624dc1c69c7abd6e3161`, claim `d6a3d3dee2797e7078e376e6cc01`, Character span `[1063, 1147)`; Source `https://5d8ec042a571.consortium.invalid/disputed`.
  > - Entity Veloria-5D8EC042; revision R9; archival retention period: 30 calendar days.

## World 40: 2ae1c308770eaecc98299006e3de

Question IDs: `9f1aba8a4432f63db4910e316dd8`, `07d870f45fb5607be4a58d3feea3`.

Collection IDs: `5eed0ee71ddb54137bccd373d895`, `cae62a4e29d8a83c8fa10e96749c`.

Entity: Veloria-2AE1C308; Rendering: list; Support structure: equivalent_support; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Willow-33; retention_days = 30 calendar days; review_days = 14 working days.

**D1 Consistency of required facts with the original text: pass**

The R3 route Willow-33, retention period of 30 calendar days, and review interval of 14 working days are given in the target-entity list sentences S03/S04/S05.

Evidence: S03, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three independent-current assertions fully bind Entity/R3/predicate/value; this chunk is an alternative to the three distributed chunks. The complete external-domain chunk requires a separate permission check.

Evidence: S03, S04, S05, S08, S09, S10.

**D3 Temporal and revision status: pass**

R2/Juniper-34 is the old route; R3/Juniper-34 in S06 contradicts the current Willow-33. The temporal and value distinctions are correct.

Evidence: S03, S01, S06.

**D4 Source policy: pass**

Only 2ae1c308770e.registry.invalid is allowed; the three correct facts S08–S10 come from consortium and are semantically valid but cannot count toward allowed-source coverage.

Evidence: S08, S09, S10, S06.

**Findings for this world**

- Semantic validity together with source_allowed=False is not an annotation contradiction; these express different dimensions.
- The independent-current chunk in the allowed domain already supplies all three facts.

**Original-text evidence index**

- **S03**: chunk `e61cdf65bc74b967c018e6f903e1`, claim `390b8cb14319293f41cd0cfa892f`, Character span `[968, 1033)`; Source `https://2ae1c308770e.registry.invalid/independent-current`.
  > - Entity Veloria-2AE1C308; revision R3; service route: Willow-33.
- **S04**: chunk `e61cdf65bc74b967c018e6f903e1`, claim `0a2f0622e26d94096ec7917bbf77`, Character span `[1035, 1119)`; Source `https://2ae1c308770e.registry.invalid/independent-current`.
  > - Entity Veloria-2AE1C308; revision R3; archival retention period: 30 calendar days.
- **S05**: chunk `e61cdf65bc74b967c018e6f903e1`, claim `b8e64d953e8712dae106b6ce6fae`, Character span `[1121, 1199)`; Source `https://2ae1c308770e.registry.invalid/independent-current`.
  > - Entity Veloria-2AE1C308; revision R3; file review interval: 14 working days.
- **S08**: chunk `c25206b6bd6b74b872e8e56c9c2e`, claim `2a872ae7c166989bc6e8ca721577`, Character span `[1070, 1135)`; Source `https://2ae1c308770e.consortium.invalid/complete-current`.
  > - Entity Veloria-2AE1C308; revision R3; service route: Willow-33.
- **S09**: chunk `c25206b6bd6b74b872e8e56c9c2e`, claim `e21c733f952c3cbaa155b4bbbe9c`, Character span `[1137, 1221)`; Source `https://2ae1c308770e.consortium.invalid/complete-current`.
  > - Entity Veloria-2AE1C308; revision R3; archival retention period: 30 calendar days.
- **S10**: chunk `c25206b6bd6b74b872e8e56c9c2e`, claim `e00d38fb57fc688edda5c48155ee`, Character span `[1223, 1301)`; Source `https://2ae1c308770e.consortium.invalid/complete-current`.
  > - Entity Veloria-2AE1C308; revision R3; file review interval: 14 working days.
- **S01**: chunk `041fbb24b94a4d93c42e600dd900`, claim `7c953d4f6b00cf0c11942974a0b0`, Character span `[1068, 1134)`; Source `https://2ae1c308770e.registry.invalid/archive`.
  > - Entity Veloria-2AE1C308; revision R2; service route: Juniper-34.
- **S06**: chunk `957ab3ce077901ac990a32bd8590`, claim `b73d16a30de3e60f7ce2b361a5ee`, Character span `[984, 1050)`; Source `https://2ae1c308770e.consortium.invalid/disputed`.
  > - Entity Veloria-2AE1C308; revision R3; service route: Juniper-34.

## World 41: 7d6eedafd815933dffcc17201b5f

Question IDs: `1ad2c40973799899a46104d081df`, `ec6d294690e920834f2d37610378`.

Collection IDs: `7a768bedc4f408118548bd579526`, `4b2febd32d80baaa6bdf803c9dbd`.

Entity: Veloria-7D6EEDAF; Rendering: list; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: retention_days = 90 calendar days; review_days = 14 working days.

**D1 Consistency of required facts with the original text: pass**

The R6 retention period of 90 calendar days and review interval of 14 working days are given in S01 and S05, fully matching the two requested fields.

Evidence: S01, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

Both list assertions specify Veloria-7D6EEDAF and R6; repeating retention-period replicas cannot complete the complementary two-fact support distributed across two URLs.

Evidence: S01, S05.

**D3 Temporal and revision status: pass**

R5/60 days is the old retention period; R6/60 days in S04 contradicts the current 90 days. The revision and date statuses are appropriately distinguished.

Evidence: S01, S06, S04.

**D4 Source policy: pass**

Unrestricted sources do not exclude 7d6eedafd815.consortium.invalid; S04 is source-allowed but factually contradictory, and these judgments must not be conflated.

Evidence: S01, S04.

**Findings for this world**

- Both Annex assertions have correct values but a different subject and cannot provide alternative support for the requested entity.

**Original-text evidence index**

- **S01**: chunk `4c6c06ac6f6461b9a0351c0aa29d`, claim `2eee09e8bd39e16b4355a5e3168b`, Character span `[410, 494)`; Source `https://7d6eedafd815.registry.invalid/replica-2`.
  > - Entity Veloria-7D6EEDAF; revision R6; archival retention period: 90 calendar days.
- **S05**: chunk `78eae9952183329d0cbe0e6b6442`, claim `924ebaf0cfd04f28440630c85fc9`, Character span `[406, 484)`; Source `https://7d6eedafd815.registry.invalid/operative-part-1`.
  > - Entity Veloria-7D6EEDAF; revision R6; file review interval: 14 working days.
- **S06**: chunk `737b188508b2890c9083a0357fe5`, claim `0dcc14c898b74789632ac5e62994`, Character span `[390, 474)`; Source `https://7d6eedafd815.registry.invalid/archive`.
  > - Entity Veloria-7D6EEDAF; revision R5; archival retention period: 60 calendar days.
- **S04**: chunk `ec48eb14ba5aab28a7548697978e`, claim `bbe9f28276a88c847102c3d35886`, Character span `[405, 489)`; Source `https://7d6eedafd815.consortium.invalid/disputed`.
  > - Entity Veloria-7D6EEDAF; revision R6; archival retention period: 60 calendar days.

## World 42: d47d281811828f77c9b138603dda

Question IDs: `b71a3bd81f1c6d5b50ca5a68ed94`, `a3d4e247e486e6af7abb01e47cfe`.

Collection IDs: `a9a558995c9fdcb6a9407754f89a`, `6a25e7491b2623f685bc9663a50e`.

Entity: Veloria-D47D2818; Rendering: list; Support structure: equivalent_support; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Willow-30; review_days = 5 working days; retention_days = 90 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R6 values Willow-30, 5 working days, and 90 calendar days are supported by the list sentences S06/S04/S01, respectively.

Evidence: S06, S04, S01.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each span fully binds the entity, revision, and field; equivalent support permits either the complete single chunk or the three distributed chunks, rather than requiring every path through a three-URL presence rule.

Evidence: S01, S04, S06.

**D3 Temporal and revision status: pass**

R5/Willow-50 is obsolete on the query date; R6/Willow-50 in S07 contradicts the current Willow-30. Sharing the Willow prefix does not make them identical values.

Evidence: S06, S05, S07.

**D4 Source policy: pass**

The question has no allowed-source prefix, so S07 on consortium is source-allowed; the designated operative-record page is not the only page allowed by policy.

Evidence: S06, S07.

**Findings for this world**

- Equivalent sets provide alternative paths to complete support; replicas and Annex do not change the number of required fields.

**Original-text evidence index**

- **S06**: chunk `6bb49718f15209250acd4d16e8ef`, claim `e0158886c3da45a4567dbd86c451`, Character span `[608, 673)`; Source `https://d47d28181182.registry.invalid/replica-10`.
  > - Entity Veloria-D47D2818; revision R6; service route: Willow-30.
- **S04**: chunk `ce26cb170d885c0dd547d5cc816b`, claim `f65dbd681c9967c07ddf8e46c735`, Character span `[581, 658)`; Source `https://d47d28181182.registry.invalid/operative-part-1`.
  > - Entity Veloria-D47D2818; revision R6; file review interval: 5 working days.
- **S01**: chunk `4c8ac1dfb0bd230ea0c54aa5668b`, claim `6970df5c2f5541e390add2935322`, Character span `[572, 656)`; Source `https://d47d28181182.registry.invalid/operative-part-2`.
  > - Entity Veloria-D47D2818; revision R6; archival retention period: 90 calendar days.
- **S05**: chunk `72aef3cffd4507bba1402653c0a2`, claim `a626b2fe962d2d41d9e7ba72246e`, Character span `[599, 664)`; Source `https://d47d28181182.registry.invalid/archive`.
  > - Entity Veloria-D47D2818; revision R5; service route: Willow-50.
- **S07**: chunk `86658235155ecbfe8c4233979018`, claim `627f13deaa76996d80513a5c2b66`, Character span `[603, 668)`; Source `https://d47d28181182.consortium.invalid/disputed`.
  > - Entity Veloria-D47D2818; revision R6; service route: Willow-50.

## World 43: 28b5106dc8a5ca65f016f0ba3919

Question IDs: `b8b5e52277812e148c7d6b61ffc2`, `fe99cfa05eebadf2bb1329d227a0`.

Collection IDs: `d67e9c1485221c46f71a15bb308f`, `db41d45e5165df53ca42f70f4f53`.

Entity: Veloria-28B5106D; Rendering: list; Support structure: position; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Willow-64; release_code = Permit-K32; review_days = 11 working days.

**D1 Consistency of required facts with the original text: pass**

R7 requires route Willow-64, Permit-K32, and a review interval of 11 working days; the values in S03/S02/S04 all agree.

Evidence: S03, S02, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each primary list span contains the entity and R7, starting around characters 885–969; position changes visibility, but the original assertions remain complete.

Evidence: S02, S03, S04.

**D3 Temporal and revision status: pass**

R6/Aster-84 belongs to the old revision; R7/Aster-84 in S07 contradicts the current Willow-64. Status is not determined solely by the occurrence of an old value.

Evidence: S03, S08, S07.

**D4 Source policy: pass**

Sources are restricted to 28b5106dc8a5.registry.invalid; primary supports are allowed, whereas S07 on consortium/disputed is not. Policy flags agree with the original URLs.

Evidence: S02, S03, S04, S07.

**Findings for this world**

- Correct route replicas cannot replace the code or review interval; identical Annex values should also be excluded.

**Original-text evidence index**

- **S03**: chunk `5e8e05e4c02ac32ac63b0e462565`, claim `b0585d170f6a8d16fe99080daf7b`, Character span `[969, 1034)`; Source `https://28b5106dc8a5.registry.invalid/replica-10`.
  > - Entity Veloria-28B5106D; revision R7; service route: Willow-64.
- **S02**: chunk `f507ec20989bb6537cbe67a5fe9f`, claim `7b04521db9f4f6ae3832d2ecc249`, Character span `[968, 1047)`; Source `https://28b5106dc8a5.registry.invalid/operative-record`.
  > - Entity Veloria-28B5106D; revision R7; release authorization code: Permit-K32.
- **S04**: chunk `7a1d87bd854b78ad41d2b0599d05`, claim `22dfdac4f388a8d8122d6f74dc65`, Character span `[885, 963)`; Source `https://28b5106dc8a5.registry.invalid/operative-record`.
  > - Entity Veloria-28B5106D; revision R7; file review interval: 11 working days.
- **S08**: chunk `d3ebfa1e9e75d6203d5f3a466642`, claim `b1f13745a639c534b3ec26a1fba8`, Character span `[944, 1008)`; Source `https://28b5106dc8a5.registry.invalid/archive`.
  > - Entity Veloria-28B5106D; revision R6; service route: Aster-84.
- **S07**: chunk `926ac51fed5518ac6de093462d53`, claim `c6887bc472efd7564e73534a20a2`, Character span `[910, 974)`; Source `https://28b5106dc8a5.consortium.invalid/disputed`.
  > - Entity Veloria-28B5106D; revision R7; service route: Aster-84.

## World 44: 805164c17a4a8ee79b53dfd32a98

Question IDs: `d8bf2ecebd866454bbf4210256f3`, `6e267caad53d4cb410014ddae1c9`.

Collection IDs: `c7603196e87b29e0f9ca09469ac8`, `e5164f31068dfcb5908592f31d4a`.

Entity: Veloria-805164C1; Rendering: list; Support structure: same_url_complementary; Required fact count: 3; Overall judgment: **pass**.

Required facts: retention_days = 60 calendar days; release_code = Permit-R70; review_days = 3 working days.

**D1 Consistency of required facts with the original text: pass**

The R3 values 60 calendar days, Permit-R70, and 3 working days are supplied by S05/S02/S01, respectively, matching the three-field question.

Evidence: S05, S02, S01.

**D2 Complete assertions, complementary support, and alternative support: pass**

All three list assertions fully bind the subject and R3; although they share the operative-record URL, they remain three complementary pieces of textual support.

Evidence: S01, S02, S05.

**D3 Temporal and revision status: pass**

R2/180 days is the old retention period; R3/180 days in S03 contradicts the current 60 days. Identical values of 180 days do not imply the same status.

Evidence: S05, S04, S03.

**D4 Source policy: pass**

The 805164c17a4a.registry.invalid allowlist permits primary supports and prohibits consortium/disputed; Annex is within the allowlist but has the wrong subject, which is a separate dimension.

Evidence: S01, S02, S05, S03, S07.

**Findings for this world**

- Retention of a shared-URL page does not establish complete support for three facts; subject, revision, relationship, and value must all be retained.

**Original-text evidence index**

- **S05**: chunk `8d0f8471d0344d4ef7740da7b0f5`, claim `e43b8df5d6238ab4f5b42d3e55ca`, Character span `[1371, 1455)`; Source `https://805164c17a4a.registry.invalid/operative-record`.
  > - Entity Veloria-805164C1; revision R3; archival retention period: 60 calendar days.
- **S02**: chunk `c6ade0fc6a49e574723ec277e5ab`, claim `d38589c2037a9ec0fad3aaa0f0d7`, Character span `[1472, 1551)`; Source `https://805164c17a4a.registry.invalid/operative-record`.
  > - Entity Veloria-805164C1; revision R3; release authorization code: Permit-R70.
- **S01**: chunk `646649cf6c8f9654fbb9c08e269e`, claim `31fb74994e756e3be23f0ab3fd21`, Character span `[1378, 1455)`; Source `https://805164c17a4a.registry.invalid/operative-record`.
  > - Entity Veloria-805164C1; revision R3; file review interval: 3 working days.
- **S04**: chunk `59fba0109c02a6cd346d38b01af0`, claim `789b1e4cb19c7af7bbfcd85b5c22`, Character span `[1366, 1451)`; Source `https://805164c17a4a.registry.invalid/archive`.
  > - Entity Veloria-805164C1; revision R2; archival retention period: 180 calendar days.
- **S03**: chunk `681fd448a3f271379665535fb202`, claim `9645a74697976a6a4e47103d3deb`, Character span `[1373, 1458)`; Source `https://805164c17a4a.consortium.invalid/disputed`.
  > - Entity Veloria-805164C1; revision R3; archival retention period: 180 calendar days.
- **S07**: chunk `4da27e6b4eb4233fde0275846a2d`, claim `301c62a0e1608bfe9783342ab6dc`, Character span `[309, 399)`; Source `https://805164c17a4a.registry.invalid/annex-0`.
  > - Entity Veloria-805164C1-Annex; revision R3; archival retention period: 60 calendar days.

## World 45: 00000588c8c6fbb0d7423c13c49b

Question IDs: `3ab5a10c00acab73d0da88005154`, `d2a734879ffab06145b433bedb07`.

Collection IDs: `e41dbe1f07651bf4e2fe35b24080`, `c476713ba966924f0e1b8ce0f642`.

Entity: Veloria-00000588; Rendering: list; Support structure: single_chunk; Required fact count: 4; Overall judgment: **pass**.

Required facts: review_days = 21 working days; retention_days = 180 calendar days; release_code = Permit-R12; route = Juniper-44.

**D1 Consistency of required facts with the original text: pass**

The R3 question requires 21 working days, 180 calendar days, Permit-R12, and Juniper-44; S02–S05 provide positive examples for the target entity.

Evidence: S02, S03, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four list sentences share one operative-record chunk, with each span specifying the entity and R3; this establishes complete single-chunk support from the text rather than a page label alone.

Evidence: S02, S03, S04, S05.

**D3 Temporal and revision status: pass**

The R2 value of 3 working days is obsolete; S06 still gives 3 days under R3, contradicting the current 21 days. The archive/disputed status distinction is correct.

Evidence: S02, S07, S06.

**D4 Source policy: pass**

There is no source-prefix restriction, so S06 on consortium is source-allowed; unrestricted sources must not be misrepresented as registry-only or operative-record-only.

Evidence: S06, S02.

**Findings for this world**

- The world ID retains its leading zeros as an original string; entity 00000588 must not be confused with Annex.
- Four-field support in one chunk must still be scored individually as four facts.

**Original-text evidence index**

- **S02**: chunk `ab1b9d90ab0b01de051b4777a46f`, claim `14768a1816b8295a0284097b811d`, Character span `[196, 274)`; Source `https://00000588c8c6.registry.invalid/operative-record`.
  > - Entity Veloria-00000588; revision R3; file review interval: 21 working days.
- **S03**: chunk `ab1b9d90ab0b01de051b4777a46f`, claim `8e8195df098962b07d963135b054`, Character span `[276, 361)`; Source `https://00000588c8c6.registry.invalid/operative-record`.
  > - Entity Veloria-00000588; revision R3; archival retention period: 180 calendar days.
- **S04**: chunk `ab1b9d90ab0b01de051b4777a46f`, claim `e0da589aaf70f8093e520ee9ed76`, Character span `[363, 442)`; Source `https://00000588c8c6.registry.invalid/operative-record`.
  > - Entity Veloria-00000588; revision R3; release authorization code: Permit-R12.
- **S05**: chunk `ab1b9d90ab0b01de051b4777a46f`, claim `a8e1da1ada2be6a4289baeafe6fe`, Character span `[444, 510)`; Source `https://00000588c8c6.registry.invalid/operative-record`.
  > - Entity Veloria-00000588; revision R3; service route: Juniper-44.
- **S07**: chunk `c05462e99d40007697968ec6493d`, claim `518e90ca44f92b6df7f0c04c4152`, Character span `[199, 276)`; Source `https://00000588c8c6.registry.invalid/archive`.
  > - Entity Veloria-00000588; revision R2; file review interval: 3 working days.
- **S06**: chunk `6bcae5f4f9c4094fb988bb446790`, claim `868fb843d53cef9602eaa5ece391`, Character span `[199, 276)`; Source `https://00000588c8c6.consortium.invalid/disputed`.
  > - Entity Veloria-00000588; revision R3; file review interval: 3 working days.

## World 46: 3b5b264f59a8257f41238d8b38c4

Question IDs: `8a9044d317c46b355cefa4067ec8`, `7c6ad581505f8347b5f2aa02b883`.

Collection IDs: `78d3482e5bbb09ec7ed3a7d775dc`, `a607b31f7b3b3e20edc2caa7dea1`.

Entity: Veloria-3B5B264F; Rendering: list; Support structure: temporal_conflict; Required fact count: 4; Overall judgment: **pass**.

Required facts: retention_days = 180 calendar days; review_days = 5 working days; release_code = Permit-K33; route = Aster-44.

**D1 Consistency of required facts with the original text: pass**

The four R8 fields are 180 days, 5 working days, Permit-K33, and Aster-44; S11/S15/S13/S12 each agree with the question and current facts.

Evidence: S11, S15, S13, S12.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four list assertions fully bind the target entity and R8; obsolete or contradictory combinations are not valid alternatives even if all four fields occur within one chunk.

Evidence: S11, S12, S13, S15.

**D3 Temporal and revision status: pass**

The R7 combination 90 days/14 days/R84/Cobalt-37 in S01–S04 is obsolete; S05–S08 repeat it under R8 and must be current-revision contradictions.

Evidence: S01, S02, S03, S04, S05, S06, S07, S08.

**D4 Source policy: pass**

The question leaves sources unrestricted, so consortium/disputed is allowed despite its four contradictory assertions; valid registry supports are also allowed. Both judgments agree with the rules.

Evidence: S05, S06, S07, S08, S11.

**Findings for this world**

- All four fields have temporal and conflicting-value comparisons; “four answers are present” does not mean four correct facts are supported.

**Original-text evidence index**

- **S11**: chunk `95184eb9a7751a53d6aab950c47c`, claim `ae21c5c813bd41164f71b08996bf`, Character span `[908, 993)`; Source `https://3b5b264f59a8.registry.invalid/operative-record`.
  > - Entity Veloria-3B5B264F; revision R8; archival retention period: 180 calendar days.
- **S15**: chunk `9ee94600c216a0ed621f4075cc55`, claim `4335f0505b666843e0a3d4b929f9`, Character span `[904, 981)`; Source `https://3b5b264f59a8.registry.invalid/operative-record`.
  > - Entity Veloria-3B5B264F; revision R8; file review interval: 5 working days.
- **S13**: chunk `c2e683fc76b703a782eefe2f1f27`, claim `7d8ad54edaebb8f0e61ad7a9120c`, Character span `[889, 968)`; Source `https://3b5b264f59a8.registry.invalid/operative-record`.
  > - Entity Veloria-3B5B264F; revision R8; release authorization code: Permit-K33.
- **S12**: chunk `a20aef79eb2295a58159e004ebfe`, claim `13e7f529e703cf00c3916e51320c`, Character span `[862, 926)`; Source `https://3b5b264f59a8.registry.invalid/operative-record`.
  > - Entity Veloria-3B5B264F; revision R8; service route: Aster-44.
- **S01**: chunk `5ab247a7167934e85fe89e06b6cf`, claim `47eec8c781d793d69895181bfb38`, Character span `[983, 1067)`; Source `https://3b5b264f59a8.registry.invalid/archive`.
  > - Entity Veloria-3B5B264F; revision R7; archival retention period: 90 calendar days.
- **S02**: chunk `5ab247a7167934e85fe89e06b6cf`, claim `de0b93020dc9fd2828509ca47152`, Character span `[1069, 1147)`; Source `https://3b5b264f59a8.registry.invalid/archive`.
  > - Entity Veloria-3B5B264F; revision R7; file review interval: 14 working days.
- **S03**: chunk `5ab247a7167934e85fe89e06b6cf`, claim `16ca2a0e7b2d9dd3f798b2da2df9`, Character span `[1149, 1228)`; Source `https://3b5b264f59a8.registry.invalid/archive`.
  > - Entity Veloria-3B5B264F; revision R7; release authorization code: Permit-R84.
- **S04**: chunk `5ab247a7167934e85fe89e06b6cf`, claim `3e735ed9f6f99b792ec86738b0fe`, Character span `[1230, 1295)`; Source `https://3b5b264f59a8.registry.invalid/archive`.
  > - Entity Veloria-3B5B264F; revision R7; service route: Cobalt-37.
- **S05**: chunk `bbbb3e3426a149d79f97d61c9602`, claim `2e7ef342aee4c171b4abdd35a6ce`, Character span `[880, 964)`; Source `https://3b5b264f59a8.consortium.invalid/disputed`.
  > - Entity Veloria-3B5B264F; revision R8; archival retention period: 90 calendar days.
- **S06**: chunk `bbbb3e3426a149d79f97d61c9602`, claim `1a6ea778fdebce4bec876369078b`, Character span `[966, 1044)`; Source `https://3b5b264f59a8.consortium.invalid/disputed`.
  > - Entity Veloria-3B5B264F; revision R8; file review interval: 14 working days.
- **S07**: chunk `bbbb3e3426a149d79f97d61c9602`, claim `d18d7ec65b011f296ed836a35564`, Character span `[1046, 1125)`; Source `https://3b5b264f59a8.consortium.invalid/disputed`.
  > - Entity Veloria-3B5B264F; revision R8; release authorization code: Permit-R84.
- **S08**: chunk `bbbb3e3426a149d79f97d61c9602`, claim `06319743813c4f1790beb159c652`, Character span `[1127, 1192)`; Source `https://3b5b264f59a8.consortium.invalid/disputed`.
  > - Entity Veloria-3B5B264F; revision R8; service route: Cobalt-37.

## World 47: a5fa36c530566d533c4771f19520

Question IDs: `033e260dd50399a45f9ebf03cffb`, `dfb54567e4f3f80eccb33b03f380`.

Collection IDs: `67cf2624d5eccff76f20632576f0`, `f67a96a4b592f29bd089b7d2a5fd`.

Entity: Veloria-A5FA36C5; Rendering: prose; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: retention_days = 180 calendar days; release_code = Permit-V11.

**D1 Consistency of required facts with the original text: pass**

The requested R6 retention period and authorization code are 180 calendar days and Permit-V11; S01/S05 directly express both values.

Evidence: S01, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

Both prose sentences fully contain the entity, R6, field, and value, in operative-record and operative-part-1, respectively, providing complementary support across URLs.

Evidence: S01, S05.

**D3 Temporal and revision status: pass**

R5/30 calendar days is the old retention period; S06 gives 30 days under R6, contradicting the current 180 days. The semantic annotation is appropriate.

Evidence: S01, S04, S06.

**D4 Source policy: pass**

There is no source-prefix restriction, so S06 on consortium and the primary registry supports are all allowed; S06's invalidity cannot be attributed to policy prohibition.

Evidence: S01, S05, S06.

**Findings for this world**

- The two Annex sentences concern a different entity; identical values do not make them usable alternative factual support.

**Original-text evidence index**

- **S01**: chunk `4ac66af6312a8b9ff69553175df3`, claim `8f24c2e1310ccf27be27c6a266c9`, Character span `[1941, 2036)`; Source `https://a5fa36c53056.registry.invalid/operative-record`.
  > For entity Veloria-A5FA36C5 in revision R6, the archival retention period is 180 calendar days.
- **S05**: chunk `63b84595ffd55909e15bdb944bf4`, claim `62769ee915e50f3aa57b17d35c93`, Character span `[1940, 2029)`; Source `https://a5fa36c53056.registry.invalid/operative-part-1`.
  > For entity Veloria-A5FA36C5 in revision R6, the release authorization code is Permit-V11.
- **S04**: chunk `e2b12c846f815e514eb32f5a0f58`, claim `a507e675b6bb4c24805397ca0778`, Character span `[1950, 2044)`; Source `https://a5fa36c53056.registry.invalid/archive`.
  > For entity Veloria-A5FA36C5 in revision R5, the archival retention period is 30 calendar days.
- **S06**: chunk `7cfc6ec74ffddbdbc20b570bc102`, claim `c998cc9d386ca7375a0b7c593991`, Character span `[1918, 2012)`; Source `https://a5fa36c53056.consortium.invalid/disputed`.
  > For entity Veloria-A5FA36C5 in revision R6, the archival retention period is 30 calendar days.

## World 48: 3a37b73d1aa428a54d6c284ec518

Question IDs: `b70a5aca598792f324b739ae62ad`, `6264e69aff2ae71fc10fa5ea7314`.

Collection IDs: `640a3c9d9b597aa656d43bc23c3d`, `829d671c227a8bff73934c9528d2`.

Entity: Veloria-3A37B73D; Rendering: prose; Support structure: equivalent_support; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Willow-37; review_days = 5 working days; release_code = Permit-M14.

**D1 Consistency of required facts with the original text: pass**

The R6 question requests Willow-37, 5 working days, and Permit-M14; the target-entity prose sentences S06/S07/S08 provide these individually.

Evidence: S06, S07, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three sentences in the independent-current chunk each fully bind the subject and R6; distributed support and the complete chunk are alternative paths. An identical-value external-domain chunk does not become usable merely through completeness.

Evidence: S06, S07, S08, S02, S03, S04.

**D3 Temporal and revision status: pass**

R5/Cobalt-44 is the old route; R6/Cobalt-44 in S10 conflicts with the current Willow-37. The revision-status distinction is correct.

Evidence: S06, S01, S10.

**D4 Source policy: pass**

Sources are restricted to 3a37b73d1aa4.registry.invalid; the complete consortium chunk S02–S04 has correct current content but still violates the source prefix.

Evidence: S02, S03, S04, S10, S06.

**Findings for this world**

- Complete, correct chunks from external and allowed domains support the same facts but differ in source acceptability.

**Original-text evidence index**

- **S06**: chunk `9924fbce09f9bcb5b422437095b8`, claim `c98525c08623a7a6f2c5c04097fb`, Character span `[393, 468)`; Source `https://3a37b73d1aa4.registry.invalid/independent-current`.
  > For entity Veloria-3A37B73D in revision R6, the service route is Willow-37.
- **S07**: chunk `9924fbce09f9bcb5b422437095b8`, claim `6bbf4ba33e0060741a6f5f91eae5`, Character span `[470, 557)`; Source `https://3a37b73d1aa4.registry.invalid/independent-current`.
  > For entity Veloria-3A37B73D in revision R6, the file review interval is 5 working days.
- **S08**: chunk `9924fbce09f9bcb5b422437095b8`, claim `441623f55bf19ec4d38dff7591bc`, Character span `[559, 648)`; Source `https://3a37b73d1aa4.registry.invalid/independent-current`.
  > For entity Veloria-3A37B73D in revision R6, the release authorization code is Permit-M14.
- **S02**: chunk `56077485b442ae1012fd82592f50`, claim `49e6247e09c2d99465b0d98ccda7`, Character span `[386, 461)`; Source `https://3a37b73d1aa4.consortium.invalid/complete-current`.
  > For entity Veloria-3A37B73D in revision R6, the service route is Willow-37.
- **S03**: chunk `56077485b442ae1012fd82592f50`, claim `d801460be154ca9ce984c92642f9`, Character span `[463, 550)`; Source `https://3a37b73d1aa4.consortium.invalid/complete-current`.
  > For entity Veloria-3A37B73D in revision R6, the file review interval is 5 working days.
- **S04**: chunk `56077485b442ae1012fd82592f50`, claim `d4ce1e83aa564bb943fe934dd47a`, Character span `[552, 641)`; Source `https://3a37b73d1aa4.consortium.invalid/complete-current`.
  > For entity Veloria-3A37B73D in revision R6, the release authorization code is Permit-M14.
- **S01**: chunk `b6adb07ff5d68cddf89bdc3b33df`, claim `6107aef4f950e6f4338da4f25c87`, Character span `[401, 476)`; Source `https://3a37b73d1aa4.registry.invalid/archive`.
  > For entity Veloria-3A37B73D in revision R5, the service route is Cobalt-44.
- **S10**: chunk `9253fd02588b4351f75f6f529224`, claim `fceda6498540cc5344ece3d08d76`, Character span `[389, 464)`; Source `https://3a37b73d1aa4.consortium.invalid/disputed`.
  > For entity Veloria-3A37B73D in revision R6, the service route is Cobalt-44.

## World 49: 1c6479724d60de8fda56fea250d0

Question IDs: `f6e4507f8d9c49c92cf87723efe1`, `f7d28e9cd16853e2a5bdd3c82a49`.

Collection IDs: `dd5d1b363320c5ef29b01f940de2`, `b7c894a14f23f59900cff4b72249`.

Entity: Veloria-1C647972; Rendering: prose; Support structure: position; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Cobalt-71; review_days = 11 working days; retention_days = 30 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R6 route Cobalt-71, review interval of 11 working days, and retention period of 30 calendar days are explicitly supported by S08/S03/S05.

Evidence: S08, S03, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three complete prose spans occur around characters 4577–4650 and all include the subject, R6, and relationship; a very late position does not mean the original fact spans are incomplete.

Evidence: S03, S05, S08.

**D3 Temporal and revision status: pass**

R5/Cobalt-17 is obsolete; S01 specifies R6 but still gives Cobalt-17, contradicting the current Cobalt-71. Reversing the digits does not identify the same route.

Evidence: S08, S02, S01.

**D4 Source policy: pass**

Unrestricted sources permit consortium and registry; S01 is incorrect because of its current value rather than an external-domain policy. Both variant questions have the same rules.

Evidence: S01, S08.

**Findings for this world**

- The complete subject and revision should be retained; Cobalt-71 and Cobalt-17 differ only in digit order but are conflicting values.
- This review of original text does not establish complete actual delivery for the late-position case.

**Original-text evidence index**

- **S08**: chunk `b18b2d4a697552275075efc04354`, claim `a3079cd7e597edae6aba2126e696`, Character span `[4650, 4725)`; Source `https://1c6479724d60.registry.invalid/operative-record`.
  > For entity Veloria-1C647972 in revision R6, the service route is Cobalt-71.
- **S03**: chunk `f41011b25db35c2f1dddbb359a4c`, claim `a2666b25434ccec931ba3f37eebc`, Character span `[4577, 4665)`; Source `https://1c6479724d60.registry.invalid/operative-record`.
  > For entity Veloria-1C647972 in revision R6, the file review interval is 11 working days.
- **S05**: chunk `919e24b92afb3e9f587c4a13ef30`, claim `8cf77baccfb5263b3584cd99421f`, Character span `[4615, 4709)`; Source `https://1c6479724d60.registry.invalid/operative-record`.
  > For entity Veloria-1C647972 in revision R6, the archival retention period is 30 calendar days.
- **S02**: chunk `a8692fa61e45e35e8d951a296638`, claim `4e25c47ded129e1f5e409557cbe5`, Character span `[4598, 4673)`; Source `https://1c6479724d60.registry.invalid/archive`.
  > For entity Veloria-1C647972 in revision R5, the service route is Cobalt-17.
- **S01**: chunk `59f87883ed6733c8ed7ab4374d18`, claim `64b9606ae1e4d31b01e148c6ff68`, Character span `[4704, 4779)`; Source `https://1c6479724d60.consortium.invalid/disputed`.
  > For entity Veloria-1C647972 in revision R6, the service route is Cobalt-17.

## World 50: fb48bf3b55218711963fa24177f0

Question IDs: `26cebe977f967d5f35d38c6a9bda`, `7064e8f2ab08956f5f6910d6c99e`.

Collection IDs: `07561d57709e4c57e797a5c57cea`, `83c44861df37306495949440a2b6`.

Entity: Veloria-FB48BF3B; Rendering: prose; Support structure: same_url_complementary; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Aster-50; release_code = Permit-K67; retention_days = 120 calendar days.

**D1 Consistency of required facts with the original text: pass**

Aster-50, Permit-K67, and 120 calendar days requested by the R9 question are supported by S02/S06/S01, respectively; all three fields and values agree.

Evidence: S02, S06, S01.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each prose assertion restates the subject and R9; primary supports share operative-record but occupy different chunks. Route repetition cannot replace the code and retention period.

Evidence: S01, S02, S06.

**D3 Temporal and revision status: pass**

R8/Juniper-70 is the obsolete route; R9/Juniper-70 in S08 contradicts the current Aster-50. Both negative-example labels are appropriate.

Evidence: S02, S04, S08.

**D4 Source policy: pass**

The fb48bf3b5521.registry.invalid allowlist permits primary supports and archive; S08 on consortium/disputed should have source_allowed=False.

Evidence: S01, S02, S06, S08.

**Findings for this world**

- Same-URL complementary structure is compatible with complete support spans, but the designated page's presence alone cannot establish coverage of three facts.

**Original-text evidence index**

- **S02**: chunk `21599bd4076bc5aa56c7313b022f`, claim `545a4136f8872a6b9251aa9ed1cf`, Character span `[1183, 1257)`; Source `https://fb48bf3b5521.registry.invalid/replica-3`.
  > For entity Veloria-FB48BF3B in revision R9, the service route is Aster-50.
- **S06**: chunk `5f07f351703a3ca0ed8d2a44c09d`, claim `1df631eb185c26043a160f334a20`, Character span `[1141, 1230)`; Source `https://fb48bf3b5521.registry.invalid/operative-record`.
  > For entity Veloria-FB48BF3B in revision R9, the release authorization code is Permit-K67.
- **S01**: chunk `66f841b27064214d0e8a40242a5a`, claim `c7b1b44a3d1c07a6c852cba75fb6`, Character span `[1269, 1364)`; Source `https://fb48bf3b5521.registry.invalid/operative-record`.
  > For entity Veloria-FB48BF3B in revision R9, the archival retention period is 120 calendar days.
- **S04**: chunk `7c6198cabda5476debe0a9a94ed1`, claim `db3e647e5ff48c054e15f316dd99`, Character span `[1196, 1272)`; Source `https://fb48bf3b5521.registry.invalid/archive`.
  > For entity Veloria-FB48BF3B in revision R8, the service route is Juniper-70.
- **S08**: chunk `931a16a529757a769945ec57334b`, claim `a42b08eeb9e8721ea6ee4fcea883`, Character span `[1261, 1337)`; Source `https://fb48bf3b5521.consortium.invalid/disputed`.
  > For entity Veloria-FB48BF3B in revision R9, the service route is Juniper-70.

## World 51: 738fc4bbde90930cb1e5ac5031ee

Question IDs: `1f93cfabdc24c8581d6abab9e412`, `f91e6de0f9dddfbb4d36c2993288`.

Collection IDs: `abe244ed2b8138d949529f124d73`, `d101b5ef5fe59461376345995c6a`.

Entity: Veloria-738FC4BB; Rendering: prose; Support structure: single_chunk; Required fact count: 3; Overall judgment: **pass**.

Required facts: retention_days = 120 calendar days; review_days = 21 working days; release_code = Permit-M15.

**D1 Consistency of required facts with the original text: pass**

The R7 retention period of 120 calendar days, review interval of 21 working days, and Permit-M15 are supported by S06/S07/S08, respectively; all three requested fields have textual evidence.

Evidence: S06, S07, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three sentences in one operative-record chunk each restate the target entity and R7, establishing complete single-chunk support for three facts; identical-value Annex sentences are outside this set.

Evidence: S06, S07, S08.

**D3 Temporal and revision status: pass**

R6/60 calendar days is obsolete; R7/60 days in S04 contradicts the current 120 days. A value's origin in old truth does not make it currently correct.

Evidence: S06, S05, S04.

**D4 Source policy: pass**

There is no source allowlist, so S04 on 738fc4bbde90.consortium.invalid is also source-allowed; source permission does not change its contradictory retention-period value.

Evidence: S04, S06.

**Findings for this world**

- The structure supports three facts within one chunk, but each sentence's subject and revision remain necessary support content.

**Original-text evidence index**

- **S06**: chunk `1adec50fa0c5fc25ff401dc38b35`, claim `0627c8125cd89d9ce048f0f1a03b`, Character span `[288, 383)`; Source `https://738fc4bbde90.registry.invalid/operative-record`.
  > For entity Veloria-738FC4BB in revision R7, the archival retention period is 120 calendar days.
- **S07**: chunk `1adec50fa0c5fc25ff401dc38b35`, claim `7c31fa3c1269af9672da235bbebe`, Character span `[385, 473)`; Source `https://738fc4bbde90.registry.invalid/operative-record`.
  > For entity Veloria-738FC4BB in revision R7, the file review interval is 21 working days.
- **S08**: chunk `1adec50fa0c5fc25ff401dc38b35`, claim `37d8cc799b56bf4e514b7d7fcc94`, Character span `[475, 564)`; Source `https://738fc4bbde90.registry.invalid/operative-record`.
  > For entity Veloria-738FC4BB in revision R7, the release authorization code is Permit-M15.
- **S05**: chunk `d59326c376e5d5c6b0a0e57d2631`, claim `fb490d0ad0b37503d841d68cb5bc`, Character span `[393, 487)`; Source `https://738fc4bbde90.registry.invalid/archive`.
  > For entity Veloria-738FC4BB in revision R6, the archival retention period is 60 calendar days.
- **S04**: chunk `3aa6c686bb428d912672b2338398`, claim `8ed2e34247e7f3c87609fcb234af`, Character span `[288, 382)`; Source `https://738fc4bbde90.consortium.invalid/disputed`.
  > For entity Veloria-738FC4BB in revision R7, the archival retention period is 60 calendar days.

## World 52: e3e6cf4c37189bf7f3570cee10a0

Question IDs: `24d69718de96b8820b05f9852e6a`, `00b107a2ea9ff42c8fedb2d74492`.

Collection IDs: `7f5b3ea6dd54952d91ec5f6f05e4`, `eb9f53859a91b4955da588dae80b`.

Entity: Veloria-E3E6CF4C; Rendering: prose; Support structure: temporal_conflict; Required fact count: 3; Overall judgment: **pass**.

Required facts: release_code = Permit-K72; review_days = 3 working days; retention_days = 60 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R3 question requires Permit-K72, 3 working days, and 60 calendar days; S01/S10/S06 each explicitly give the corresponding value.

Evidence: S01, S10, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three current sentences are complete prose assertions containing the subject, R3, and field; neither three complete old-value sentences nor three complete current contradictions can replace them.

Evidence: S01, S06, S10.

**D3 Temporal and revision status: pass**

The R2 combination R19/11 days/90 days is obsolete; S02–S04 bind that old combination to R3 and should be current-revision contradictions, distinct from the valid K72/3 days/60 days.

Evidence: S02, S03, S04, S07, S08, S09.

**D4 Source policy: pass**

Sources are restricted to e3e6cf4c3718.registry.invalid; positive examples and archive comply, whereas S02–S04 on consortium do not.

Evidence: S01, S06, S10, S02, S03, S04.

**Findings for this world**

- Each of the three fields has temporal and value-based negative examples; current Annex values still concern a different subject.

**Original-text evidence index**

- **S01**: chunk `34d5a92f212b9bf4d286c9faccfc`, claim `e51b657329ffd165e717356d4cd2`, Character span `[520, 609)`; Source `https://e3e6cf4c3718.registry.invalid/replica-4`.
  > For entity Veloria-E3E6CF4C in revision R3, the release authorization code is Permit-K72.
- **S10**: chunk `8fc6499c2e877fe06d1ab5a29909`, claim `86f5ba1b30325bd5f1d670829eaf`, Character span `[595, 682)`; Source `https://e3e6cf4c3718.registry.invalid/operative-record`.
  > For entity Veloria-E3E6CF4C in revision R3, the file review interval is 3 working days.
- **S06**: chunk `a6da54f6a8bbb2a0b873bbf8d5a4`, claim `987e5019a5c0b6ced8f97090db94`, Character span `[498, 592)`; Source `https://e3e6cf4c3718.registry.invalid/operative-record`.
  > For entity Veloria-E3E6CF4C in revision R3, the archival retention period is 60 calendar days.
- **S02**: chunk `e903103775e4d27b63dd308be522`, claim `4fb1dd5eef8bad977ade74ab602a`, Character span `[588, 677)`; Source `https://e3e6cf4c3718.consortium.invalid/disputed`.
  > For entity Veloria-E3E6CF4C in revision R3, the release authorization code is Permit-R19.
- **S03**: chunk `e903103775e4d27b63dd308be522`, claim `55a48a54e35be159d6fefe1d17f0`, Character span `[679, 767)`; Source `https://e3e6cf4c3718.consortium.invalid/disputed`.
  > For entity Veloria-E3E6CF4C in revision R3, the file review interval is 11 working days.
- **S04**: chunk `e903103775e4d27b63dd308be522`, claim `94b4ae0c9f431961d279a334cc90`, Character span `[769, 863)`; Source `https://e3e6cf4c3718.consortium.invalid/disputed`.
  > For entity Veloria-E3E6CF4C in revision R3, the archival retention period is 90 calendar days.
- **S07**: chunk `f31f6c65bb4409b85335201d994c`, claim `b113498cc991591344b332a75121`, Character span `[475, 564)`; Source `https://e3e6cf4c3718.registry.invalid/archive`.
  > For entity Veloria-E3E6CF4C in revision R2, the release authorization code is Permit-R19.
- **S08**: chunk `f31f6c65bb4409b85335201d994c`, claim `391ab852a8caebefac8248448a73`, Character span `[566, 654)`; Source `https://e3e6cf4c3718.registry.invalid/archive`.
  > For entity Veloria-E3E6CF4C in revision R2, the file review interval is 11 working days.
- **S09**: chunk `f31f6c65bb4409b85335201d994c`, claim `e1d42d88b9fcdf1800a939e0f419`, Character span `[656, 750)`; Source `https://e3e6cf4c3718.registry.invalid/archive`.
  > For entity Veloria-E3E6CF4C in revision R2, the archival retention period is 90 calendar days.

## World 53: b3ed6ba208622e9c917319eae357

Question IDs: `6c8bbe79e388020ac7f0a9cdb67a`, `1d71048e8509dc85cdd2e6c987ef`.

Collection IDs: `e471d18d9f6b43b4e69a036e2bb6`, `5b37a6fd17a9f1cda88a158cd2fe`.

Entity: Veloria-B3ED6BA2; Rendering: qa; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: route = Aster-79; retention_days = 120 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R3 route Aster-79 and retention period of 120 calendar days are supported by the complete QA pairs S02 and S03; the requested fields and values agree.

Evidence: S02, S03.

**D2 Complete assertions, complementary support, and alternative support: pass**

Both spans include the subject/R3/field in the question and value in the answer, across two primary URLs; answer lines alone cannot replace these joint spans.

Evidence: S02, S03.

**D3 Temporal and revision status: pass**

R2/Aster-54 is obsolete; S06 answers Aster-54 under R3, contradicting the current Aster-79. Both status labels are supported.

Evidence: S02, S04, S06.

**D4 Source policy: pass**

The b3ed6ba20862.registry.invalid allowlist permits both primary supports and prohibits S06 on consortium/disputed; source rules are identical in both variants.

Evidence: S02, S03, S06.

**Findings for this world**

- Both facts across the two URLs must be supported; identical routes or retention periods in Annex do not complete support for the target entity.

**Original-text evidence index**

- **S02**: chunk `02723a366adc7280ae4de3087365`, claim `168db72e09994a3c7955e18a37b0`, Character span `[1566, 1655)`; Source `https://b3ed6ba20862.registry.invalid/operative-record`.
  > Q: Under revision R3, what is the service route for entity Veloria-B3ED6BA2? A: Aster-79.
- **S03**: chunk `05e6a8d49ede66c5838db798498d`, claim `ac3360965cd009218af1cf198c6c`, Character span `[1575, 1685)`; Source `https://b3ed6ba20862.registry.invalid/operative-part-1`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-B3ED6BA2? A: 120 calendar days.
- **S04**: chunk `dfcc5e1a896248ba301b28b93ccf`, claim `854215a431fe1a3893e0f7bf7bec`, Character span `[1594, 1683)`; Source `https://b3ed6ba20862.registry.invalid/archive`.
  > Q: Under revision R2, what is the service route for entity Veloria-B3ED6BA2? A: Aster-54.
- **S06**: chunk `fbd53aa63ec87c62865bf1ab065f`, claim `9628d4df99fb3b406fca4b8d2c8b`, Character span `[1595, 1684)`; Source `https://b3ed6ba20862.consortium.invalid/disputed`.
  > Q: Under revision R3, what is the service route for entity Veloria-B3ED6BA2? A: Aster-54.

## World 54: 30682341dec9b4b4ea6ad58ffdc6

Question IDs: `be8b4920c1478598f0a416592d1f`, `3f57701dd34f8a184ff4cbdbab47`.

Collection IDs: `d3cd7b5148011c7cc60671056b77`, `04f45ed00ef83c532073e09971df`.

Entity: Veloria-30682341; Rendering: qa; Support structure: equivalent_support; Required fact count: 2; Overall judgment: **pass**.

Required facts: retention_days = 60 calendar days; review_days = 21 working days.

**D1 Consistency of required facts with the original text: pass**

R3 requires 60 calendar days and 21 working days; S01 and S05 express these fields, and both requested facts have correct current QA support.

Evidence: S01, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The question in each complete Q+A pair includes the entity and R3; the external-domain complete-current chunk supplies both facts completely and is a valid alternative under unrestricted sources.

Evidence: S01, S05.

**D3 Temporal and revision status: pass**

R2/180 calendar days is the old retention period; R3/180 days in S02 contradicts the current 60 days and is not equivalent support.

Evidence: S01, S04, S02.

**D4 Source policy: pass**

The question has no allowed-prefix restriction, so the consortium/complete-current source of S05 is allowed; an external domain must not automatically be prohibited.

Evidence: S05, S02.

**Findings for this world**

- The complete external-domain chunk here should be source-allowed, unlike in earlier worlds with restricted policies.
- Equivalent support can span different sources; the designated page is not the only valid source.

**Original-text evidence index**

- **S01**: chunk `6cc956e0ed2d3b68b17c23dd58a2`, claim `366d44e4654034afd6d7ff8ea3b1`, Character span `[858, 967)`; Source `https://30682341dec9.registry.invalid/replica-2`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-30682341? A: 60 calendar days.
- **S05**: chunk `c82187693dd6f7d6698f156b88c4`, claim `6ccfdeed7d1fd8b5c117d8d6c80d`, Character span `[993, 1096)`; Source `https://30682341dec9.consortium.invalid/complete-current`.
  > Q: Under revision R3, what is the file review interval for entity Veloria-30682341? A: 21 working days.
- **S04**: chunk `d79ea3cdb4bf6851423e6d3e0e84`, claim `8ed14bf594ef60c103ed9033fb4f`, Character span `[920, 1030)`; Source `https://30682341dec9.registry.invalid/archive`.
  > Q: Under revision R2, what is the archival retention period for entity Veloria-30682341? A: 180 calendar days.
- **S02**: chunk `f1c692ce340691f9286efc5a0a52`, claim `80c4cbabf5198e22fd0ac7d0eacd`, Character span `[909, 1019)`; Source `https://30682341dec9.consortium.invalid/disputed`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-30682341? A: 180 calendar days.

## World 55: f799a1d7497389521e6d74147f46

Question IDs: `919b10a0809749099b8008609af8`, `2996bd482f91b06101c9ebc25f54`.

Collection IDs: `7c250eb9f65ab02850c1d12cbba9`, `573c8c7adfecf4b75a0de2b00a58`.

Entity: Veloria-F799A1D7; Rendering: qa; Support structure: position; Required fact count: 2; Overall judgment: **pass**.

Required facts: route = Willow-81; release_code = Permit-K32.

**D1 Consistency of required facts with the original text: pass**

The R4 question requires Willow-81 and Permit-K32; the target-entity QA pairs S02/S05 give the current route and code, respectively.

Evidence: S02, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The support spans around characters 3251 and 3434 include Q+A, retaining the subject and R4 despite their late positions; detecting answer values alone does not establish complete bindings.

Evidence: S02, S05.

**D3 Temporal and revision status: pass**

R3/Willow-33 is obsolete; R4/Willow-33 in S03 contradicts the current Willow-81. The conflicting-value status agrees with the text.

Evidence: S02, S04, S03.

**D4 Source policy: pass**

Only f799a1d74973.registry.invalid is allowed; S02/S05 comply, whereas S03 on consortium/disputed does not.

Evidence: S02, S05, S03.

**Findings for this world**

- Late placement affects delivery measurement rather than original factual correctness; 81 or K32 in Annex must not substitute for target-entity support.

**Original-text evidence index**

- **S02**: chunk `f24a769cf8af8037e34caa96e74d`, claim `00153e562aedc22c8088a344293b`, Character span `[3251, 3341)`; Source `https://f799a1d74973.registry.invalid/replica-1`.
  > Q: Under revision R4, what is the service route for entity Veloria-F799A1D7? A: Willow-81.
- **S05**: chunk `127424d12d8232e45c016ec6f7a1`, claim `c7f8170b520f843c2caa1191c8f3`, Character span `[3434, 3538)`; Source `https://f799a1d74973.registry.invalid/operative-record`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-F799A1D7? A: Permit-K32.
- **S04**: chunk `8e06c81a72c5b074f33f47d2666d`, claim `941227d6ac4ffecc399ec81389aa`, Character span `[3270, 3360)`; Source `https://f799a1d74973.registry.invalid/archive`.
  > Q: Under revision R3, what is the service route for entity Veloria-F799A1D7? A: Willow-33.
- **S03**: chunk `73824dc7bdbbb49eba8811ac7060`, claim `bb51689d62d01d7415c52241249a`, Character span `[3367, 3457)`; Source `https://f799a1d74973.consortium.invalid/disputed`.
  > Q: Under revision R4, what is the service route for entity Veloria-F799A1D7? A: Willow-33.

## World 56: b3dd9bd88d26ac26e8350e3a40fe

Question IDs: `b2685c7cc6aa4eddf8255906caac`, `5876feebb42414b437d2eadb3418`.

Collection IDs: `a82f5b663af95480f9f3810557a2`, `30f9ec1207adf03d0aa850576acc`.

Entity: Veloria-B3DD9BD8; Rendering: qa; Support structure: same_url_complementary; Required fact count: 4; Overall judgment: **pass**.

Required facts: route = Willow-18; retention_days = 60 calendar days; release_code = Permit-V30; review_days = 11 working days.

**D1 Consistency of required facts with the original text: pass**

The R5 values Willow-18, 60 calendar days, Permit-V30, and 11 working days are supported in order by S04/S05/S08/S01, matching all four fields.

Evidence: S04, S05, S08, S01.

**D2 Complete assertions, complementary support, and alternative support: pass**

All four QA pairs bind the entity, R5, and field; the original primary supports share a URL but occupy different chunks. Route replicas cannot complete retention, authorization, and review-interval support.

Evidence: S01, S04, S05, S08.

**D3 Temporal and revision status: pass**

R4/Juniper-53 is obsolete on the query date; R5/Juniper-53 in S03 conflicts with Willow-18. Obsolete and current contradictory statuses must not be merged.

Evidence: S04, S07, S03.

**D4 Source policy: pass**

Unrestricted sources permit registry and consortium; S03 is source-allowed but does not support the correct route. There is no additional implicit registry allowlist.

Evidence: S03, S04.

**Findings for this world**

- A single page's presence does not establish complete same-URL complementary support for four facts; the three Annex values do not concern the target entity.

**Original-text evidence index**

- **S04**: chunk `e7b4ad0965979c88ba71feb1af47`, claim `dc0c1e11e93562abfe1295c6dc56`, Character span `[873, 963)`; Source `https://b3dd9bd88d26.registry.invalid/replica-11`.
  > Q: Under revision R5, what is the service route for entity Veloria-B3DD9BD8? A: Willow-18.
- **S05**: chunk `07dd8c81a152748442377defe570`, claim `6bacb19e6271b9273e309fd339ec`, Character span `[829, 938)`; Source `https://b3dd9bd88d26.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the archival retention period for entity Veloria-B3DD9BD8? A: 60 calendar days.
- **S08**: chunk `28f3b4d1dc53aa89ea8cc690077e`, claim `bad0b49f4140f324b7c0f1b83fd6`, Character span `[840, 944)`; Source `https://b3dd9bd88d26.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-B3DD9BD8? A: Permit-V30.
- **S01**: chunk `d61b5743e51880633c70db2a9382`, claim `3913ae5c70ff26c6c128905ee9c4`, Character span `[906, 1009)`; Source `https://b3dd9bd88d26.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the file review interval for entity Veloria-B3DD9BD8? A: 11 working days.
- **S07**: chunk `04b0c0206aaad602386090ebcd7b`, claim `f12e390c3a091770ad3323de5d86`, Character span `[866, 957)`; Source `https://b3dd9bd88d26.registry.invalid/archive`.
  > Q: Under revision R4, what is the service route for entity Veloria-B3DD9BD8? A: Juniper-53.
- **S03**: chunk `ff3fc5088ef0e91ea9354be6c36c`, claim `00898b5c07aa64c07e0de52cafeb`, Character span `[882, 973)`; Source `https://b3dd9bd88d26.consortium.invalid/disputed`.
  > Q: Under revision R5, what is the service route for entity Veloria-B3DD9BD8? A: Juniper-53.

## World 57: 975318bd0ee28083ddc732e51a5c

Question IDs: `92630d1f0e27e6057d6dc8b278d2`, `4d188e9d6f64872054f2314b7738`.

Collection IDs: `3ece4f33504e25d5f2ae8998ef8c`, `e52ba961b861705c2b954e1d1588`.

Entity: Veloria-975318BD; Rendering: qa; Support structure: single_chunk; Required fact count: 3; Overall judgment: **pass**.

Required facts: retention_days = 90 calendar days; route = Cobalt-13; review_days = 11 working days.

**D1 Consistency of required facts with the original text: pass**

The requested R8 values 90 calendar days, Cobalt-13, and 11 working days are supported by the three target-entity QA pairs S06/S07/S08.

Evidence: S06, S07, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

One operative-record chunk contains three complete Q+A pairs, with each question restating the entity and R8; complete single-chunk support thus has an explicit textual basis.

Evidence: S06, S07, S08.

**D3 Temporal and revision status: pass**

R7/180 calendar days is the old value; S04 still answers 180 days under R8, contradicting the current 90 days. The annotation is appropriate.

Evidence: S06, S03, S04.

**D4 Source policy: pass**

975318bd0ee2.registry.invalid is the only allowed prefix; positive examples and archive comply, whereas S04 on consortium/disputed does not.

Evidence: S06, S07, S08, S04.

**Findings for this world**

- One chunk still contains multiple distinct required facts; retaining only the first QA pair does not establish completeness for all three.

**Original-text evidence index**

- **S06**: chunk `bd7a0854e255e23e93d48c07a456`, claim `a9e5699ab4506cbd306a9a3943d3`, Character span `[765, 874)`; Source `https://975318bd0ee2.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the archival retention period for entity Veloria-975318BD? A: 90 calendar days.
- **S07**: chunk `bd7a0854e255e23e93d48c07a456`, claim `87341769177eeea367596842dbef`, Character span `[876, 966)`; Source `https://975318bd0ee2.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the service route for entity Veloria-975318BD? A: Cobalt-13.
- **S08**: chunk `bd7a0854e255e23e93d48c07a456`, claim `63713afae0b8e3cfb7ad3effbef3`, Character span `[968, 1071)`; Source `https://975318bd0ee2.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the file review interval for entity Veloria-975318BD? A: 11 working days.
- **S03**: chunk `f2737da11d5863448145f8f9b96f`, claim `3a66564807b54c09b684cfe8d954`, Character span `[762, 872)`; Source `https://975318bd0ee2.registry.invalid/archive`.
  > Q: Under revision R7, what is the archival retention period for entity Veloria-975318BD? A: 180 calendar days.
- **S04**: chunk `d523ed049c1324578b561af3ec78`, claim `2f4d7213f8b3a9158a28ace7acee`, Character span `[790, 900)`; Source `https://975318bd0ee2.consortium.invalid/disputed`.
  > Q: Under revision R8, what is the archival retention period for entity Veloria-975318BD? A: 180 calendar days.

## World 58: ffe9e2f1acff4bfa727e29dc173f

Question IDs: `ba0d21856cf34a4a82369f659f12`, `c54a5254e7b55b718a77ba4c72a9`.

Collection IDs: `9776be761c4374c2715bdf7aaf37`, `b0ca864468c2a46dbb630675291f`.

Entity: Veloria-FFE9E2F1; Rendering: qa; Support structure: temporal_conflict; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Juniper-53; release_code = Permit-K49; retention_days = 30 calendar days.

**D1 Consistency of required facts with the original text: pass**

R5 requires Juniper-53, Permit-K49, and 30 calendar days; S01/S09/S08 provide the three correct QA pairs, respectively.

Evidence: S01, S09, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

All three Q+A pairs bind the entity, revision, and field; a complete negative-example chunk with three answers still cannot form a valid support set.

Evidence: S01, S08, S09.

**D3 Temporal and revision status: pass**

The R4 combination Juniper-88/K10/120 days is obsolete; S10–S12 repeat it under R5, contradicting the current 53/K49/30 days.

Evidence: S03, S04, S05, S10, S11, S12.

**D4 Source policy: pass**

There is no allowed-prefix restriction, so the consortium sources of S10–S12 are all allowed; their errors concern current values rather than source policy.

Evidence: S10, S11, S12, S01.

**Findings for this world**

- Similar route and code names still denote conflicting field values; revision labels cannot replace value checks.

**Original-text evidence index**

- **S01**: chunk `e0f5c07284e9f92eda71ed582101`, claim `fd9b4f411102a7508caf499e9673`, Character span `[1055, 1146)`; Source `https://ffe9e2f1acff.registry.invalid/replica-2`.
  > Q: Under revision R5, what is the service route for entity Veloria-FFE9E2F1? A: Juniper-53.
- **S09**: chunk `fabc304e6806e47ddfc5470da6d4`, claim `ccbf2e80a71ec6f68b942f889c5d`, Character span `[1075, 1179)`; Source `https://ffe9e2f1acff.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-FFE9E2F1? A: Permit-K49.
- **S08**: chunk `c2158fd8d418cdc815367062703c`, claim `ad8a3d6b803a0076bf0220b59b59`, Character span `[1085, 1194)`; Source `https://ffe9e2f1acff.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the archival retention period for entity Veloria-FFE9E2F1? A: 30 calendar days.
- **S03**: chunk `bc361bfe34b83341bda7b2c2b880`, claim `14ecc81bd922e7698cc75bd42c13`, Character span `[989, 1080)`; Source `https://ffe9e2f1acff.registry.invalid/archive`.
  > Q: Under revision R4, what is the service route for entity Veloria-FFE9E2F1? A: Juniper-88.
- **S04**: chunk `bc361bfe34b83341bda7b2c2b880`, claim `fdb32d674a1a41f29112e9e08a8f`, Character span `[1082, 1186)`; Source `https://ffe9e2f1acff.registry.invalid/archive`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-FFE9E2F1? A: Permit-K10.
- **S05**: chunk `bc361bfe34b83341bda7b2c2b880`, claim `a221cad47a73bff8a4a206a1d180`, Character span `[1188, 1298)`; Source `https://ffe9e2f1acff.registry.invalid/archive`.
  > Q: Under revision R4, what is the archival retention period for entity Veloria-FFE9E2F1? A: 120 calendar days.
- **S10**: chunk `e248cbffccc814d1af53b3bb4ec2`, claim `dec5610275b6f3de9eced2d74b0b`, Character span `[1088, 1179)`; Source `https://ffe9e2f1acff.consortium.invalid/disputed`.
  > Q: Under revision R5, what is the service route for entity Veloria-FFE9E2F1? A: Juniper-88.
- **S11**: chunk `e248cbffccc814d1af53b3bb4ec2`, claim `d9ce8a4365bc07e0284002ea751a`, Character span `[1181, 1285)`; Source `https://ffe9e2f1acff.consortium.invalid/disputed`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-FFE9E2F1? A: Permit-K10.
- **S12**: chunk `e248cbffccc814d1af53b3bb4ec2`, claim `de4ed2363d522b9c7d828841d6dd`, Character span `[1287, 1397)`; Source `https://ffe9e2f1acff.consortium.invalid/disputed`.
  > Q: Under revision R5, what is the archival retention period for entity Veloria-FFE9E2F1? A: 120 calendar days.

## World 59: 16fb086fedbe1e4ea86a1b372dd4

Question IDs: `04b972fffc6093db9d649cdefabb`, `3d62aa03de225c5961da6dad8762`.

Collection IDs: `500fb0a2ab9674dbf26723fb4c3f`, `8800e0e46497bdb57eb461505acc`.

Entity: Veloria-16FB086F; Rendering: list; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: release_code = Permit-V67; route = Willow-53.

**D1 Consistency of required facts with the original text: pass**

The R9 authorization code Permit-V67 and route Willow-53 are expressed in the list assertions S03 and S01, respectively; both requested fields have support.

Evidence: S03, S01.

**D2 Complete assertions, complementary support, and alternative support: pass**

Both list spans fully include Veloria-16FB086F, R9, relationship, and value; code and route supports are distributed across two URL types and must be combined.

Evidence: S01, S03.

**D3 Temporal and revision status: pass**

R8/Permit-M51 is obsolete; R9/M51 in S06 contradicts the current V67. The obsolete and contradictory annotations agree with revisions and values.

Evidence: S03, S02, S06.

**D4 Source policy: pass**

The 16fb086fedbe.registry.invalid allowlist permits positive examples and prohibits S06 on consortium/disputed; both variants preserve identical rules.

Evidence: S01, S03, S06.

**Findings for this world**

- Code replicas do not provide the route; identical-value Annex assertions cannot complete support for the target subject either.

**Original-text evidence index**

- **S03**: chunk `b0cb0f14e6ca1df80bf416f7a5b2`, claim `4995082a417692c2a231d664cc25`, Character span `[905, 984)`; Source `https://16fb086fedbe.registry.invalid/replica-3`.
  > - Entity Veloria-16FB086F; revision R9; release authorization code: Permit-V67.
- **S01**: chunk `00c8315f37d5ce2207249b903d08`, claim `371c17700396992bfa6c348b58d2`, Character span `[873, 938)`; Source `https://16fb086fedbe.registry.invalid/operative-part-1`.
  > - Entity Veloria-16FB086F; revision R9; service route: Willow-53.
- **S02**: chunk `99f809e9e7dc54559eb6145d6160`, claim `1386b81718e92478885c3e7837b5`, Character span `[969, 1048)`; Source `https://16fb086fedbe.registry.invalid/archive`.
  > - Entity Veloria-16FB086F; revision R8; release authorization code: Permit-M51.
- **S06**: chunk `13410a26803d2d27b0d5996674da`, claim `f81ea64f31d906c28b1edebcd49e`, Character span `[913, 992)`; Source `https://16fb086fedbe.consortium.invalid/disputed`.
  > - Entity Veloria-16FB086F; revision R9; release authorization code: Permit-M51.

## World 60: 45c1f70280fd73897112cf240472

Question IDs: `a16f902b658aec9842be3f60603c`, `4559d0d4a3f7f343f86139fa742a`.

Collection IDs: `5f002b98865ed188fe5ad9906674`, `65b00b73189ec4fc999c0bef9a79`.

Entity: Veloria-45C1F702; Rendering: list; Support structure: equivalent_support; Required fact count: 2; Overall judgment: **pass**.

Required facts: review_days = 5 working days; route = Cobalt-19.

**D1 Consistency of required facts with the original text: pass**

R3 requires 5 working days and Cobalt-19; S04/S05 supply complete target-entity list assertions matching both requested fields.

Evidence: S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

Both assertions in the complete-current chunk include the subject/R3/relationship/value and can replace the distributed primary supports; either complete set suffices.

Evidence: S04, S05.

**D3 Temporal and revision status: pass**

R2/14 working days is obsolete; R3/14 days in S02 contradicts the current 5 days. A historical value is not a current equivalent expression.

Evidence: S04, S06, S02.

**D4 Source policy: pass**

Unrestricted sources allow the correct complete chunk S04/S05 on 45c1f70280fd.consortium.invalid to count as allowed support; S02 on the same domain remains excluded because of its contradictory content.

Evidence: S04, S05, S02.

**Findings for this world**

- The same consortium host contains both a complete correct chunk and a current contradictory chunk; source identity cannot replace semantic judgment.
- The 5 days and Cobalt-19 in Annex concern a different subject.

**Original-text evidence index**

- **S04**: chunk `4f315baa4b0462c65f9f1f677b34`, claim `ee951c9b2b4fc13d359f9def0a2a`, Character span `[2154, 2231)`; Source `https://45c1f70280fd.consortium.invalid/complete-current`.
  > - Entity Veloria-45C1F702; revision R3; file review interval: 5 working days.
- **S05**: chunk `4f315baa4b0462c65f9f1f677b34`, claim `ec6cca82b7a83d62d08906cda1b9`, Character span `[2233, 2298)`; Source `https://45c1f70280fd.consortium.invalid/complete-current`.
  > - Entity Veloria-45C1F702; revision R3; service route: Cobalt-19.
- **S06**: chunk `0b4de6b38be1492316c28750992c`, claim `f69743afde43d40be3a9af988389`, Character span `[2210, 2288)`; Source `https://45c1f70280fd.registry.invalid/archive`.
  > - Entity Veloria-45C1F702; revision R2; file review interval: 14 working days.
- **S02**: chunk `7589e0902a822e1d3381e0a75c8e`, claim `d8613ac61d1a2aac4c68f0cb062b`, Character span `[2138, 2216)`; Source `https://45c1f70280fd.consortium.invalid/disputed`.
  > - Entity Veloria-45C1F702; revision R3; file review interval: 14 working days.
