# Supplementary Methods S7 — Inter-coder reliability assessment (Cohen's κ)

This supplement documents the blinded re-coding (a second blinded coding pass) used to quantify the
reproducibility of the literature design classification reported in §3.3 of the
main manuscript, and the coding-completeness limitations it revealed.

## S7.1 Sampling design

- **Source corpus.** The authoritative coding table
  `③ 真实数据应用/literature_coding_table_UPDATED.xlsx` (695 primary studies).
- **Stratified random sample.** A sample of **50 studies** was drawn, stratified
  by the three prevalence tiers of Figure 4 in proportions **31 / 100 / 202**
  (conservative / typical / structural), so that the sample mirrors the full
  corpus's risk distribution. Random seed = **2026** (reproducible).
- **Blind coding.** A second blinded coding pass by co-author C. Yan (C.Y.)
  re-judged each study from the **paper text only**, independently of the original
  coding session (the original coder, J.W., was excluded) and blind to the sealed
  answer key, using a codebook (`kappa_codebook_S1_20260903.md`) defining three
  fields:
  1. `design_type` — `两步法MR中介` vs `不属于两步法MR中介-排除`.
  2. `IV_selection_strategy` — `分开选IV` / `MVMR联合估计` / `无法判断`.
  3. `reports_overlap_risk` — `是` / `否`.
- **Sealed answer key.** The original AI coding was held in a sealed file
  (`③ 真实数据应用/temp/_sealed_do_not_open/kappa_answer_key_20260903.csv`, with a
  working copy at `code/kappa/kappa_answer_key_20260903.csv`) and not opened until
  after blind coding was complete. The blind sheet exposed only
  `study_id / pmid / first_author_year / journal / title` (no leaked judgment
  columns); 8 missing full texts were located by PMID / title via the publisher
  or PubMed.
- **Standardization.** Five answer-key entries stored the IV strategy as verbose
  free text (e.g., "drug-target MR + MVMR + two-step mediation MR …"); these were
  mapped to the 3-category scheme before comparison. Blank answer-key entries were
  treated as **missing** and excluded from the corresponding κ (reported
  transparently below).

## S7.2 Cohen's κ results

Cohen's κ = (Po − Pe) / (1 − Pe), where Po is observed agreement and Pe is expected
agreement under marginal independence.

These statistics were computed with `compute_kappa_2nd.py` (in
`code/kappa_chenyan_task/`) from Chen Yan's blind re-code
(`code/kappa_chenyan_task/kappa_second_coder_chenyan_FILLED.csv`) against the
sealed answer key; the full per-field report — including bootstrap 95% confidence
intervals and PABAK (= 2·Po − 1) — is in `code/kappa_chenyan_task/kappa_2nd_report.csv`.

| Field | n (valid pairs) | Blank excluded | Observed agreement Po | Cohen's κ (95% CI) | Interpretation |
|---|---|---|---|---|---|
| `design_type` | 50 | 0 | 1.000 (50/50) | **undefined** (Pe → 1 artifact; see S7.3) | report Po / PABAK = 1.00 |
| `IV_selection_strategy` | 35 | 15 | 0.743 (26/35) | **0.44** (0.17–0.69) | moderate |
| `reports_overlap_risk` | 8 | 42 | 0.875 (7/8) | **0.78** (0.43–1.0) | low power (n = 8) |
| **OVERALL** (macro, excl. artifact field) | — | — | — | **0.61** | avg of the two non-artifact fields |

### S7.3 The undefined-κ artifact on `design_type`

The κ on `design_type` is **undefined**, not evidence of poor reliability. It is a
direct consequence of the answer key containing **zero** "exclude" instances: the
original AI coding classified all 50 sampled studies as `两步法MR中介`, so the
expected-agreement term Pe → 1.0 and κ collapses. The actual observed agreement is
**100% (50/50)**: C. Yan classified all 50 sampled studies as `两步法MR中介` and
there were **no** design_type disagreements. The single-category key makes κ
mathematically undefined, so we report observed agreement and PABAK (= 1.00) for
this field.

### S7.4 `IV_selection_strategy` disagreements (n = 9 of 35)

Confusion matrix (rows = C. Yan's blind re-code, columns = original key):

| blind \ key | MVMR联合估计 | 分开选IV | 无法判断 |
|---|---|---|---|
| MVMR联合估计 | 4 | 0 | 0 |
| 分开选IV | 2 | 21 | 7 |
| 无法判断 | 0 | 0 | 1 |

- **2 studies** the original key tagged `MVMR联合估计` but C. Yan classed as
  `分开选IV` two-step mediation with an MVMR *sensitivity* check (S168, S230). These
  use MVMR to validate the direct effect, but the mediation indirect effect is still
  estimated by the sequential product method — so C. Yan's code is the stricter,
  design-accurate label.
- **7 studies** the original key left as `无法判断` but C. Yan classed as
  `分开选IV` (S005, S009, S044, S046, S049, S057, S070) because she judged the
  instrument source was stated explicitly enough to classify.
- C. Yan's MVMR assignment agreed with the key on 4 of the 6 key-MVMR studies
  (S235, S236, S351, S406); the 2 disagreements above (S168, S230) are the remaining
  MVMR-tagged studies.

### S7.5 `reports_overlap_risk` (n = 8)

Only 8 of 50 sampled studies had a populated `reports_overlap_risk` entry in the
original key (42 blank). κ = 0.78 (95% CI 0.43–1.0) with Po = 0.875; the single
disagreement is S311 (C. Yan = 部分, key = 是). With n = 8 the estimate is too
unstable to report as a reliability benchmark; it is included only for transparency.

## S7.6 Coding-completeness limitation (meta-finding)

The κ exercise surfaced a flaw in the *original* coding table itself, independent
of coder agreement:

- In this 50-study subset, `IV_selection_strategy` was **blank for 15 studies**
  (30%) and `reports_overlap_risk` was **blank for 42 studies** (84%).
- The "merged IV pool" design was recorded as **free text**, not a structured
  field, which is why §3.3 required a hand re-screen of every merged-pool tag.

Consequently the prevalence counts in §3.3 (39.3% at-risk under the typical
classification; 35.2% non-disclosure among the assessable subset) are **lower
bounds conditional on the information the original authors reported**, not exact
census figures. This incompleteness is acknowledged as a limitation in §4(3) and
strengthens the paper's central message that the field does not systematically
tag or report the overlap-prone configuration our correction targets.

## S7.7 Reproducibility artifacts

- Blind coding sheet: `③ 真实数据应用/temp/kappa_blind_coding_sheet_20260903.csv`
- Prior within-team blind re-code (50 studies, W.B.): `③ 真实数据应用/temp/kappa_recode_wb_20260904.csv`
- Original AI coding (extracted): `③ 真实数据应用/temp/kappa_original_ai_from_updated_20260904.csv`
- Sealed answer key: `③ 真实数据应用/temp/_sealed_do_not_open/kappa_answer_key_20260903.csv` (working copy `code/kappa/kappa_answer_key_20260903.csv`)
- **Reporting second-coder re-code (C. Yan, 50 studies):** `code/kappa_chenyan_task/kappa_second_coder_chenyan_FILLED.csv`
- **Reporting κ computation:** `code/kappa_chenyan_task/compute_kappa_2nd.py` → `code/kappa_chenyan_task/kappa_2nd_report.csv`
