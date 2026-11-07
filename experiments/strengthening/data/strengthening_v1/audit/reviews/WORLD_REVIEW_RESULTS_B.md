# Dimension-level review results for 60 worlds: B


This review covers 60 worlds, 120 paired questions, and 183 required facts. All 60 overall world judgments and all 240 dimension-level judgments are `pass` (no annotation issues requiring correction were identified).

## World 01: 9ed5c47057168100a21bdc8c7cf7

Question IDs: `7372f8da9bfcc833658a55c809c5`, `0c51c0b4918f467ffb8710fb18fd`.

Collection IDs: `83a3a46112fe1203e5c524c974e9`, `9b365ba139e8eef59a60c0a91ca9`.

Entity: Veloria-9ED5C470; Rendering: list; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: release_code = Permit-R21; review_days = 7 working days.

**D1 Consistency of required facts with the original text: pass**

The question requires R3 release_code and review_days; Permit-R21 in S01 and 7 working days in S04 match individually. Identical values for the Annex subject do not answer the question.

Evidence: S01, S03, S04, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The two fields are complementary in A39/A10 and B39/B10, respectively. S01 and S04 both include the subject, R3, and complete value; retaining only the authorization code does not provide complete support.

Evidence: S01, S04.

**D3 Temporal and revision status: pass**

2035-06-01 falls within R3's validity period. Permit-R66 under R2 is obsolete; S05 presents Permit-R66 under R3 and is a current contradiction rather than an old-revision assertion.

Evidence: S01, S02, S05.

**D4 Source policy: pass**

The question restricts sources to 9ed5c4705716.registry.invalid; S05 is disallowed because it comes from consortium.invalid. Annex on an allowed host must still be excluded for its mismatched subject.

Evidence: S03, S05.

**Findings for this world**

- The 12 replicas repeat the authorization code and cannot supply the other field; source compliance and semantic relevance are separate conditions.

**Original-text evidence index**

- **S01**: chunk `68e6f65479806d015781f377ba65`, claim `ab1b68a6338d0ff1b62573453bad`, Character span `[474, 553)`; Source `https://9ed5c4705716.registry.invalid/replica-2`.
  > - Entity Veloria-9ED5C470; revision R3; release authorization code: Permit-R21.
- **S03**: chunk `42f1ae662884a506673694a3d6ab`, claim `edeebdd10af30c34cb25e5a08a98`, Character span `[109, 194)`; Source `https://9ed5c4705716.registry.invalid/annex-0`.
  > - Entity Veloria-9ED5C470-Annex; revision R3; release authorization code: Permit-R21.
- **S04**: chunk `cfe34e7b87c7fb197e8cd6ee1695`, claim `d6be94398b0eb51bd7f3ba5fbda4`, Character span `[508, 585)`; Source `https://9ed5c4705716.registry.invalid/operative-part-1`.
  > - Entity Veloria-9ED5C470; revision R3; file review interval: 7 working days.
- **S06**: chunk `ccb225751f978d2c96e8b8386d8d`, claim `21d88a5d72db0a4fed550754142d`, Character span `[202, 285)`; Source `https://9ed5c4705716.registry.invalid/annex-1`.
  > - Entity Veloria-9ED5C470-Annex; revision R3; file review interval: 7 working days.
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

The question lists four fields; Permit-K32, Juniper-76, 21 working days, and 60 calendar days are supported by S04, S01, S06, and S03, respectively.

Evidence: S01, S03, S04, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The distributed chunks A39/A03/A47/A17 and complete independent chunk A45 are alternative support paths, not two sets required simultaneously; each marked sentence binds the subject and R3.

Evidence: S01, S03, S04, S06.

**D3 Temporal and revision status: pass**

S08 contains the old R2 code Permit-M34, whereas S07 asserts that same old value under R3. Distinguishing obsolete from contradictory is correct.

Evidence: S04, S07, S08.

**D4 Source policy: pass**

allowed_url_prefixes is empty, so S07 on consortium is also admissible, but its Permit-M34 still conflicts with the R3 fact; the host alone cannot justify prohibition.

Evidence: S07.

**Findings for this world**

- An unrestricted source policy does not remove factual contradictions; complete independent support is an OR alternative.

**Original-text evidence index**

- **S01**: chunk `af0758625c1a88494c5d37147e0f`, claim `7c60a7d0c719d2d933c41e0f378a`, Character span `[1847, 1913)`; Source `https://decda79e6f4b.registry.invalid/operative-part-1`.
  > - Entity Veloria-DECDA79E; revision R3; service route: Juniper-76.
- **S03**: chunk `a5a3c6a137a4a7e897851855d722`, claim `cf858feaf23ae0922a5b742a7536`, Character span `[1818, 1902)`; Source `https://decda79e6f4b.registry.invalid/operative-part-3`.
  > - Entity Veloria-DECDA79E; revision R3; archival retention period: 60 calendar days.
- **S04**: chunk `5ee2b697efa208f022e21f6f784f`, claim `cbf4c9762c675479b55d63fab664`, Character span `[1864, 1943)`; Source `https://decda79e6f4b.registry.invalid/operative-record`.
  > - Entity Veloria-DECDA79E; revision R3; release authorization code: Permit-K32.
- **S06**: chunk `811186a1dc7593ff0a17ab7eea70`, claim `f9fe70b0aa7f0398d6eb868694c0`, Character span `[2021, 2099)`; Source `https://decda79e6f4b.registry.invalid/independent-current`.
  > - Entity Veloria-DECDA79E; revision R3; file review interval: 21 working days.
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

The R5 route Aster-50, retention period of 180 calendar days, and review interval of 3 working days agree with S01/S03/S05; Annex sentences such as S02 concern a different entity.

Evidence: S01, S03, S05, S02.

**D2 Complete assertions, complementary support, and alternative support: pass**

A07/A30/A52 jointly provide the required support. S05 occupies 3244:3321; earlier values cannot replace complete semantics, and the marked sentence itself is complete.

Evidence: S01, S03, S05.

**D3 Temporal and revision status: pass**

Aster-83 under R4 belongs to the old revision; Aster-83 still presented under R5 is a current contradiction. R5 applies as of 2035-06-01.

Evidence: S06, S08, S01.

**D4 Source policy: pass**

This question has no host restriction, so registry and consortium can both be sources; S08 should be excluded for contradictory content rather than URL permission.

Evidence: S06, S08.

**Findings for this world**

- Support occurs late in a long text; complete original-text support does not establish visibility within the scoring prefix.

**Original-text evidence index**

- **S01**: chunk `5cc7fbf72e252a6941c8329daa08`, claim `15a2aee067c2959829dcf6324c30`, Character span `[3184, 3248)`; Source `https://5d003b94793c.registry.invalid/replica-7`.
  > - Entity Veloria-5D003B94; revision R5; service route: Aster-50.
- **S03**: chunk `829e9850d8606228da490b275303`, claim `942922f2f08544d621070a17034e`, Character span `[3184, 3269)`; Source `https://5d003b94793c.registry.invalid/operative-record`.
  > - Entity Veloria-5D003B94; revision R5; archival retention period: 180 calendar days.
- **S05**: chunk `7d448d29da933cf3097c2d032f78`, claim `488e321bdaee31fb56d78839c028`, Character span `[3244, 3321)`; Source `https://5d003b94793c.registry.invalid/operative-record`.
  > - Entity Veloria-5D003B94; revision R5; file review interval: 3 working days.
- **S02**: chunk `3cb75b2960ad2db23b9ab999301b`, claim `ad114ca107631ed7a8ab14f3b1a7`, Character span `[614, 697)`; Source `https://5d003b94793c.registry.invalid/annex-2`.
  > - Entity Veloria-5D003B94-Annex; revision R5; file review interval: 3 working days.
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

The four requested values are Permit-R19, Cobalt-56, 120 calendar days, and 14 working days; S01/S05/S06/S04 satisfy them without treating identical Annex values as target-entity facts.

Evidence: S01, S04, S05, S06, S03.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four same-URL chunks A02/A46/A47/A41 must be combined. Each complete sentence retains the subject, R6, and value; code replicas cannot replace the remaining three fields.

Evidence: S01, S04, S05, S06.

**D3 Temporal and revision status: pass**

R6 in June 2035 supersedes R5, whose validity ends on 2035-01-01; the distinct labels for the old Permit-V14 in S02 and current incorrect Permit-V14 in S08 are appropriate.

Evidence: S02, S08.

**D4 Source policy: pass**

Only dc7967fc8538.registry.invalid is allowed; S08 on consortium is noncompliant. Annex remains on an allowed host but has irrelevant content.

Evidence: S03, S08.

**Findings for this world**

- Same-source chunks provide complementary support; repeated occurrences of one authorization code do not cover four fields.

**Original-text evidence index**

- **S01**: chunk `0a90fc0387e9e6dcaa40449c5b8e`, claim `21216d8dd6c7242f9bd6d35277ff`, Character span `[497, 576)`; Source `https://dc7967fc8538.registry.invalid/operative-record`.
  > - Entity Veloria-DC7967FC; revision R6; release authorization code: Permit-R19.
- **S04**: chunk `ebd96e153849307361c61e9166c5`, claim `66e5feff2601c1b3e9acdc9cbfc2`, Character span `[477, 555)`; Source `https://dc7967fc8538.registry.invalid/operative-record`.
  > - Entity Veloria-DC7967FC; revision R6; file review interval: 14 working days.
- **S05**: chunk `3560427dc5582121950f71a7084a`, claim `c0a2528f7dee6292df12567a716c`, Character span `[478, 543)`; Source `https://dc7967fc8538.registry.invalid/operative-record`.
  > - Entity Veloria-DC7967FC; revision R6; service route: Cobalt-56.
- **S06**: chunk `d8fe53a0a6dee2ac9a71451e4991`, claim `22f912378b5e5c961a5cc1f1d20d`, Character span `[500, 585)`; Source `https://dc7967fc8538.registry.invalid/operative-record`.
  > - Entity Veloria-DC7967FC; revision R6; archival retention period: 120 calendar days.
- **S03**: chunk `8fd478db8986feed53acf0a577a9`, claim `71a38d44c7568a445b10e00e6500`, Character span `[701, 786)`; Source `https://dc7967fc8538.registry.invalid/annex-0`.
  > - Entity Veloria-DC7967FC-Annex; revision R6; release authorization code: Permit-R19.
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

R8 requests the retention period and review interval; S01=60 calendar days and S02=3 working days satisfy the question. Identical Annex values must not be included.

Evidence: S01, S02, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

S01/S02 occur in the same complete chunk A47, and replica chunks also carry both sentences; each complete sentence permits checks of subject, revision, predicate, and value.

Evidence: S01, S02.

**D3 Temporal and revision status: pass**

The old R7 revision gives 180 calendar days, whereas R8 requires 60; the old assertion in S03 and current contradiction in S06 should be handled separately.

Evidence: S01, S03, S06.

**D4 Source policy: pass**

Sources are restricted to e19e0a9d0cbf.registry.invalid, excluding consortium.invalid in S06; the replicas containing S01/S02 remain on an allowed host after regrouping.

Evidence: S01, S02, S06.

**Findings for this world**

- The single chunk already supports both fields; the old value 180 must not be mistaken for the current retention period.

**Original-text evidence index**

- **S01**: chunk `7863bd021867f20076ef2fb0ad79`, claim `086e606b35f4f092da6e13c9435f`, Character span `[888, 972)`; Source `https://e19e0a9d0cbf.registry.invalid/replica-10`.
  > - Entity Veloria-E19E0A9D; revision R8; archival retention period: 60 calendar days.
- **S02**: chunk `7863bd021867f20076ef2fb0ad79`, claim `978434e0b2a28e9b4340f99f6c1b`, Character span `[974, 1051)`; Source `https://e19e0a9d0cbf.registry.invalid/replica-10`.
  > - Entity Veloria-E19E0A9D; revision R8; file review interval: 3 working days.
- **S04**: chunk `26fcb547b5431f038f4629aab7e6`, claim `bbf521650ffddeb3fda0496a8a48`, Character span `[510, 600)`; Source `https://e19e0a9d0cbf.registry.invalid/annex-2`.
  > - Entity Veloria-E19E0A9D-Annex; revision R8; archival retention period: 60 calendar days.
- **S05**: chunk `c589a4a06c83f3ffedfcdf763445`, claim `814e35a4d0cf0f6f3537040ee724`, Character span `[817, 900)`; Source `https://e19e0a9d0cbf.registry.invalid/annex-1`.
  > - Entity Veloria-E19E0A9D-Annex; revision R8; file review interval: 3 working days.
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

Cobalt-41, Permit-M61, and 180 calendar days in S05/S08/S12 cover the three R6 fields; none of the three Annex assertions matches the target entity.

Evidence: S05, S08, S12, S01, S06, S07.

**D2 Complete assertions, complementary support, and alternative support: pass**

A62/A27/A78 supply three complete predicates, with the R6 subject and values intact; one currently contradictory document cannot replace their joint support.

Evidence: S05, S08, S12.

**D3 Temporal and revision status: pass**

S09–S11 explicitly specify R5 and the old values Permit-R40/Aster-63/60 days; S02–S04 bind those values to R6, making all three contradictory.

Evidence: S02, S03, S04, S09, S10, S11.

**D4 Source policy: pass**

The unrestricted policy permits the disputed host; the problem with S02–S04 is their contradictory content. The question imposes no additional prohibition on consortium.

Evidence: S02, S03, S04.

**Findings for this world**

- Current contradictions affect all three fields, so checking only the first authorization code is insufficient; obsolete text and current incorrect values must be counted separately.

**Original-text evidence index**

- **S05**: chunk `b0aaa1b6a277151f9bf1ec1be611`, claim `e64d836c22b1c424ad372fc4fec8`, Character span `[1160, 1225)`; Source `https://dd0a8cf59b42.registry.invalid/operative-record`.
  > - Entity Veloria-DD0A8CF5; revision R6; service route: Cobalt-41.
- **S08**: chunk `732d2076906e7d6cf00cf7ef68e2`, claim `1840b4e80f4603a138398da8048e`, Character span `[1152, 1231)`; Source `https://dd0a8cf59b42.registry.invalid/operative-record`.
  > - Entity Veloria-DD0A8CF5; revision R6; release authorization code: Permit-M61.
- **S12**: chunk `5f5100bf310c58f1d316dd92006a`, claim `7cadd4cc321e00487ead9bf9aeae`, Character span `[1171, 1256)`; Source `https://dd0a8cf59b42.registry.invalid/operative-record`.
  > - Entity Veloria-DD0A8CF5; revision R6; archival retention period: 180 calendar days.
- **S01**: chunk `a604f4dc0554b00d344d594195a4`, claim `9df9ddb310c27b4f155718f68f27`, Character span `[577, 648)`; Source `https://dd0a8cf59b42.registry.invalid/annex-1`.
  > - Entity Veloria-DD0A8CF5-Annex; revision R6; service route: Cobalt-41.
- **S06**: chunk `afeb22364272a4c1df5c80bdd0d6`, claim `e5ce60821ca6052fece26682841f`, Character span `[689, 774)`; Source `https://dd0a8cf59b42.registry.invalid/annex-0`.
  > - Entity Veloria-DD0A8CF5-Annex; revision R6; release authorization code: Permit-M61.
- **S07**: chunk `2ac4654e5a248c1be5785ed6b2d8`, claim `e403834b433e5773e032147293c8`, Character span `[403, 494)`; Source `https://dd0a8cf59b42.registry.invalid/annex-2`.
  > - Entity Veloria-DD0A8CF5-Annex; revision R6; archival retention period: 180 calendar days.
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

The two required facts are the R5 authorization code Permit-R64 and 5 working days; S01/S06 comply, whereas the Annex suffix in S02/S05 changes the subject.

Evidence: S01, S06, S02, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The cross-URL chunks A43/A80 must both be retained. S01 and S06 are complete narrative sentences; repeating the authorization code does not supply the review interval.

Evidence: S01, S06.

**D3 Temporal and revision status: pass**

Permit-R85 under R4 is obsolete; S04 asserting Permit-R85 under R5 is a current contradiction and must not be mixed with the valid R5 Permit-R64.

Evidence: S01, S03, S04.

**D4 Source policy: pass**

The question has no allowed-prefix restriction; even though S04 comes from a different publishing host, its support must be rejected on factual-contradiction grounds.

Evidence: S04.

**Findings for this world**

- This question combines unrestricted sources with cross-source complementary support; page retention does not guarantee retention of both assertions.

**Original-text evidence index**

- **S01**: chunk `03872f31fac3b53ad38618058fd1`, claim `1e0b6468f8304fe71465fc6e593f`, Character span `[1433, 1522)`; Source `https://cbca62047199.registry.invalid/replica-7`.
  > For entity Veloria-CBCA6204 in revision R5, the release authorization code is Permit-R64.
- **S06**: chunk `4c888668350381698560f2761538`, claim `54158188eb13b8b1a36f5b178262`, Character span `[1369, 1456)`; Source `https://cbca62047199.registry.invalid/operative-part-1`.
  > For entity Veloria-CBCA6204 in revision R5, the file review interval is 5 working days.
- **S02**: chunk `5dfb63e7c8b7c4818a80f620fac5`, claim `79d7ec4becea237c3aac846558b5`, Character span `[783, 878)`; Source `https://cbca62047199.registry.invalid/annex-0`.
  > For entity Veloria-CBCA6204-Annex in revision R5, the release authorization code is Permit-R64.
- **S05**: chunk `f893c65f9af7d8d67b50d18a226f`, claim `49e4270ebf21f6e4fe1f2093997c`, Character span `[495, 588)`; Source `https://cbca62047199.registry.invalid/annex-1`.
  > For entity Veloria-CBCA6204-Annex in revision R5, the file review interval is 5 working days.
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

The four R5 values Cobalt-67, 5 working days, 90 calendar days, and Permit-R84 in S06/S03/S01/S04 match the question; identical Annex values are invalid for this subject.

Evidence: S01, S03, S04, S06, S02, S05, S13.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four-chunk set and complete A77 chunk each supply all four fields. S08–S11 also have complete correct content but require separate source-policy checks, rather than relabeling them as contradictory.

Evidence: S01, S03, S04, S06, S08, S09, S10, S11.

**D3 Temporal and revision status: pass**

R5 applies as of 2035-06-01: R4/Cobalt-78 in S07 is obsolete, whereas Cobalt-78 under R5 in S12 is currently incorrect.

Evidence: S06, S07, S12.

**D4 Source policy: pass**

Only registry.invalid is allowed; the complete correct consortium support S08–S11 remains noncompliant. Semantic validity and source_allowed=False can hold simultaneously.

Evidence: S08, S09, S10, S11, S12.

**Findings for this world**

- A key distinction: correct complete text from a disallowed source can remain semantically valid but cannot receive admissible-support credit.

**Original-text evidence index**

- **S01**: chunk `6cf9cab91e4e4f8f2901d62d853d`, claim `03946032854ec8f9225faf240e2e`, Character span `[686, 780)`; Source `https://0725e021b81b.registry.invalid/operative-part-2`.
  > For entity Veloria-0725E021 in revision R5, the archival retention period is 90 calendar days.
- **S03**: chunk `b83127afa42713160c72a9da9869`, claim `5a5273d26fd5d77107ecbbd19d3e`, Character span `[692, 779)`; Source `https://0725e021b81b.registry.invalid/operative-part-1`.
  > For entity Veloria-0725E021 in revision R5, the file review interval is 5 working days.
- **S04**: chunk `2f9d051588ff90fdbd290e2b241f`, claim `8733cc7055f40bc0842b76b3c5ac`, Character span `[663, 752)`; Source `https://0725e021b81b.registry.invalid/operative-part-3`.
  > For entity Veloria-0725E021 in revision R5, the release authorization code is Permit-R84.
- **S06**: chunk `8b95a7988a9f6ddde43139cf7459`, claim `0092b83f7079252070c347229cca`, Character span `[674, 749)`; Source `https://0725e021b81b.registry.invalid/operative-record`.
  > For entity Veloria-0725E021 in revision R5, the service route is Cobalt-67.
- **S02**: chunk `f6cdd861a3679474a61ec9435321`, claim `77d06cb4a03547f8429837e62150`, Character span `[202, 302)`; Source `https://0725e021b81b.registry.invalid/annex-2`.
  > For entity Veloria-0725E021-Annex in revision R5, the archival retention period is 90 calendar days.
- **S05**: chunk `91861ff883ad869c8f1415c2fa46`, claim `00a86b7d4d2add49f4ca499d8547`, Character span `[296, 389)`; Source `https://0725e021b81b.registry.invalid/annex-1`.
  > For entity Veloria-0725E021-Annex in revision R5, the file review interval is 5 working days.
- **S13**: chunk `a53b5e8ff4807c4ea746159ce247`, claim `09f5d3639be43da44807e7529d9a`, Character span `[593, 674)`; Source `https://0725e021b81b.registry.invalid/annex-0`.
  > For entity Veloria-0725E021-Annex in revision R5, the service route is Cobalt-67.
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

The R5 question requires 11 working days, Permit-R31, and 90 calendar days, covered individually by S01/S06/S05; identical Annex fields still do not answer for the target entity.

Evidence: S01, S05, S06, S02, S03, S07.

**D2 Complete assertions, complementary support, and alternative support: pass**

A31/A55/A49 jointly cover three facts; their late sentences fully include the entity and R5, whereas early background cannot serve as assertion support.

Evidence: S01, S05, S06.

**D3 Temporal and revision status: pass**

The value 21 working days belongs to R4 in S04 and is obsolete; in S08 it belongs to R5 and contradicts the current 11 days. The labels agree with the temporal requirements.

Evidence: S01, S04, S08.

**D4 Source policy: pass**

Unrestricted sources mean the consortium host of S08 is not prohibited; its failure to support the question comes from the mismatch between 21 and 11.

Evidence: S08.

**Findings for this world**

- The 12 replicas increase repetition of the review-interval fact, not necessarily support for the authorization code and retention period.

**Original-text evidence index**

- **S01**: chunk `6d6b54e0bd232a2d483efd3209e3`, claim `ac9bcbaa9daaae76dd728cc5461f`, Character span `[1133, 1221)`; Source `https://ee8731d6c6b1.registry.invalid/replica-4`.
  > For entity Veloria-EE8731D6 in revision R5, the file review interval is 11 working days.
- **S05**: chunk `74e689f7f19c965fb8c73ffc7e96`, claim `7897baa589ace6a512e1ad885e5c`, Character span `[1160, 1254)`; Source `https://ee8731d6c6b1.registry.invalid/operative-record`.
  > For entity Veloria-EE8731D6 in revision R5, the archival retention period is 90 calendar days.
- **S06**: chunk `135921500a4d7c559633926c2d6a`, claim `f51208b75ad2f7e3a69cd92bb53b`, Character span `[1172, 1261)`; Source `https://ee8731d6c6b1.registry.invalid/operative-record`.
  > For entity Veloria-EE8731D6 in revision R5, the release authorization code is Permit-R31.
- **S02**: chunk `603ad476ae9d5be1840a2d9be2de`, claim `8b2ee7ddd59f3de7a63c9acaa8aa`, Character span `[506, 600)`; Source `https://ee8731d6c6b1.registry.invalid/annex-0`.
  > For entity Veloria-EE8731D6-Annex in revision R5, the file review interval is 11 working days.
- **S03**: chunk `3e1bf2816d7f23e0440070a6ae69`, claim `e6891f07ddfed7f5b3dfa5480e8b`, Character span `[494, 589)`; Source `https://ee8731d6c6b1.registry.invalid/annex-1`.
  > For entity Veloria-EE8731D6-Annex in revision R5, the release authorization code is Permit-R31.
- **S07**: chunk `766725e03be68c52b15caa67630d`, claim `7438f789ebd31ba2fab85ab9d188`, Character span `[800, 900)`; Source `https://ee8731d6c6b1.registry.invalid/annex-2`.
  > For entity Veloria-EE8731D6-Annex in revision R5, the archival retention period is 90 calendar days.
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

