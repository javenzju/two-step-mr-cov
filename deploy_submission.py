#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deploy_submission.py
====================================================================
EJE 投稿包「网络依赖步骤」一键执行脚本。封装以下动作：

  A. 推送本地 git 提交到 GitHub
       - 直连（清代理）优先；可选经 --proxy；可选 --github-pat 临时注入
       - 禁用交互式凭据提示（GIT_TERMINAL_PROMPT=0），自动重试
  B. 上传 Zenodo 归档（zenodo_upload.zip + zenodo_metadata.json）并取回永久 DOI
       - 仅用 Python 标准库 urllib，无需 pip install
  C. 将 DOI 回填到正文占位符 10.5281/zenodo.XXXXXXX
  D. 重建 docx（运行 D61_build_docx.py）
  E. 同步到 ⑥ EJE 投稿包

设计原则：仅依赖标准库；任一步骤失败都清晰报错且不破坏已生成产物；
          每个步骤可用开关独立跳过。

--------------------------------------------------------------------
用法（在联网且具备凭据的机器上运行）：
--------------------------------------------------------------------
  # 执行全部（Zenodo 需要 token）：
  python deploy_submission.py --zenodo-token ZENOODO_TOKEN

  # 仅推送 git 并重建（例如 DOI 已手动取得）：
  python deploy_submission.py --no-zenodo --doi 10.5281/zenodo.1234567

  # 仅推送 git（暂不处理 Zenodo）：
  python deploy_submission.py --no-zenodo

  # 指定 GitHub PAT 推送（推完不落盘）：
  python deploy_submission.py --no-zenodo --github-pat ghp_xxx

  # 走代理（如本机开了 Clash/V2Ray）：
  python deploy_submission.py --proxy http://127.0.0.1:10808 --zenodo-token TOKEN

  # 仅做 Zenodo 上传 + 回填 + 重建（跳过 push）：
  python deploy_submission.py --skip-push --zenodo-token TOKEN

  # 环境变量亦可：export ZENODO_TOKEN=... ; export GITHUB_TOKEN=...
--------------------------------------------------------------------
注意：
  - Zenodo token 需要 "deposit:actions" 与 "deposit:write" 权限。
  - GitHub PAT 需要 repo 范围。
  - 本机若出站写操作被 reset / Zenodo 不可达，脚本会报错并跳过，不会
    破坏已生成的 docx / md。
