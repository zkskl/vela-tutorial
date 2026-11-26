# 06 — Merangkai Jadi Agent Otomatis

Tujuan: agent menjalankan tiga rutinitas harian tanpa menyentuh data sensitif di repo.

## Struktur yang disarankan

```
agent/
├── check.py      # status miner + eligibility renewal (read-only)
├── chat.py       # chat harian, resume dari log
├── claim.py      # klaim renewal (jeda panjang + lock)
└── logs/         # JSONL per tugas per batch per tanggal
```

Semua skrip membaca kredensial dari `.env` / file session di luar repo.

## Prinsip yang membuat agent tidak merusak data

1. **Read-only dulu.** Cek status sebelum mengubah apa pun; laporkan temuan.
2. **Idempoten.** Log `ok` per akun per hari → jalankan ulang hanya mengerjakan sisa.
3. **Sekuensial + jitter.** Tidak ada paralel agresif untuk aksi yang menyentuh akun.
4. **Gagal = lapor.** Jangan retry buta; rekam error mentah lalu pindah akun.
5. **Verifikasi setelah aksi.** Klaim → cek `/v1/passes`; miner → cek `accepted`.

## Contoh cron harian

```cron
15 7 * * *  cd /opt/agent && . .venv/bin/activate && python check.py  >> logs/check.log 2>&1
30 7 * * *  cd /opt/agent && . .venv/bin/activate && python chat.py   >> logs/chat.log  2>&1
10 9 * * *  cd /opt/agent && . .venv/bin/activate && python claim.py  >> logs/claim.log 2>&1
```

Tambahkan lock file pada `claim.py`, dan pastikan dua cron tidak menumpuk
(mis. `flock -n /tmp/claim.lock`).

## Kalau memakai LLM sebagai operator

- Beri agent **hanya** akses baca untuk observasi; aksi destruktif harus eksplisit.
- Semua nilai rahasia di-inject lewat environment, **bukan** di prompt atau repo.
- Minta agent menulis bukti (nama worker, `accepted`, tx/log) sebelum menyatakan selesai.