R3 requires Permit-K24, 11 working days, Aster-32, and 180 calendar days; S09/S04/S07/S05 assert them about the same subject, covering all four fields.

Evidence: S04, S05, S07, S09.

**D2 Complete assertions, complementary support, and alternative support: pass**

The same-URL chunks A79/A64/A73/A69 must be combined, with four sentences each binding a complete predicate; retaining the operative-record page identity does not guarantee all four sentences.

Evidence: S04, S05, S07, S09.

**D3 Temporal and revision status: pass**

R2/Permit-R32 in S02 is obsolete, whereas R3/Permit-R32 in S01 is a current contradiction; neither can replace R3/Permit-K24.

Evidence: S01, S02, S09.

**D4 Source policy: pass**

There is no source restriction, so S01 on consortium remains an allowed source; Annex documents are excluded because of their different subject rather than domain.

Evidence: S01, S03, S06, S08.

**Findings for this world**

- The four same-source chunks are complementary; source compliance and complete coverage are separate judgments.

**Original-text evidence index**

- **S04**: chunk `91118933c9d3eff2798dacde44ac`, claim `6824ff3e43ddc284bf13d65e430f`, Character span `[668, 756)`; Source `https://d9c577be4011.registry.invalid/operative-record`.
  > For entity Veloria-D9C577BE in revision R3, the file review interval is 11 working days.
- **S05**: chunk `68e61f95343f8779fb10bdb44f0f`, claim `ab9e3f4a039160c2e9988825683e`, Character span `[672, 767)`; Source `https://d9c577be4011.registry.invalid/operative-record`.
  > For entity Veloria-D9C577BE in revision R3, the archival retention period is 180 calendar days.
- **S07**: chunk `1411d67c0e657883e4e5cd9eef5b`, claim `d26ae58331d5ad1e215c969dc1bc`, Character span `[683, 757)`; Source `https://d9c577be4011.registry.invalid/operative-record`.
  > For entity Veloria-D9C577BE in revision R3, the service route is Aster-32.
- **S09**: chunk `81ad9c76766c73d4b611f5d8a821`, claim `9f24d341076147701eb2cbf7704e`, Character span `[699, 788)`; Source `https://d9c577be4011.registry.invalid/operative-record`.
  > For entity Veloria-D9C577BE in revision R3, the release authorization code is Permit-K24.
- **S01**: chunk `c9f4e6a2970a4586f5da28d20475`, claim `7f0341799870675c59bb79d40244`, Character span `[679, 768)`; Source `https://d9c577be4011.consortium.invalid/disputed`.
  > For entity Veloria-D9C577BE in revision R3, the release authorization code is Permit-R32.
- **S02**: chunk `e284618786ce83517cccf448dee3`, claim `908ef1788fecfc3a18281510ab8a`, Character span `[678, 767)`; Source `https://d9c577be4011.registry.invalid/archive`.
  > For entity Veloria-D9C577BE in revision R2, the release authorization code is Permit-R32.
- **S03**: chunk `aa7d32afa990639338791c64b96a`, claim `99bb341afe16c309e7a2416b4f4d`, Character span `[593, 687)`; Source `https://d9c577be4011.registry.invalid/annex-1`.
  > For entity Veloria-D9C577BE-Annex in revision R3, the file review interval is 11 working days.
- **S06**: chunk `06d7f76fc725a9eb61943d2bac43`, claim `1cd86726c78903ffd92e78d0819c`, Character span `[308, 388)`; Source `https://d9c577be4011.registry.invalid/annex-2`.
  > For entity Veloria-D9C577BE-Annex in revision R3, the service route is Aster-32.
- **S08**: chunk `c6a65f1c5eb2e6d63432a6f49485`, claim `db52bc19137f8540f9fd61d75199`, Character span `[395, 490)`; Source `https://d9c577be4011.registry.invalid/annex-0`.
  > For entity Veloria-D9C577BE-Annex in revision R3, the release authorization code is Permit-K24.

## World 11: 3e76e34590e189ccea5f9eed9618

Question IDs: `8a8fa5a3d750fbda1343aa714c9a`, `db53c4c02f91d811c3610c5a5999`.

Collection IDs: `45ee5a714cd97a627670770aeac8`, `b09eedbdc743986853960cd2511f`.

Entity: Veloria-3E76E345; Rendering: prose; Support structure: single_chunk; Required fact count: 4; Overall judgment: **pass**.

Required facts: route = Cobalt-74; review_days = 5 working days; release_code = Permit-V46; retention_days = 30 calendar days.

**D1 Consistency of required facts with the original text: pass**

The four-field question corresponds to the R4 values Cobalt-74, 5 working days, Permit-V46, and 30 calendar days; S01–S04 match individually. Identical Annex values cannot be transferred to the target entity.

Evidence: S01, S02, S03, S04, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four complete statements share chunk A66 and its replicas; each includes the subject and R4, without requiring assembly from fragments about different entities.

Evidence: S01, S02, S03, S04.

**D3 Temporal and revision status: pass**

R3/Willow-57 in S05 is obsolete as of 2035-01-01; S09 presents Willow-57 as R4 and is a current contradiction, not a substitute for Cobalt-74.

Evidence: S01, S05, S09.

**D4 Source policy: pass**

There is no host allowlist, so S09 remains source-allowed on consortium; semantic contradiction and source permission are separate. Annex sources are allowed too but have a different subject.

Evidence: S06, S09.

**Findings for this world**

- One chunk supports all four fields, but complete correct content can coexist with a currently incorrect route.

**Original-text evidence index**

- **S01**: chunk `4c212546778baada4bf656d85fe3`, claim `6af4aab66106c9397eb86f3308e6`, Character span `[1365, 1440)`; Source `https://3e76e34590e1.registry.invalid/replica-0`.
  > For entity Veloria-3E76E345 in revision R4, the service route is Cobalt-74.
- **S02**: chunk `4c212546778baada4bf656d85fe3`, claim `2a314ad491cbf5112e55ad169dcc`, Character span `[1442, 1529)`; Source `https://3e76e34590e1.registry.invalid/replica-0`.
  > For entity Veloria-3E76E345 in revision R4, the file review interval is 5 working days.
- **S03**: chunk `4c212546778baada4bf656d85fe3`, claim `7afca8a394235a1d425b8c93ec7d`, Character span `[1531, 1620)`; Source `https://3e76e34590e1.registry.invalid/replica-0`.
  > For entity Veloria-3E76E345 in revision R4, the release authorization code is Permit-V46.
- **S04**: chunk `4c212546778baada4bf656d85fe3`, claim `049967120df74d050b711a1cf880`, Character span `[1622, 1716)`; Source `https://3e76e34590e1.registry.invalid/replica-0`.
  > For entity Veloria-3E76E345 in revision R4, the archival retention period is 30 calendar days.
- **S06**: chunk `573155a16a68cc7634c3f2835f85`, claim `3f2e3c96c0c59cad234c6762f0e0`, Character span `[403, 484)`; Source `https://3e76e34590e1.registry.invalid/annex-0`.
  > For entity Veloria-3E76E345-Annex in revision R4, the service route is Cobalt-74.
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

S01/S12/S13/S06 give the R6 values 11 working days, 60 calendar days, Permit-R80, and Cobalt-56; all are requested target-entity fields.

Evidence: S01, S06, S12, S13.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each field binds R6 and the target entity in its own complete sentence; the four chunks form a complete support set. Annex sentences cannot fill missing fields.

Evidence: S01, S06, S12, S13, S11, S14, S15.

**D3 Temporal and revision status: pass**

The R5 combination of 14 days/120 days/Permit-R10/Aster-30 in S02–S05 is obsolete; S07–S10 use those four old values under R6, forming a current contradictory group.

Evidence: S02, S03, S04, S05, S07, S08, S09, S10.

**D4 Source policy: pass**

The question imposes no host restriction, so the contradictory group is source-allowed; an unrestricted policy neither removes factual contradictions nor adds a consortium-domain prohibition.

Evidence: S07, S08, S09, S10.

**Findings for this world**

- All four fields in this world have obsolete and current contradictory examples; every field needs checking, and the date supports R6 rather than R5.

**Original-text evidence index**

- **S01**: chunk `7e665e46acdc6f6fb202393f6e26`, claim `ca8d104beadb4bd9af20fa7adb92`, Character span `[1294, 1382)`; Source `https://9b7186639521.registry.invalid/replica-8`.
  > For entity Veloria-9B718663 in revision R6, the file review interval is 11 working days.
- **S06**: chunk `a4374e37532dd3b7438c18dc05ca`, claim `510a0c7de51a03b78f658be43017`, Character span `[1252, 1327)`; Source `https://9b7186639521.registry.invalid/operative-record`.
  > For entity Veloria-9B718663 in revision R6, the service route is Cobalt-56.
- **S12**: chunk `7015b034a79c5ff308a2d000f35d`, claim `5c8c3c162f6752b45f1f2c815d64`, Character span `[1290, 1384)`; Source `https://9b7186639521.registry.invalid/operative-record`.
  > For entity Veloria-9B718663 in revision R6, the archival retention period is 60 calendar days.
- **S13**: chunk `632baaacdf088bd719e83cbb565f`, claim `1e7893a37099e88b257080fada89`, Character span `[1251, 1340)`; Source `https://9b7186639521.registry.invalid/operative-record`.
  > For entity Veloria-9B718663 in revision R6, the release authorization code is Permit-R80.
- **S11**: chunk `b8039bddc111e3ebe9f74e536ee0`, claim `87d5acc43036bac6b8e8b5ce0e2d`, Character span `[602, 696)`; Source `https://9b7186639521.registry.invalid/annex-0`.
  > For entity Veloria-9B718663-Annex in revision R6, the file review interval is 11 working days.
- **S14**: chunk `67246f3eae6071e76bb38a507b5c`, claim `24cf251f5f70162ba1809cda5fed`, Character span `[292, 387)`; Source `https://9b7186639521.registry.invalid/annex-2`.
  > For entity Veloria-9B718663-Annex in revision R6, the release authorization code is Permit-R80.
- **S15**: chunk `e065ff43f96872f66cc175fc6b10`, claim `0aa57bf3e4493eb79a307ccd1638`, Character span `[387, 487)`; Source `https://9b7186639521.registry.invalid/annex-1`.
  > For entity Veloria-9B718663-Annex in revision R6, the archival retention period is 60 calendar days.
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

The four R6 answers 180 calendar days, Permit-V16, Willow-84, and 7 working days appear in S01/S04/S07/S05, respectively; Annex QA cannot stand in for target-entity answers.

Evidence: S01, S04, S05, S07, S02, S03, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each complete annotation includes the subject, R6, and attribute in the question plus the value in the answer; the answer line alone is insufficient, and all four cross-URL QA chunks must be combined.

Evidence: S01, S04, S05, S07.

**D3 Temporal and revision status: pass**

S09 answers 60 days under R5 and is obsolete; S06 answers 60 days under R6 and contradicts the current 180 days. QA formatting does not change this temporal distinction.

Evidence: S01, S06, S09.

**D4 Source policy: pass**

Sources are restricted to 17f56219004c.registry.invalid; S06 on disputed is disallowed because its host is consortium.invalid. Other valid QA sources fall within the allowed prefix.

Evidence: S01, S04, S05, S06, S07.

**Findings for this world**

- Truncating the question or delivering only an answer value such as 180 does not retain the complete factual binding.

**Original-text evidence index**

- **S01**: chunk `45d14b5e0dfd3f4b6bb921c02e06`, claim `c65c2595a67ad4467071534252e3`, Character span `[786, 896)`; Source `https://17f56219004c.registry.invalid/replica-11`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-17F56219? A: 180 calendar days.
- **S04**: chunk `b901db79df8f59a84bb76eaa37f5`, claim `b4790a62d50b80161751e2818eb4`, Character span `[790, 894)`; Source `https://17f56219004c.registry.invalid/operative-part-1`.
  > Q: Under revision R6, what is the release authorization code for entity Veloria-17F56219? A: Permit-V16.
- **S05**: chunk `00b9ad918aa404b1e2acc4cfe670`, claim `6bb4d270e706d3fd01e24d96b130`, Character span `[777, 879)`; Source `https://17f56219004c.registry.invalid/operative-part-3`.
  > Q: Under revision R6, what is the file review interval for entity Veloria-17F56219? A: 7 working days.
- **S07**: chunk `bb6e24abf98d5e1d17ab00db4ad8`, claim `06fb75c75e436330ed9deb77089b`, Character span `[756, 846)`; Source `https://17f56219004c.registry.invalid/operative-part-2`.
  > Q: Under revision R6, what is the service route for entity Veloria-17F56219? A: Willow-84.
- **S02**: chunk `715890130ac7950bcace726b49f6`, claim `4d09728216849eadb9e5e7b65741`, Character span `[498, 614)`; Source `https://17f56219004c.registry.invalid/annex-0`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-17F56219-Annex? A: 180 calendar days.
- **S03**: chunk `fd3d03991ecc97d903ff82aeec23`, claim `3fc5e0c6439d510dc0a41f6801b0`, Character span `[518, 614)`; Source `https://17f56219004c.registry.invalid/annex-2`.
  > Q: Under revision R6, what is the service route for entity Veloria-17F56219-Annex? A: Willow-84.
- **S08**: chunk `711df209b22cf6ac6c7ce88ad8fd`, claim `dbe17ff179035de852d32b21abf5`, Character span `[494, 604)`; Source `https://17f56219004c.registry.invalid/annex-1`.
  > Q: Under revision R6, what is the release authorization code for entity Veloria-17F56219-Annex? A: Permit-V16.
- **S06**: chunk `00d0dbb973d38647b3aff5713b70`, claim `3e7df42a36cc3c3cbb88f8ada73e`, Character span `[793, 902)`; Source `https://17f56219004c.consortium.invalid/disputed`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-17F56219? A: 60 calendar days.
- **S09**: chunk `3b002c183ce01f4329394b7a45b1`, claim `1e8478342ccf4cdee1c5b769a639`, Character span `[798, 907)`; Source `https://17f56219004c.registry.invalid/archive`.
  > Q: Under revision R5, what is the archival retention period for entity Veloria-17F56219? A: 60 calendar days.

## World 14: 069ab1d069588c45b5a65a717488

Question IDs: `81cc2a2c444442fbd02b6eb3357c`, `5ad0edeabbae89289c15f47ecd42`.

Collection IDs: `e7ec1c45fc800ba4ac6a11ca545b`, `923d6c1cdf0b361ffb99fc058a51`.

Entity: Veloria-069AB1D0; Rendering: qa; Support structure: equivalent_support; Required fact count: 4; Overall judgment: **pass**.

Required facts: release_code = Permit-M63; review_days = 3 working days; retention_days = 90 calendar days; route = Aster-82.

**D1 Consistency of required facts with the original text: pass**

The four R6 values Permit-M63, 3 working days, 90 calendar days, and Aster-82 are supported by S02–S05; the old Permit-K49 and identical Annex values are excluded separately.

Evidence: S02, S03, S04, S05, S08, S09.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each support span includes the complete Q+A; the four distributed chunks and independent complete chunk are alternative paths. S10–S13 have correct content but noncompliant sources and must not be treated as current contradictions.

Evidence: S02, S03, S04, S05, S10, S11, S12, S13.

**D3 Temporal and revision status: pass**

R6 applies as of 2035-06-01: R5/Permit-K49 in S08 is obsolete, whereas R6/Permit-K49 in S01 is contradictory. The revision conditions are clear.

Evidence: S01, S02, S08.

**D4 Source policy: pass**

Only 069ab1d06958.registry.invalid is allowed; the four valid QA pairs in consortium.complete-current remain disallowed for admissible coverage.

Evidence: S10, S11, S12, S13, S01.

**Findings for this world**

- Alternative support requires choosing a complete set; semantic validity does not automatically establish policy-compliant sources.

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
- **S09**: chunk `4aa8de0bdb4e46885ca5ba665a6f`, claim `bed4e5885b6adc56e1083c01bafc`, Character span `[403, 513)`; Source `https://069ab1d06958.registry.invalid/annex-0`.
  > Q: Under revision R6, what is the release authorization code for entity Veloria-069AB1D0-Annex? A: Permit-M63.
- **S10**: chunk `cff2439d205d70b3021ac8793d2e`, claim `7f3766bfd19b2aadf0ee6da49ecc`, Character span `[1754, 1858)`; Source `https://069ab1d06958.consortium.invalid/complete-current`.
  > Q: Under revision R6, what is the release authorization code for entity Veloria-069AB1D0? A: Permit-M63.
- **S11**: chunk `cff2439d205d70b3021ac8793d2e`, claim `b805fb5f0edfa148938df468bd4d`, Character span `[1860, 1962)`; Source `https://069ab1d06958.consortium.invalid/complete-current`.
  > Q: Under revision R6, what is the file review interval for entity Veloria-069AB1D0? A: 3 working days.
- **S12**: chunk `cff2439d205d70b3021ac8793d2e`, claim `b5e5c53a22bc50d08353ef6e5045`, Character span `[1964, 2073)`; Source `https://069ab1d06958.consortium.invalid/complete-current`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-069AB1D0? A: 90 calendar days.
- **S13**: chunk `cff2439d205d70b3021ac8793d2e`, claim `4730c47eace1af78a39549ff24b2`, Character span `[2075, 2164)`; Source `https://069ab1d06958.consortium.invalid/complete-current`.
  > Q: Under revision R6, what is the service route for entity Veloria-069AB1D0? A: Aster-82.
- **S01**: chunk `adf816e5f02aa4ed6cc115a6e07c`, claim `70577205403059ae95cdffedd7c3`, Character span `[1767, 1871)`; Source `https://069ab1d06958.consortium.invalid/disputed`.
  > Q: Under revision R6, what is the release authorization code for entity Veloria-069AB1D0? A: Permit-K49.

## World 15: 435622fa3cb24a56eee9e34e19bd

Question IDs: `ac7b54ce6074833e0d225c14beae`, `246371684aaf628fa4835b3c5213`.

Collection IDs: `bb221ba6e5ea1cbf072c84d9e1a2`, `4d512ec429d41e56805b48e3e102`.

Entity: Veloria-435622FA; Rendering: qa; Support structure: position; Required fact count: 3; Overall judgment: **pass**.

Required facts: release_code = Permit-K39; route = Willow-47; review_days = 21 working days.

**D1 Consistency of required facts with the original text: pass**

The R5 question requires Permit-K39, Willow-47, and 21 working days; the QA pairs S03/S06/S08 cover them exactly, and the Annex suffix must not be ignored.

Evidence: S03, S06, S08, S01, S04, S07.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each of the three supports requires reading question and answer together; complete QA pairs late in the text remain valid original support and cannot be replaced by values without a subject.

Evidence: S03, S06, S08.

**D3 Temporal and revision status: pass**

R4/Permit-K34 in S05 is obsolete; that value under R5 in S02 is a current contradiction. The actual R5 authorization code is Permit-K39.

Evidence: S02, S03, S05.

**D4 Source policy: pass**

435622fa3cb2.registry.invalid is the only allowed prefix; S02 on consortium is disallowed, whereas Annex on registry is irrelevant solely because of its wrong subject.

Evidence: S01, S02, S04, S07.

**Findings for this world**

- The 4 replicas repeat only the authorization code; route and review QA must still be delivered separately.

**Original-text evidence index**

- **S03**: chunk `165cb6c0ad20a39ad32a52ccf55d`, claim `1be330eef9d6995a465b73b375d8`, Character span `[2141, 2245)`; Source `https://435622fa3cb2.registry.invalid/replica-0`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-435622FA? A: Permit-K39.
- **S06**: chunk `c0ced5cf8e74dc31a741e92599df`, claim `52c2db8a87c96c9183ed44cc7c54`, Character span `[2148, 2238)`; Source `https://435622fa3cb2.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the service route for entity Veloria-435622FA? A: Willow-47.
- **S08**: chunk `2b57eda11cad763b4357ff0126dc`, claim `a24943bf2adc2cbc75d2fbb8e3f8`, Character span `[2219, 2322)`; Source `https://435622fa3cb2.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the file review interval for entity Veloria-435622FA? A: 21 working days.
- **S01**: chunk `9d3bee6509922bc191fd39987627`, claim `ae730fefc0b17bcf313c6c18555e`, Character span `[205, 315)`; Source `https://435622fa3cb2.registry.invalid/annex-0`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-435622FA-Annex? A: Permit-K39.
- **S04**: chunk `100b9547664f026249b62ddb60aa`, claim `ae06e1c243f47e7ae00cdc15498e`, Character span `[812, 908)`; Source `https://435622fa3cb2.registry.invalid/annex-1`.
  > Q: Under revision R5, what is the service route for entity Veloria-435622FA-Annex? A: Willow-47.
- **S07**: chunk `222263429034c52617908b7ce5f1`, claim `e133e4174a12ade9170675b3e7b2`, Character span `[862, 971)`; Source `https://435622fa3cb2.registry.invalid/annex-2`.
  > Q: Under revision R5, what is the file review interval for entity Veloria-435622FA-Annex? A: 21 working days.
- **S02**: chunk `bc7d78b4e8157fcc6907bb131efa`, claim `b359bc07ad2cb94f239eac6be30b`, Character span `[2152, 2256)`; Source `https://435622fa3cb2.consortium.invalid/disputed`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-435622FA? A: Permit-K34.
- **S05**: chunk `803208df2c43f3f4a43231a5acb1`, claim `f0925e543931440713a417a8f302`, Character span `[2184, 2288)`; Source `https://435622fa3cb2.registry.invalid/archive`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-435622FA? A: Permit-K34.

## World 16: 1b46f5e19cfbc0387e4a647d3406

Question IDs: `ed7222eb7c3288fc0c68b57a4d45`, `d5e424d2b2b50620ff17534c1e90`.

Collection IDs: `c7464854301d8efcb6b8246eb5f4`, `4ed1224c1e163f749374960bc3e4`.

Entity: Veloria-1B46F5E1; Rendering: qa; Support structure: same_url_complementary; Required fact count: 4; Overall judgment: **pass**.

Required facts: retention_days = 90 calendar days; route = Aster-88; review_days = 3 working days; release_code = Permit-V57.

**D1 Consistency of required facts with the original text: pass**

The four R6 fields 90 calendar days, Aster-88, 3 working days, and Permit-V57 are given in S01/S06/S02/S09, matching both requested fields and units.

Evidence: S01, S02, S06, S09.

**D2 Complete assertions, complementary support, and alternative support: pass**

Different QA chunks on one URL provide complementary support, and all four Q+A pairs must be retained separately; a retention-period replica alone does not provide the other three fields.

Evidence: S01, S02, S06, S09.

**D3 Temporal and revision status: pass**

R5/60 days in S03 is obsolete; S08 specifies R6 but still gives 60 days and is contradictory rather than valid support for the current retention period of 90 days.

Evidence: S01, S03, S08.

**D4 Source policy: pass**

The 1b46f5e19cfb.registry.invalid allowlist permits valid QA and old-revision sources; S08 on consortium.invalid is noncompliant. Permission is not determined by the text R6.

Evidence: S01, S02, S06, S08, S09.

**Findings for this world**

- Complete QA is the semantic support unit for this sample; a shared URL does not guarantee survival of all four complementary chunks.

**Original-text evidence index**

- **S01**: chunk `fb490a299fd0a98f4afecfe487b9`, claim `80b4d2df431ae0cd8b87474b92f5`, Character span `[1369, 1478)`; Source `https://1b46f5e19cfb.registry.invalid/replica-10`.
  > Q: Under revision R6, what is the archival retention period for entity Veloria-1B46F5E1? A: 90 calendar days.
- **S02**: chunk `ae3b18bc17f1afd042952faf9222`, claim `f42d3f11ecce317e2a1ea7685a89`, Character span `[1350, 1452)`; Source `https://1b46f5e19cfb.registry.invalid/operative-record`.
  > Q: Under revision R6, what is the file review interval for entity Veloria-1B46F5E1? A: 3 working days.
