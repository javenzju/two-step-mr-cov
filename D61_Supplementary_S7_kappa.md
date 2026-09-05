# Supplementary Methods S7 — Inter-coder reliability assessment (Cohen's κ)

This supplement documents the independent blind re-coding used to quantify the
reproducibility of the literature design classification reported in §3.3 of the
main manuscript, and the coding-completeness limitations it revealed.

## S7.1 Sampling design

- **Source corpus.** The authoritative coding table
  `③ 真实数据应用/literature_coding_table_UPDATED.xlsx` (695 primary studies).
- **Stratified random sample.** A sample of **50 studies** was drawn, stratified
  by the three prevalence tiers of Figure 4 in proportions **31 / 100 / 202**
  (conservative / typical / structural), so that the sample mirrors the full
  corpus's risk distribution. Random seed = **2026** (reproducible).
- **Blind coding.** A second blinded coding pass re-judged each study from the
  **paper text only**, independently of the original coding session, using a codebook
  (`kappa_codebook_S1_20260903.md`) defining three fields:
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

These statistics were computed with `compute_kappa_2nd.py` (in `code/`) from the blind re-code (`code/kappa_second_coder_template.csv`) against the sealed answer key; the full per-field report — including bootstrap 95% confidence intervals and PABAK (= 2·Po − 1) — is in `code/kappa_2nd_report.csv`.

| Field | n (valid pairs) | Blank excluded | Observed agreement Po | Cohen's κ | Interpretation |
|---|---|---|---|---|---|
| `design_type` | 50 | 0 | 0.940 (47/50) | **0.00** | statistical artifact (see S7.3) |
| `IV_selection_strategy` | 35 | 15 | 0.743 (26/35) | **0.50** | moderate |
| `reports_overlap_risk` | 8 | 42 | 0.750 (6/8) | **0.50** | low power (n = 8) |

### S7.3 The κ = 0.00 artifact on `design_type`

The κ of 0.00 on `design_type` is **not** evidence of poor reliability. It is a
direct consequence of the answer key containing **zero** "exclude" instances: the
original AI coding classified all 50 sampled studies as `两步法MR中介`, so the
expected-agreement term Pe → 1.0 and κ collapses to 0 regardless of observed
agreement. The actual observed agreement is 94.0% (47/50). The three genuine
disagreements are edge cases in which network or individual-level mediation was
conflated with the two-step *product* method:

- **S097** — NHANES network toxicology; no explicit two-step product method.
- **S044** — individual-level MRI mediation, not two-step summary-data MR.
- **S423** — individual-level causal mediation analysis.

The second coder classified all three as `不属于两步法MR中介-排除`; the original
key had coded them `两步法MR中介`.

### S7.4 `IV_selection_strategy` disagreements (n = 9 of 35)

Confusion matrix (rows = blind re-code, columns = original key):

| blind \ key | MVMR联合估计 | 分开选IV | 无法判断 |
|---|---|---|---|
| MVMR联合估计 | 0 | 0 | 0 |
| 分开选IV | 6 | 18 | 0 |
| 无法判断 | 0 | 3 | 8 |

- **6 studies** the original key tagged `MVMR联合估计` but the blind coder classed
  as `分开选IV` two-step mediation with an MVMR *sensitivity* check
  (S168, S235, S236, S230, S351, S406). These use MVMR to validate the direct
  effect, but the mediation indirect effect is still estimated by the sequential
  product method — so the blind code is the stricter, design-accurate label.
- **3 studies** the blind coder marked `无法判断` vs original `分开选IV`
  (S352, S384, S390) because the paper did not state the instrument source
  explicitly enough to classify.

### S7.5 `reports_overlap_risk` (n = 8)

Only 8 of 50 sampled studies had a populated `reports_overlap_risk` entry in the
original key (42 blank). κ = 0.50 with Po = 0.75; the two disagreements are
S208 (blind = 是, key = 否) and S053 (blind = 否, key = 是). With n = 8 the
estimate is too unstable to report as a reliability benchmark; it is included only
for transparency.

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
- Blind re-code (50 studies): `③ 真实数据应用/temp/kappa_recode_wb_20260904.csv`
- Original AI coding (extracted): `③ 真实数据应用/temp/kappa_original_ai_from_updated_20260904.csv`
- Sealed answer key: `③ 真实数据应用/temp/_sealed_do_not_open/kappa_answer_key_20260903.csv` (working copy `code/kappa/kappa_answer_key_20260903.csv`)
- Blind re-code used for κ: `③ 真实数据应用/temp/kappa_recode_wb_20260904.csv` (loaded into `code/kappa_second_coder_template.csv`)
- κ computation: `code/compute_kappa_2nd.py` → `code/kappa_2nd_report.csv`
