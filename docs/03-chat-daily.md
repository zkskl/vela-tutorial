# 03 — Chat Harian lewat WebSocket IM

Chat dikirim dari akun user ke bot miliknya sendiri.

## Alur

1. `POST /v1/collaboration/me/im/session` → kredensial IM:
   `sdkAppId`, `userId`, `userSig`.
2. Buka WebSocket ke endpoint IM platform (format umum
   `wss://<HOST_IM>/ws?sdkappid=<SDK_APP_ID>&usersig=<USER_SIG>&identifier=<USER_ID>&random=<RAND>&apiVersion=...`).
3. Login (`login`), lalu `sendmsg` ke `bot.userId`.
4. Cek `retcode == 0` di `head` respons.

## Kerangka minimal

```python
def chat_once(session, bot_user_id, text, ws_connect, TimClient, retries=3):
    for attempt in range(retries):
        creds = session.post(f"{API}/v1/collaboration/me/im/session").json()
        if not creds.get("sdkAppId"):
            time.sleep(4); continue          # sesi IM belum siap
        ws = ws_connect(creds["sdkAppId"])
        client = TimClient(ws, creds["sdkAppId"])
        login = client.login(creds["userId"], creds["userSig"])
        if (login.get("head") or {}).get("retcode") != 0:
            ws.close(); time.sleep(3); continue
        resp = client.sendmsg(bot_user_id, text)
        ws.close()
        if (resp.get("head") or {}).get("retcode") == 0:
            return True
        time.sleep(3)
    return False
```

## Jeda & anti-flag

- **Sekuensial satu akun pada satu waktu**, jeda acak **4–7 detik**.
- Kalau gagal: jeda tambahan 10–15 detik sebelum retry.
- Variasikan isi pesan (mis. kombinasikan sapaan + topik) supaya tidak identik.
- Log per akun (JSONL) supaya bisa **resume**: akun yang sudah `ok` hari itu dilewati.
