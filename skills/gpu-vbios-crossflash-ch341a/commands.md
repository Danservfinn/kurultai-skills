# Commands

Placeholder conventions:
- `<CHIP>` — the exact chip name string printed by `flashrom -p ch341a_spi` in Step 5 (e.g. `M25P80`, `"MX25L8006E/MX25L8008"`). Quote it in the shell if it contains `/`.
- `<ROM_URL>` — a working URL for the WX9100 ROM (see Step 1 source list).
- All other commands are literal.

## Step 1 — download VBIOS
```bash
# primary (may fail: TechPowerUp bot check)
curl -L -o WX9100_BIOS.rom \
  "https://www.techpowerup.com/vgabios/218718/AMD.WX9100.16384.171219.rom"
# fallback A: known Wayback snapshot
curl -L -o WX9100_BIOS.rom \
  "https://web.archive.org/web/20241117031505/https://www.techpowerup.com/vgabios/218718/AMD.WX9100.16384.171219.rom"
# fallback B: alternate build snapshot (ID 217771, date 180922)
curl -L -o WX9100_BIOS.rom \
  "https://web.archive.org/web/20231221081036/https://www.techpowerup.com/vgabios/217771/AMD.WX9100.16384.180922.rom"
# fallback C: find any snapshot via CDX API
curl -s "http://web.archive.org/cdx/search/cdx?url=techpowerup.com/vgabios/218718/AMD.WX9100.16384.171219.rom&output=text&fl=timestamp,original,statuscode&filter=statuscode:200&limit=5"
# then: curl -L -o WX9100_BIOS.rom "https://web.archive.org/web/<TIMESTAMP>/<ORIGINAL_URL>"
```

## Step 2 — verify image
```bash
stat -c%s WX9100_BIOS.rom   # Linux; expect 262144
stat -f%z WX9100_BIOS.rom   # macOS; expect 262144
file WX9100_BIOS.rom        # accept any variant containing 0x1002:0x6861
xxd WX9100_BIOS.rom | grep -i 6861        # fallback device check
strings WX9100_BIOS.rom | grep -i "113-D051"  # fallback SKU check
```

## Step 3 — pad to 1 MiB
```bash
dd if=/dev/zero of=pad.bin bs=1k count=768
cat WX9100_BIOS.rom pad.bin > WX9100_171219_padded.rom
stat -c%s WX9100_171219_padded.rom   # expect 1048576
```

## Step 4 — USB detection
```bash
lsusb | grep 1a86
dmesg | grep -i ch341
```

## Step 5 — chip detection (read-only)
```bash
flashrom -p ch341a_spi
```

## Step 6 — double backup
```bash
flashrom -p ch341a_spi -c <CHIP> -r mi25_backup1.rom
flashrom -p ch341a_spi -c <CHIP> -r mi25_backup2.rom
sha1sum mi25_backup1.rom mi25_backup2.rom   # hashes must match EACH OTHER
cp mi25_backup1.rom /somewhere/safe/
```

## Step 7 — flash
```bash
flashrom -p ch341a_spi -c <CHIP> -w WX9100_171219_padded.rom -V
# expect: "Verifying flash... VERIFIED."
```

## Step 8 — post-boot verification
```bash
lspci -nn | grep Vega     # expect 1002:6861 Radeon Pro WX 9100
rocm-smi
```

## Step 9 — revert
```bash
flashrom -p ch341a_spi -c <CHIP> -w mi25_backup1.rom -V