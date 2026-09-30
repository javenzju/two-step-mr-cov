"""
Quantify the practical cost of the naive (uncorrected) variance in two-step MR
mediation: translate the SE inflation ratio k = SE_naive / SD(alpha_hat*beta_hat)
into (a) statistical power loss and (b) equivalent sample-size penalty.

Logic
-----
Wald test of H0: alpha*beta = 0.  Let sigma = SD(alpha_hat*beta_hat) (true
sampling SD) and let the analyst report SE.  The non-centrality actually
realised is lambda_used = theta / SE_used.

  corrected: SE_corr ~ sigma * r_c   (r_c = ratio_corr_over_sd, ~1.00-1.02)
  naive    : SE_naive = sigma * r_n  (r_n = ratio_naive_over_sd, up to ~1.65)

Fix the true effect so that the CORRECTED test attains 80% power:
  lambda_corr = z_{0.975} + z_{0.80} = 1.95996 + 0.84162 = 2.80158
Then theta/sigma = lambda_corr * r_c, and the naive non-centrality is
  lambda_naive = (theta/sigma) / r_n = lambda_corr * r_c / r_n
  power_naive  = Phi(lambda_naive - 1.95996)   (+ negligible lower tail)

Sample-size equivalence: SD(alpha_hat*beta_hat) ~ 1/sqrt(N) when both GWAS
sample sizes scale together (Var(alpha_hat), Var(beta_hat) and the shared-SNP
covariance all scale as 1/N).  To shrink the naive SD by the factor needed to
match the corrected SE, N must be multiplied by k^2 where k = r_n / r_c.
"""
import csv, math, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "temp", "M4b_regime_map_20260930.csv")
OUT  = os.path.join(HERE, "temp", "M4b_power_penalty_20261001.csv")

def Phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

Z_A   = 1.959963985          # two-sided alpha = 0.05
Z_80  = 0.841621234          # target power 0.80
LAM80 = Z_A + Z_80           # non-centrality giving 80% power

def main():
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    log = []
    def P(s=""):
        print(s); log.append(str(s))

    P("=== Power / sample-size penalty from the regime map ===")
    P(f"source: {SRC}   ({len(rows)} cells)")
    P(f"target: corrected test at 80% power  ->  lambda_corr = {LAM80:.4f}")
    P("")

    groups = defaultdict(list)
    for r in rows:
        key = (r["strength"], int(r["n_shared"]))
        groups[key].append({
            "r_n": float(r["ratio_naive_over_sd"]),
            "r_c": float(r["ratio_corr_over_sd"]),
            "dSE": float(r["dSE_pct"]),
        })

    out_rows = []
    P(f"{'strength':<14}{'n_s':>5}{'k=SE_naive/SD':>16}{'pow_naive@80':>14}{'dPow':>8}{'N_mult=k^2':>12}")
    P("-"*72)
    for strength in sorted({k[0] for k in groups}):
        for n_s in sorted({k[1] for k in groups if k[0]==strength}, key=lambda x:int(x)):
            g = groups[(strength, n_s)]
            # use mean of the ratio; report min-max as range
            r_n = sum(x["r_n"] for x in g)/len(g)
            r_c = sum(x["r_c"] for x in g)/len(g)
            k   = r_n / r_c                      # inflation of naive SE over corrected SE
            lam_n = LAM80 * r_c / r_n            # naive non-centrality
            pow_n = Phi(lam_n - Z_A) + Phi(-lam_n - Z_A)
            nmult = k*k
            rng_n = (min(x["r_n"] for x in g), max(x["r_n"] for x in g))
            P(f"{strength:<14}{n_s:>5}{r_n:>16.3f}{pow_n:>14.3f}{0.80-pow_n:>8.3f}{nmult:>12.2f}"
              f"   [r_n range {rng_n[0]:.2f}-{rng_n[1]:.2f}]")
            out_rows.append(dict(strength=strength, n_shared=n_s, ratio_naive_over_sd=r_n,
                                 ratio_corr_over_sd=r_c, k=k, lam_naive=lam_n,
                                 power_naive_at80=pow_n, power_drop=0.80-pow_n,
                                 N_multiplier=nmult,
                                 extra_pct=(nmult-1)*100))
        P("")

    # headline: strong + very strong instruments at full overlap
    P("=== HEADLINE: high-overlap regime (n_s = 50) ===")
    for strength in sorted({k[0] for k in groups}):
        g = groups.get((strength, 50))
        if not g: continue
        r_n = sum(x["r_n"] for x in g)/len(g); r_c = sum(x["r_c"] for x in g)/len(g)
        k = r_n/r_c; lam=LAM80*r_c/r_n; pw=Phi(lam-Z_A)+Phi(-lam-Z_A)
        P(f"  {strength:<14} k={k:.3f}  power {pw*100:.1f}% (vs 80%)  "
          f"drop {80-pw*100:.1f} pp   N x{k*k:.2f}  (+{(k*k-1)*100:.0f}% participants)")

    # the realised literature regime
    P("")
    P("=== Realised literature regime (n_s = 0..3) ===")
    for strength in sorted({k[0] for k in groups}):
        g = groups.get((strength, 0))
        if not g: continue
        r_n = sum(x["r_n"] for x in g)/len(g); r_c = sum(x["r_c"] for x in g)/len(g)
        k = r_n/r_c; lam=LAM80*r_c/r_n; pw=Phi(lam-Z_A)+Phi(-lam-Z_A)
        P(f"  {strength:<14} k={k:.3f}  power {pw*100:.1f}%  N x{k*k:.2f}")

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader(); w.writerows(out_rows)
    P("")
    P(f"[saved] {OUT}")
    with open(os.path.join(HERE,"temp","M4b_power_penalty_20261001.log"),"w",encoding="utf-8") as f:
        f.write("\n".join(log))

if __name__ == "__main__":
    main()
