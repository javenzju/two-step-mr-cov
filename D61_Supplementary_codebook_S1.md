# Supplementary Material S11 — Codebook for the literature audit

This codebook defines every field of the literature-audit table that underlies §3.2–§3.3 of the main
manuscript (prevalence of overlap-capable designs) and the reliability assessment in Supplementary
Methods S7. It is written for a reader who wishes to interpret, reproduce or challenge the audit; the
full table (`literature_coding_table_UPDATED.xlsx`, 695 coded reports / 489 primary studies) and the
coding scripts are in the public repository.

Only the fields that enter a reported number are defined here.

## Variables

### `study_id`
Internal identifier of the coded report (e.g. S014, S110, S366). Stable across the audit, the
π_shared screen (Table S3.1) and the batch re-estimation (Table S3.2, main-text Table 2).

### `design_type` — primary design classification
Whether the report implements a *two-step (product-method) MR mediation* analysis. | Value | Meaning | |---|---| | two-step MR mediation | The report multiplies a step-1 (exposure→mediator) and a step-2 (mediator→outcome) IVW estimate. | | MVMR variant / merged-pool | A multivariable design in which one combined instrument set is reused across both steps — the maximal-overlap regime (see Supplementary Methods S8). | | not two-step MR mediation (excluded) | Individual-level mediation, regression-based mediation, single-chain MR, or a purely methodological paper. Excluded from all denominators. |

This field is ascertainable for **all 333** two-step-capable records and is the basis of the
"overlap-capable" numerator; its inter-coder reproducibility is κ = 1.00 (PABAK), see S7.

### `IV_selection_strategy` — how the instrument sets were built
Determines whether the two steps *can* share instruments, i.e. whether Cov(α̂, β̂) can be non-zero. | Value | Meaning | Overlap-capable? | |---|---|---| | separate IV selection | Instruments chosen independently for each step, typically from distinct GWAS. | No (unless the pools coincide by accession) | | MVMR joint estimation | One instrument set fitted jointly across both steps. | Yes | | merged IV pool | Candidate pools deliberately combined to increase power. | Yes — maximal | | undeterminable | The report does not describe instrument selection well enough to classify. | Unknown |

Inter-coder κ = 0.44 [0.17–0.69] on this field (S7). It is therefore **not** used to compute the
headline prevalence; it is reported only descriptively, and the headline rests on `design_type`
(κ = 1.00) together with `reports_overlap_disclosure`.

### `reports_overlap_disclosure` — did the report state how overlap was handled? | Value | Meaning | |---|---| | yes | The number of shared instruments, the overlap proportion, or an explicit correction is reported. | | no | Overlap is possible given the design but is neither reported nor corrected. | | not ascertainable | Full text unavailable, or instrument selection is not described. |

Ascertainable for **54 of 333** records; 19 of these 54 (35.2% [95% CI 23.8–48.5%]) reported or
adjusted for overlap. This field is *not* used in the headline numerator precisely because it is
ascertainable for only a subset.

### `n_shared` (`n_s`) and `π_shared`
Number and proportion of instruments shared between the two steps, computed as the exact rsID
intersection of the clumped step-1 and step-2 instrument sets:

$$\pi_{\text{shared}} = \frac{n_s}{\min(p_X,\ p_M)}$$

where `p_X` and `p_M` are the numbers of instruments in steps 1 and 2. Both are computed from
public summary statistics, not taken from the publications (which is the point of the audit).
π_shared > 0 defines "genuine overlap"; the sub-threshold cut used for the headline is π_shared > 0.019.

### Degenerate (self-mediating) trios
Where the exposure and mediator resolve to the *same* GWAS accession, α̂ = 1.0 exactly and
π_shared = 1.0. These are mapping artefacts, not substantive mediation, and are flagged
(`degenerate = TRUE`) rather than counted as mediation evidence. S320 and S293 are the two instances.

## How the headline figures are derived | Figure | Definition | Source | |---|---|---| | 39.3% (95% CI 34.2–44.7%) | Of all 333 two-step-capable records, the share whose `design_type` is overlap-capable **and** whose overlap handling is not disclosed. | `design_type` (ascertainable for all 333) + `reports_overlap_disclosure` | | 19/54 (35.2%) | Share of records with ascertainable disclosure status that reported or adjusted for overlap. | `reports_overlap_disclosure` | | 5/108 (4.6%, 95% CI 2.0–10.4%) | Non-degenerate trios with genuine overlap, among the 108 successfully re-estimated. | `n_shared`, `π_shared`, `degenerate` | | 7/108 (6.5%, 95% CI 3.2–12.8%) | As above, counting the two degenerate self-mediating designs. | as above | | 8/42 (19.0%) | Phase-A π_shared screen only; denominator 42 and no degeneracy or threshold exclusions. **Not comparable** to the figures above (see Table S3.1 note). | `π_shared` |

## Reproducibility

Blind re-coding of a stratified 50-study sample against a sealed answer key is documented in
Supplementary Methods S7, together with the per-field κ, its bootstrap 95% CI and the
"prevalence→1-artifact" diagnostic. The calculator (`compute_kappa_2nd.py`), the coding template and
the answer key are in the public repository, so a third party can repeat the reliability assessment.
