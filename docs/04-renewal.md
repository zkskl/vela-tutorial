# 04 — Klaim Active Renewal (+1 bulan)

## Cek eligibility

```http
GET /v1/passes/active-renewal/eligibility
```

Field penting di `data`:

| Field | Arti |
|---|---|
| `active_days` | umur aktif akun (hari) |
| `eligible` | `true` kalau siklus sudah memenuhi syarat |
| `claim_status` | `delivered` · `unclaimed` · `reserved` |

Arti status:

- **delivered** — renewal sudah diberikan platform. Tidak perlu diapa-apakan.
- **unclaimed** — tersedia dan bisa diklaim.
- **reserved** — belum waktunya/tertahan; tunggu siklus berikutnya.

## Klaim

```http
POST /v1/passes/active-renewal/claim
{}
```

Hanya jalankan kalau `eligible == true` **dan** `claim_status == "unclaimed"`.

## Pola aman (yang dipakai repo ini)

```python
ok = e.get("eligible") and e.get("claim_status") == "unclaimed"
if ok:
    r = session.post(f"{API}/v1/passes/active-renewal/claim", json={})
    time.sleep(6)
    after = session.get(f"{API}/v1/passes").json()   # verifikasi
```

- **Sekuensial**, jeda **60–105 detik** setiap klaim berhasil.
- Pakai **lock file** supaya dua proses tidak klaim akun yang sama:

```python
import os, sys
LOCK = "claim.lock"
if os.path.exists(LOCK):
    sys.exit("proses lain sedang jalan")
open(LOCK, "w").close()
```

- Jangan pernah burst-paralel: klaim dobel/flag lebih mahal daripada waktu tunggu.
