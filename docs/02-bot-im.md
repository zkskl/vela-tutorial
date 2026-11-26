# 02 — Membuat Bot IM via API

Setiap instance punya satu akun chat; bot IM dipakai sebagai lawan bicara.

## Cek bot yang sudah ada

```http
GET /v1/collaboration/me/bots
```

Respons: `{"items": [ ... ]}`. Kalau `items` kosong → belum ada bot.

## Buat bot

```http
POST /v1/collaboration/me/bots
{"instanceId": "<INSTANCE_ID>", "botId": "<INSTANCE_ID>", "displayName": "<NAMA_BOT>"}
```

Perilaku yang wajar terjadi:

- HTTP **502** sering muncul **padahal bot tetap dibuat** → jangan langsung retry buta, poll dulu.
- Status bot berpindah `provisioning` → `ready` dalam ±1–2 menit.
- Error `bot_host_delivery_failed` → hapus lalu buat ulang:

```http
DELETE /v1/collaboration/me/bots/<ID_BOT_UUID>
```

## Pola polling yang benar

```python
import time

def ensure_bot(session, instance_id, name, tries=3):
    for attempt in range(tries):
        r = session.post(f"{API}/v1/collaboration/me/bots", json={
            "instanceId": instance_id, "botId": instance_id, "displayName": name})
        if r.status_code in (200, 201, 502):
            for _ in range(40):          # tunggu maks ~2 menit
                items = session.get(f"{API}/v1/collaboration/me/bots").json().get("items") or []
                ready = [b for b in items if b.get("status") == "ready"]
                if ready:
                    return ready[0]
                time.sleep(3)
        time.sleep(5)
    raise RuntimeError("bot tidak siap")
```

Aturan praktis:

- Proses **sekuensial**, jeda 3–5 detik antar instance.
- Jangan paralel agresif: endpoint ini rawan 429/502.
