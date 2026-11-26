# 05 — Miner di Sandbox (opsional)

Kalau sandbox dipakai untuk mining, ini pola yang aman dan bisa diverifikasi.

## Aturan dasar

1. **Satu instance = satu proses miner.** Dua miner di satu box saling mencuri CPU/RAM
   dan justru menurunkan hasil.
2. Jalankan sebagai **user biasa** (bukan root) bila sandbox tidak memberi root.
3. Catat **nama worker unik** per box dan simpan ke CSV — tanpa itu kamu tidak bisa
   membuktikan box mana menghasilkan share.
4. Verifikasi memakai **share `accepted`**, bukan hashrate lokal.

## Pola pasang (tanpa systemd, user biasa)

```bash
pkill -x <NAMA_BINER> 2>/dev/null; sleep 2
mkdir -p ~/miner/bin
B=$(find ~/miner/bin -maxdepth 2 -type f -name <NAMA_BINER> | head -1)
[ -x "$B" ] || ( cd ~/miner/bin && curl -fsSL -m 240 "<URL_TARBALL_MINER>" -o m.tgz && tar xzf m.tgz && rm -f m.tgz )
B=$(find ~/miner/bin -maxdepth 2 -type f -name <NAMA_BINER> | head -1); chmod +x "$B"
cd $(dirname "$B")
setsid nohup "$B" --pool-url "stratum+tcp://<POOL_HOST:PORT>" \
  --pool-worker "vm-$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')" \
  --address "<ALAMAT_POOL_KAMU>" --threads 2 --allow-oversubscribe \
  --cpu-page-mode auto > ~/miner.log 2>&1 < /dev/null &
sleep 20
echo "proses=$(pgrep -x <NAMA_BINER> | wc -l)"
grep -c "new job" ~/miner.log
```

Catatan penting:

- Variabel yang di-set di dalam subshell `( ... )` **hilang** setelah blok selesai.
  Baca ulang path binary **setelah** blok download, jangan di dalamnya.
- `--threads 2` sering butuh `--allow-oversubscribe` di box kecil.
- Pool yang kamu pakai adalah pilihanmu sendiri; repo ini tidak menyertakan alamat pool.

## Verifikasi (wajib)

```bash
# jumlah proses (jangan pakai pgrep -xc sendirian: exit code 1 saat nol match)
echo "S=$(pgrep -x <NAMA_BINER> | wc -l)"

# pool yang benar-benar dipakai
ps -eo args | grep '[<NAMA_BINER>] --pool' | grep -o 'stratum+[^ ]*'

# share nyata dari pool API (akun kamu)
curl -s "https://<POOL_API>/api/miner/<ALAMAT_POOL_KAMU>" | head -c 300
```

Yang dianggap **bukti sehat**: `accepted` naik antar dua snapshot 5 menit,
`rejected` 0, dan `new job` bertambah di log.