- **S06**: chunk `aa1218be4990a4af34ffb539fa4c`, claim `17241d064ac7755e2dab4f07248a`, Character span `[1356, 1445)`; Source `https://1b46f5e19cfb.registry.invalid/operative-record`.
  > Q: Under revision R6, what is the service route for entity Veloria-1B46F5E1? A: Aster-88.
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

The two R4 values are Permit-M65 and 60 calendar days; S03/S04 match the question. Identical Annex QA values are not target-entity facts.

Evidence: S03, S04, S05, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

One complete chunk carries two Q+A pairs, and replicas retain both; the support spans include the entity, revision, and attribute in the questions.

Evidence: S03, S04.

**D3 Temporal and revision status: pass**

S01 gives Permit-K82 under R3 and is obsolete, whereas S02 gives Permit-K82 under R4 and is contradictory; S03 establishes the currently valid code.

Evidence: S01, S02, S03.

**D4 Source policy: pass**

There is no allowlist, so S02 on consortium may enter the source set but cannot serve as correct support; allowed source and factual validity remain distinct.

Evidence: S02, S03, S04.

**Findings for this world**

- Under an unrestricted policy, incorrect sources can still legitimately enter the context; the two current valid QA pairs in one chunk support the complete answer.

**Original-text evidence index**

- **S03**: chunk `1eb57f10ec9c3676f9a868ca6e8f`, claim `b802095879c73d826d62547c5536`, Character span `[294, 398)`; Source `https://5eee3a0bbf1b.registry.invalid/replica-3`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-5EEE3A0B? A: Permit-M65.
- **S04**: chunk `1eb57f10ec9c3676f9a868ca6e8f`, claim `30cfcad639a690786b9114f78255`, Character span `[400, 509)`; Source `https://5eee3a0bbf1b.registry.invalid/replica-3`.
  > Q: Under revision R4, what is the archival retention period for entity Veloria-5EEE3A0B? A: 60 calendar days.
- **S05**: chunk `08ff278880ffc0e597b05bc5610b`, claim `cd16d341d090d4fb3fca66ae7337`, Character span `[309, 419)`; Source `https://5eee3a0bbf1b.registry.invalid/annex-0`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-5EEE3A0B-Annex? A: Permit-M65.
- **S06**: chunk `162dac6f7bf5c4a3681d882aadc6`, claim `e95a859c4f44c1b3245cc870137d`, Character span `[205, 320)`; Source `https://5eee3a0bbf1b.registry.invalid/annex-1`.
  > Q: Under revision R4, what is the archival retention period for entity Veloria-5EEE3A0B-Annex? A: 60 calendar days.
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

R3 requires Aster-58, 120 calendar days, and 11 working days, fully answered by the target-entity QA pairs S11/S04/S06.

Evidence: S04, S06, S11.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three QA chunks contribute route, retention, and review support separately, with annotated spans covering question and answer; Annex QA is not equivalent to target-entity QA.

Evidence: S04, S06, S11, S05, S10, S12.

**D3 Temporal and revision status: pass**

The R2 values Cobalt-13/30 days/7 days in S07–S09 are obsolete; S01–S03 present those old values as R3 and are current contradictions. Separate judgments are appropriate.

Evidence: S01, S02, S03, S07, S08, S09.

**D4 Source policy: pass**

The question restricts sources to e3b68dc94f4e.registry.invalid; the consortium document S01–S03 is both disallowed and contradictory to current facts. Both error properties should be preserved separately.

Evidence: S01, S02, S03.

**Findings for this world**

- A disputed document listing three values together does not provide complete valid support; all three values are incorrect.

**Original-text evidence index**

- **S04**: chunk `04e2fbccb404fa038200e09e69b5`, claim `7fbc946fa908c8a2a9b8995b7616`, Character span `[688, 798)`; Source `https://e3b68dc94f4e.registry.invalid/operative-record`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-E3B68DC9? A: 120 calendar days.
- **S06**: chunk `e54796a6066401d50056ad44b3b3`, claim `1e6111e178da357431dc7a3625fa`, Character span `[684, 787)`; Source `https://e3b68dc94f4e.registry.invalid/operative-record`.
  > Q: Under revision R3, what is the file review interval for entity Veloria-E3B68DC9? A: 11 working days.
- **S11**: chunk `9803bc3c7a02f4e5d8227f32df4f`, claim `2fac7c2226ed46195eb90036f0a0`, Character span `[675, 764)`; Source `https://e3b68dc94f4e.registry.invalid/operative-record`.
  > Q: Under revision R3, what is the service route for entity Veloria-E3B68DC9? A: Aster-58.
- **S05**: chunk `d1acdd491103bae8d5104fb960a8`, claim `01b296a2f9e4905beb015e4a1f8b`, Character span `[801, 910)`; Source `https://e3b68dc94f4e.registry.invalid/annex-2`.
  > Q: Under revision R3, what is the file review interval for entity Veloria-E3B68DC9-Annex? A: 11 working days.
- **S10**: chunk `5acb0a6fb0f793cf03792b00cae6`, claim `724f82280e9dc022437404ca6f23`, Character span `[399, 515)`; Source `https://e3b68dc94f4e.registry.invalid/annex-1`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-E3B68DC9-Annex? A: 120 calendar days.
- **S12**: chunk `d2440a81de54440810a2afade289`, claim `3295116a6d54a082dddd99da6f43`, Character span `[590, 685)`; Source `https://e3b68dc94f4e.registry.invalid/annex-0`.
  > Q: Under revision R3, what is the service route for entity Veloria-E3B68DC9-Annex? A: Aster-58.
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

The four R8 fields are 3 working days, 120 calendar days, Permit-R19, and Cobalt-66; S07/S09/S04/S05 match, and Annex cannot substitute for them.

Evidence: S04, S05, S07, S09, S02, S03, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four complete cross-source list sentences must be combined; each directly states the entity, R8, attribute, and value rather than relying on value matching alone.

Evidence: S04, S05, S07, S09.

**D3 Temporal and revision status: pass**

R7/7 working days in S08 is obsolete; R8/7 working days in S01 contradicts the current 3 days. Identical values do not justify merging labels.

Evidence: S01, S07, S08.

**D4 Source policy: pass**

There is no source restriction, so the consortium URL of S01 does not violate policy; the four valid assertions on multiple registry URLs are all allowed as well.

Evidence: S01, S04, S05, S07, S09.

**Findings for this world**

- Cross-URL complementary support requires combining original evidence fact by fact; the designated page need not contain all four fields.

**Original-text evidence index**

- **S04**: chunk `e237ecfe0c3f1df1a43c12f20ccc`, claim `30cedf4ee0ee6f55870cb0aae224`, Character span `[489, 568)`; Source `https://05bc08a3df74.registry.invalid/operative-part-2`.
  > - Entity Veloria-05BC08A3; revision R8; release authorization code: Permit-R19.
- **S05**: chunk `545623d43eccb2c415903390da33`, claim `77021e62ab82e7610dc9a89303a7`, Character span `[504, 569)`; Source `https://05bc08a3df74.registry.invalid/operative-part-3`.
  > - Entity Veloria-05BC08A3; revision R8; service route: Cobalt-66.
- **S07**: chunk `647e1b921d62654e774599605b95`, claim `6d3aed85186bd9c29863848cc0f6`, Character span `[492, 569)`; Source `https://05bc08a3df74.registry.invalid/operative-record`.
  > - Entity Veloria-05BC08A3; revision R8; file review interval: 3 working days.
- **S09**: chunk `bce88af57de9ebde2cc8385cf8aa`, claim `e990dc8e020a3b31d37e15db7ded`, Character span `[485, 570)`; Source `https://05bc08a3df74.registry.invalid/operative-part-1`.
  > - Entity Veloria-05BC08A3; revision R8; archival retention period: 120 calendar days.
- **S02**: chunk `6e9b49886ff1e416fd4633ed230e`, claim `704a0486df126262f9aaa4bc1222`, Character span `[689, 780)`; Source `https://05bc08a3df74.registry.invalid/annex-1`.
  > - Entity Veloria-05BC08A3-Annex; revision R8; archival retention period: 120 calendar days.
- **S03**: chunk `16a0cced603590f1d1ecee9bafba`, claim `fe21d622b0e4324fe995189228cd`, Character span `[922, 1007)`; Source `https://05bc08a3df74.registry.invalid/annex-2`.
  > - Entity Veloria-05BC08A3-Annex; revision R8; release authorization code: Permit-R19.
- **S06**: chunk `f479740ad8fb4d020788ec57b8b1`, claim `c47ecddc644344697f0f13399ea2`, Character span `[693, 776)`; Source `https://05bc08a3df74.registry.invalid/annex-0`.
  > - Entity Veloria-05BC08A3-Annex; revision R8; file review interval: 3 working days.
- **S01**: chunk `145a2e29fb0a0a797a1f51d4ecf3`, claim `e1074a8238e51841336920e2397e`, Character span `[488, 565)`; Source `https://05bc08a3df74.consortium.invalid/disputed`.
  > - Entity Veloria-05BC08A3; revision R8; file review interval: 7 working days.
- **S08**: chunk `aa49261d015054f8bf8e17cdfeda`, claim `d9d9ce827fc9f07156589bf8fc73`, Character span `[489, 566)`; Source `https://05bc08a3df74.registry.invalid/archive`.
  > - Entity Veloria-05BC08A3; revision R7; file review interval: 7 working days.

## World 20: 9dc35b8464be88ace1e5e7f10d27

Question IDs: `0a1819be4aac8153516bb2b26a83`, `f39acf1c9887aac2f8993179e807`.

Collection IDs: `9af81259ed4fed3ad1f72e9a654c`, `246222dd81c17cce36367f155071`.

Entity: Veloria-9DC35B84; Rendering: list; Support structure: equivalent_support; Required fact count: 4; Overall judgment: **pass**.

Required facts: review_days = 3 working days; route = Cobalt-74; release_code = Permit-V31; retention_days = 120 calendar days.

**D1 Consistency of required facts with the original text: pass**

R7 requires 3 working days, Cobalt-74, Permit-V31, and 120 calendar days; S03/S01/S06/S05 match the field list individually.

Evidence: S01, S03, S05, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

Either the four-chunk path or independent complete chunk suffices; both sets need not be retained in full. Each complete list sentence contains the entity, R7, attribute, and value.

Evidence: S01, S03, S05, S06.

**D3 Temporal and revision status: pass**

The old R6 value of 7 working days occurs in S02, whereas S08 asserts 7 days under R7 and is contradictory; the current value in June 2035 is 3 days under R7.

Evidence: S02, S03, S08.

**D4 Source policy: pass**

The question leaves sources unrestricted; although S08 is admissible, its incorrect value receives no correct-support credit. Identical Annex values do not become relevant merely because their URLs are allowed.

Evidence: S04, S07, S08, S09.

**Findings for this world**

- The existence of alternative complete support does not make any individual chunk sufficient; one complete four-field set is required.

**Original-text evidence index**

- **S01**: chunk `4794ae55a186602b069c57716353`, claim `cb70712090a454252494a5655d33`, Character span `[916, 981)`; Source `https://9dc35b8464be.registry.invalid/operative-part-1`.
  > - Entity Veloria-9DC35B84; revision R7; service route: Cobalt-74.
- **S03**: chunk `d78d54544518492794b7e15f0402`, claim `e1ea14a9a214527758b3bb17562c`, Character span `[858, 935)`; Source `https://9dc35b8464be.registry.invalid/operative-record`.
  > - Entity Veloria-9DC35B84; revision R7; file review interval: 3 working days.
- **S05**: chunk `f4e79911234c5001e7db888d57be`, claim `2b5aa8c4eb36cd210617ece24fcd`, Character span `[897, 982)`; Source `https://9dc35b8464be.registry.invalid/operative-part-3`.
  > - Entity Veloria-9DC35B84; revision R7; archival retention period: 120 calendar days.
- **S06**: chunk `fbeb0b3782cd54aaa4a641d8daca`, claim `f469c608e5cfcff87b6c63f60e70`, Character span `[1026, 1105)`; Source `https://9dc35b8464be.registry.invalid/independent-current`.
  > - Entity Veloria-9DC35B84; revision R7; release authorization code: Permit-V31.
- **S02**: chunk `7cc2e29ddeb435eae03889cbbe10`, claim `b2f6034b84dc54db7edc054dbcb2`, Character span `[885, 962)`; Source `https://9dc35b8464be.registry.invalid/archive`.
  > - Entity Veloria-9DC35B84; revision R6; file review interval: 7 working days.
- **S08**: chunk `25d6510bf977d3ecae292d1c85be`, claim `15cec993ed29942baad5563f15c7`, Character span `[896, 973)`; Source `https://9dc35b8464be.consortium.invalid/disputed`.
  > - Entity Veloria-9DC35B84; revision R7; file review interval: 7 working days.
- **S04**: chunk `dfc4dba6c8c9582be82cb663b4f2`, claim `c69e6982f6328bc62115fc89e0c5`, Character span `[297, 368)`; Source `https://9dc35b8464be.registry.invalid/annex-1`.
  > - Entity Veloria-9DC35B84-Annex; revision R7; service route: Cobalt-74.
- **S07**: chunk `6aa511aef725abb0e124f420bbcd`, claim `cc193523fcb3ec55c1af6f28bbb3`, Character span `[799, 882)`; Source `https://9dc35b8464be.registry.invalid/annex-0`.
  > - Entity Veloria-9DC35B84-Annex; revision R7; file review interval: 3 working days.
- **S09**: chunk `49f183eaa85f2ed731c2f12022f0`, claim `4a8b46a9d6e4246aaf1ecc830b64`, Character span `[780, 865)`; Source `https://9dc35b8464be.registry.invalid/annex-2`.
  > - Entity Veloria-9DC35B84-Annex; revision R7; release authorization code: Permit-V31.

## World 21: c201c231abe8aa12a684560d5e82

Question IDs: `8c8fbdeb044fbe9421a7e92d35e2`, `f06db1c2bbb57a19124e63aa02f9`.

Collection IDs: `5cff2de60b2c44a13691fa451166`, `331c4c414fe7b54aecde59111aa6`.

Entity: Veloria-C201C231; Rendering: list; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: review_days = 14 working days; retention_days = 120 calendar days.

**D1 Consistency of required facts with the original text: pass**

The two R8 values 14 working days and 120 calendar days are directly given in S01/S04; identical Annex values cannot count toward the target-entity answer.

Evidence: S01, S02, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

Review and retention support comes from two complete cross-URL list sentences, both explicitly naming Veloria-C201C231 and R8; retaining one field does not satisfy the two-item list.

Evidence: S01, S04.

**D3 Temporal and revision status: pass**

R7/5 working days in S03 is the old value; S06 specifies R8 but gives 5 days and is a current contradiction, disagreeing with the R8 value of 14 days in June 2035.

Evidence: S01, S03, S06.

**D4 Source policy: pass**

There is no allowed-prefix restriction, so S06 on consortium is source-allowed but contradicts the current value; the designated operative-record is not the only allowed page.

Evidence: S04, S06.

**Findings for this world**

- Retaining background or Annex does not supply another valid field, and an unrestricted policy does not replace revision checks.

**Original-text evidence index**

- **S01**: chunk `532af9c962ef658200f7564aaabc`, claim `a91a1bf2c53e3f65c28b154c97f5`, Character span `[798, 876)`; Source `https://c201c231abe8.registry.invalid/replica-10`.
  > - Entity Veloria-C201C231; revision R8; file review interval: 14 working days.
- **S02**: chunk `db55311e00612abc33208ca2398c`, claim `e4219121c40614dda7ad1dd2e72a`, Character span `[605, 689)`; Source `https://c201c231abe8.registry.invalid/annex-2`.
  > - Entity Veloria-C201C231-Annex; revision R8; file review interval: 14 working days.
- **S04**: chunk `a1697a907fc33f9e27c86471a266`, claim `468b7c11699516d6de5ec8d8b585`, Character span `[779, 864)`; Source `https://c201c231abe8.registry.invalid/operative-part-1`.
  > - Entity Veloria-C201C231; revision R8; archival retention period: 120 calendar days.
- **S05**: chunk `d310e6c1572b32cec5c2ec75d635`, claim `26fc6688a44c197b1a18e80ad8f6`, Character span `[593, 684)`; Source `https://c201c231abe8.registry.invalid/annex-1`.
  > - Entity Veloria-C201C231-Annex; revision R8; archival retention period: 120 calendar days.
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

The four requested R5 values Permit-M18, Cobalt-20, 14 working days, and 120 calendar days are supported by S05/S04/S12/S10, respectively, with no field omitted.

Evidence: S04, S05, S10, S12.

**D2 Complete assertions, complementary support, and alternative support: pass**

Distributed chunks and the independent complete chunk provide alternative paths; all four list assertions contain entity/revision/attribute/value. S06–S09 also have complete correct content, but source permission is judged separately.

Evidence: S04, S05, S06, S07, S08, S09, S10, S12.

**D3 Temporal and revision status: pass**

R4/Permit-R16 in S01 is obsolete; R5/Permit-R16 in S03 is a current contradiction. Identical values do not justify merging the two error types.

Evidence: S01, S03, S05.

**D4 Source policy: pass**

Only ae9adbe4331d.registry.invalid is allowed; the complete correct consortium text S06–S09 is noncompliant, and S03 has both contradictory content and a disallowed source.

Evidence: S03, S06, S07, S08, S09.

**Findings for this world**

- Alternative complete support and source-admissible complete support must be checked separately.

**Original-text evidence index**

- **S04**: chunk `543e17ac856ba60fc858bd888460`, claim `eff554c5edc9e43c152a1e83d0c0`, Character span `[488, 553)`; Source `https://ae9adbe4331d.registry.invalid/operative-part-1`.
  > - Entity Veloria-AE9ADBE4; revision R5; service route: Cobalt-20.
- **S05**: chunk `6d475def1e02fc2417427e613452`, claim `187ba39009d117cdf5e5abf8533f`, Character span `[472, 551)`; Source `https://ae9adbe4331d.registry.invalid/replica-3`.
  > - Entity Veloria-AE9ADBE4; revision R5; release authorization code: Permit-M18.
- **S10**: chunk `8d16e1284a4c8fa390099d2d65d9`, claim `21693bbd4fd121215d6460074017`, Character span `[481, 566)`; Source `https://ae9adbe4331d.registry.invalid/operative-part-3`.
  > - Entity Veloria-AE9ADBE4; revision R5; archival retention period: 120 calendar days.
- **S12**: chunk `6fb9801044fadd2432fbf043f654`, claim `03176654971efd66158a54c24202`, Character span `[497, 575)`; Source `https://ae9adbe4331d.registry.invalid/operative-part-2`.
  > - Entity Veloria-AE9ADBE4; revision R5; file review interval: 14 working days.
- **S06**: chunk `ec757da539edf70cb1dea52484e6`, claim `7213718c8aa55cc1276a97da5b81`, Character span `[500, 579)`; Source `https://ae9adbe4331d.consortium.invalid/complete-current`.
  > - Entity Veloria-AE9ADBE4; revision R5; release authorization code: Permit-M18.
- **S07**: chunk `ec757da539edf70cb1dea52484e6`, claim `f761996bcd0aed29806d4d5b3a7a`, Character span `[581, 646)`; Source `https://ae9adbe4331d.consortium.invalid/complete-current`.
  > - Entity Veloria-AE9ADBE4; revision R5; service route: Cobalt-20.
- **S08**: chunk `ec757da539edf70cb1dea52484e6`, claim `93ff82d8d5d178173aed91a345f4`, Character span `[648, 726)`; Source `https://ae9adbe4331d.consortium.invalid/complete-current`.
  > - Entity Veloria-AE9ADBE4; revision R5; file review interval: 14 working days.
- **S09**: chunk `ec757da539edf70cb1dea52484e6`, claim `c10f7bffbef324e2563d1a5e5d78`, Character span `[728, 813)`; Source `https://ae9adbe4331d.consortium.invalid/complete-current`.
  > - Entity Veloria-AE9ADBE4; revision R5; archival retention period: 120 calendar days.
- **S01**: chunk `8a432d53d49b40b85b8f7f976c7a`, claim `6249571d8acf38373c7229d26997`, Character span `[497, 576)`; Source `https://ae9adbe4331d.registry.invalid/archive`.
  > - Entity Veloria-AE9ADBE4; revision R4; release authorization code: Permit-R16.
- **S03**: chunk `916f8324861f30832d2025ce5148`, claim `a67ed046b25fcedbaf8340467e11`, Character span `[490, 569)`; Source `https://ae9adbe4331d.consortium.invalid/disputed`.
  > - Entity Veloria-AE9ADBE4; revision R5; release authorization code: Permit-R16.

## World 23: d208d439525a70477d9124aaf205

Question IDs: `84aa02fb1b56ef73aa1bae7028bf`, `d0434050b4d5caea15c0cc41952b`.

Collection IDs: `50f87db591078b3717c5f7edfa5b`, `922e57fa70d4d7e3e3c3047ae17e`.

Entity: Veloria-D208D439; Rendering: list; Support structure: position; Required fact count: 3; Overall judgment: **pass**.

Required facts: retention_days = 30 calendar days; release_code = Permit-M85; review_days = 7 working days.

**D1 Consistency of required facts with the original text: pass**

R3 requests 30 calendar days, Permit-M85, and 7 working days; S01/S07/S04 give the current values. Identical Annex values do not change the target-entity truth.

Evidence: S01, S04, S07, S03, S05, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

All three complete list sentences contain Veloria-D208D439 and R3; late assertions in the position scenario still require complete delivery, rather than excerpts containing only 30 or Permit-M85.

Evidence: S01, S04, S07.

**D3 Temporal and revision status: pass**

The R2 value of 90 days in S02 is obsolete, whereas the R3 value of 90 days in S08 is a current contradiction; the valid R3 retention period is 30 days in S01.

Evidence: S01, S02, S08.

**D4 Source policy: pass**

Only d208d439525a.registry.invalid is allowed, excluding S08 on consortium; Annex on the same allowed host receives no support credit because of its wrong subject.

Evidence: S03, S05, S06, S08.

**Findings for this world**

- ????????????????????????

**Original-text evidence index**

- **S01**: chunk `852acc775135a6e05d3b40430b97`, claim `6fdc38dd86895ca123b1da258813`, Character span `[3255, 3339)`; Source `https://d208d439525a.registry.invalid/replica-3`.
  > - Entity Veloria-D208D439; revision R3; archival retention period: 30 calendar days.
- **S04**: chunk `d97786735593c14debc85d16086b`, claim `cd3ec8148ddfa4a9f283ed93789c`, Character span `[3254, 3331)`; Source `https://d208d439525a.registry.invalid/operative-record`.
  > - Entity Veloria-D208D439; revision R3; file review interval: 7 working days.
- **S07**: chunk `d4f3fa27aeae4e975214a3cf6bc1`, claim `65f1047d4cc7be3bafdc0c4bbe42`, Character span `[3212, 3291)`; Source `https://d208d439525a.registry.invalid/operative-record`.
  > - Entity Veloria-D208D439; revision R3; release authorization code: Permit-M85.
- **S03**: chunk `30c4b63cc3a2f5d721108f80df35`, claim `f4d7d2d32954078a5282199021ea`, Character span `[292, 377)`; Source `https://d208d439525a.registry.invalid/annex-1`.
  > - Entity Veloria-D208D439-Annex; revision R3; release authorization code: Permit-M85.
- **S05**: chunk `a8ac9b2a5c11cebd6ecaeffad5e4`, claim `552e308077cb2f1b0abce461a0a5`, Character span `[581, 664)`; Source `https://d208d439525a.registry.invalid/annex-2`.
  > - Entity Veloria-D208D439-Annex; revision R3; file review interval: 7 working days.
- **S06**: chunk `8d5af58ca6a7e8696b5e0e784161`, claim `cd98e3fb3878452107738d3dd7fb`, Character span `[400, 490)`; Source `https://d208d439525a.registry.invalid/annex-0`.
  > - Entity Veloria-D208D439-Annex; revision R3; archival retention period: 30 calendar days.
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

The four R6 values Permit-K28, 11 working days, 60 calendar days, and Juniper-18 correspond to S04/S05/S09/S07, matching the question and values.

