# -*- coding: utf-8 -*-
"""Klaim active-renewal — sekuensial, jeda 60-105 detik, lock file, resume.

Pakai:
  python scripts/claim_renewal.py --dry     # cek eligibility saja
  python scripts/claim_renewal.py           # klaim yang eligible & unclaimed
"""
import json, os, random, sys, time

from lightvela_client import API, DOMAIN, load_sessions, make_session

DB = os.environ.get("SESSION_DB", "/tmp/sess.sqlite")
CJ = os.environ.get("CONTAINERS_JSON", "/tmp/containers.json")
H = {"Accept": "application/json",
     "Origin": f"https://{DOMAIN}", "Referer": f"https://{DOMAIN}/"}
LOCK = "/tmp/claim.lock"
LOG = os.path.join("logs", f"claim_{time.strftime('%Y%m%d')}.jsonl")
DRY = "--dry" in sys.argv
os.makedirs("logs", exist_ok=True)

if os.path.exists(LOCK) and not DRY:
    sys.exit("lock ada — proses lain sedang jalan")


def eligibility(s):
    r = s.get(f"{API}/v1/passes/active-renewal/eligibility", headers=H, timeout=25).json()
    return r.get("data") or {}


def main():
    if not DRY:
        open(LOCK, "w").close()
    try:
        rows = load_sessions(DB, CJ)
        for i, row in enumerate(rows, 1):
            s = make_session(row["cookie"])
            e = eligibility(s)
            out = {"name": row["name"], "days": e.get("active_days"),
                   "eligible": e.get("eligible"), "claim_status": e.get("claim_status")}
            if e.get("eligible") and e.get("claim_status") == "unclaimed" and not DRY:
                r = s.post(f"{API}/v1/passes/active-renewal/claim", headers=H, json={}, timeout=40)
                out["http"] = r.status_code
                out["status"] = "claimed" if r.status_code < 300 else "fail"
                time.sleep(6)
                out["after"] = (s.get(f"{API}/v1/passes", headers=H, timeout=25).json() or {})
            else:
                out["status"] = "dry" if DRY else "skip"
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(out, ensure_ascii=False)[:900] + "\n")
            print(f"[{i}/{len(rows)}] {row['name']:16s} {out['status']:8s} "
                  f"days={out['days']} elig={out['eligible']} cs={out['claim_status']}")
            time.sleep(random.uniform(60, 105) if out.get("status") == "claimed"
                       else random.uniform(3, 6))
    finally:
        if os.path.exists(LOCK) and not DRY:
            os.remove(LOCK)


if __name__ == "__main__":
    main()
