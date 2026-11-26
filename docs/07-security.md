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
# 1) cookie/token literal, email, dan alamat IPv4
grep -rEn '(session=[A-Za-z0-9+/=]{8,}|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|[0-9]{1,3}(\.[0-9]{1,3}){3})' .
# 2) kandidat alamat wallet/pool (base58 panjang)
grep -rEn '[1-9A-HJ-NP-Za-km-z]{40,}' .
# 3) URL tunnel/domain sementara milikmu (cek manual, host-nya spesifik)
grep -rEn 'https?://[a-z0-9-]+\.[a-z]+' . | grep -v 'example\|schema'
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