Evidence: S04, S05, S07, S09.

**D2 Complete assertions, complementary support, and alternative support: pass**

Although all valid sentences have the operative-record URL, each complete field occurs in a different chunk; the shared URL identity cannot replace the complementary relationship among four chunks.

Evidence: S04, S05, S07, S09.

**D3 Temporal and revision status: pass**

S02 explicitly gives the old R5/Permit-R19; S01 gives that value under R6 and is currently incorrect. The correct R6 authorization code is Permit-K28.

Evidence: S01, S02, S04.

**D4 Source policy: pass**

The question leaves sources unrestricted, so S01 on consortium remains admissible; identical Annex values are irrelevant solely because of the different entity.

Evidence: S01, S03, S06, S08.

**Findings for this world**

- This four-chunk same-source structure should be judged by fact coverage rather than URL occurrence alone.

**Original-text evidence index**

- **S04**: chunk `1635952ff73731f786f24b779f62`, claim `4a1574e468b72374683505070439`, Character span `[1029, 1108)`; Source `https://2e4ba86c499e.registry.invalid/operative-record`.
  > - Entity Veloria-2E4BA86C; revision R6; release authorization code: Permit-K28.
- **S05**: chunk `4cae39ea7a85a46b2612a98e1ffe`, claim `96c362995e28815907c413193eb5`, Character span `[1074, 1152)`; Source `https://2e4ba86c499e.registry.invalid/operative-record`.
  > - Entity Veloria-2E4BA86C; revision R6; file review interval: 11 working days.
- **S07**: chunk `f0d3719f12e6cd3b9f3158c0b3aa`, claim `828021f75edb88ad76204485377f`, Character span `[955, 1021)`; Source `https://2e4ba86c499e.registry.invalid/operative-record`.
  > - Entity Veloria-2E4BA86C; revision R6; service route: Juniper-18.
- **S09**: chunk `5ec605a89c2c01d741cf13722070`, claim `9deb262b5eed6c9a27c6cbc29856`, Character span `[1075, 1159)`; Source `https://2e4ba86c499e.registry.invalid/operative-record`.
  > - Entity Veloria-2E4BA86C; revision R6; archival retention period: 60 calendar days.
- **S01**: chunk `9777a1c52b9945a8859006970d19`, claim `5a2758f06a62c49bf123f937746c`, Character span `[990, 1069)`; Source `https://2e4ba86c499e.consortium.invalid/disputed`.
  > - Entity Veloria-2E4BA86C; revision R6; release authorization code: Permit-R19.
- **S02**: chunk `85f67e594647ada177b7cf618e40`, claim `99fbc5f2cd1b98514773808e4fbe`, Character span `[1070, 1149)`; Source `https://2e4ba86c499e.registry.invalid/archive`.
  > - Entity Veloria-2E4BA86C; revision R5; release authorization code: Permit-R19.
- **S03**: chunk `2bd5f9a3ba8799bd3153dadf90c3`, claim `3b0b0ced53d4b1f547aef6e0f4d9`, Character span `[296, 380)`; Source `https://2e4ba86c499e.registry.invalid/annex-1`.
  > - Entity Veloria-2E4BA86C-Annex; revision R6; file review interval: 11 working days.
- **S06**: chunk `d6b7061863ec36df2ed234d13a8e`, claim `7a15ed8debad839cf74e74ab5224`, Character span `[680, 765)`; Source `https://2e4ba86c499e.registry.invalid/annex-0`.
  > - Entity Veloria-2E4BA86C-Annex; revision R6; release authorization code: Permit-K28.
- **S08**: chunk `fe5af4082eb5cee1eff289c7ef09`, claim `809c6904cd698c10d365fe72ec62`, Character span `[618, 708)`; Source `https://2e4ba86c499e.registry.invalid/annex-2`.
  > - Entity Veloria-2E4BA86C-Annex; revision R6; archival retention period: 60 calendar days.

## World 25: 6c8a166e4aaa4ce866c1acc6ba6e

Question IDs: `480c9a5b77a52fa882798f8d9f13`, `1f819fc4d3c84b43625df3af3af7`.

Collection IDs: `571b62697829a2d6cb40e0425546`, `d4dfda99f9d189fb4e7cc04f1ca0`.

Entity: Veloria-6C8A166E; Rendering: list; Support structure: single_chunk; Required fact count: 4; Overall judgment: **pass**.

Required facts: release_code = Permit-R69; route = Aster-59; review_days = 11 working days; retention_days = 90 calendar days.

**D1 Consistency of required facts with the original text: pass**

R7 requires Permit-R69, Aster-59, 11 working days, and 90 calendar days; S01–S04 support each under the same subject and revision.

Evidence: S01, S02, S03, S04.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four complete list sentences share one complete chunk and its replicas, without assembly across Annex or obsolete revisions; all marked spans include field-binding information.

Evidence: S01, S02, S03, S04.

**D3 Temporal and revision status: pass**

R6/Permit-R68 in S05 is obsolete, whereas R7/Permit-R68 in S09 contradicts the current Permit-R69; the date requirement does not support R6.

Evidence: S01, S05, S09.

**D4 Source policy: pass**

The unrestricted policy permits consortium and registry sources; the contradictory content of S09 should not be relabeled as source prohibition.

Evidence: S05, S09.

**Findings for this world**

- Complete single-chunk support can occur in a replica; a replica URL differing from the designated page does not by itself invalidate it.

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

The two R5 fields 14 working days and Aster-10 are explicitly stated in S04/S05; identical Annex values do not concern the target entity.

Evidence: S01, S04, S05, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

The complete list sentences S04/S05 jointly support the answer; the whole incorrect two-field chunk S06/S07 cannot count as a complete valid set.

Evidence: S04, S05, S06, S07.

**D3 Temporal and revision status: pass**

The R4 values 5 days/Juniper-64 in S02/S03 are obsolete; the same old values under R5 in S06/S07 are current contradictions. Combining revision and value checks is correct.

Evidence: S02, S03, S06, S07.

**D4 Source policy: pass**

allowed_url_prefixes is empty, so S06/S07 are source-allowed but do not support current facts; the question provides no basis for prohibiting the consortium host.

Evidence: S06, S07.

**Findings for this world**

- Current contradictions cover both fields; the presence of all answer fields alone does not establish grounding.

**Original-text evidence index**

- **S01**: chunk `9a66df750251d329b18f5f076229`, claim `d814e14c0202b93e8aca8814664d`, Character span `[670, 754)`; Source `https://3fe7f2cc3eec.registry.invalid/annex-2`.
  > - Entity Veloria-3FE7F2CC-Annex; revision R5; file review interval: 14 working days.
- **S04**: chunk `08aa2feea13702961d9767123d56`, claim `6566759fb4042a8e6b8e910a0014`, Character span `[889, 967)`; Source `https://3fe7f2cc3eec.registry.invalid/operative-record`.
  > - Entity Veloria-3FE7F2CC; revision R5; file review interval: 14 working days.
- **S05**: chunk `cbded3e5dd6ee8a7fea8f36c07b3`, claim `c7f216b6d6156dc24e884a82a7d4`, Character span `[814, 878)`; Source `https://3fe7f2cc3eec.registry.invalid/operative-record`.
  > - Entity Veloria-3FE7F2CC; revision R5; service route: Aster-10.
- **S08**: chunk `ede23400877af765c6534ae18706`, claim `91b1b987570f1cbf420711661635`, Character span `[506, 576)`; Source `https://3fe7f2cc3eec.registry.invalid/annex-1`.
  > - Entity Veloria-3FE7F2CC-Annex; revision R5; service route: Aster-10.
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

The R8 question requires 14 working days and Cobalt-36; S02/S03 are narrative sentences with the correct subject and revision. Annex must not be merged with them.

Evidence: S02, S03, S05, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

Review and route support come from different URLs, with complete sentences retaining the entity, R8, and predicate; 14 days alone is not a complete fact.

Evidence: S02, S03.

**D3 Temporal and revision status: pass**

R7/3 working days in S01 is obsolete; R8/3 days in S04 is a current contradiction and should be distinguished from the valid R8 value of 14 days.

Evidence: S01, S02, S04.

**D4 Source policy: pass**

Unrestricted sources do not exclude the consortium text in S04, but its 3-day value is semantically incorrect; source compliance does not guarantee valid support.

Evidence: S04.

**Findings for this world**

- Cross-source support for both independent fields must be present; old-revision information about the same entity must not enter the current answer.

**Original-text evidence index**

- **S02**: chunk `6479ec2adf4cd6ed4b3ddbba2d12`, claim `bfbec4132d21c541afdf95cac293`, Character span `[199, 287)`; Source `https://d7d75ad5d3d9.registry.invalid/operative-record`.
  > For entity Veloria-D7D75AD5 in revision R8, the file review interval is 14 working days.
- **S03**: chunk `2b357ac30ffa3e579f3f4237c2c0`, claim `534fe8407b2592fe751dd208407e`, Character span `[196, 271)`; Source `https://d7d75ad5d3d9.registry.invalid/operative-part-1`.
  > For entity Veloria-D7D75AD5 in revision R8, the service route is Cobalt-36.
- **S05**: chunk `ef7f581027df5f0238a003402403`, claim `41356ce2dfe93f8418575ba28b9e`, Character span `[309, 390)`; Source `https://d7d75ad5d3d9.registry.invalid/annex-1`.
  > For entity Veloria-D7D75AD5-Annex in revision R8, the service route is Cobalt-36.
- **S06**: chunk `b5f53cc8f961a9b8feafd545e736`, claim `779b89e174b2b076ee8e8e754cc1`, Character span `[791, 885)`; Source `https://d7d75ad5d3d9.registry.invalid/annex-2`.
  > For entity Veloria-D7D75AD5-Annex in revision R8, the file review interval is 14 working days.
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

The R9 review interval of 21 working days and retention period of 60 calendar days in S01/S06 match the question; identical Annex values concern a different subject.

Evidence: S01, S02, S05, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The two distributed chunks and independent complete chunk are alternatives; S03/S04 also contain complete correct R9 values but cannot bypass source constraints to receive admissible credit.

Evidence: S01, S03, S04, S06.

**D3 Temporal and revision status: pass**

R8/14 working days in S07 is obsolete; R9/14 days in S08 is a current contradiction. The current R9 value of 21 days agrees with the query date.

Evidence: S01, S07, S08.

**D4 Source policy: pass**

Sources are restricted to edc0e70b068d.registry.invalid; S03/S04 are complete and correct but disallowed on consortium.complete-current. S08 is disallowed too.

Evidence: S03, S04, S08.

**Findings for this world**

- This set of negative examples separates content truth from source policy; complete correct replicas outside the allowlist cannot replace support from allowed sources.

**Original-text evidence index**

- **S01**: chunk `6105e29bf8d894e8af502ea7a947`, claim `41b714a6a7ca4c34c5fde73dd300`, Character span `[1595, 1683)`; Source `https://edc0e70b068d.registry.invalid/operative-record`.
  > For entity Veloria-EDC0E70B in revision R9, the file review interval is 21 working days.
- **S02**: chunk `d2968c6b73226b925628574f7fd4`, claim `555b26ac1d66c39646717808f9b9`, Character span `[490, 584)`; Source `https://edc0e70b068d.registry.invalid/annex-2`.
  > For entity Veloria-EDC0E70B-Annex in revision R9, the file review interval is 21 working days.
- **S05**: chunk `279f11ce78a85449f8e73183a244`, claim `6ac8b78062c495d499df614e735f`, Character span `[305, 405)`; Source `https://edc0e70b068d.registry.invalid/annex-1`.
  > For entity Veloria-EDC0E70B-Annex in revision R9, the archival retention period is 60 calendar days.
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

The four R9 values Cobalt-73, 3 working days, Permit-V31, and 60 calendar days correspond to S01/S08/S07/S03; Annex refers to a different semantic subject.

Evidence: S01, S03, S07, S08, S02, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

All four complete statements contain the subject and R9; the position scenario does not use isolated values as spans. Visibility within a long-text prefix must be separated from original-text completeness.

Evidence: S01, S03, S07, S08.

**D3 Temporal and revision status: pass**

R8/Willow-84 in S09 is obsolete, whereas R9/Willow-84 in S06 is contradictory; the correct current route is Cobalt-73 in S01.

Evidence: S01, S06, S09.

**D4 Source policy: pass**

Only 40a25298fb49.registry.invalid is allowed; S06 is disallowed on consortium, and its incorrect route also constitutes a content contradiction.

Evidence: S06.

**Findings for this world**

- The presence of all four supports in the original text does not mean the budget permits delivery of every late assertion.

**Original-text evidence index**

- **S01**: chunk `707ab8557c46940468504cf862e2`, claim `6d0f085e174f3be6bc58fa5efcb8`, Character span `[698, 773)`; Source `https://40a25298fb49.registry.invalid/replica-3`.
  > For entity Veloria-40A25298 in revision R9, the service route is Cobalt-73.
- **S03**: chunk `ddbe8ae2d950c0c903647c3d66fa`, claim `c70dbc3249b7fe2a68491447cd55`, Character span `[664, 758)`; Source `https://40a25298fb49.registry.invalid/operative-record`.
  > For entity Veloria-40A25298 in revision R9, the archival retention period is 60 calendar days.
- **S07**: chunk `ab4e9dc5cd78ef57e148b2f23b36`, claim `eeb7096f300230cef81b330cef6a`, Character span `[702, 791)`; Source `https://40a25298fb49.registry.invalid/operative-record`.
  > For entity Veloria-40A25298 in revision R9, the release authorization code is Permit-V31.
- **S08**: chunk `5f7f554510d182f4d2594c224f5b`, claim `929f57123b42cc848c3bd20ad358`, Character span `[676, 763)`; Source `https://40a25298fb49.registry.invalid/operative-record`.
  > For entity Veloria-40A25298 in revision R9, the file review interval is 3 working days.
- **S02**: chunk `661c60ac3c8e726f5162f72d501a`, claim `e9b21f4f2e935d8cc5b76878cd36`, Character span `[868, 961)`; Source `https://40a25298fb49.registry.invalid/annex-1`.
  > For entity Veloria-40A25298-Annex in revision R9, the file review interval is 3 working days.
- **S04**: chunk `8c198b152f3580a94fe61fd64c42`, claim `bf8ffb521aff43537699ff0ec549`, Character span `[700, 781)`; Source `https://40a25298fb49.registry.invalid/annex-0`.
  > For entity Veloria-40A25298-Annex in revision R9, the service route is Cobalt-73.
- **S05**: chunk `d5a85d8fbe25c533465c153d364d`, claim `38b3885eff5e6a55f8035f26c43f`, Character span `[305, 400)`; Source `https://40a25298fb49.registry.invalid/annex-2`.
  > For entity Veloria-40A25298-Annex in revision R9, the release authorization code is Permit-V31.
- **S06**: chunk `9f792895637c5872daaff0532d8f`, claim `93c4699519e7530dd976ac765e18`, Character span `[691, 766)`; Source `https://40a25298fb49.consortium.invalid/disputed`.
  > For entity Veloria-40A25298 in revision R9, the service route is Willow-84.
- **S09**: chunk `bf2ac554dd64d1bf7f0e175807de`, claim `e353e2456727def0ef0647a5bd71`, Character span `[678, 753)`; Source `https://40a25298fb49.registry.invalid/archive`.
  > For entity Veloria-40A25298 in revision R8, the service route is Willow-84.

## World 30: 26e56412928bd49d9b924657b892

Question IDs: `62a08e711fd6b062ab1103360464`, `8b1ac140a5236463595e8272f9f1`.

Collection IDs: `9f4386f750e64f3cd4d73ca81efb`, `a9522f5d4039a76513a6cfc0094a`.

Entity: Veloria-26E56412; Rendering: prose; Support structure: same_url_complementary; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Aster-14; retention_days = 120 calendar days; release_code = Permit-V71.

**D1 Consistency of required facts with the original text: pass**

R5 requires Aster-14, 120 calendar days, and Permit-V71; S02/S04/S06 answer all three with correct units. Identical Annex values are irrelevant.

Evidence: S02, S04, S06, S01, S03, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three same-URL chunks provide complementary support, each statement fully binding Veloria-26E56412 and R5; route replicas cannot replace retention or authorization-code support.

Evidence: S02, S04, S06.

**D3 Temporal and revision status: pass**

R4/Juniper-33 in S05 is obsolete, whereas R5/Juniper-33 in S07 is currently incorrect; the question as of 2035-06-01 requires R5/Aster-14.

Evidence: S02, S05, S07.

**D4 Source policy: pass**

The 26e56412928b.registry.invalid allowlist permits current supports and the old archive; S07 on consortium is noncompliant. An allowed old-revision source is not necessarily temporally valid.

Evidence: S02, S04, S05, S06, S07.

**Findings for this world**

- Source filtering and obsolete-revision filtering cannot substitute for each other; archive can be source-compliant but invalid.

**Original-text evidence index**

- **S02**: chunk `d97da26481f342a2d2dba5412c35`, claim `b495522038f82ac2bb2b07f5c74d`, Character span `[607, 681)`; Source `https://26e56412928b.registry.invalid/replica-1`.
  > For entity Veloria-26E56412 in revision R5, the service route is Aster-14.
- **S04**: chunk `c164284c0c1ca96fce1ce67dda30`, claim `c9092ca931b58466d8a70baa477b`, Character span `[587, 682)`; Source `https://26e56412928b.registry.invalid/operative-record`.
  > For entity Veloria-26E56412 in revision R5, the archival retention period is 120 calendar days.
- **S06**: chunk `2c676cbf5cdd411260dfb13a7bd3`, claim `dd950635b5758eb16632b61b6f67`, Character span `[674, 763)`; Source `https://26e56412928b.registry.invalid/operative-record`.
  > For entity Veloria-26E56412 in revision R5, the release authorization code is Permit-V71.
- **S01**: chunk `9450c9d65b1eb54946f0ba05b2dc`, claim `8b380e5072ddd6d24eea2d0899fa`, Character span `[710, 790)`; Source `https://26e56412928b.registry.invalid/annex-0`.
  > For entity Veloria-26E56412-Annex in revision R5, the service route is Aster-14.
- **S03**: chunk `573625d74f33cd8596c0013e2020`, claim `05ed86e49fceea55990d1190393d`, Character span `[407, 508)`; Source `https://26e56412928b.registry.invalid/annex-1`.
  > For entity Veloria-26E56412-Annex in revision R5, the archival retention period is 120 calendar days.
- **S08**: chunk `b36a673f12e026a2632fa2206c3e`, claim `17182f273e5ce472c357fec509f7`, Character span `[300, 395)`; Source `https://26e56412928b.registry.invalid/annex-2`.
  > For entity Veloria-26E56412-Annex in revision R5, the release authorization code is Permit-V71.
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

The four R6 values 14 working days, Permit-K81, 30 calendar days, and Willow-48 are fully stated in S01–S04; identical Annex values do not concern the requested entity.

Evidence: S01, S02, S03, S04, S05, S07, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

All four sentences occur together in one chunk and its replicas, with the subject and R6 in every span; complete support does not require borrowing from other entities or obsolete documents.

Evidence: S01, S02, S03, S04.

**D3 Temporal and revision status: pass**

R5/7 working days in S06 is obsolete; R6/7 days in S09 contradicts the current 14 days. The revision selection agrees with 2035-06-01.

Evidence: S01, S06, S09.

**D4 Source policy: pass**

Sources are restricted to 5e6b32b22ee4.registry.invalid, excluding S09 on consortium; the old S06 on an allowed host still fails the current-fact requirement.

Evidence: S06, S09.

**Findings for this world**

- The old review interval and current contradiction must be distinguished by revision; a single-chunk structure does not mean any truncation preserves every sentence.

**Original-text evidence index**

- **S01**: chunk `73c448f860287225a78e88109bf8`, claim `4ceb8f632c1300585dff51f63921`, Character span `[979, 1067)`; Source `https://5e6b32b22ee4.registry.invalid/replica-0`.
  > For entity Veloria-5E6B32B2 in revision R6, the file review interval is 14 working days.
- **S02**: chunk `73c448f860287225a78e88109bf8`, claim `b9ae88831a24b2d15c45f793118b`, Character span `[1069, 1158)`; Source `https://5e6b32b22ee4.registry.invalid/replica-0`.
  > For entity Veloria-5E6B32B2 in revision R6, the release authorization code is Permit-K81.
- **S03**: chunk `73c448f860287225a78e88109bf8`, claim `ee77abdcb6e5c24fe89a0097d8b1`, Character span `[1160, 1254)`; Source `https://5e6b32b22ee4.registry.invalid/replica-0`.
  > For entity Veloria-5E6B32B2 in revision R6, the archival retention period is 30 calendar days.
- **S04**: chunk `73c448f860287225a78e88109bf8`, claim `49185794171a41eabc2bab3ad126`, Character span `[1256, 1331)`; Source `https://5e6b32b22ee4.registry.invalid/replica-0`.
  > For entity Veloria-5E6B32B2 in revision R6, the service route is Willow-48.
- **S05**: chunk `703bb4fab6cfcb09040613e7a788`, claim `9ad91481eefe58f8bb2d84da9a95`, Character span `[399, 499)`; Source `https://5e6b32b22ee4.registry.invalid/annex-2`.
  > For entity Veloria-5E6B32B2-Annex in revision R6, the archival retention period is 30 calendar days.
- **S07**: chunk `db2748c7dd3178cd975877d756b2`, claim `06069ec9181d6162f3f11bee56b0`, Character span `[691, 786)`; Source `https://5e6b32b22ee4.registry.invalid/annex-1`.
  > For entity Veloria-5E6B32B2-Annex in revision R6, the release authorization code is Permit-K81.
- **S08**: chunk `63acc21b0dbf530ddf7fd0896bb9`, claim `832b0263c2e2702ff0659549b69c`, Character span `[217, 311)`; Source `https://5e6b32b22ee4.registry.invalid/annex-0`.
  > For entity Veloria-5E6B32B2-Annex in revision R6, the file review interval is 14 working days.
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

The requested R4 values 120 calendar days and Willow-61 appear in S01/S06; identical Annex values do not become relevant support through value agreement.

Evidence: S01, S02, S05, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The two complete statements bind the subject and R4 separately, and complementary support requires both; a currently incorrect complete two-field chunk cannot substitute for them.

Evidence: S01, S06, S07, S08.

**D3 Temporal and revision status: pass**

S03/S04 give 180 days and Willow-11 under R3 and are obsolete; S07/S08 give the same old values under R4 and are current contradictions. Temporal/revision labels are appropriate.

Evidence: S03, S04, S07, S08.

**D4 Source policy: pass**

The question has no domain allowlist, so S07/S08 are permitted sources but incorrect current assertions; all consortium sources should not be additionally excluded.

Evidence: S07, S08.

**Findings for this world**

- Under unrestricted sources, current errors and valid support coexist; exposure and coverage should remain distinct.

**Original-text evidence index**

- **S01**: chunk `02d0bfeecc9ff28bb960d79e605d`, claim `2346c0d38fc3896b9a04088065a6`, Character span `[294, 389)`; Source `https://522c7cc27a9f.registry.invalid/replica-1`.
  > For entity Veloria-522C7CC2 in revision R4, the archival retention period is 120 calendar days.
- **S02**: chunk `8fdfd85072f2381e76ada3ef8b9f`, claim `296a4af28ce5c22c16c3ff91a879`, Character span `[796, 897)`; Source `https://522c7cc27a9f.registry.invalid/annex-2`.
  > For entity Veloria-522C7CC2-Annex in revision R4, the archival retention period is 120 calendar days.
- **S05**: chunk `3083aa4758a410f3acb6223f006e`, claim `ae106e58cc3e938928a18af99a54`, Character span `[395, 476)`; Source `https://522c7cc27a9f.registry.invalid/annex-1`.
  > For entity Veloria-522C7CC2-Annex in revision R4, the service route is Willow-61.
