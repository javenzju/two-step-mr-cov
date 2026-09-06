# two-step-mr-cov

**Correcting for instrument overlap in two-step summary-data Mendelian randomization mediation: a closed-form covariance and its empirical prevalence**

Companion code, data, and figures for the manuscript submitted to the *European Journal of Human Genetics* (EJHG).

> Authors: Yan Chen¹, Jianfeng Wang²
> ¹ Department of General Practice, The First Affiliated Hospital of Zhejiang Chinese Medical University (Zhejiang Provincial Hospital of Chinese Medicine), Hangzhou, China.
> ² Department of Respiratory Diseases, The First Affiliated Hospital of Zhejiang Chinese Medical University (Zhejiang Provincial Hospital of Chinese Medical University), Hangzhou, China.
> Correspondence: Jianfeng Wang, 2001m@163.com

---

## What this repository contains

This repository archives the full computational workflow behind the paper: the closed-form covariance correction tool, its validation, the empirical literature screen, the batch re-estimation of published trios, and the inter-coder reliability work package.

```
code/
  method_core/                 # core closed-form tool + validation
    S10_prod_mr_cov_tool.R                 # estimate_cov_prod_mr() — closed-form Cov(α̂,β̂) and CI
    weak_instrument_threshold_FIXED.R      # weak-instrument threshold (F-statistic) scan
    S16_bootstrap_fallback_indirect_var_FIXED.R  # bootstrap fallback for indirect-effect variance
    T2_validation.R                        # 100-grid-point validation of the correction
    T5_bootstrap_coverage.R               # bootstrap coverage simulation
  replication/                # empirical re-estimation from public GWAS
    M4b_phaseB_pipeline.py                # Phase-B batch re-estimation (OpenGWAS REST /tophits + /associations)
    M4b_stage1_pishared.py                # π_shared / SNP-overlap computation
    M4b_stage2_recompute.py               # re-compute corrected SE on recovered trios
    M4b_pishared_20260904.csv             # π_shared outputs
    M4b_stage2_recompute_20260904.csv     # re-estimation outputs
    M4b_rhoMY_empirical_20260904.py/.csv  # empirical ρ_MY estimates (harmonized GWAS effect sizes)
    S245_resolve_mediators.py             # S245 accession resolution
    S245_pi_shared.py                     # S245 SNP-overlap computation
  correct_cov_prod_mr.R       # TwoSampleMR-compatible wrapper mr_cov_correct() (+ self-test test_correct_cov_prod_mr.R)
  correct_from_ieugwasr.py    # ieugwasr-compatible wrapper mr_mediation_correct_from_frames()
  TOOL_README.md              # usage guide for the wrappers
  compute_kappa_2nd.py        # inter-coder reliability calculator (Pe→1-artifact detection + bootstrap CI)
  D61_fill_kappa_template.py  # loads the second-coder labels into the template
  kappa_second_coder_template.csv          # second-coder labels (50 studies)
  kappa_second_coder_template_BLANK.csv   # blank instrument for an independent coder
  kappa_2nd_report.csv       # computed agreement / κ / PABAK / bootstrap CI
  kappa_instructions.md       # coding instructions
  kappa/                     # sealed answer key
    kappa_answer_key_20260903.csv
  literature_coding_table_UPDATED.xlsx    # full 695-row literature coding table

figure/                      # all six figures (PNG + SVG sources)
  Fig1_conceptual.png … Fig6_batch_forest.png
  Fig5_pisweep.svg / Fig6_batch_forest.svg
  eq1.png … eq4.png          # display equations rendered as images for the Word manuscript

references/                  # reference-building scripts and the PubMed dump
  D61_references_pubmed.txt  # 1,364 deduplicated PubMed records (8 query groups)
  D61_novelty_check.txt      # novelty-check evidence (group-7 strict queries → 0 hits)
  D61_build_refs.py / D61_pick_recent_refs.py / D61_verify_refs.py / D61_build_reflist.py / D61_check_citations.py / D61_novelty_check.py
  根据检索词抓取_PubMed_记录_D61引用检索版.py   # original user-provided PubMed fetcher

D61_论文终稿_20260906.docx / .md   # submission manuscript (Times New Roman, justified, 40 references)
D61_Supplementary_S1-S6_derivation.md   # closed-form derivations (S1–S6)
D61_Supplementary_S7_kappa.md           # inter-coder reliability (S7)
D61_Supplementary_S8_batch.md          # batch re-estimation (S8)
D61_Supplementary_codebook_S1.md       # literature coding codebook
cover_letter_EJHG_20260904.md          # EJHG cover letter
```

## Reproducing the results

**1. Closed-form correction (R, requires TwoSampleMR / ieugwasr).**
Load `code/method_core/S10_prod_mr_cov_tool.R` to obtain `estimate_cov_prod_mr()`. The TwoSampleMR-compatible wrapper is `code/correct_cov_prod_mr.R` (`mr_cov_correct()`); the ieugwasr-compatible wrapper is `code/correct_from_ieugwasr.py` (`mr_mediation_correct_from_frames()`). Run `code/test_correct_cov_prod_mr.R` to self-test against the D56 ground truth.

> Note: the R wrappers depend on `TwoSampleMR`/`ieugwasr`. On the build machine (R 4.6.0) these packages trigger a segmentation fault on load, so the live TwoSampleMR re-estimation was performed elsewhere; the Python REST pipeline (`code/replication/`) reproduces the π_shared and re-estimation steps without the R packages via the OpenGWAS REST `/tophits` and `/associations` endpoints.

**2. Validation (R).** `code/method_core/T2_validation.R` (100 grid points) and `code/method_core/T5_bootstrap_coverage.R`.

**3. Empirical literature screen.** The 695-row coding table is `code/literature_coding_table_UPDATED.xlsx`; the manuscript reports the 39.3% / 19.0% / 4-of-6 figures derived from it.

**4. Batch re-estimation (Python).** `code/replication/M4b_phaseB_pipeline.py` resolves candidate trios to public GWAS accessions, computes π_shared, and re-estimates the corrected SE. Outputs are the `M4b_*_20260904.csv` files.

**5. Inter-coder reliability (Python, no dependencies).** `python code/compute_kappa_2nd.py` reads `code/kappa_second_coder_template.csv` against `code/kappa/kappa_answer_key_20260903.csv` and writes `code/kappa_2nd_report.csv`. It detects the Pe→1 κ-collapse artifact and reports observed agreement, Cohen's κ (with bootstrap 95% CI), and PABAK.

## Data sources

Real GWAS summary statistics were obtained through **IEU OpenGWAS** (https://gwas.mrcieu.ac.uk) and are subject to the OpenGWAS data-use policy. The BMI → waist → CHD illustration uses trait IDs `ieu-a-2`, `ieu-a-61`, `ieu-a-7`; the S245 re-examination uses `ieu-a-302`, `met-a-509`, `prot-a-2100`, `finn-b-CD2_MULTIPLE_MYELOMA_PLASMA_CELL`. Instrument sets were extracted via the OpenGWAS REST `/tophits` endpoint.

## Archiving

A public GitHub repository is at `https://github.com/javenzju/two-step-mr-cov`. An archived copy with a frozen DOI will be deposited at **Zenodo** (DOI: `10.5281/zenodo.XXXXXXX`, to be minted on acceptance).

## License

Code is released under the MIT License (see `LICENSE`). The manuscript text and figures are released for scholarly reuse under the terms of the journal upon publication.

## How to cite

See `CITATION.cff`. Until the paper is published, please cite the repository.
