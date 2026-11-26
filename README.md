# Vela Sandbox Automation — Tutorial

Panduan publik untuk mengotomasi siklus harian akun sandbox **Vela (LightVela)**:

1. menyiapkan akun & instance,
2. membuat bot IM untuk tiap instance,
3. mengirim pesan harian ke bot (chat daily),
4. klaim *active renewal* (+1 bulan) saat eligible,
5. opsional: menjalankan miner di dalam sandbox,
6. merangkai semuanya jadi agent otomatis (cron + guardrail).

> Repo ini **tanpa data pribadi**: semua nilai rahasia memakai placeholder
> (`<...>`) dan harus diisi sendiri di file `.env` yang tidak di-commit.

## Prasyarat

- Python 3.10+ (`requests` / `curl_cffi`), `bash`, akses HTTP keluar.
- Satu akun platform per container/instance (cookie `lc_session` disimpan browser).
- Untuk chat: WebSocket ke layanan IM platform (butuh `sdkAppId`, `userId`, `userSig`).
- Untuk miner (opsional): binary miner pihak ketiga, pool milik sendiri.

## Peta dokumen

| Dokumen | Isi |
|---|---|
| [docs/01-instance.md](docs/01-instance.md) | Akun, instance, cookie session |
| [docs/02-bot-im.md](docs/02-bot-im.md) | Membuat bot IM via API |
| [docs/03-chat-daily.md](docs/03-chat-daily.md) | Chat harian lewat WebSocket IM |
| [docs/04-renewal.md](docs/04-renewal.md) | Eligibility & klaim renewal |
| [docs/05-mining.md](docs/05-mining.md) | Miner di sandbox (opsional) |
| [docs/06-agent.md](docs/06-agent.md) | Merangkai jadi agent otomatis |
| [docs/07-security.md](docs/07-security.md) | Aturan keamanan data |

## Mulai cepat

```bash
git clone <URL_REPO_INI> vela-tutorial
cd vela-tutorial
cp .env.example .env        # isi kredensial sendiri
python -m venv .venv && . .venv/bin/activate
pip install requests curl_cffi websocket-client
python scripts/chat_daily.py --dry
```

## Etika & batasan

- Gunakan hanya pada akun yang kamu miliki / diizinkan.
- Patuhi Terms of Service platform dan hukum setempat.
- Semua jeda (jitter) di repo ini ada supaya trafik tetap wajar — jangan dihapus.

Lisensi: MIT.
