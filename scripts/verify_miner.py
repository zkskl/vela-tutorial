# -*- coding: utf-8 -*-
"""Verifikasi miner per instance: jumlah proses, pool-url, worker, load, RAM."""
import os, sys

from lightvela_client import exec_cmd, instances, load_sessions, make_session, auth

DB = os.environ.get("SESSION_DB", "/tmp/sess.sqlite")
CJ = os.environ.get("CONTAINERS_JSON", "/tmp/containers.json")
BIN = os.environ.get("MINER_BIN", "miner")

CMD = (f"echo S=$(pgrep -x {BIN} | wc -l); "
       f"ps -eo args | grep '[{BIN[0]}]{BIN[1:]} --pool' | head -1 | grep -o 'stratum+[^ ]*'; "
       f"ps -eo args | grep '[{BIN[0]}]{BIN[1:]} --pool' | head -1 | grep -o -- '--pool-worker [^ ]*'; "
       "cat /proc/loadavg | cut -d' ' -f1; free -m | awk '/Mem:/{print $7}'")

for row in load_sessions(DB, CJ):
    s = make_session(row["cookie"])
    _, hh = auth(s)
    its = instances(s, hh)
    if not its:
        print(f"{row['name']:16s} no-instance"); continue
    out = exec_cmd(s, hh, its[0]["instance_id"], CMD)
    print(f"{row['name']:16s} {out.replace(chr(10), ' | ')[:120]}")
