# -*- coding: utf-8 -*-
"""
push_to_github.py
Push local commits of the submission repository to GitHub, trying in order:
  1. direct HTTPS (no proxy)
  2. local HTTP proxy 127.0.0.1:10808 (Clash/V2Ray default)
Whichever succeeds, it then verifies the remote HEAD and prints a clear report.

Usage (run on the machine that has GitHub credentials):
    python push_to_github.py

Notes
-----
* GitHub no longer accepts account passwords over HTTPS. If authentication is
  requested, supply a Personal Access Token (repo scope) as the password, or
  configure the credential manager first:
      git config credential.helper manager
* If the proxy is not running, start your proxy client and re-run this script.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROXY = "http://127.0.0.1:10808"


def run(args, env=None):
    """Run a command, return (returncode, combined output)."""
    p = subprocess.run(args, cwd=ROOT, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "").strip()


def clean_env():
    env = os.environ.copy()
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        env.pop(k, None)
    return env


def main():
    print("=" * 68)
    print("Push submission repository to GitHub")
    print("=" * 68)

    rc, out = run(["git", "log", "--oneline", "-1"])
    print(f"local HEAD : {out}")

    attempts = [
        ("direct (no proxy)", ["-c", "http.proxy=", "-c", "https.proxy="], clean_env()),
        (f"proxy {PROXY}",
         [f"-c", f"http.proxy={PROXY}", "-c", f"https.proxy={PROXY}"], clean_env()),
    ]

    last_out = ""
    for label, cfg, env in attempts:
        print(f"\n--- trying {label} ---")
        rc, out = run(["git"] + cfg + ["push", "origin", "master"], env=env)
        last_out = out
        print(out if out else "(no output)")
        if rc == 0:
            print(f"\n[OK] branch push succeeded via {label}")
            rc2, head = run(["git", "ls-remote", "origin", "HEAD"], env=env)
            print(f"remote HEAD now: {head}")
            # push tags as well so a GitHub release (and Zenodo DOI) can be cut
            rc3, tout = run(["git"] + cfg + ["push", "origin", "--tags"], env=env)
            print("\n--- pushing tags ---")
            print(tout if tout else "(no output)")
            if rc3 == 0:
                rc4, tags = run(["git", "ls-remote", "--tags", "origin"], env=env)
                print("remote tags:\n" + tags)
            else:
                print(f"[WARN] tag push failed (exit {rc3}); run 'git push origin --tags' manually")
            print("\nNext: open https://zenodo.org, sign in with GitHub, and link")
            print("the repository javenzju/two-step-mr-cov to mint the DOI.")
            return 0
        print(f"[FAIL] exit {rc} via {label}")

    print("\n" + "=" * 68)
    print("Push did not succeed. Most likely causes:")
    print("  1. No GitHub credential in this environment -> provide a PAT")
    print("     (repo scope) when prompted, or run: git config credential.helper manager")
    print("  2. Network blocked / proxy not running -> start your proxy client")
    print("     (default 127.0.0.1:10808) and re-run this script.")
    print("  3. No local commits to push (already up to date).")
    print("=" * 68)
    return 1


if __name__ == "__main__":
    sys.exit(main())
