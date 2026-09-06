# Second-coder blind re-coding — instructions

This package lets a **blinded human coder** re-code a stratified sample of 50
studies so that inter-coder reliability (Cohen's κ) can be reported honestly. The
original coding (the sealed answer key) was produced by the study team following
the codebook; κ is only meaningful if the second coder is a different person who has
**not** seen the answer key.

## Files

| File | What it is |
|---|---|
| `kappa_second_coder_template_BLANK.csv` | **The sheet you fill.** Columns `study_id, pmid, first_author_year, journal, title` are visible (bibliographic metadata only); `design_type, IV_selection_strategy, reports_overlap_risk` are **blank** for you to fill. Save your work under a new name (e.g. `kappa_second_coder_chenyan_FILLED.csv`). |
| `kappa_second_coder_template.csv` | ⚠️ **DO NOT OPEN.** This file is already pre-filled with the prior within-team re-code; opening it would break your blindness. Use only `kappa_second_coder_template_BLANK.csv`. |
| `code/kappa/kappa_answer_key_20260903.csv` | The sealed answer key. **Do NOT open until you have submitted your labels.** |
| `compute_kappa_2nd.py` | Calculator. Reads your filled file + the sealed key, prints per-field κ, observed agreement, Pe→1-artifact flags, bootstrap 95% CI, and the macro-averaged κ. It never invents your labels. |
| `kappa_codebook_S1_20260903` (in the submission package) | The coding rules. |

## Procedure

1. **Open** `kappa_second_coder_template.csv`. You will see 50 studies with only
   bibliographic metadata — no exposure/mediator/outcome labels, no risk flags.
2. **For each study**, obtain the full text (PMID is given; use PubMed). Apply the
   coding rules in the codebook (`D61_Supplementary_codebook_S1.md`) and write your
   judgement into the **three** blank columns:
   - `design_type` — one of: `两步法MR中介` (summary-data two-step product-method
     mediation, i.e. explicit Step-1/Step-2 structure) or `不属于两步法MR中介-排除`
     (not two-step summary-data mediation: individual-level mediation, Cox-regression
     mediation, single-chain MR, or wrong research question). *Do NOT use `MVMR变体`
     here — the 50-study blind sample contains only two-step studies, so this field is
     effectively binary.*
   - `IV_selection_strategy` — one of: `分开选IV` (Step-1 and Step-2 pick instruments
     independently), `MVMR联合估计` (merged MVMR joint estimation of direct+indirect),
     `无法判断` (paper does not state the instrument source clearly enough to classify).
   - `reports_overlap_risk` — `是` (the paper explicitly discusses/recognises overlap
     risk), `部分` (mentions it partially but not quantified), or `否` (does not
     discuss it).
3. **Save** your file under a new name, e.g. `kappa_second_coder_chenyan_FILLED.csv`.
   Do **not** overwrite the BLANK template.
4. **Only now**, run the calculator, pointing it at YOUR file:

   ```bash
   python compute_kappa_2nd.py --second kappa_second_coder_chenyan_FILLED.csv
   ```

   It writes `code/kappa_2nd_report.csv` and prints a summary. (Running without
   `--second` would silently reuse the pre-filled `kappa_second_coder_template.csv`
   and give the prior within-team numbers — not yours.)
5. **If a field shows `Pe->1 ARTIFACT`** (κ collapses to 0.00 because the answer key
   contains only one category for that field in this 50-study sample), report the
   observed agreement `Po` instead — κ is undefined there, not evidence of
   disagreement. This is exactly what happened for `design_type` in the sealed sample
   (all 50 are two-step mediation studies; observed agreement was 94.0%).

## Integrity rules

- The second coder must be a **human who is blind to the sealed answer key and to
  the paper's hypothesis** (that overlap is common and usually uncorrected). The
  original coder (J.W.) must **not** perform the second coding — re-coding one's own
  key is circular and inflates agreement. A co-author who did not create the key
  (e.g., C.Y.) is acceptable as a *within-team blinded rater*, provided they were not
  involved in designing the coding scheme and stay blind to the key until their
  labels are submitted. A fully external independent rater remains the gold standard
  and is preferred wherever one is available.
- The second coder must be blind to the answer key until their labels are submitted.
- Do not copy values from the answer key — that would invalidate κ.
- `compute_kappa_2nd.py` refuses to run if the coding columns are empty; it never
  fabricates labels.
- Inter-coder reliability is strongest when the second coder is an external
  independent rater; a *within-team blinded* second coder (a co-author blind to the
  key) is an acceptable substitute when no external rater is available, and must be
  disclosed as such. A κ computed by the original coder on their own key is invalid
  and must never be reported.