- **S06**: chunk `071f9293f5413eb7c65b899133f6`, claim `fe59229aa4f0f0ea96b264cd1c93`, Character span `[302, 377)`; Source `https://522c7cc27a9f.registry.invalid/operative-record`.
  > For entity Veloria-522C7CC2 in revision R4, the service route is Willow-61.
- **S07**: chunk `ef75ac6117915ea4bbd11e5baff1`, claim `84e46df1d1a9dfa87ffcc2c6372a`, Character span `[299, 394)`; Source `https://522c7cc27a9f.consortium.invalid/disputed`.
  > For entity Veloria-522C7CC2 in revision R4, the archival retention period is 180 calendar days.
- **S08**: chunk `ef75ac6117915ea4bbd11e5baff1`, claim `95aee202df34b780fd445d312b0b`, Character span `[396, 471)`; Source `https://522c7cc27a9f.consortium.invalid/disputed`.
  > For entity Veloria-522C7CC2 in revision R4, the service route is Willow-11.
- **S03**: chunk `8dbce1c2cb96f9f94d333c064b91`, claim `0bf7561f47cf128fb8803931502a`, Character span `[291, 386)`; Source `https://522c7cc27a9f.registry.invalid/archive`.
  > For entity Veloria-522C7CC2 in revision R3, the archival retention period is 180 calendar days.
- **S04**: chunk `8dbce1c2cb96f9f94d333c064b91`, claim `17fc5e57e7d6c2682a71ca30f116`, Character span `[388, 463)`; Source `https://522c7cc27a9f.registry.invalid/archive`.
  > For entity Veloria-522C7CC2 in revision R3, the service route is Willow-11.

## World 33: b1af6c74b835e6d857dcce8b3ac7

Question IDs: `097b732f6c272ec76847f06be8da`, `384bfb4850c2a5b5eba376441ce4`.

Collection IDs: `5053b69fda51669d4bed38865f3f`, `e90b1c4659421d6e805d05d9875e`.

Entity: Veloria-B1AF6C74; Rendering: qa; Support structure: cross_url_complementary; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Aster-63; release_code = Permit-K69; retention_days = 60 calendar days.

**D1 Consistency of required facts with the original text: pass**

R4 requires Aster-63, Permit-K69, and 60 calendar days, supplied by the Q+A pairs S06/S08/S04; Annex questions explicitly name a different entity.

Evidence: S04, S06, S08, S01, S02, S07.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each of the three cross-URL QA supports must include its question and answer; the entity/revision in another chunk cannot be borrowed to complete an answer line.

Evidence: S04, S06, S08.

**D3 Temporal and revision status: pass**

R3/Willow-82 in S03 is obsolete, whereas R4/Willow-82 in S05 is a current contradiction; S06/Aster-63 provides valid R4 route support.

Evidence: S03, S05, S06.

**D4 Source policy: pass**

The unrestricted source policy permits the consortium text in S05; its route-value contradiction, rather than host identity, excludes it from correct support.

Evidence: S05.

**Findings for this world**

- Complete support in this world requires three distinct QA attributes, not merely a page or answer value occurring.

**Original-text evidence index**

- **S04**: chunk `78801c1ad2b70d44c20ecd0c27eb`, claim `cfd9dcbd94a744d3edca3ae4eb75`, Character span `[1920, 2029)`; Source `https://b1af6c74b835.registry.invalid/operative-part-2`.
  > Q: Under revision R4, what is the archival retention period for entity Veloria-B1AF6C74? A: 60 calendar days.
- **S06**: chunk `b7170771363e5aa190d3328bfed2`, claim `06fccc721579eb0cd1eb216c6b98`, Character span `[2049, 2138)`; Source `https://b1af6c74b835.registry.invalid/operative-record`.
  > Q: Under revision R4, what is the service route for entity Veloria-B1AF6C74? A: Aster-63.
- **S08**: chunk `78847513c1de47d97d6bae775731`, claim `80bce18eccae4b22d6fabe11b9f4`, Character span `[1950, 2054)`; Source `https://b1af6c74b835.registry.invalid/operative-part-1`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-B1AF6C74? A: Permit-K69.
- **S01**: chunk `796e3cb1545b1ee61019c034ddb3`, claim `f3f35915bc75bc3e18f422bd6cae`, Character span `[388, 503)`; Source `https://b1af6c74b835.registry.invalid/annex-2`.
  > Q: Under revision R4, what is the archival retention period for entity Veloria-B1AF6C74-Annex? A: 60 calendar days.
- **S02**: chunk `7af25d9cdc2266b095c416ac71b6`, claim `d4287f45d2d4e4494389eebd8bad`, Character span `[412, 522)`; Source `https://b1af6c74b835.registry.invalid/annex-1`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-B1AF6C74-Annex? A: Permit-K69.
- **S07**: chunk `9825d8d3608faf9b79a8cf83658f`, claim `47d9a3862a296223255bb856bd78`, Character span `[217, 312)`; Source `https://b1af6c74b835.registry.invalid/annex-0`.
  > Q: Under revision R4, what is the service route for entity Veloria-B1AF6C74-Annex? A: Aster-63.
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

The two R6 values Willow-43 and 14 working days appear in S02/S03, respectively; identical Annex QA values do not match the target entity.

Evidence: S01, S02, S03, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The combined chunks and complete independent-current QA chunk are alternative paths; both Q+A pairs bind R6 and the subject, and all alternative paths need not be present simultaneously.

Evidence: S02, S03.

**D3 Temporal and revision status: pass**

R5/Aster-81 in S05 is obsolete, whereas R6/Aster-81 in S04 is a current contradiction; the valid R6 route Willow-43 cannot be replaced by an old record with that same conflicting value.

Evidence: S02, S04, S05.

**D4 Source policy: pass**

There is no allowlist, so consortium.disputed is source-allowed but its Aster-81 is incorrect; an allowed host does not directly determine factual validity.

Evidence: S04, S05.

**Findings for this world**

- Alternative support may preserve completeness when a particular chunk is lost; this does not make any individual QA pair sufficient.

**Original-text evidence index**

- **S01**: chunk `d9338821d8cb49f9dfc3f09ddce9`, claim `7a98887af45915d3b25e8be1dcb7`, Character span `[385, 481)`; Source `https://39ebf7945377.registry.invalid/annex-2`.
  > Q: Under revision R6, what is the service route for entity Veloria-39EBF794-Annex? A: Willow-43.
- **S02**: chunk `9e4f2e350acfe2bb56e25edbde37`, claim `9c4bafe186e161926981098532ad`, Character span `[809, 899)`; Source `https://39ebf7945377.registry.invalid/independent-current`.
  > Q: Under revision R6, what is the service route for entity Veloria-39EBF794? A: Willow-43.
- **S03**: chunk `9e4f2e350acfe2bb56e25edbde37`, claim `587140a7f2efead7b8552042fd14`, Character span `[901, 1004)`; Source `https://39ebf7945377.registry.invalid/independent-current`.
  > Q: Under revision R6, what is the file review interval for entity Veloria-39EBF794? A: 14 working days.
- **S06**: chunk `dcca5a4dbf06ba039bb4d2c2b081`, claim `782f5577d911b4eb920d04fcc786`, Character span `[891, 1000)`; Source `https://39ebf7945377.registry.invalid/annex-1`.
  > Q: Under revision R6, what is the file review interval for entity Veloria-39EBF794-Annex? A: 14 working days.
- **S04**: chunk `8d573ec00fc70aa9cabcc05322ec`, claim `3e434375f2ccf0eea8fee92671d5`, Character span `[805, 894)`; Source `https://39ebf7945377.consortium.invalid/disputed`.
  > Q: Under revision R6, what is the service route for entity Veloria-39EBF794? A: Aster-81.
- **S05**: chunk `f835330500868379c38b74b8e3e0`, claim `99f994a3aebf8d9f4c07e8a60332`, Character span `[770, 859)`; Source `https://39ebf7945377.registry.invalid/archive`.
  > Q: Under revision R5, what is the service route for entity Veloria-39EBF794? A: Aster-81.

## World 35: b4efb019e822cf2464209df9c08b

Question IDs: `ebc1465a1ded3321840519436b79`, `d6543e8063a96bb075615d0261d4`.

Collection IDs: `81e530b8b796d4ba78a68b62a101`, `0672b48a0cb3f682551abb4b9d8c`.

Entity: Veloria-B4EFB019; Rendering: qa; Support structure: position; Required fact count: 3; Overall judgment: **pass**.

Required facts: release_code = Permit-M64; retention_days = 120 calendar days; route = Juniper-87.

**D1 Consistency of required facts with the original text: pass**

The R7 values Permit-M64, 120 calendar days, and Juniper-87 are supported by the target-entity QA pairs S04/S07/S06; the Annex suffix changes the referent entity.

Evidence: S04, S06, S07, S01, S03, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

Support spans include question and answer; the position scenario still requires a complete subject–revision–attribute–value binding. An answer value alone does not establish retention of the late QA pair.

Evidence: S04, S06, S07.

**D3 Temporal and revision status: pass**

S02 gives the old R6/Permit-V61, whereas S05 gives Permit-V61 under R7 and is a current contradiction; the valid R7 code is Permit-M64 in S04.

Evidence: S02, S04, S05.

**D4 Source policy: pass**

The question has no domain restriction, so S05 on consortium is source-compliant but factually incorrect; a content error must not be changed into a permission error.

Evidence: S05.

**Findings for this world**

- The current and old values of the late authorization code differ in their characters; complete QA and revision information provide the basis for distinguishing them.

**Original-text evidence index**

- **S04**: chunk `d1d490126484ced04482548fc3a9`, claim `17a969c6bf22ad6e688f7c91747f`, Character span `[394, 498)`; Source `https://b4efb019e822.registry.invalid/replica-3`.
  > Q: Under revision R7, what is the release authorization code for entity Veloria-B4EFB019? A: Permit-M64.
- **S06**: chunk `b7503f8056a9ad2aa38c510823b2`, claim `98a91da49bb38e1a5f524e70f421`, Character span `[405, 496)`; Source `https://b4efb019e822.registry.invalid/operative-record`.
  > Q: Under revision R7, what is the service route for entity Veloria-B4EFB019? A: Juniper-87.
- **S07**: chunk `13ba5e7a400602ae84d39fd759cc`, claim `46b7707c0d379449cadb473fe195`, Character span `[406, 516)`; Source `https://b4efb019e822.registry.invalid/operative-record`.
  > Q: Under revision R7, what is the archival retention period for entity Veloria-B4EFB019? A: 120 calendar days.
- **S01**: chunk `4f38d26961516372e6b8c1f4897b`, claim `6da68a994412120b8c7df2f20c83`, Character span `[605, 702)`; Source `https://b4efb019e822.registry.invalid/annex-2`.
  > Q: Under revision R7, what is the service route for entity Veloria-B4EFB019-Annex? A: Juniper-87.
- **S03**: chunk `6816fa5c6e8a18165b82b707efbe`, claim `dd1a4081f158ab5bb2046477512f`, Character span `[894, 1010)`; Source `https://b4efb019e822.registry.invalid/annex-1`.
  > Q: Under revision R7, what is the archival retention period for entity Veloria-B4EFB019-Annex? A: 120 calendar days.
- **S08**: chunk `666ca44327271328c216858566ae`, claim `3eaaefdf29c7494ca5c4a7945f8a`, Character span `[801, 911)`; Source `https://b4efb019e822.registry.invalid/annex-0`.
  > Q: Under revision R7, what is the release authorization code for entity Veloria-B4EFB019-Annex? A: Permit-M64.
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

R8 requires Willow-39, Permit-V55, 60 calendar days, and 5 working days; S02/S08/S03/S07 match individually, whereas Annex QA is irrelevant.

Evidence: S02, S03, S07, S08, S01, S04, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four same-URL QA chunks are complementary, each annotation containing the complete question and answer; route replicas do not contain the other three required fields.

Evidence: S02, S03, S07, S08.

**D3 Temporal and revision status: pass**

R7/Willow-61 in S09 is obsolete; S05 asserts Willow-61 under R8 and is a current contradiction. The question's R8 is valid as of June 2035.

Evidence: S02, S05, S09.

**D4 Source policy: pass**

Sources are restricted to 29ecbcc62ac8.registry.invalid, making S05 on consortium.invalid noncompliant; S09 is source-compliant but remains obsolete.

Evidence: S05, S09.

**Findings for this world**

- Multiple chunks sharing one URL must not be treated as an indivisible lossless unit; completeness of each QA pair requires a separate judgment.

**Original-text evidence index**

- **S02**: chunk `b57f98b468903399916a21356dab`, claim `8ac5a4cae85afe8e3eeae3d70357`, Character span `[1499, 1589)`; Source `https://29ecbcc62ac8.registry.invalid/replica-9`.
  > Q: Under revision R8, what is the service route for entity Veloria-29ECBCC6? A: Willow-39.
- **S03**: chunk `d8e631bc569e01352ad60851efad`, claim `168bdd5318e507d6a5353a3390de`, Character span `[1338, 1447)`; Source `https://29ecbcc62ac8.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the archival retention period for entity Veloria-29ECBCC6? A: 60 calendar days.
- **S07**: chunk `426a12803840f4d2ec4d2abefd55`, claim `42976f7591536e5d7539d0305915`, Character span `[1394, 1496)`; Source `https://29ecbcc62ac8.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the file review interval for entity Veloria-29ECBCC6? A: 5 working days.
- **S08**: chunk `197ecb0d41c4774e5b5a5c75599d`, claim `be2dea5c58a7dbe792a330469e23`, Character span `[1464, 1568)`; Source `https://29ecbcc62ac8.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the release authorization code for entity Veloria-29ECBCC6? A: Permit-V55.
- **S01**: chunk `05a1c0a4cfba4da6964576b548b5`, claim `82efe555c3f512573e0ad2174fc3`, Character span `[606, 716)`; Source `https://29ecbcc62ac8.registry.invalid/annex-1`.
  > Q: Under revision R8, what is the release authorization code for entity Veloria-29ECBCC6-Annex? A: Permit-V55.
- **S04**: chunk `11a66173704bbb05cc0c8c359947`, claim `459b3ef260709c0ea773d6374520`, Character span `[392, 488)`; Source `https://29ecbcc62ac8.registry.invalid/annex-0`.
  > Q: Under revision R8, what is the service route for entity Veloria-29ECBCC6-Annex? A: Willow-39.
- **S06**: chunk `0e54c4d6227a83e678b0776def5a`, claim `c02025b15d640aa5bdcc97640134`, Character span `[499, 614)`; Source `https://29ecbcc62ac8.registry.invalid/annex-2`.
  > Q: Under revision R8, what is the archival retention period for entity Veloria-29ECBCC6-Annex? A: 60 calendar days.
- **S05**: chunk `781d674923f795973dc9d76f9c0b`, claim `31174b868f77a10de70723f9e929`, Character span `[1468, 1558)`; Source `https://29ecbcc62ac8.consortium.invalid/disputed`.
  > Q: Under revision R8, what is the service route for entity Veloria-29ECBCC6? A: Willow-61.
- **S09**: chunk `7e772b192a7dbaded6e2dbc19a4d`, claim `bf8b5ee746af80fdd100b7cadaad`, Character span `[1350, 1440)`; Source `https://29ecbcc62ac8.registry.invalid/archive`.
  > Q: Under revision R7, what is the service route for entity Veloria-29ECBCC6? A: Willow-61.

## World 37: a14db04fc497b5cf89ea45d7053d

Question IDs: `06e46f2893dea942fb3b12191024`, `e98e2bdcb3f930e8b31d7d186568`.

Collection IDs: `9ec1cdbf58d4a189f1a19cb4339c`, `8adad641aaec0862d5ad544126be`.

Entity: Veloria-A14DB04F; Rendering: qa; Support structure: single_chunk; Required fact count: 4; Overall judgment: **pass**.

Required facts: release_code = Permit-M20; review_days = 7 working days; route = Willow-67; retention_days = 60 calendar days.

**D1 Consistency of required facts with the original text: pass**

The four R8 values Permit-M20, 7 working days, Willow-67, and 60 calendar days occur in the target-entity QA pairs S02–S05, matching the truth and question.

Evidence: S02, S03, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four Q+A pairs occupy one complete chunk and its replicas; each question supplies the subject, R8, and attribute, and the answer supplies the value, without relying on Annex fragments.

Evidence: S02, S03, S04, S05.

**D3 Temporal and revision status: pass**

The old R7 code Permit-R69 occurs in S01; Permit-R69 still given under R8 in S07 is a current contradiction. The current code should be Permit-M20.

Evidence: S01, S02, S07.

**D4 Source policy: pass**

There is no source allowlist, so S07 on consortium is admissible but semantically incorrect; Annex assertions S06/S08/S09 remain irrelevant despite allowed sources.

Evidence: S06, S07, S08, S09.

**Findings for this world**

- The four-field single-chunk structure can provide complete support, but it does not automatically eliminate exposure to incorrect current QA.

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
- **S06**: chunk `b38cbfad9fbc5e7d47e1bca56d31`, claim `53643c3d59b86f561d177798a118`, Character span `[491, 601)`; Source `https://a14db04fc497.registry.invalid/annex-0`.
  > Q: Under revision R8, what is the release authorization code for entity Veloria-A14DB04F-Annex? A: Permit-M20.
- **S08**: chunk `82024d2bdf5e8ccb4358c3764b4a`, claim `917b586775b0a215e6c21fba3973`, Character span `[202, 298)`; Source `https://a14db04fc497.registry.invalid/annex-2`.
  > Q: Under revision R8, what is the service route for entity Veloria-A14DB04F-Annex? A: Willow-67.
- **S09**: chunk `620863314ed7f1e46311f110d96d`, claim `5e0c5bdcdacb89166f6a83016cda`, Character span `[300, 408)`; Source `https://a14db04fc497.registry.invalid/annex-1`.
  > Q: Under revision R8, what is the file review interval for entity Veloria-A14DB04F-Annex? A: 7 working days.

## World 38: 7695c91d098f4b3d52e2d26188fa

Question IDs: `d5f39d2ea82d21f007ece297472d`, `3e313e98a1f2a06f41e35e3202a1`.

Collection IDs: `a9746ecb9ac9f2769fc3f3b1afed`, `8c7d799af86525f306a84587becd`.

Entity: Veloria-7695C91D; Rendering: qa; Support structure: temporal_conflict; Required fact count: 3; Overall judgment: **pass**.

Required facts: review_days = 14 working days; route = Juniper-64; retention_days = 90 calendar days.

**D1 Consistency of required facts with the original text: pass**

The R7 question requests 14 working days, Juniper-64, and 90 calendar days, supplied individually by S05/S11/S10; Annex QA refers to another subject.

Evidence: S05, S10, S11, S01, S06, S12.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three valid Q+A pairs provide complementary support, each fully specifying subject/revision/attribute/value; three incorrect values together in a disputed chunk are not complete correct support.

Evidence: S05, S07, S08, S09, S10, S11.

**D3 Temporal and revision status: pass**

The R6 values 11 days/Cobalt-79/30 days in S02–S04 are obsolete; S07–S09 repeat them under R7 and are current contradictions. The distinction is consistent across all three fields.

Evidence: S02, S03, S04, S07, S08, S09.

**D4 Source policy: pass**

Only 7695c91d098f.registry.invalid is allowed; S07–S09 on consortium are both noncompliant and contradictory. The old archive remains source-allowed.

Evidence: S02, S03, S04, S07, S08, S09.

**Findings for this world**

- Source filtering can remove disallowed disputed documents but does not automatically remove obsolete revisions on allowed hosts.

**Original-text evidence index**

- **S05**: chunk `8fcca4b3b817a1cf53b4f12b99ad`, claim `58a60b5184865fe3c90c3f7d340f`, Character span `[1069, 1172)`; Source `https://7695c91d098f.registry.invalid/replica-3`.
  > Q: Under revision R7, what is the file review interval for entity Veloria-7695C91D? A: 14 working days.
- **S10**: chunk `a01091958daab9b1791f150d0fca`, claim `5938e80ffc75166b0b4f593fde3f`, Character span `[1067, 1176)`; Source `https://7695c91d098f.registry.invalid/operative-record`.
  > Q: Under revision R7, what is the archival retention period for entity Veloria-7695C91D? A: 90 calendar days.
- **S11**: chunk `234249a8bdde5bf0ec804040f41c`, claim `eb0273bbd422fdab5ea1462907fa`, Character span `[1064, 1155)`; Source `https://7695c91d098f.registry.invalid/operative-record`.
  > Q: Under revision R7, what is the service route for entity Veloria-7695C91D? A: Juniper-64.
- **S01**: chunk `1bea85e687733b6582bcf22261c0`, claim `070137a3069ae3c1e3ab849fb921`, Character span `[578, 687)`; Source `https://7695c91d098f.registry.invalid/annex-0`.
  > Q: Under revision R7, what is the file review interval for entity Veloria-7695C91D-Annex? A: 14 working days.
- **S06**: chunk `c4d1d4b67e1cec5d054d66cc825c`, claim `8938f2be70a5f52e0dd9e81a831c`, Character span `[511, 608)`; Source `https://7695c91d098f.registry.invalid/annex-1`.
  > Q: Under revision R7, what is the service route for entity Veloria-7695C91D-Annex? A: Juniper-64.
- **S12**: chunk `abe0ef2d28f17faa81596ecfa8a1`, claim `69856b2828bae22245055846efd7`, Character span `[783, 898)`; Source `https://7695c91d098f.registry.invalid/annex-2`.
  > Q: Under revision R7, what is the archival retention period for entity Veloria-7695C91D-Annex? A: 90 calendar days.
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

The two R9 fields are 90 calendar days and Aster-24; S04/S01 fully match the question. Identical Annex values are not equivalent to target-entity facts.

Evidence: S01, S02, S04, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The retention and route sentences on different URLs are complementary, with both complete list sentences specifying the subject and R9; retaining only the designated operative-record does not establish route retention.

Evidence: S01, S04.

**D3 Temporal and revision status: pass**

The old R8/30 days in S05 and current conflicting R9/30 days in S03 should be distinguished; the current valid retention period is 90 days.

Evidence: S03, S04, S05.

**D4 Source policy: pass**

Sources are restricted to 5d8ec042a571.registry.invalid; S03 on consortium is prohibited, whereas S01 on operative-part-1 is within the allowlist and is not disallowed merely because it is not the designated page.

Evidence: S01, S03.

**Findings for this world**

- Designated pages and allowed sources form different sets; allowed cross-page support can contribute required facts.

**Original-text evidence index**

- **S01**: chunk `15319045e694c6c808a0e2996192`, claim `c04c9a1b8755c1b92dc05eae0a33`, Character span `[1075, 1139)`; Source `https://5d8ec042a571.registry.invalid/operative-part-1`.
  > - Entity Veloria-5D8EC042; revision R9; service route: Aster-24.
- **S02**: chunk `9b3aa7eaf55efbbf7c40b8885bdc`, claim `53fda58f4d454e322421baa3b430`, Character span `[519, 609)`; Source `https://5d8ec042a571.registry.invalid/annex-0`.
  > - Entity Veloria-5D8EC042-Annex; revision R9; archival retention period: 90 calendar days.
- **S04**: chunk `b4256ca7b68ab0aeb1304aa767da`, claim `b5944231364d7e96b4aa84291e0e`, Character span `[1065, 1149)`; Source `https://5d8ec042a571.registry.invalid/operative-record`.
  > - Entity Veloria-5D8EC042; revision R9; archival retention period: 90 calendar days.
- **S06**: chunk `f6592a48a20ec0a8fef496d1f7be`, claim `4873e5e468701807b206e4ebce85`, Character span `[201, 271)`; Source `https://5d8ec042a571.registry.invalid/annex-1`.
  > - Entity Veloria-5D8EC042-Annex; revision R9; service route: Aster-24.
- **S03**: chunk `66d71be5624dc1c69c7abd6e3161`, claim `d6a3d3dee2797e7078e376e6cc01`, Character span `[1063, 1147)`; Source `https://5d8ec042a571.consortium.invalid/disputed`.
  > - Entity Veloria-5D8EC042; revision R9; archival retention period: 30 calendar days.
