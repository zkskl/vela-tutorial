# -*- coding: utf-8 -*-
"""Chat harian ke bot tiap instance — sekuensial, jeda 4-7 detik, resume dari log.

Pakai:
  python scripts/chat_daily.py            # kirim ke semua yang belum ok hari ini
  python scripts/chat_daily.py --dry      # hanya cek prasyarat
"""
import json, os, random, sys, time

from lightvela_client import API, load_sessions, make_session

OPEN = ["halo", "hai", "pagi", "siang", "sore", "eh", "oi", "hey"]
CORE = ["lagi apa hari ini", "udah makan belum", "sibuk ga sekarang",
        "hari ini gimana", "kabar kamu gimana", "semangat ya hari ini"]

DB = os.environ.get("SESSION_DB", "/tmp/sess.sqlite")
CJ = os.environ.get("CONTAINERS_JSON", "/tmp/containers.json")
LOG = os.path.join("logs", f"chat_{time.strftime('%Y%m%d')}.jsonl")
DRY = "--dry" in sys.argv
os.makedirs("logs", exist_ok=True)


def done():
    if not os.path.exists(LOG):
        return set()
    out = set()
    for line in open(LOG, encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("status") == "ok":
            out.add(r["name"])
    return out


def msg(seed, used):
    r = random.Random(seed)
    m = f"{r.choice(OPEN)} {r.choice(CORE)}"
    for _ in range(200):
        if m not in used:
            break
        m = f"{r.choice(OPEN)} {r.choice(CORE)}"
    used.add(m)
    return m


def chat(session, bot_user_id, text, ws_connect, TimClient, retries=3):
    for _ in range(retries):
        creds = session.post(f"{API}/v1/collaboration/me/im/session", timeout=30).json()
        if not creds.get("sdkAppId"):
            time.sleep(4); continue
        ws = ws_connect(creds["sdkAppId"])
        c = TimClient(ws, creds["sdkAppId"])
        lg = c.login(creds["userId"], creds["userSig"])
        if (lg.get("head") or {}).get("retcode") != 0:
            ws.close(); time.sleep(3); continue
        r = c.sendmsg(bot_user_id, text); ws.close()
        if (r.get("head") or {}).get("retcode") == 0:
            return True, "ok"
        time.sleep(3)
    return False, "fail"


def main():
    sys.path.insert(0, os.path.dirname(__file__))
    import im_client  # modul WebSocket IM milikmu (sdkAppId/userSig)
    rows = load_sessions(DB, CJ)
    skip, used = done(), set()
    todo = [r for r in rows if r["name"] not in skip]
    print(f"total {len(rows)} · sudah ok {len(skip)} · sisa {len(todo)}")
    if DRY:
        for r in todo:
            print("  akan dikirim:", r["name"]); 
        return
    for i, row in enumerate(todo, 1):
        s = make_session(row["cookie"])
        bots = (s.get(f"{API}/v1/collaboration/me/bots", timeout=25).json() or {}).get("items") or []
        if not bots:
            print(f"[{i}/{len(todo)}] {row['name']} skip: no bot")
            continue
        text = msg(abs(hash(row["name"])) % 100000, used)
        ok, status = chat(s, bots[0]["userId"], text, im_client.ws_connect, im_client.TimClient)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"name": row["name"], "status": status, "msg": text}) + "\n")
        print(f"[{i}/{len(todo)}] {row['name']:16s} {status}")
        time.sleep(12 if not ok else random.uniform(4, 7))


if __name__ == "__main__":
    main()
