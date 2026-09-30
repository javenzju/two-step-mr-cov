# Cover Letter — *European Journal of Epidemiology* (EJE)

**Target journal:** *European Journal of Epidemiology* (EJE; Springer; CAS 2025 大类 医学 2区 / 小类 公共卫生与流行病学 2区; JCR Q1; IF 6.6 (2025), 5-year 8.8; **Hybrid — no APC under the subscription model**, which fits the provincial-funding constraint). Submission to first decision (median): 8 days.

**Why EJE:** scope explicitly covers "epidemiologic and **statistical methods**" and the journal "publishes ... **methodological developments**"; EJE also maintains an ongoing open collection on **Epidemiologic Methods** ("novel epidemologic methods and updates on methodological topics"), which is the exact category of this manuscript.

---

Dear Editors,

Please consider our manuscript, "Correcting for instrument overlap in two-step summary-data Mendelian randomization mediation: a semi-analytic covariance and how often it is left unreported," as a methodological article in the *European Journal of Epidemiology*, for the journal's Epidemiologic Methods collection.

Two-step (product-method) Mendelian randomization mediation now appears in hundreds of published studies, and its product-method variance assumes that the exposure-step and mediator-step estimates are independent. When the steps share instruments, or the mediator and outcome GWAS share participants, they are not, and the standard variance omits a covariance term that a recent summary-data framework (Lin et al., *Statistics in Medicine* 2025) explicitly left open.

We (i) derive that covariance in semi-analytic form (exact modulo one numerical-integration step) and show that it is negative for both same-signed and opposite-signed mediation, so the conventional delta-method variance is conservative and no "widening" regime exists; (ii) audit 333 published two-step MR mediation studies, of which 39.3% used an overlap-capable design without disclosing how overlap was handled; and (iii) re-estimate 108 trios from public summary statistics, finding genuine overlap in five, where the correction narrowed standard errors modestly (median −1.6%) and altered no conclusion. Because the correction is always conservative, its cost is under-power rather than false positives — but a regime map shows that in the merged-pool, high-overlap designs the field already runs without disclosure, the uncorrected interval can be up to 65% wider than the true sampling variability, a material power penalty. The contribution is therefore to settle the direction of the correction analytically, to quantify when its magnitude matters, to document the reporting gap that hides it, and to supply a tool and a reporting recommendation (shared-instrument counts) that close it.

We believe the paper suits the journal's readership: it builds on the appraisal of MR mediation methods previously published in *EJE* (Carter et al., 2021) and extends STROBE-MR reporting practice. Code and data are archived on GitHub and Zenodo (10.5281/zenodo.22725281). The manuscript is not under consideration elsewhere. The authors declare no competing interests. We request publication under the subscription model (no APC).

Sincerely,
Jianfeng Wang (corresponding author; 2001m@163.com) and Yan Chen
The First Affiliated Hospital of Zhejiang Chinese Medical University (Zhejiang Provincial Hospital of Chinese Medicine), Hangzhou, China

---

*Internal notes (verify before submission):*
1. EiC: the masthead listed **Albert Hofman, MD, PhD** (Erasmus MC / Harvard) as Editor-in-Chief in September 2026. The salutation here uses the neutral "Dear Editors" at the author's instruction to avoid a wrong name; switch to "Dear Professor Hofman" only after re-confirming the current EiC on the EJE submission site.
2. EJE requires a structured abstract of 150–250 words (current manuscript abstract = 232 words, Background/Methods/Results/Conclusions). Keywords: 6 (EJE requires 4–6).
3. EJE has **no stated word limit for Original Articles** (limits apply only to Short Communications, 2000 words, and Letters, 1000 words). Current main text is ~6,100 words; a possible request to shorten at revision remains likely, so the Step-3 compression is still advisable for readability even though not mandatory.
4. Do **not** include Highlights or a Graphical Abstract — those are Elsevier/JCE requirements, not EJE.
5. This cover letter is the trimmed one-page version per the author's review: it leads with the gap (Lin 2025) and EJE fit, keeps limitations out of the opening, and drops the ρ_MY "fourth contribution" claim (consistent with the Step-1 plan to drop that contribution).
6. The "39.3% at-risk" headline is design-based (includes the 279 overlap-handling-unassessable studies via design_type); the audited corpus's overlap-handling disclosure was assessable in only 54/333 (19/54 = 35.2% reported/adjusted). Both numbers are stated in the manuscript Methods.
7. Title changed to "...and how often it is left unreported" to avoid reading "empirical prevalence" as the actual occurrence rate; confirm this matches the manuscript title before submission (manuscript title change is part of Step 2/3).
8. Zenodo DOI 10.5281/zenodo.22725281 is the minted archive DOI (no placeholder remains in the manuscript).
9. Carter et al., 2021 = Eur J Epidemiol;36(5):465–478 (MR mediation methods appraisal) — author/year verified; in-text number to be re-checked after the reference renumbering.