- **S05**: chunk `bd78ea957a5a60b3689719ea8c6a`, claim `6c866042e11e354accf0ef122c7d`, Character span `[1052, 1136)`; Source `https://5d8ec042a571.registry.invalid/archive`.
  > - Entity Veloria-5D8EC042; revision R8; archival retention period: 30 calendar days.

## World 40: 2ae1c308770eaecc98299006e3de

Question IDs: `9f1aba8a4432f63db4910e316dd8`, `07d870f45fb5607be4a58d3feea3`.

Collection IDs: `5eed0ee71ddb54137bccd373d895`, `cae62a4e29d8a83c8fa10e96749c`.

Entity: Veloria-2AE1C308; Rendering: list; Support structure: equivalent_support; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Willow-33; retention_days = 30 calendar days; review_days = 14 working days.

**D1 Consistency of required facts with the original text: pass**

The requested R3 values Willow-33, 30 calendar days, and 14 working days are given in S03–S05; identical Annex values cannot be transferred to the target entity.

Evidence: S03, S04, S05, S02, S07, S11.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three-chunk path and independent complete chunk provide alternative support; S08–S10 also contain complete correct content, but admissible coverage requires a separate source check.

Evidence: S03, S04, S05, S08, S09, S10.

**D3 Temporal and revision status: pass**

S01 gives the old R2/Juniper-34, whereas S06 asserts Juniper-34 under R3 and is a current contradiction; the correct R3 route is Willow-33.

Evidence: S01, S03, S06.

**D4 Source policy: pass**

Only 2ae1c308770e.registry.invalid is allowed; the complete correct consortium text S08–S10 remains noncompliant and cannot be treated as equivalent to the independent complete registry chunk for coverage under source constraints.

Evidence: S06, S08, S09, S10.

**Findings for this world**

- Semantic correctness, completeness, and source permission are three distinct checks; this world includes complete support that is correct but disallowed.

**Original-text evidence index**

- **S03**: chunk `e61cdf65bc74b967c018e6f903e1`, claim `390b8cb14319293f41cd0cfa892f`, Character span `[968, 1033)`; Source `https://2ae1c308770e.registry.invalid/independent-current`.
  > - Entity Veloria-2AE1C308; revision R3; service route: Willow-33.
- **S04**: chunk `e61cdf65bc74b967c018e6f903e1`, claim `0a2f0622e26d94096ec7917bbf77`, Character span `[1035, 1119)`; Source `https://2ae1c308770e.registry.invalid/independent-current`.
  > - Entity Veloria-2AE1C308; revision R3; archival retention period: 30 calendar days.
- **S05**: chunk `e61cdf65bc74b967c018e6f903e1`, claim `b8e64d953e8712dae106b6ce6fae`, Character span `[1121, 1199)`; Source `https://2ae1c308770e.registry.invalid/independent-current`.
  > - Entity Veloria-2AE1C308; revision R3; file review interval: 14 working days.
- **S02**: chunk `08258ae18f0a9d797e43e4a97ac3`, claim `bb1d4808911435c09706b0a794aa`, Character span `[808, 892)`; Source `https://2ae1c308770e.registry.invalid/annex-2`.
  > - Entity Veloria-2AE1C308-Annex; revision R3; file review interval: 14 working days.
- **S07**: chunk `e9e152f4d2f1cc6a7c3a6ff22743`, claim `2f2343a8b882b92c38fd2684732f`, Character span `[479, 569)`; Source `https://2ae1c308770e.registry.invalid/annex-1`.
  > - Entity Veloria-2AE1C308-Annex; revision R3; archival retention period: 30 calendar days.
- **S11**: chunk `935e11545a65c8d47dd14749ec82`, claim `a1c0433ddb66438523bd70009dbe`, Character span `[625, 696)`; Source `https://2ae1c308770e.registry.invalid/annex-0`.
  > - Entity Veloria-2AE1C308-Annex; revision R3; service route: Willow-33.
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

R6 requires 90 calendar days and 14 working days; S01/S05 answer the target retention period and review interval, respectively. Identical Annex values do not support the same entity.

Evidence: S01, S02, S03, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The two complete cross-URL list sentences are complementary; multiple 90-day retention replicas cannot produce the missing 14-day fact. Both subject and R6 are within the spans.

Evidence: S01, S05.

**D3 Temporal and revision status: pass**

R5/60 days in S06 is obsolete; R6/60 days in S04 is a current contradiction. The correct current retention period is 90 days.

Evidence: S01, S04, S06.

**D4 Source policy: pass**

The question leaves sources unrestricted, so S04 on consortium is source-allowed but incorrect; the source policy does not prohibit all nondesignated pages.

Evidence: S04, S05.

**Findings for this world**

- Retention of the designated page and delivery of the review assertion from another page require separate judgments.

**Original-text evidence index**

- **S01**: chunk `4c6c06ac6f6461b9a0351c0aa29d`, claim `2eee09e8bd39e16b4355a5e3168b`, Character span `[410, 494)`; Source `https://7d6eedafd815.registry.invalid/replica-2`.
  > - Entity Veloria-7D6EEDAF; revision R6; archival retention period: 90 calendar days.
- **S02**: chunk `b1a0151aee28029514b7e82c524b`, claim `8e4f63892369a2f58b7d31bb86cc`, Character span `[510, 594)`; Source `https://7d6eedafd815.registry.invalid/annex-1`.
  > - Entity Veloria-7D6EEDAF-Annex; revision R6; file review interval: 14 working days.
- **S03**: chunk `7b0ce4ae203c41d2803421220c81`, claim `ef9aaa6ebfd8f9c0e3170c8a940b`, Character span `[614, 704)`; Source `https://7d6eedafd815.registry.invalid/annex-0`.
  > - Entity Veloria-7D6EEDAF-Annex; revision R6; archival retention period: 90 calendar days.
- **S05**: chunk `78eae9952183329d0cbe0e6b6442`, claim `924ebaf0cfd04f28440630c85fc9`, Character span `[406, 484)`; Source `https://7d6eedafd815.registry.invalid/operative-part-1`.
  > - Entity Veloria-7D6EEDAF; revision R6; file review interval: 14 working days.
- **S04**: chunk `ec48eb14ba5aab28a7548697978e`, claim `bbe9f28276a88c847102c3d35886`, Character span `[405, 489)`; Source `https://7d6eedafd815.consortium.invalid/disputed`.
  > - Entity Veloria-7D6EEDAF; revision R6; archival retention period: 60 calendar days.
- **S06**: chunk `737b188508b2890c9083a0357fe5`, claim `0dcc14c898b74789632ac5e62994`, Character span `[390, 474)`; Source `https://7d6eedafd815.registry.invalid/archive`.
  > - Entity Veloria-7D6EEDAF; revision R5; archival retention period: 60 calendar days.

## World 42: d47d281811828f77c9b138603dda

Question IDs: `b71a3bd81f1c6d5b50ca5a68ed94`, `a3d4e247e486e6af7abb01e47cfe`.

Collection IDs: `a9a558995c9fdcb6a9407754f89a`, `6a25e7491b2623f685bc9663a50e`.

Entity: Veloria-D47D2818; Rendering: list; Support structure: equivalent_support; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Willow-30; review_days = 5 working days; retention_days = 90 calendar days.

**D1 Consistency of required facts with the original text: pass**

The three R6 values Willow-30, 5 working days, and 90 calendar days in S06/S04/S01 match the question; the three identical Annex values cannot be transferred to the target entity.

Evidence: S01, S04, S06, S02, S03, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

The distributed three-chunk set and single complete alternative must each cover all three fields; S01/S04/S06 fully state the target entity, R6, and attribute values. Alternative paths must not be required simultaneously.

Evidence: S01, S04, S06.

**D3 Temporal and revision status: pass**

R5/Willow-50 in S05 is obsolete; R6/Willow-50 in S07 contradicts the current Willow-30. Using R6 agrees with the query date.

Evidence: S05, S06, S07.

**D4 Source policy: pass**

There is no allowlist, so S07 on consortium is admissible but contributes no correct route support; Annex on registry is also source-compliant but semantically irrelevant.

Evidence: S02, S03, S07, S08.

**Findings for this world**

- An alternative complete chunk can offset the loss of a particular distributed chunk; this does not make the currently incorrect route valid support.

**Original-text evidence index**

- **S01**: chunk `4c8ac1dfb0bd230ea0c54aa5668b`, claim `6970df5c2f5541e390add2935322`, Character span `[572, 656)`; Source `https://d47d28181182.registry.invalid/operative-part-2`.
  > - Entity Veloria-D47D2818; revision R6; archival retention period: 90 calendar days.
- **S04**: chunk `ce26cb170d885c0dd547d5cc816b`, claim `f65dbd681c9967c07ddf8e46c735`, Character span `[581, 658)`; Source `https://d47d28181182.registry.invalid/operative-part-1`.
  > - Entity Veloria-D47D2818; revision R6; file review interval: 5 working days.
- **S06**: chunk `6bb49718f15209250acd4d16e8ef`, claim `e0158886c3da45a4567dbd86c451`, Character span `[608, 673)`; Source `https://d47d28181182.registry.invalid/replica-10`.
  > - Entity Veloria-D47D2818; revision R6; service route: Willow-30.
- **S02**: chunk `0ca14bb564db0c1111709f9f7897`, claim `57fe60715cbd7ebaefee998c794c`, Character span `[693, 776)`; Source `https://d47d28181182.registry.invalid/annex-1`.
  > - Entity Veloria-D47D2818-Annex; revision R6; file review interval: 5 working days.
- **S03**: chunk `0261dc192a80f5fa726695ce35b1`, claim `1a61279c52bfd5a43fec7c230327`, Character span `[503, 593)`; Source `https://d47d28181182.registry.invalid/annex-2`.
  > - Entity Veloria-D47D2818-Annex; revision R6; archival retention period: 90 calendar days.
- **S08**: chunk `a14aba733a192f18285eaf439436`, claim `a247c3aa47d2cfd7b9a83f27d081`, Character span `[804, 875)`; Source `https://d47d28181182.registry.invalid/annex-0`.
  > - Entity Veloria-D47D2818-Annex; revision R6; service route: Willow-30.
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

R7 requires Willow-64, Permit-K32, and 11 working days; S03/S02/S04 answer completely. The Annex wording refers to a different entity.

Evidence: S02, S03, S04, S01, S05, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

The late list supports remain complete subject–revision–predicate–value assertions; all three fields must be retained for completeness. Values cannot be inferred from background wording in the prefix.

Evidence: S02, S03, S04.

**D3 Temporal and revision status: pass**

R6/Aster-84 in S08 is obsolete, whereas R7/Aster-84 in S07 is a current contradiction; R7/Willow-64 in S03 is the matching value.

Evidence: S03, S07, S08.

**D4 Source policy: pass**

Sources are restricted to 28b5106dc8a5.registry.invalid, excluding S07 on consortium; Annex lies within the allowlist but its entity suffix still makes it irrelevant.

Evidence: S01, S05, S06, S07.

**Findings for this world**

- source_allowed and subject correctness must not be merged into one label.

**Original-text evidence index**

- **S02**: chunk `f507ec20989bb6537cbe67a5fe9f`, claim `7b04521db9f4f6ae3832d2ecc249`, Character span `[968, 1047)`; Source `https://28b5106dc8a5.registry.invalid/operative-record`.
  > - Entity Veloria-28B5106D; revision R7; release authorization code: Permit-K32.
- **S03**: chunk `5e8e05e4c02ac32ac63b0e462565`, claim `b0585d170f6a8d16fe99080daf7b`, Character span `[969, 1034)`; Source `https://28b5106dc8a5.registry.invalid/replica-10`.
  > - Entity Veloria-28B5106D; revision R7; service route: Willow-64.
- **S04**: chunk `7a1d87bd854b78ad41d2b0599d05`, claim `22dfdac4f388a8d8122d6f74dc65`, Character span `[885, 963)`; Source `https://28b5106dc8a5.registry.invalid/operative-record`.
  > - Entity Veloria-28B5106D; revision R7; file review interval: 11 working days.
- **S01**: chunk `ecdcd1a96a9cba7a38c4fa2d2167`, claim `d9b90def655aae39f4bd0a39d710`, Character span `[614, 699)`; Source `https://28b5106dc8a5.registry.invalid/annex-1`.
  > - Entity Veloria-28B5106D-Annex; revision R7; release authorization code: Permit-K32.
- **S05**: chunk `16578eada13ef036f8ef589ab3f3`, claim `c1b4193c01cf560600571d8a7119`, Character span `[894, 965)`; Source `https://28b5106dc8a5.registry.invalid/annex-0`.
  > - Entity Veloria-28B5106D-Annex; revision R7; service route: Willow-64.
- **S06**: chunk `f127d672ecc26e2f8e88a2de289e`, claim `9b5b8b1046e342eb13c435b2c083`, Character span `[304, 388)`; Source `https://28b5106dc8a5.registry.invalid/annex-2`.
  > - Entity Veloria-28B5106D-Annex; revision R7; file review interval: 11 working days.
- **S07**: chunk `926ac51fed5518ac6de093462d53`, claim `c6887bc472efd7564e73534a20a2`, Character span `[910, 974)`; Source `https://28b5106dc8a5.consortium.invalid/disputed`.
  > - Entity Veloria-28B5106D; revision R7; service route: Aster-84.
- **S08**: chunk `d3ebfa1e9e75d6203d5f3a466642`, claim `b1f13745a639c534b3ec26a1fba8`, Character span `[944, 1008)`; Source `https://28b5106dc8a5.registry.invalid/archive`.
  > - Entity Veloria-28B5106D; revision R6; service route: Aster-84.

## World 44: 805164c17a4a8ee79b53dfd32a98

Question IDs: `d8bf2ecebd866454bbf4210256f3`, `6e267caad53d4cb410014ddae1c9`.

Collection IDs: `c7603196e87b29e0f9ca09469ac8`, `e5164f31068dfcb5908592f31d4a`.

Entity: Veloria-805164C1; Rendering: list; Support structure: same_url_complementary; Required fact count: 3; Overall judgment: **pass**.

Required facts: retention_days = 60 calendar days; release_code = Permit-R70; review_days = 3 working days.

**D1 Consistency of required facts with the original text: pass**

R3 requires 60 calendar days, Permit-R70, and 3 working days; S05/S02/S01 match the question individually, whereas all identical Annex values have a mismatched subject.

Evidence: S01, S02, S05, S06, S07, S08.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three fields occupy different complete sentences/chunks on one URL, and the support set must cover all three; URL-level retention alone does not establish completeness.

Evidence: S01, S02, S05.

**D3 Temporal and revision status: pass**

R2/180 days in S04 is obsolete; R3/180 days in S03 is a current contradiction. The valid R3 retention period is 60 days in S05.

Evidence: S03, S04, S05.

**D4 Source policy: pass**

The allowlist is 805164c17a4a.registry.invalid, excluding S03 on consortium; the allowed archive still requires exclusion because R2 is obsolete.

Evidence: S03, S04.

**Findings for this world**

- Same-source complementary support coexists with obsolete-revision interference; host or page identity alone cannot justify support credit.

**Original-text evidence index**

- **S01**: chunk `646649cf6c8f9654fbb9c08e269e`, claim `31fb74994e756e3be23f0ab3fd21`, Character span `[1378, 1455)`; Source `https://805164c17a4a.registry.invalid/operative-record`.
  > - Entity Veloria-805164C1; revision R3; file review interval: 3 working days.
- **S02**: chunk `c6ade0fc6a49e574723ec277e5ab`, claim `d38589c2037a9ec0fad3aaa0f0d7`, Character span `[1472, 1551)`; Source `https://805164c17a4a.registry.invalid/operative-record`.
  > - Entity Veloria-805164C1; revision R3; release authorization code: Permit-R70.
- **S05**: chunk `8d0f8471d0344d4ef7740da7b0f5`, claim `e43b8df5d6238ab4f5b42d3e55ca`, Character span `[1371, 1455)`; Source `https://805164c17a4a.registry.invalid/operative-record`.
  > - Entity Veloria-805164C1; revision R3; archival retention period: 60 calendar days.
- **S06**: chunk `15dada75ded1ede6468733e195e0`, claim `72152f1560886fef50dcbd11cf35`, Character span `[704, 787)`; Source `https://805164c17a4a.registry.invalid/annex-2`.
  > - Entity Veloria-805164C1-Annex; revision R3; file review interval: 3 working days.
- **S07**: chunk `4da27e6b4eb4233fde0275846a2d`, claim `301c62a0e1608bfe9783342ab6dc`, Character span `[309, 399)`; Source `https://805164c17a4a.registry.invalid/annex-0`.
  > - Entity Veloria-805164C1-Annex; revision R3; archival retention period: 60 calendar days.
- **S08**: chunk `d078aa8507a1c3955be51036e5ff`, claim `3e69fe60e5a7e15d991cad8f9822`, Character span `[796, 881)`; Source `https://805164c17a4a.registry.invalid/annex-1`.
  > - Entity Veloria-805164C1-Annex; revision R3; release authorization code: Permit-R70.
- **S03**: chunk `681fd448a3f271379665535fb202`, claim `9645a74697976a6a4e47103d3deb`, Character span `[1373, 1458)`; Source `https://805164c17a4a.consortium.invalid/disputed`.
  > - Entity Veloria-805164C1; revision R3; archival retention period: 180 calendar days.
- **S04**: chunk `59fba0109c02a6cd346d38b01af0`, claim `789b1e4cb19c7af7bbfcd85b5c22`, Character span `[1366, 1451)`; Source `https://805164c17a4a.registry.invalid/archive`.
  > - Entity Veloria-805164C1; revision R2; archival retention period: 180 calendar days.

## World 45: 00000588c8c6fbb0d7423c13c49b

Question IDs: `3ab5a10c00acab73d0da88005154`, `d2a734879ffab06145b433bedb07`.

Collection IDs: `e41dbe1f07651bf4e2fe35b24080`, `c476713ba966924f0e1b8ce0f642`.

Entity: Veloria-00000588; Rendering: list; Support structure: single_chunk; Required fact count: 4; Overall judgment: **pass**.

Required facts: review_days = 21 working days; retention_days = 180 calendar days; release_code = Permit-R12; route = Juniper-44.

**D1 Consistency of required facts with the original text: pass**

The four R3 fields 21 working days, 180 calendar days, Permit-R12, and Juniper-44 are given individually in S02–S05, agreeing with both truth and question.

Evidence: S02, S03, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four sentences in one complete chunk each contain the entity, R3, and attribute value, without combining different Annex records; the annotated single-chunk support set is appropriate.

Evidence: S02, S03, S04, S05.

**D3 Temporal and revision status: pass**

R2/3 working days in S07 is obsolete; R3/3 days in S06 is a current contradiction, correctly distinguished from R3/21 days.

Evidence: S02, S06, S07.

**D4 Source policy: pass**

There is no source restriction, so S06 on consortium is allowed but incorrect; the same-host Annex records S01/S08/S09 cannot receive target-entity support credit through source permission either.

Evidence: S01, S06, S08, S09.

**Findings for this world**

- One chunk can support all four requested fields, but additional incorrect current assertions still require separate exposure records.

**Original-text evidence index**

- **S02**: chunk `ab1b9d90ab0b01de051b4777a46f`, claim `14768a1816b8295a0284097b811d`, Character span `[196, 274)`; Source `https://00000588c8c6.registry.invalid/operative-record`.
  > - Entity Veloria-00000588; revision R3; file review interval: 21 working days.
- **S03**: chunk `ab1b9d90ab0b01de051b4777a46f`, claim `8e8195df098962b07d963135b054`, Character span `[276, 361)`; Source `https://00000588c8c6.registry.invalid/operative-record`.
  > - Entity Veloria-00000588; revision R3; archival retention period: 180 calendar days.
- **S04**: chunk `ab1b9d90ab0b01de051b4777a46f`, claim `e0da589aaf70f8093e520ee9ed76`, Character span `[363, 442)`; Source `https://00000588c8c6.registry.invalid/operative-record`.
  > - Entity Veloria-00000588; revision R3; release authorization code: Permit-R12.
- **S05**: chunk `ab1b9d90ab0b01de051b4777a46f`, claim `a8e1da1ada2be6a4289baeafe6fe`, Character span `[444, 510)`; Source `https://00000588c8c6.registry.invalid/operative-record`.
  > - Entity Veloria-00000588; revision R3; service route: Juniper-44.
- **S06**: chunk `6bcae5f4f9c4094fb988bb446790`, claim `868fb843d53cef9602eaa5ece391`, Character span `[199, 276)`; Source `https://00000588c8c6.consortium.invalid/disputed`.
  > - Entity Veloria-00000588; revision R3; file review interval: 3 working days.
- **S07**: chunk `c05462e99d40007697968ec6493d`, claim `518e90ca44f92b6df7f0c04c4152`, Character span `[199, 276)`; Source `https://00000588c8c6.registry.invalid/archive`.
  > - Entity Veloria-00000588; revision R2; file review interval: 3 working days.
- **S01**: chunk `f7597bfaa2abb057c7f912f06877`, claim `32a84ff89f72fb404ea3d83d7e22`, Character span `[865, 949)`; Source `https://00000588c8c6.registry.invalid/annex-0`.
  > - Entity Veloria-00000588-Annex; revision R3; file review interval: 21 working days.
- **S08**: chunk `329c9305ccd0bac64312827b0a77`, claim `fced7737c078abc650d31f0fc35b`, Character span `[205, 296)`; Source `https://00000588c8c6.registry.invalid/annex-1`.
  > - Entity Veloria-00000588-Annex; revision R3; archival retention period: 180 calendar days.
- **S09**: chunk `225871171d2e05b57b9e24552e3c`, claim `c4ea7f9f7b1c81b2535287cb53f1`, Character span `[872, 957)`; Source `https://00000588c8c6.registry.invalid/annex-2`.
  > - Entity Veloria-00000588-Annex; revision R3; release authorization code: Permit-R12.

## World 46: 3b5b264f59a8257f41238d8b38c4

Question IDs: `8a9044d317c46b355cefa4067ec8`, `7c6ad581505f8347b5f2aa02b883`.

Collection IDs: `78d3482e5bbb09ec7ed3a7d775dc`, `a607b31f7b3b3e20edc2caa7dea1`.

Entity: Veloria-3B5B264F; Rendering: list; Support structure: temporal_conflict; Required fact count: 4; Overall judgment: **pass**.

Required facts: retention_days = 180 calendar days; review_days = 5 working days; release_code = Permit-K33; route = Aster-44.

**D1 Consistency of required facts with the original text: pass**

The four R8 values 180 calendar days, 5 working days, Permit-K33, and Aster-44 are supported by S11/S15/S13/S12, respectively; Annex entries concern a different entity.

Evidence: S11, S12, S13, S15, S09, S10, S14.

**D2 Complete assertions, complementary support, and alternative support: pass**

All four valid sentences fully bind Veloria-3B5B264F and R8; four-field coverage requires their combination. The four incorrect values in the current disputed chunk cannot count as a complete correct answer.

Evidence: S11, S12, S13, S15.

**D3 Temporal and revision status: pass**

S01–S04 give 90 days/14 days/Permit-R84/Cobalt-37 under R7 and are obsolete; S05–S08 bind those old values to R8 and are all current contradictions.

Evidence: S01, S02, S03, S04, S05, S06, S07, S08.

**D4 Source policy: pass**

The unrestricted policy permits the incorrect consortium chunk; source compliance cannot replace field-by-field content checks, and the question provides no allowlist.

Evidence: S05, S06, S07, S08.

**Findings for this world**

- Four current errors coexist with four valid supports; complete coverage does not establish that the generator has resolved the contradictions.

**Original-text evidence index**

- **S11**: chunk `95184eb9a7751a53d6aab950c47c`, claim `ae21c5c813bd41164f71b08996bf`, Character span `[908, 993)`; Source `https://3b5b264f59a8.registry.invalid/operative-record`.
  > - Entity Veloria-3B5B264F; revision R8; archival retention period: 180 calendar days.
