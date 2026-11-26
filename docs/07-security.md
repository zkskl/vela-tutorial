# 07 — Keamanan Data (baca sebelum commit)

Repo tutorial ini **tidak boleh** memuat data operasional siapa pun.

## Jangan pernah commit

| Data | Contoh |
|---|---|
| Cookie session | nilai `lc_session` |
| File database browser | `cookies.sqlite`, `containers.json` |
| Email / akun | alamat email asli |
| Host / IP infra | IP relay, IP VPS, tunnel URL |
| Alamat wallet / pool | string base58 alamat pool |
| Nama worker asli | `<prefix>-<8 hex>` milikmu |
| Log operasional | `*.jsonl`, `*.log` berisi akun |

## Aturan penyimpanan

```bash
chmod 600 .env cookies.sqlite        # hanya pemilik yang bisa baca
cp cookies.sqlite /tmp/sess.sqlite   # salinan read-only untuk dipakai skrip
```

- Simpan kredensial **di luar** direktori repo (`/etc/agent/.env`, `~/.config/...`).
- Jangan pernah menempel token/cookie ke chat, issue, atau commit message.
- Sebelum `git push`, jalankan pemindai kebocoran:

```bash
grep -rEn '(session=|@[a-z]+\.[a-z]{2,}|[0-9]{1,3}(\.[0-9]{1,3}){3}|https?://[a-z0-9-]+\.(ngrok|trycloudflare|localtunnel)\.[a-z]+)' .
grep -rEn '[1-9A-HJ-NP-Za-km-z]{40,}' .    # kandidat alamat wallet/pool
```

Kalau ada hasil → **jangan push**, bersihkan dulu.

## .gitignore minimal

```gitignore
.env
*.sqlite
*.sqlite-*
*.jsonl
*.log
logs/
.venv/
__pycache__/
```
