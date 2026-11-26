# -*- coding: utf-8 -*-
"""Helper: muat session per container dari salinan cookies.sqlite (read-only)."""
import json, os, sqlite3

API = os.environ.get("API_BASE", "https://api.example-platform.tld").rstrip("/")
DOMAIN = os.environ.get("DOMAIN_PLATFORM", "example-platform.tld")


def load_sessions(db_path, containers_json):
    db = sqlite3.connect(f"file:{db_path}?mode=ro&immutable=1", uri=True)
    cookies = {}
    for oa, val in db.execute(
        "select originAttributes, value from moz_cookies "
        "where host like ? and name='lc_session'", (f"%{DOMAIN}%",)
    ):
        uc = int(oa.split("userContextId=")[-1]) if "userContextId=" in oa else 0
        cookies[uc] = val
    names = {}
    if os.path.exists(containers_json):
        names = {c["userContextId"]: (c.get("name") or "")
                 for c in json.load(open(containers_json, encoding="utf-8")).get("identities", [])}
    return [{"uc": uc, "name": names.get(uc) or f"uc{uc}", "cookie": val}
            for uc, val in sorted(cookies.items())]


def make_session(cookie):
    from curl_cffi import requests as creq
    s = creq.Session(impersonate="chrome")
    s.cookies.set("lc_session", cookie, domain=DOMAIN)
    return s


def auth(session):
    """-> (session dict, headers ber-token)"""
    h = {"Accept": "application/json",
         "Origin": f"https://{DOMAIN}", "Referer": f"https://{DOMAIN}/"}
    ss = (session.get(f"{API}/auth/session", timeout=25).json() or {}).get("session") or {}
    return ss, {**h, "Authorization": f"Bearer {ss.get('sessionToken')}"}


def instances(session, headers):
    d = (session.get(f"{API}/v1/instances", headers=headers, timeout=25).json() or {}).get("data") or {}
    return d.get("items") or []


def exec_cmd(session, headers, instance_id, command, timeout=120, user="agentuser"):
    body = {"command": command, "run_as_user": user, "execution_backend": "tat"}
    r = session.post(f"{API}/v1/instances/{instance_id}/debug/exec",
                     headers=headers, json=body, timeout=timeout).json()
    return ((r.get("data") or {}).get("output") or "").strip()