====================================================================
"""
import os
import sys
import re
import json
import time
import shutil
import argparse
import subprocess
from urllib import request as ureq
from urllib.error import HTTPError, URLError

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = ROOT
MANUSCRIPT_MD = os.path.join(ROOT, "D61_论文终稿_20260906.md")
BUILD_SCRIPT = os.path.join(ROOT, "D61_build_docx.py")
DOCX_OUT = os.path.join(ROOT, "D61_论文终稿_20260906.docx")
ZENODO_ZIP = os.path.join(ROOT, "temp", "zenodo_upload.zip")
ZENODO_META = os.path.join(ROOT, "zenodo_metadata.json")
PKG_DOCX = os.path.join(ROOT, "..", "⑥ EJE_投稿包_20260910", "two-step-MR-overlap_manuscript.docx")
DOI_PLACEHOLDER = re.compile(r"10\.5281/zenodo\.XXXXXXX")

ZENODO_API = "https://zenodo.org/api"


def log(msg):
    print(f"[deploy] {msg}", flush=True)


def run(cmd, env=None, cwd=REPO):
    """运行子进程，返回 (returncode, combined_output)。"""
    p = subprocess.run(cmd, cwd=cwd, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "").strip()


# ----------------------------------------------------------------------
# A. git push
# ----------------------------------------------------------------------
def git_push(github_pat=None, proxy=None, retries=3, push_timeout=60):
    log("步骤 A: 推送 git 提交到 GitHub ...")
    env = os.environ.copy()
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        env.pop(k, None)
    if proxy:
        env["https_proxy"] = env["http_proxy"] = proxy
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_HTTP_TIMEOUT"] = str(push_timeout)

    # 构造 proxy 相关的 -c 参数
    proxy_cfg = []
    if proxy:
        proxy_cfg = ["-c", f"http.proxy={proxy}", "-c", f"https.proxy={proxy}"]
    else:
        proxy_cfg = ["-c", "http.proxy=", "-c", "https.proxy="]

    # 临时注入 PAT（推完还原，token 不落盘）
    orig_url = None
    if github_pat:
        rc, out = run(["git", "remote", "get-url", "origin"])
        if rc == 0:
            orig_url = out.strip()
            run(["git", "remote", "set-url", "origin",
                 f"https://{github_pat}@github.com/javenzju/two-step-mr-cov.git"])
            log("已临时注入 GitHub PAT 到 remote URL（推完还原）")

    try:
        for attempt in range(1, retries + 1):
            log(f"  push 尝试 {attempt}/{retries} ...")
            rc, out = run(
                ["git", "-c", f"http.timeout={push_timeout}"] + proxy_cfg +
                ["push", "origin", "master"], env=env)
            if rc == 0:
                log("  ✅ git push 成功（远程 HEAD 已更新）")
                return True
            log(f"  ⚠ push 失败 (rc={rc}): {out[:200]}")
            if attempt < retries:
                time.sleep(3)
        log("  ❌ git push 在经过重试后仍失败（多为网络出站写被 reset）。")
        log("     请在有稳定网络（或开启代理）的机器重跑本脚本，或手动 `git push origin master`。")
        return False
    finally:
        if orig_url is not None:
            run(["git", "remote", "set-url", "origin", orig_url])
            log("已还原 remote URL（PAT 未落盘）")


# ----------------------------------------------------------------------
# B. Zenodo 上传
# ----------------------------------------------------------------------
def _http_json(method, url, token=None, data=None, timeout=30, proxy=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if data is not None:
        if isinstance(data, (dict, list)):
            data = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        else:
            headers["Content-Type"] = "application/octet-stream"
    handlers = []
    if proxy:
        from urllib.request import ProxyHandler
        handlers.append(ProxyHandler({"http": proxy, "https": proxy}))
    opener = ureq.build_opener(*handlers) if handlers else ureq.build_opener()
    req = ureq.Request(url, data=data, method=method, headers=headers)
    with opener.open(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", "replace")
        return resp.status, (json.loads(body) if body else {})


def zenodo_upload(token, proxy=None):
    log("步骤 B: 上传归档到 Zenodo 并取回 DOI ...")
    if not os.path.exists(ZENODO_ZIP):
        raise FileNotFoundError(f"找不到 {ZENODO_ZIP}")
    if not os.path.exists(ZENODO_META):
        raise FileNotFoundError(f"找不到 {ZENODO_META}")

    # 1) 创建空 deposit
    log("  创建 deposit ...")
    st, dep = _http_json("POST", f"{ZENODO_API}/deposit/depositions",
                         token=token, data=b"{}", timeout=30, proxy=proxy)
    if st not in (200, 201):
        raise RuntimeError(f"创建 deposit 失败 HTTP {st}: {dep}")
    dep_id = dep["id"]
    bucket = dep["links"]["bucket"]
    log(f"  deposit id={dep_id}")

    # 2) 上传 zip 到 bucket
    log(f"  上传 {os.path.basename(ZENODO_ZIP)} ({os.path.getsize(ZENODO_ZIP)//1024} KB) ...")
    with open(ZENODO_ZIP, "rb") as f:
        zip_bytes = f.read()
    st, _ = _http_json("PUT", f"{bucket}/{os.path.basename(ZENODO_ZIP)}",
                       token=token, data=zip_bytes, timeout=120, proxy=proxy)
    if st not in (200, 201):
        raise RuntimeError(f"上传文件失败 HTTP {st}")

    # 3) 更新 metadata
    log("  写入 metadata ...")
    meta = json.load(open(ZENODO_META, encoding="utf-8"))
    st, _ = _http_json("PUT", f"{ZENODO_API}/deposit/depositions/{dep_id}",
                       token=token, data={"metadata": meta["metadata"]},
                       timeout=30, proxy=proxy)
    if st not in (200, 201):
        raise RuntimeError(f"更新 metadata 失败 HTTP {st}")

    # 4) 发布
    log("  发布 deposit ...")
    st, pub = _http_json("POST",
                         f"{ZENODO_API}/deposit/depositions/{dep_id}/actions/publish",
                         token=token, timeout=30, proxy=proxy)
    if st not in (200, 201):
        raise RuntimeError(f"发布失败 HTTP {st}: {pub}")
    doi = pub.get("doi") or f"10.5281/zenodo.{dep_id}"
    log(f"  ✅ Zenodo 发布成功，DOI = {doi}")
    return doi


# ----------------------------------------------------------------------
# C. 回填 DOI
# ----------------------------------------------------------------------
def backfill_doi(doi):
    log(f"步骤 C: 回填 DOI {doi} 到正文占位符 ...")
    txt = open(MANUSCRIPT_MD, encoding="utf-8").read()
    if not DOI_PLACEHOLDER.search(txt):
        log("  未找到占位符 10.5281/zenodo.XXXXXXX（可能已回填），跳过。")
        return False
    txt2 = DOI_PLACEHOLDER.sub(doi, txt)
    open(MANUSCRIPT_MD, "w", encoding="utf-8").write(txt2)
    log("  ✅ 正文已回填 DOI。")
    return True


# ----------------------------------------------------------------------
# D. 重建 docx
# ----------------------------------------------------------------------
def rebuild_docx():
    log("步骤 D: 重建 docx（运行 D61_build_docx.py）...")
    rc, out = run([sys.executable, BUILD_SCRIPT], cwd=ROOT)
    if rc != 0:
        raise RuntimeError(f"重建 docx 失败 rc={rc}: {out[-300:]}")
    log(f"  ✅ 已重建 {os.path.basename(DOCX_OUT)}")


# ----------------------------------------------------------------------
# E. 同步到 ⑥ 投稿包
# ----------------------------------------------------------------------
def sync_pkg():
    log("步骤 E: 同步 docx 到 ⑥ EJE 投稿包 ...")
    if not os.path.exists(DOCX_OUT):
        raise FileNotFoundError(f"找不到 {DOCX_OUT}，请先运行重建")
    os.makedirs(os.path.dirname(PKG_DOCX), exist_ok=True)
    shutil.copy2(DOCX_OUT, PKG_DOCX)
    log(f"  ✅ 已同步到 {PKG_DOCX}")


# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="EJE 投稿包网络步骤一键部署")
    ap.add_argument("--no-zenodo", action="store_true", help="跳过 Zenodo 上传")
    ap.add_argument("--skip-push", action="store_true", help="跳过 git push")
    ap.add_argument("--skip-rebuild", action="store_true", help="跳过重建+同步（仅 push/upload/回填）")
    ap.add_argument("--zenodo-token", default=os.environ.get("ZENODO_TOKEN"), help="Zenodo API token")
    ap.add_argument("--github-pat", default=os.environ.get("GITHUB_TOKEN"), help="GitHub PAT（临时注入）")
    ap.add_argument("--proxy", default=None, help="HTTP/HTTPS 代理 URL")
    ap.add_argument("--doi", default=None, help="手动指定已存在的 DOI，直接回填+重建+同步（不触发上传）")
    ap.add_argument("--push-retries", type=int, default=3)
    ap.add_argument("--push-timeout", type=int, default=60)
    args = ap.parse_args()

    log("=" * 60)
    log("EJE 投稿包部署脚本启动")
    log(f"  仓库: {REPO}")
    log(f"  Zenodo: {'跳过' if args.no_zenodo else ('手动DOI' if args.doi else ('有token' if args.zenodo_token else '无token→将跳过'))}")
    log(f"  git push: {'跳过' if args.skip_push else '执行'}")
    log("=" * 60)

    # A. push
    push_ok = True
    if not args.skip_push:
        push_ok = git_push(github_pat=args.github_pat, proxy=args.proxy,
                           retries=args.push_retries, push_timeout=args.push_timeout)
    else:
        log("步骤 A: 跳过 git push（--skip-push）")

    # B/C/D/E. Zenodo 相关
    if args.doi:
        # 手动指定 DOI：直接回填 + 重建 + 同步
        log("检测到 --doi，直接回填 + 重建 + 同步（不访问 Zenodo）")
        backfill_doi(args.doi)
        if not args.skip_rebuild:
            rebuild_docx()
            sync_pkg()
    elif not args.no_zenodo and args.zenodo_token:
        try:
            doi = zenodo_upload(args.zenodo_token, proxy=args.proxy)
            backfill_doi(doi)
            if not args.skip_rebuild:
                rebuild_docx()
                sync_pkg()
        except Exception as e:
            log(f"❌ Zenodo 步骤失败: {e}")
            log("  若网络不可达或 token 无效，请在有网机器重跑，或先手动在 Zenodo 网页建归档后用 --doi 回填。")
    else:
        log("步骤 B/C/D/E: 跳过 Zenodo（--no-zenodo 或未提供 --zenodo-token）。")
        log("  如需回填 DOI，请: python deploy_submission.py --doi 10.5281/zenodo.XXXX --no-zenodo")

    log("=" * 60)
    log("脚本结束。")
    if not push_ok and not args.skip_push:
        log("⚠ git push 未成功，请在稳定网络环境重跑本脚本或手动 `git push origin master`。")
    log("=" * 60)


if __name__ == "__main__":
    main()
