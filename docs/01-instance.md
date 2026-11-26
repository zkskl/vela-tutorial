# 01 — Akun, Instance, dan Cookie Session

## 1. Akun & instance

1. Daftar akun di situs platform (`https://<DOMAIN_PLATFORM>`).
2. Buat instance sandbox (nama bebas, mis. `My AI Companion`).
3. Satu instance = satu sandbox Linux yang bisa di-`exec` lewat API debug.

## 2. Cookie session

Autentikasi memakai cookie `lc_session` (di-set saat login di browser).

Menyimpan cookie ke file (contoh dengan Firefox container):

1. Buka profil Firefox khusus, login akun.
2. Tutup browser (supaya `cookies.sqlite` tidak terkunci).
3. Salin **read-only**:

```bash
cp "<PROFILE_DIR>/cookies.sqlite" /tmp/sess.sqlite
```

> Jangan pernah menyalin cookie ke dalam repo git. Lihat `docs/07-security.md`.

## 3. Membaca cookie + identitas container

```python
import json, sqlite3

def load_sessions(db_path, containers_json):
    db = sqlite3.connect(f"file:{db_path}?mode=ro&immutable=1", uri=True)
    cookies = {}
    for oa, val in db.execute(
        "select originAttributes, value from moz_cookies "
        "where host like '%<DOMAIN_PLATFORM>%' and name='lc_session'"
    ):
        uc = int(oa.split("userContextId=")[-1]) if "userContextId=" in oa else 0
        cookies[uc] = val
    names = {c["userContextId"]: c.get("name") or ""
             for c in json.load(open(containers_json))["identities"]}
    return [{"uc": uc, "name": names.get(uc), "cookie": val}
            for uc, val in sorted(cookies.items())]
```

`userContextId` = id container Firefox; `name` = label container.

## 4. Endpoint dasar

| Fungsi | Method & path |
|---|---|
| Sesi & user | `GET /auth/session` |
| Daftar instance | `GET /v1/instances` |
| Exec di instance | `POST /v1/instances/{instance_id}/debug/exec` |

Body exec:

```json
{"command": "echo hello", "run_as_user": "agentuser", "execution_backend": "tat"}
```

Catatan penting:

- User `agentuser` **bukan root**; `sudo` akan minta password.
- Output exec bisa kosong walau perintah jalan (timeout/DNS) → selalu verifikasi ulang.
- Pecah perintah panjang jadi 2–3 perintah pendek; pipe bertingkat sering hilang output.