- **S12**: chunk `a20aef79eb2295a58159e004ebfe`, claim `13e7f529e703cf00c3916e51320c`, Character span `[862, 926)`; Source `https://3b5b264f59a8.registry.invalid/operative-record`.
  > - Entity Veloria-3B5B264F; revision R8; service route: Aster-44.
- **S13**: chunk `c2e683fc76b703a782eefe2f1f27`, claim `7d8ad54edaebb8f0e61ad7a9120c`, Character span `[889, 968)`; Source `https://3b5b264f59a8.registry.invalid/operative-record`.
  > - Entity Veloria-3B5B264F; revision R8; release authorization code: Permit-K33.
- **S15**: chunk `9ee94600c216a0ed621f4075cc55`, claim `4335f0505b666843e0a3d4b929f9`, Character span `[904, 981)`; Source `https://3b5b264f59a8.registry.invalid/operative-record`.
  > - Entity Veloria-3B5B264F; revision R8; file review interval: 5 working days.
- **S09**: chunk `c06d0496843b662559b6401b6535`, claim `a07bdb023cbe3050ffbf3fbc4d82`, Character span `[697, 780)`; Source `https://3b5b264f59a8.registry.invalid/annex-1`.
  > - Entity Veloria-3B5B264F-Annex; revision R8; file review interval: 5 working days.
- **S10**: chunk `4048c9ef702f38f3ece00abd060b`, claim `15aa6740ef42091fd7f5c509b519`, Character span `[597, 688)`; Source `https://3b5b264f59a8.registry.invalid/annex-0`.
  > - Entity Veloria-3B5B264F-Annex; revision R8; archival retention period: 180 calendar days.
- **S14**: chunk `5811fd3d7616d021930d44b9b5b6`, claim `50b86f18a36d13e99273f5fe0967`, Character span `[594, 679)`; Source `https://3b5b264f59a8.registry.invalid/annex-2`.
  > - Entity Veloria-3B5B264F-Annex; revision R8; release authorization code: Permit-K33.
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

The two R6 values 180 calendar days and Permit-V11 are supported by S01/S05; identical retention periods or authorization codes in Annex do not refer to the target entity.

Evidence: S01, S02, S03, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The two complete cross-URL prose sentences are complementary, each including the entity, R6, attribute, and value; obtaining only the retention-period page still leaves the code missing.

Evidence: S01, S05.

**D3 Temporal and revision status: pass**

R5/30 days in S04 is obsolete, whereas R6/30 days in S06 is a current contradiction; R6/180 days applies on 2035-06-01.

Evidence: S01, S04, S06.

**D4 Source policy: pass**

There is no host allowlist, so S06 on consortium is source-allowed but incorrect; operative-part-1 can also legitimately contribute the authorization code.

Evidence: S05, S06.

**Findings for this world**

- Correct cross-page support can occur on a nondesignated page; page labels do not identify the location of factual support.

**Original-text evidence index**

- **S01**: chunk `4ac66af6312a8b9ff69553175df3`, claim `8f24c2e1310ccf27be27c6a266c9`, Character span `[1941, 2036)`; Source `https://a5fa36c53056.registry.invalid/operative-record`.
  > For entity Veloria-A5FA36C5 in revision R6, the archival retention period is 180 calendar days.
- **S02**: chunk `f766e091bce4f80b9385a5602300`, claim `ce11b534dc09140805f0edace222`, Character span `[582, 677)`; Source `https://a5fa36c53056.registry.invalid/annex-1`.
  > For entity Veloria-A5FA36C5-Annex in revision R6, the release authorization code is Permit-V11.
- **S03**: chunk `628dee61d0fa91e153168b0561d8`, claim `cb2004bb0e0e39cdf9990ccbdfe9`, Character span `[773, 874)`; Source `https://a5fa36c53056.registry.invalid/annex-0`.
  > For entity Veloria-A5FA36C5-Annex in revision R6, the archival retention period is 180 calendar days.
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

R6 requires Willow-37, 5 working days, and Permit-M14; S06–S08 explicitly state current values for the same subject. Identical Annex values are irrelevant.

Evidence: S06, S07, S08, S05, S09, S11.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three-chunk path and complete independent-current chunk are alternatives; S02–S04 are also complete and correct, but content validity must be distinguished from source compliance.

Evidence: S02, S03, S04, S06, S07, S08.

**D3 Temporal and revision status: pass**

R5/Cobalt-44 in S01 is obsolete, whereas R6/Cobalt-44 in S10 is a current contradiction; the R6 route should be Willow-37.

Evidence: S01, S06, S10.

**D4 Source policy: pass**

Only 3a37b73d1aa4.registry.invalid is allowed; S02–S04 on consortium.complete-current are correct and complete but prohibited for admissible support. S10 is noncompliant too.

Evidence: S02, S03, S04, S10.

**Findings for this world**

- An independent complete alternative remains on the allowed host; a complete chunk from a disallowed source cannot be an equally compliant substitute.

**Original-text evidence index**

- **S06**: chunk `9924fbce09f9bcb5b422437095b8`, claim `c98525c08623a7a6f2c5c04097fb`, Character span `[393, 468)`; Source `https://3a37b73d1aa4.registry.invalid/independent-current`.
  > For entity Veloria-3A37B73D in revision R6, the service route is Willow-37.
- **S07**: chunk `9924fbce09f9bcb5b422437095b8`, claim `6bbf4ba33e0060741a6f5f91eae5`, Character span `[470, 557)`; Source `https://3a37b73d1aa4.registry.invalid/independent-current`.
  > For entity Veloria-3A37B73D in revision R6, the file review interval is 5 working days.
- **S08**: chunk `9924fbce09f9bcb5b422437095b8`, claim `441623f55bf19ec4d38dff7591bc`, Character span `[559, 648)`; Source `https://3a37b73d1aa4.registry.invalid/independent-current`.
  > For entity Veloria-3A37B73D in revision R6, the release authorization code is Permit-M14.
- **S05**: chunk `b8c36e21347a8b1e537e8ad51a7f`, claim `fb9c837efc94ae618833ea510c3e`, Character span `[415, 510)`; Source `https://3a37b73d1aa4.registry.invalid/annex-2`.
  > For entity Veloria-3A37B73D-Annex in revision R6, the release authorization code is Permit-M14.
- **S09**: chunk `b613481eaf9450c496086a1fde50`, claim `d5f097d8e2c421541f571ecae7f8`, Character span `[496, 577)`; Source `https://3a37b73d1aa4.registry.invalid/annex-0`.
  > For entity Veloria-3A37B73D-Annex in revision R6, the service route is Willow-37.
- **S11**: chunk `5a8e2bdb4414c72b22d5dc5af296`, claim `313bb38c6a676c0b671b0c3396b1`, Character span `[765, 858)`; Source `https://3a37b73d1aa4.registry.invalid/annex-1`.
  > For entity Veloria-3A37B73D-Annex in revision R6, the file review interval is 5 working days.
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

The R6 values Cobalt-71, 11 working days, and 30 calendar days occur in S08/S03/S05, matching the requested fields and values; Annex refers to another entity.

Evidence: S03, S05, S08, S04, S06, S07.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three late prose assertions in the position scenario fully bind the subject and R6; completeness of the reviewed annotations does not imply complete delivery within the budget.

Evidence: S03, S05, S08.

**D3 Temporal and revision status: pass**

R5/Cobalt-17 in S02 is obsolete, whereas R6/Cobalt-17 in S01 is a current contradiction; the two occurrences of the old value cannot replace the current route Cobalt-71.

Evidence: S01, S02, S08.

**D4 Source policy: pass**

Under unrestricted sources, S01 on consortium is admissible; its error comes from a current route contradiction rather than a host prohibition in the question.

Evidence: S01.

**Findings for this world**

- The obsolete and current contradictory texts differ only in revision; retaining the complete revision binding is necessary to distinguish them.

**Original-text evidence index**

- **S03**: chunk `f41011b25db35c2f1dddbb359a4c`, claim `a2666b25434ccec931ba3f37eebc`, Character span `[4577, 4665)`; Source `https://1c6479724d60.registry.invalid/operative-record`.
  > For entity Veloria-1C647972 in revision R6, the file review interval is 11 working days.
- **S05**: chunk `919e24b92afb3e9f587c4a13ef30`, claim `8cf77baccfb5263b3584cd99421f`, Character span `[4615, 4709)`; Source `https://1c6479724d60.registry.invalid/operative-record`.
  > For entity Veloria-1C647972 in revision R6, the archival retention period is 30 calendar days.
- **S08**: chunk `b18b2d4a697552275075efc04354`, claim `a3079cd7e597edae6aba2126e696`, Character span `[4650, 4725)`; Source `https://1c6479724d60.registry.invalid/operative-record`.
  > For entity Veloria-1C647972 in revision R6, the service route is Cobalt-71.
- **S04**: chunk `85af8d72c8ba8ccf80cf095812bb`, claim `26a9972bdbe6cf7b0b94a4499733`, Character span `[599, 693)`; Source `https://1c6479724d60.registry.invalid/annex-1`.
  > For entity Veloria-1C647972-Annex in revision R6, the file review interval is 11 working days.
- **S06**: chunk `eeb47025eaeac66b305edda989a6`, claim `310fee3f5e4685c7545ac4ddc0b3`, Character span `[618, 699)`; Source `https://1c6479724d60.registry.invalid/annex-0`.
  > For entity Veloria-1C647972-Annex in revision R6, the service route is Cobalt-71.
- **S07**: chunk `864a48cb922b49ac65d521af7da1`, claim `ab5822918d5f213c90bf1b3f24f8`, Character span `[202, 302)`; Source `https://1c6479724d60.registry.invalid/annex-2`.
  > For entity Veloria-1C647972-Annex in revision R6, the archival retention period is 30 calendar days.
- **S01**: chunk `59f87883ed6733c8ed7ab4374d18`, claim `64b9606ae1e4d31b01e148c6ff68`, Character span `[4704, 4779)`; Source `https://1c6479724d60.consortium.invalid/disputed`.
  > For entity Veloria-1C647972 in revision R6, the service route is Cobalt-17.
- **S02**: chunk `a8692fa61e45e35e8d951a296638`, claim `4e25c47ded129e1f5e409557cbe5`, Character span `[4598, 4673)`; Source `https://1c6479724d60.registry.invalid/archive`.
  > For entity Veloria-1C647972 in revision R5, the service route is Cobalt-17.

## World 50: fb48bf3b55218711963fa24177f0

Question IDs: `26cebe977f967d5f35d38c6a9bda`, `7064e8f2ab08956f5f6910d6c99e`.

Collection IDs: `07561d57709e4c57e797a5c57cea`, `83c44861df37306495949440a2b6`.

Entity: Veloria-FB48BF3B; Rendering: prose; Support structure: same_url_complementary; Required fact count: 3; Overall judgment: **pass**.

Required facts: route = Aster-50; release_code = Permit-K67; retention_days = 120 calendar days.

**D1 Consistency of required facts with the original text: pass**

R9 requires Aster-50, Permit-K67, and 120 calendar days; S02/S06/S01 match completely. The three identical Annex values concern an irrelevant subject.

Evidence: S01, S02, S06, S03, S05, S07.

**D2 Complete assertions, complementary support, and alternative support: pass**

Three complete statements in same-URL chunks form a complementary set; route replicas cannot replace the authorization code and retention period. Every span includes the entity and R9.

Evidence: S01, S02, S06.

**D3 Temporal and revision status: pass**

R8/Juniper-70 in S04 is obsolete, whereas R9/Juniper-70 in S08 is a current contradiction; R9/Aster-50 applies in June 2035.

Evidence: S02, S04, S08.

**D4 Source policy: pass**

The allowlist is fb48bf3b5521.registry.invalid, making S08 on consortium noncompliant; the old archive on an allowed host still requires separate temporal exclusion.

Evidence: S04, S08.

**Findings for this world**

- Three same-source complementary facts interact with source constraints; the assessment cannot be reduced to a page hit.

**Original-text evidence index**

- **S01**: chunk `66f841b27064214d0e8a40242a5a`, claim `c7b1b44a3d1c07a6c852cba75fb6`, Character span `[1269, 1364)`; Source `https://fb48bf3b5521.registry.invalid/operative-record`.
  > For entity Veloria-FB48BF3B in revision R9, the archival retention period is 120 calendar days.
- **S02**: chunk `21599bd4076bc5aa56c7313b022f`, claim `545a4136f8872a6b9251aa9ed1cf`, Character span `[1183, 1257)`; Source `https://fb48bf3b5521.registry.invalid/replica-3`.
  > For entity Veloria-FB48BF3B in revision R9, the service route is Aster-50.
- **S06**: chunk `5f07f351703a3ca0ed8d2a44c09d`, claim `1df631eb185c26043a160f334a20`, Character span `[1141, 1230)`; Source `https://fb48bf3b5521.registry.invalid/operative-record`.
  > For entity Veloria-FB48BF3B in revision R9, the release authorization code is Permit-K67.
- **S03**: chunk `8017efb02cb7c9f8f90df557ea27`, claim `c6601c2b20405098db78176196aa`, Character span `[294, 389)`; Source `https://fb48bf3b5521.registry.invalid/annex-1`.
  > For entity Veloria-FB48BF3B-Annex in revision R9, the release authorization code is Permit-K67.
- **S05**: chunk `6737da48dd97a794927db000d0f1`, claim `5438cfe39e1e434180ffc9e046aa`, Character span `[395, 496)`; Source `https://fb48bf3b5521.registry.invalid/annex-2`.
  > For entity Veloria-FB48BF3B-Annex in revision R9, the archival retention period is 120 calendar days.
- **S07**: chunk `def51704634333cbeb6db1f4c69a`, claim `2242737d1623185be8e8704e0f32`, Character span `[419, 499)`; Source `https://fb48bf3b5521.registry.invalid/annex-0`.
  > For entity Veloria-FB48BF3B-Annex in revision R9, the service route is Aster-50.
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

The requested R7 values 120 calendar days, 21 working days, and Permit-M15 are stated individually in S06–S08; identical Annex values still do not concern the target entity.

Evidence: S06, S07, S08, S01, S02, S03.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three complete prose assertions share one chunk, each binding Veloria-738FC4BB, R7, and the attribute; no information from an external subject is needed.

Evidence: S06, S07, S08.

**D3 Temporal and revision status: pass**

R6/60 days in S05 is obsolete, whereas R7/60 days in S04 is a current contradiction; the valid current retention period is 120 days in S06.

Evidence: S04, S05, S06.

**D4 Source policy: pass**

There is no source-prefix restriction, so S04 on consortium is legitimately admissible but factually contradictory; an allowed Annex source also cannot receive target-entity coverage credit.

Evidence: S01, S02, S03, S04.

**Findings for this world**

- Complete three-field support in one chunk can coexist with additional incorrect current assertions.

**Original-text evidence index**

- **S06**: chunk `1adec50fa0c5fc25ff401dc38b35`, claim `0627c8125cd89d9ce048f0f1a03b`, Character span `[288, 383)`; Source `https://738fc4bbde90.registry.invalid/operative-record`.
  > For entity Veloria-738FC4BB in revision R7, the archival retention period is 120 calendar days.
- **S07**: chunk `1adec50fa0c5fc25ff401dc38b35`, claim `7c31fa3c1269af9672da235bbebe`, Character span `[385, 473)`; Source `https://738fc4bbde90.registry.invalid/operative-record`.
  > For entity Veloria-738FC4BB in revision R7, the file review interval is 21 working days.
- **S08**: chunk `1adec50fa0c5fc25ff401dc38b35`, claim `37d8cc799b56bf4e514b7d7fcc94`, Character span `[475, 564)`; Source `https://738fc4bbde90.registry.invalid/operative-record`.
  > For entity Veloria-738FC4BB in revision R7, the release authorization code is Permit-M15.
- **S01**: chunk `70e5c6ffca169a52910911b17d87`, claim `4c67ea2997419d7ea828fb9a78f3`, Character span `[427, 528)`; Source `https://738fc4bbde90.registry.invalid/annex-0`.
  > For entity Veloria-738FC4BB-Annex in revision R7, the archival retention period is 120 calendar days.
- **S02**: chunk `a4e92b7c8f561e34261458d51bb5`, claim `696e214e2f0d3c742042474089fc`, Character span `[697, 791)`; Source `https://738fc4bbde90.registry.invalid/annex-1`.
  > For entity Veloria-738FC4BB-Annex in revision R7, the file review interval is 21 working days.
- **S03**: chunk `04c3c08edec7e81ce55543c8fe6c`, claim `7e110409197b55edac8324439a64`, Character span `[594, 689)`; Source `https://738fc4bbde90.registry.invalid/annex-2`.
  > For entity Veloria-738FC4BB-Annex in revision R7, the release authorization code is Permit-M15.
- **S04**: chunk `3aa6c686bb428d912672b2338398`, claim `8ed2e34247e7f3c87609fcb234af`, Character span `[288, 382)`; Source `https://738fc4bbde90.consortium.invalid/disputed`.
  > For entity Veloria-738FC4BB in revision R7, the archival retention period is 60 calendar days.
- **S05**: chunk `d59326c376e5d5c6b0a0e57d2631`, claim `fb490d0ad0b37503d841d68cb5bc`, Character span `[393, 487)`; Source `https://738fc4bbde90.registry.invalid/archive`.
  > For entity Veloria-738FC4BB in revision R6, the archival retention period is 60 calendar days.

## World 52: e3e6cf4c37189bf7f3570cee10a0

Question IDs: `24d69718de96b8820b05f9852e6a`, `00b107a2ea9ff42c8fedb2d74492`.

Collection IDs: `7f5b3ea6dd54952d91ec5f6f05e4`, `eb9f53859a91b4955da588dae80b`.

Entity: Veloria-E3E6CF4C; Rendering: prose; Support structure: temporal_conflict; Required fact count: 3; Overall judgment: **pass**.

Required facts: release_code = Permit-K72; review_days = 3 working days; retention_days = 60 calendar days.

**D1 Consistency of required facts with the original text: pass**

R3 requires Permit-K72, 3 working days, and 60 calendar days, fully matched by S01/S10/S06; identical Annex values do not concern the target entity.

Evidence: S01, S06, S10, S05, S11, S12.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three valid sentences each fully contain subject, R3, attribute, and value; the three incorrect values together in S02–S04 cannot count as complete valid support.

Evidence: S01, S06, S10, S02, S03, S04.

**D3 Temporal and revision status: pass**

The R2 values Permit-R19/11 days/90 days in S07–S09 are obsolete; those old values under R3 in S02–S04 are current contradictions. The revision distinction is appropriate.

Evidence: S02, S03, S04, S07, S08, S09.

**D4 Source policy: pass**

Only e3e6cf4c3718.registry.invalid is allowed, excluding S02–S04 on consortium; archive remains on an allowed host but does not satisfy the current R3 requirement.

Evidence: S02, S03, S04, S07, S08, S09.

**Findings for this world**

- Source restrictions can block the current disputed text, but obsolete documents still require exclusion using revision conditions.

**Original-text evidence index**

- **S01**: chunk `34d5a92f212b9bf4d286c9faccfc`, claim `e51b657329ffd165e717356d4cd2`, Character span `[520, 609)`; Source `https://e3e6cf4c3718.registry.invalid/replica-4`.
  > For entity Veloria-E3E6CF4C in revision R3, the release authorization code is Permit-K72.
- **S06**: chunk `a6da54f6a8bbb2a0b873bbf8d5a4`, claim `987e5019a5c0b6ced8f97090db94`, Character span `[498, 592)`; Source `https://e3e6cf4c3718.registry.invalid/operative-record`.
  > For entity Veloria-E3E6CF4C in revision R3, the archival retention period is 60 calendar days.
- **S10**: chunk `8fc6499c2e877fe06d1ab5a29909`, claim `86f5ba1b30325bd5f1d670829eaf`, Character span `[595, 682)`; Source `https://e3e6cf4c3718.registry.invalid/operative-record`.
  > For entity Veloria-E3E6CF4C in revision R3, the file review interval is 3 working days.
- **S05**: chunk `2966db86282c9ded5695fdbb83cd`, claim `de8695dcc13ca783fb9ef89914f6`, Character span `[486, 586)`; Source `https://e3e6cf4c3718.registry.invalid/annex-2`.
  > For entity Veloria-E3E6CF4C-Annex in revision R3, the archival retention period is 60 calendar days.
- **S11**: chunk `74e7c09205700b9975966f1fddc6`, claim `a3730c7c3f6e6ee37773be067376`, Character span `[507, 600)`; Source `https://e3e6cf4c3718.registry.invalid/annex-1`.
  > For entity Veloria-E3E6CF4C-Annex in revision R3, the file review interval is 3 working days.
- **S12**: chunk `565bf13c46cf1e6f3ebfa4a1271e`, claim `ad1fe84ad54218b943e3a97f31b1`, Character span `[794, 889)`; Source `https://e3e6cf4c3718.registry.invalid/annex-0`.
  > For entity Veloria-E3E6CF4C-Annex in revision R3, the release authorization code is Permit-K72.
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

The two R3 values Aster-79 and 120 calendar days are supported by the target-entity QA pairs S02/S03, respectively; Annex questions do not ask about the target entity.

Evidence: S01, S02, S03, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The complete Q+A pairs on two URLs jointly provide support: the questions supply entity/revision/attribute and the answers supply values. 120 days alone is not a complete assertion.

Evidence: S02, S03.

**D3 Temporal and revision status: pass**

R2/Aster-54 in S04 is obsolete, whereas R3/Aster-54 in S06 is a current contradiction; the valid R3 route is Aster-79 in S02.

Evidence: S02, S04, S06.

**D4 Source policy: pass**

Sources are restricted to b3ed6ba20862.registry.invalid, excluding S06 on consortium; S03 on operative-part-1 remains within the allowed scope despite not being the designated page.

Evidence: S03, S06.

**Findings for this world**

- Cross-page complementary QA support cannot be replaced by single-page retention or isolated answer values.

**Original-text evidence index**

- **S01**: chunk `20fd70f88426c684798310d2ba05`, claim `f7261ab3ff40e5ee46dc178f989d`, Character span `[896, 1012)`; Source `https://b3ed6ba20862.registry.invalid/annex-1`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-B3ED6BA2-Annex? A: 120 calendar days.
- **S02**: chunk `02723a366adc7280ae4de3087365`, claim `168db72e09994a3c7955e18a37b0`, Character span `[1566, 1655)`; Source `https://b3ed6ba20862.registry.invalid/operative-record`.
  > Q: Under revision R3, what is the service route for entity Veloria-B3ED6BA2? A: Aster-79.
- **S03**: chunk `05e6a8d49ede66c5838db798498d`, claim `ac3360965cd009218af1cf198c6c`, Character span `[1575, 1685)`; Source `https://b3ed6ba20862.registry.invalid/operative-part-1`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-B3ED6BA2? A: 120 calendar days.
- **S05**: chunk `8610ec54f9dcb07e5441f65ee2db`, claim `aa11b4817d4cf8e875f29f9f383e`, Character span `[384, 479)`; Source `https://b3ed6ba20862.registry.invalid/annex-2`.
  > Q: Under revision R3, what is the service route for entity Veloria-B3ED6BA2-Annex? A: Aster-79.
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

The R3 question asks for 60 calendar days and 21 working days; S01/S05 provide complete QA pairs. Identical Annex values do not concern Veloria-30682341.

Evidence: S01, S03, S05, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

Both distributed QA and the complete alternative chunk support both facts; S05 coming from consortium.complete-current does not affect its complete semantics, and the unrestricted policy permits its use.

Evidence: S01, S05.

**D3 Temporal and revision status: pass**

R2/180 days in S04 is obsolete, whereas R3/180 days in S02 is a current contradiction; the current R3 retention period is 60 days.

Evidence: S01, S02, S04.

**D4 Source policy: pass**

There is no allowlist, so both correct complete-current S05 and incorrect disputed S02 on consortium are source-allowed; their content truth must still be judged separately.

Evidence: S02, S05.

**Findings for this world**

