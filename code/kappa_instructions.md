# Second-coder blind re-coding — instructions

This package lets an **independent human coder** re-code a stratified sample of 50
studies so that inter-coder reliability (Cohen's κ) can be reported honestly. The
first coder was an AI (Claude); κ is only meaningful if the second coder is a
different person who has **not** seen the answer key.

## Files

| File | What it is |
|---|---|
| `kappa_second_coder_template.csv` | Blind re-coding sheet. Columns `study_id, pmid, first_author_year, journal, title` are visible; `design_type, IV_selection_strategy, significant_as_reported, risk_flag_for_reanalysis` are **blank** for you to fill. |
| `temp/_sealed_do_not_open/kappa_answer_key_20260903.csv` | The sealed answer key. **Do NOT open until you have submitted your labels.** |
| `compute_kappa_2nd.py` | Calculator. Reads your filled file + the sealed key, prints per-field κ, observed agreement, Pe→1-artifact flags, bootstrap 95% CI, and the macro-averaged κ. It never invents your labels. |
| `kappa_codebook_S1_20260903` (in the submission package) | The coding rules. |

## Procedure

1. **Open** `kappa_second_coder_template.csv`. You will see 50 studies with only
   bibliographic metadata — no exposure/mediator/outcome labels, no risk flags.
2. **For each study**, obtain the full text (PMID is given; use PubMed). Apply the
   coding rules in the codebook and write your judgement into the four blank columns:
   - `design_type` — one of: `两步法MR中介` (summary-data two-step product-method
     mediation), `MVMR` (multivariable/MVMR joint estimation), `排除` (not
     two-step summary-data mediation: individual-level mediation, Cox-regression
     mediation, single-chain MR, or wrong research question).
   - `IV_selection_strategy` — e.g. `独立选IV(标准序贯)` (Step-1 and Step-2 pick
     instruments independently), `合并IV池` (merged instrument pool), `unclear`.
   - `significant_as_reported` — `是` / `否` (did the paper report a significant
     indirect effect?).
   - `risk_flag_for_reanalysis` — `高风险` / `中风险` / `低风险` (would this study's
     published indirect-effect CI be materially altered by the covariance correction?).
3. **Save** your file under a new name, e.g. `kappa_second_coder_FILLED.csv`.
4. **Only now**, run the calculator:

   ```bash
   python compute_kappa_2nd.py --second kappa_second_coder_FILLED.csv
   ```

   It writes `temp/kappa_2nd_report.csv` and prints a summary.
5. **If a field shows `Pe->1 ARTIFACT`** (κ collapses to 0.00 because the answer key
   contains only one category for that field in this 50-study sample), report the
   observed agreement `Po` instead — κ is undefined there, not evidence of
   disagreement. This is exactly what happened for `design_type` in the sealed sample
   (all 50 are two-step mediation studies; observed agreement was 94.0%).

## Integrity rules

- The second coder must be a **truly independent human**: not a member of the
  original coding team (YC/JW), not involved in designing this study, and **blind
  to the paper's hypothesis** (that overlap is common and usually uncorrected).
- The second coder must be blind to the answer key until their labels are submitted.
- Do not copy values from the answer key — that would invalidate κ.
- `compute_kappa_2nd.py` refuses to run if the coding columns are empty; it never
  fabricates labels.
- This is the single most important reliability fix for the manuscript: a κ from a
  within-team or AI second pass is a known limitation; only an independent human
  rater produces a defensible inter-coder reliability figure.