- One consortium host can carry both correct and incorrect text; domain alone determines neither semantics nor permission.

**Original-text evidence index**

- **S01**: chunk `6cc956e0ed2d3b68b17c23dd58a2`, claim `366d44e4654034afd6d7ff8ea3b1`, Character span `[858, 967)`; Source `https://30682341dec9.registry.invalid/replica-2`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-30682341? A: 60 calendar days.
- **S03**: chunk `879022280c26c523356bd77e8ee3`, claim `47f59a0e97b39c8ff4c7e1e2798b`, Character span `[883, 998)`; Source `https://30682341dec9.registry.invalid/annex-0`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-30682341-Annex? A: 60 calendar days.
- **S05**: chunk `c82187693dd6f7d6698f156b88c4`, claim `6ccfdeed7d1fd8b5c117d8d6c80d`, Character span `[993, 1096)`; Source `https://30682341dec9.consortium.invalid/complete-current`.
  > Q: Under revision R3, what is the file review interval for entity Veloria-30682341? A: 21 working days.
- **S06**: chunk `57ead45a3dd93eaadd9b22e9f250`, claim `7b517cfdc26b59efcd7795ab2729`, Character span `[412, 521)`; Source `https://30682341dec9.registry.invalid/annex-1`.
  > Q: Under revision R3, what is the file review interval for entity Veloria-30682341-Annex? A: 21 working days.
- **S02**: chunk `f1c692ce340691f9286efc5a0a52`, claim `80c4cbabf5198e22fd0ac7d0eacd`, Character span `[909, 1019)`; Source `https://30682341dec9.consortium.invalid/disputed`.
  > Q: Under revision R3, what is the archival retention period for entity Veloria-30682341? A: 180 calendar days.
- **S04**: chunk `d79ea3cdb4bf6851423e6d3e0e84`, claim `8ed14bf594ef60c103ed9033fb4f`, Character span `[920, 1030)`; Source `https://30682341dec9.registry.invalid/archive`.
  > Q: Under revision R2, what is the archival retention period for entity Veloria-30682341? A: 180 calendar days.

## World 55: f799a1d7497389521e6d74147f46

Question IDs: `919b10a0809749099b8008609af8`, `2996bd482f91b06101c9ebc25f54`.

Collection IDs: `7c250eb9f65ab02850c1d12cbba9`, `573c8c7adfecf4b75a0de2b00a58`.

Entity: Veloria-F799A1D7; Rendering: qa; Support structure: position; Required fact count: 2; Overall judgment: **pass**.

Required facts: route = Willow-81; release_code = Permit-K32.

**D1 Consistency of required facts with the original text: pass**

The R4 question requests Willow-81 and Permit-K32, corresponding to the Q+A pairs S02/S05; identical Annex values cannot count as target-entity facts.

Evidence: S01, S02, S05, S06.

**D2 Complete assertions, complementary support, and alternative support: pass**

Both QA annotations in the position scenario include complete questions and answers, retaining subject, R4, and attribute; a late value's occurrence alone does not establish assertion completeness.

Evidence: S02, S05.

**D3 Temporal and revision status: pass**

R3/Willow-33 in S04 is obsolete, whereas R4/Willow-33 in S03 is a current contradiction; the current R4 route should be Willow-81.

Evidence: S02, S03, S04.

**D4 Source policy: pass**

Only f799a1d74973.registry.invalid is allowed, excluding S03 on consortium; Annex on registry still fails to support the target entity because of its wrong subject.

Evidence: S01, S03, S06.

**Findings for this world**

- The current correct route and authorization code still require complete delivery; an obsolete route from a disallowed source cannot substitute for them.

**Original-text evidence index**

- **S01**: chunk `eb719171d3e7c1d3708686d2a08f`, claim `0f54ff4c2e13dc1ce1396afa3bbf`, Character span `[205, 301)`; Source `https://f799a1d74973.registry.invalid/annex-2`.
  > Q: Under revision R4, what is the service route for entity Veloria-F799A1D7-Annex? A: Willow-81.
- **S02**: chunk `f24a769cf8af8037e34caa96e74d`, claim `00153e562aedc22c8088a344293b`, Character span `[3251, 3341)`; Source `https://f799a1d74973.registry.invalid/replica-1`.
  > Q: Under revision R4, what is the service route for entity Veloria-F799A1D7? A: Willow-81.
- **S05**: chunk `127424d12d8232e45c016ec6f7a1`, claim `c7f8170b520f843c2caa1191c8f3`, Character span `[3434, 3538)`; Source `https://f799a1d74973.registry.invalid/operative-record`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-F799A1D7? A: Permit-K32.
- **S06**: chunk `52c71ad15731e8ef2718d77019c8`, claim `8e9d320de02e7e56fc4a2d635a75`, Character span `[504, 614)`; Source `https://f799a1d74973.registry.invalid/annex-1`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-F799A1D7-Annex? A: Permit-K32.
- **S03**: chunk `73824dc7bdbbb49eba8811ac7060`, claim `bb51689d62d01d7415c52241249a`, Character span `[3367, 3457)`; Source `https://f799a1d74973.consortium.invalid/disputed`.
  > Q: Under revision R4, what is the service route for entity Veloria-F799A1D7? A: Willow-33.
- **S04**: chunk `8e06c81a72c5b074f33f47d2666d`, claim `941227d6ac4ffecc399ec81389aa`, Character span `[3270, 3360)`; Source `https://f799a1d74973.registry.invalid/archive`.
  > Q: Under revision R3, what is the service route for entity Veloria-F799A1D7? A: Willow-33.

## World 56: b3dd9bd88d26ac26e8350e3a40fe

Question IDs: `b2685c7cc6aa4eddf8255906caac`, `5876feebb42414b437d2eadb3418`.

Collection IDs: `a82f5b663af95480f9f3810557a2`, `30f9ec1207adf03d0aa850576acc`.

Entity: Veloria-B3DD9BD8; Rendering: qa; Support structure: same_url_complementary; Required fact count: 4; Overall judgment: **pass**.

Required facts: route = Willow-18; retention_days = 60 calendar days; release_code = Permit-V30; review_days = 11 working days.

**D1 Consistency of required facts with the original text: pass**

The four R5 fields Willow-18, 60 calendar days, Permit-V30, and 11 working days are answered individually by S04/S05/S08/S01; Annex refers to a different subject.

Evidence: S01, S04, S05, S08, S02, S06, S09.

**D2 Complete assertions, complementary support, and alternative support: pass**

The four same-URL QA chunks are complementary, with each annotation retaining the subject/R5/attribute in the question and value in the answer; route replicas cannot supply the other three fields.

Evidence: S01, S04, S05, S08.

**D3 Temporal and revision status: pass**

R4/Juniper-53 in S07 is obsolete; S03 gives Juniper-53 under R5 and is a current contradiction. The valid R5 route is Willow-18.

Evidence: S03, S04, S07.

**D4 Source policy: pass**

The question leaves sources unrestricted, so S03 on consortium is source-allowed but incorrect; the designated operative-record is not the only URL for all legitimate text.

Evidence: S03, S04.

**Findings for this world**

- Same-source chunks share a source identity but are not interchangeable in their factual contributions.

**Original-text evidence index**

- **S01**: chunk `d61b5743e51880633c70db2a9382`, claim `3913ae5c70ff26c6c128905ee9c4`, Character span `[906, 1009)`; Source `https://b3dd9bd88d26.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the file review interval for entity Veloria-B3DD9BD8? A: 11 working days.
- **S04**: chunk `e7b4ad0965979c88ba71feb1af47`, claim `dc0c1e11e93562abfe1295c6dc56`, Character span `[873, 963)`; Source `https://b3dd9bd88d26.registry.invalid/replica-11`.
  > Q: Under revision R5, what is the service route for entity Veloria-B3DD9BD8? A: Willow-18.
- **S05**: chunk `07dd8c81a152748442377defe570`, claim `6bacb19e6271b9273e309fd339ec`, Character span `[829, 938)`; Source `https://b3dd9bd88d26.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the archival retention period for entity Veloria-B3DD9BD8? A: 60 calendar days.
- **S08**: chunk `28f3b4d1dc53aa89ea8cc690077e`, claim `bad0b49f4140f324b7c0f1b83fd6`, Character span `[840, 944)`; Source `https://b3dd9bd88d26.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-B3DD9BD8? A: Permit-V30.
- **S02**: chunk `e95ad70840191e66a63eb8d17a1b`, claim `deccbcee0cc48a726a2ef94a6cb0`, Character span `[392, 488)`; Source `https://b3dd9bd88d26.registry.invalid/annex-0`.
  > Q: Under revision R5, what is the service route for entity Veloria-B3DD9BD8-Annex? A: Willow-18.
- **S06**: chunk `4eb1d98bd9316ec4cda6847fe361`, claim `4207048ad275b8f3c182d3b9216f`, Character span `[309, 419)`; Source `https://b3dd9bd88d26.registry.invalid/annex-2`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-B3DD9BD8-Annex? A: Permit-V30.
- **S09**: chunk `d67537f3765fdc93a339d8f1c152`, claim `5fe181442011d7ece917c0c9634f`, Character span `[404, 519)`; Source `https://b3dd9bd88d26.registry.invalid/annex-1`.
  > Q: Under revision R5, what is the archival retention period for entity Veloria-B3DD9BD8-Annex? A: 60 calendar days.
- **S03**: chunk `ff3fc5088ef0e91ea9354be6c36c`, claim `00898b5c07aa64c07e0de52cafeb`, Character span `[882, 973)`; Source `https://b3dd9bd88d26.consortium.invalid/disputed`.
  > Q: Under revision R5, what is the service route for entity Veloria-B3DD9BD8? A: Juniper-53.
- **S07**: chunk `04b0c0206aaad602386090ebcd7b`, claim `f12e390c3a091770ad3323de5d86`, Character span `[866, 957)`; Source `https://b3dd9bd88d26.registry.invalid/archive`.
  > Q: Under revision R4, what is the service route for entity Veloria-B3DD9BD8? A: Juniper-53.

## World 57: 975318bd0ee28083ddc732e51a5c

Question IDs: `92630d1f0e27e6057d6dc8b278d2`, `4d188e9d6f64872054f2314b7738`.

Collection IDs: `3ece4f33504e25d5f2ae8998ef8c`, `e52ba961b861705c2b954e1d1588`.

Entity: Veloria-975318BD; Rendering: qa; Support structure: single_chunk; Required fact count: 3; Overall judgment: **pass**.

Required facts: retention_days = 90 calendar days; route = Cobalt-13; review_days = 11 working days.

**D1 Consistency of required facts with the original text: pass**

R8 requires 90 calendar days, Cobalt-13, and 11 working days, given by the target-entity QA pairs S06–S08; identical Annex QA values must not be accepted.

Evidence: S06, S07, S08, S01, S02, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The three complete Q+A pairs share one complete chunk, with the subject and R8 in their questions; answer lines alone do not represent complete support.

Evidence: S06, S07, S08.

**D3 Temporal and revision status: pass**

R7/180 days in S03 is obsolete; R8/180 days in S04 is a current contradiction. The valid R8 retention period is 90 days.

Evidence: S03, S04, S06.

**D4 Source policy: pass**

Sources are restricted to 975318bd0ee2.registry.invalid, excluding S04 on consortium; S03 on archive is on an allowed host but does not satisfy the current revision.

Evidence: S03, S04.

**Findings for this world**

- Neither source-compliant old text nor source-noncompliant current incorrect text can replace the three currently valid supports.

**Original-text evidence index**

- **S06**: chunk `bd7a0854e255e23e93d48c07a456`, claim `a9e5699ab4506cbd306a9a3943d3`, Character span `[765, 874)`; Source `https://975318bd0ee2.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the archival retention period for entity Veloria-975318BD? A: 90 calendar days.
- **S07**: chunk `bd7a0854e255e23e93d48c07a456`, claim `87341769177eeea367596842dbef`, Character span `[876, 966)`; Source `https://975318bd0ee2.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the service route for entity Veloria-975318BD? A: Cobalt-13.
- **S08**: chunk `bd7a0854e255e23e93d48c07a456`, claim `63713afae0b8e3cfb7ad3effbef3`, Character span `[968, 1071)`; Source `https://975318bd0ee2.registry.invalid/operative-record`.
  > Q: Under revision R8, what is the file review interval for entity Veloria-975318BD? A: 11 working days.
- **S01**: chunk `e1b01f0a1039a8f98ae213dba9c2`, claim `5872288079d1f11e757d90b20668`, Character span `[506, 621)`; Source `https://975318bd0ee2.registry.invalid/annex-0`.
  > Q: Under revision R8, what is the archival retention period for entity Veloria-975318BD-Annex? A: 90 calendar days.
- **S02**: chunk `9a0c1320243bb280adbb9e289446`, claim `dd0e19808e674d5a7c05b6b88196`, Character span `[593, 689)`; Source `https://975318bd0ee2.registry.invalid/annex-1`.
  > Q: Under revision R8, what is the service route for entity Veloria-975318BD-Annex? A: Cobalt-13.
- **S05**: chunk `e2f94c5dd378897df05ff04b9910`, claim `e879649fbf8a691ac3cb3c743ef8`, Character span `[605, 714)`; Source `https://975318bd0ee2.registry.invalid/annex-2`.
  > Q: Under revision R8, what is the file review interval for entity Veloria-975318BD-Annex? A: 11 working days.
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

The R5 question requires Juniper-53, Permit-K49, and 30 calendar days, supported by the complete QA pairs S01/S09/S08; Annex is not the same subject.

Evidence: S01, S08, S09, S02, S06, S07.

**D2 Complete assertions, complementary support, and alternative support: pass**

Each of the three QA fields requires a complete Q+A pair; the three incorrect current disputed answers do not form complete correct support even within one chunk.

Evidence: S01, S08, S09, S10, S11, S12.

**D3 Temporal and revision status: pass**

R4/Juniper-88/Permit-K10/120 days in S03–S05 belongs to the old revision; the same values under R5 in S10–S12 are current contradictions. All three fields conflict with current truth.

Evidence: S03, S04, S05, S10, S11, S12.

**D4 Source policy: pass**

The unrestricted policy permits S10–S12 on consortium, but all three values are incorrect; allowed sources cannot replace checks of current facts.

Evidence: S10, S11, S12.

**Findings for this world**

- Obsolete and current contradictory statuses must be preserved for each field, rather than assigning only one overall “old document” label.

**Original-text evidence index**

- **S01**: chunk `e0f5c07284e9f92eda71ed582101`, claim `fd9b4f411102a7508caf499e9673`, Character span `[1055, 1146)`; Source `https://ffe9e2f1acff.registry.invalid/replica-2`.
  > Q: Under revision R5, what is the service route for entity Veloria-FFE9E2F1? A: Juniper-53.
- **S08**: chunk `c2158fd8d418cdc815367062703c`, claim `ad8a3d6b803a0076bf0220b59b59`, Character span `[1085, 1194)`; Source `https://ffe9e2f1acff.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the archival retention period for entity Veloria-FFE9E2F1? A: 30 calendar days.
- **S09**: chunk `fabc304e6806e47ddfc5470da6d4`, claim `ccbf2e80a71ec6f68b942f889c5d`, Character span `[1075, 1179)`; Source `https://ffe9e2f1acff.registry.invalid/operative-record`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-FFE9E2F1? A: Permit-K49.
- **S02**: chunk `4fa4927f7fd47c5445c22aee3899`, claim `99ba0fdcf2578cfe69c05929f74b`, Character span `[293, 390)`; Source `https://ffe9e2f1acff.registry.invalid/annex-0`.
  > Q: Under revision R5, what is the service route for entity Veloria-FFE9E2F1-Annex? A: Juniper-53.
- **S06**: chunk `f6fda8d7b4d27290dd8992cc999b`, claim `b9d0296843a126b76d7072c6142f`, Character span `[490, 600)`; Source `https://ffe9e2f1acff.registry.invalid/annex-1`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-FFE9E2F1-Annex? A: Permit-K49.
- **S07**: chunk `0b8bf0c79fdce680e6189e1e4385`, claim `d4c00acd0cd0b332f3cc4c46b70c`, Character span `[202, 317)`; Source `https://ffe9e2f1acff.registry.invalid/annex-2`.
  > Q: Under revision R5, what is the archival retention period for entity Veloria-FFE9E2F1-Annex? A: 30 calendar days.
- **S10**: chunk `e248cbffccc814d1af53b3bb4ec2`, claim `dec5610275b6f3de9eced2d74b0b`, Character span `[1088, 1179)`; Source `https://ffe9e2f1acff.consortium.invalid/disputed`.
  > Q: Under revision R5, what is the service route for entity Veloria-FFE9E2F1? A: Juniper-88.
- **S11**: chunk `e248cbffccc814d1af53b3bb4ec2`, claim `d9ce8a4365bc07e0284002ea751a`, Character span `[1181, 1285)`; Source `https://ffe9e2f1acff.consortium.invalid/disputed`.
  > Q: Under revision R5, what is the release authorization code for entity Veloria-FFE9E2F1? A: Permit-K10.
- **S12**: chunk `e248cbffccc814d1af53b3bb4ec2`, claim `de4ed2363d522b9c7d828841d6dd`, Character span `[1287, 1397)`; Source `https://ffe9e2f1acff.consortium.invalid/disputed`.
  > Q: Under revision R5, what is the archival retention period for entity Veloria-FFE9E2F1? A: 120 calendar days.
- **S03**: chunk `bc361bfe34b83341bda7b2c2b880`, claim `14ecc81bd922e7698cc75bd42c13`, Character span `[989, 1080)`; Source `https://ffe9e2f1acff.registry.invalid/archive`.
  > Q: Under revision R4, what is the service route for entity Veloria-FFE9E2F1? A: Juniper-88.
- **S04**: chunk `bc361bfe34b83341bda7b2c2b880`, claim `fdb32d674a1a41f29112e9e08a8f`, Character span `[1082, 1186)`; Source `https://ffe9e2f1acff.registry.invalid/archive`.
  > Q: Under revision R4, what is the release authorization code for entity Veloria-FFE9E2F1? A: Permit-K10.
- **S05**: chunk `bc361bfe34b83341bda7b2c2b880`, claim `a221cad47a73bff8a4a206a1d180`, Character span `[1188, 1298)`; Source `https://ffe9e2f1acff.registry.invalid/archive`.
  > Q: Under revision R4, what is the archival retention period for entity Veloria-FFE9E2F1? A: 120 calendar days.

## World 59: 16fb086fedbe1e4ea86a1b372dd4

Question IDs: `04b972fffc6093db9d649cdefabb`, `3d62aa03de225c5961da6dad8762`.

Collection IDs: `500fb0a2ab9674dbf26723fb4c3f`, `8800e0e46497bdb57eb461505acc`.

Entity: Veloria-16FB086F; Rendering: list; Support structure: cross_url_complementary; Required fact count: 2; Overall judgment: **pass**.

Required facts: release_code = Permit-V67; route = Willow-53.

**D1 Consistency of required facts with the original text: pass**

The requested R9 values Permit-V67 and Willow-53 are stated in S03/S01, respectively; identical Annex values do not support the target entity.

Evidence: S01, S03, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The two complete cross-URL list sentences jointly satisfy both fields, each including the subject and R9; repeated authorization-code text cannot replace route support.

Evidence: S01, S03.

**D3 Temporal and revision status: pass**

R8/Permit-M51 in S02 is obsolete, whereas R9/Permit-M51 in S06 is a current contradiction; the valid R9 authorization code is Permit-V67.

Evidence: S02, S03, S06.

**D4 Source policy: pass**

Sources are restricted to 16fb086fedbe.registry.invalid, excluding S06 on consortium; S01 on operative-part-1 is allowed and can contribute the route despite not being the designated page.

Evidence: S01, S06.

**Findings for this world**

- Retention of the designated page does not establish retention of a route on another page; the source allowlist is not limited to one page either.

**Original-text evidence index**

- **S01**: chunk `00c8315f37d5ce2207249b903d08`, claim `371c17700396992bfa6c348b58d2`, Character span `[873, 938)`; Source `https://16fb086fedbe.registry.invalid/operative-part-1`.
  > - Entity Veloria-16FB086F; revision R9; service route: Willow-53.
- **S03**: chunk `b0cb0f14e6ca1df80bf416f7a5b2`, claim `4995082a417692c2a231d664cc25`, Character span `[905, 984)`; Source `https://16fb086fedbe.registry.invalid/replica-3`.
  > - Entity Veloria-16FB086F; revision R9; release authorization code: Permit-V67.
- **S04**: chunk `1dcc7fff7e620dac85b60e27a57b`, claim `67a1c98789385ec1e3175c20d2c3`, Character span `[914, 985)`; Source `https://16fb086fedbe.registry.invalid/annex-1`.
  > - Entity Veloria-16FB086F-Annex; revision R9; service route: Willow-53.
- **S05**: chunk `6e43fe032d384d45ad4bc22e2109`, claim `8b2552c6417bbc64250c7918513d`, Character span `[296, 381)`; Source `https://16fb086fedbe.registry.invalid/annex-2`.
  > - Entity Veloria-16FB086F-Annex; revision R9; release authorization code: Permit-V67.
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

The R3 question requires 5 working days and Cobalt-19; S04/S05 match both fields and values. Identical Annex values do not concern the requested entity.

Evidence: S01, S03, S04, S05.

**D2 Complete assertions, complementary support, and alternative support: pass**

The two distributed chunks and complete alternative provide alternative paths; each list sentence contains the entity, R3, predicate, and value. The unrestricted policy permits the complete consortium path.

Evidence: S04, S05.

**D3 Temporal and revision status: pass**

R2/14 working days in S06 is obsolete; R3/14 days in S02 is a current contradiction. The current R3 review interval should be 5 days in S04.

Evidence: S02, S04, S06.

**D4 Source policy: pass**

allowed_url_prefixes is empty; S04/S05 on consortium.complete-current are source-allowed and correct, whereas disputed S02 is also source-allowed but incorrect.

Evidence: S02, S04, S05.

**Findings for this world**

- This final set again shows that domain alone does not determine truth; under unrestricted sources, correct alternatives on different hosts can count toward coverage.

**Original-text evidence index**

- **S01**: chunk `07b4095318866a2b0cb11ac57b7f`, claim `e572f41e28964e47c8f926eaee48`, Character span `[388, 471)`; Source `https://45c1f70280fd.registry.invalid/annex-2`.
  > - Entity Veloria-45C1F702-Annex; revision R3; file review interval: 5 working days.
- **S03**: chunk `512012e4237d02a207f91fd2d272`, claim `2bd4862bedb4846b802ba7d0c8e0`, Character span `[672, 743)`; Source `https://45c1f70280fd.registry.invalid/annex-1`.
  > - Entity Veloria-45C1F702-Annex; revision R3; service route: Cobalt-19.
- **S04**: chunk `4f315baa4b0462c65f9f1f677b34`, claim `ee951c9b2b4fc13d359f9def0a2a`, Character span `[2154, 2231)`; Source `https://45c1f70280fd.consortium.invalid/complete-current`.
  > - Entity Veloria-45C1F702; revision R3; file review interval: 5 working days.
- **S05**: chunk `4f315baa4b0462c65f9f1f677b34`, claim `ec6cca82b7a83d62d08906cda1b9`, Character span `[2233, 2298)`; Source `https://45c1f70280fd.consortium.invalid/complete-current`.
  > - Entity Veloria-45C1F702; revision R3; service route: Cobalt-19.
- **S02**: chunk `7589e0902a822e1d3381e0a75c8e`, claim `d8613ac61d1a2aac4c68f0cb062b`, Character span `[2138, 2216)`; Source `https://45c1f70280fd.consortium.invalid/disputed`.
  > - Entity Veloria-45C1F702; revision R3; file review interval: 14 working days.
- **S06**: chunk `0b4de6b38be1492316c28750992c`, claim `f69743afde43d40be3a9af988389`, Character span `[2210, 2288)`; Source `https://45c1f70280fd.registry.invalid/archive`.
  > - Entity Veloria-45C1F702; revision R2; file review interval: 14 working days.
