---
name: gpu-vbios-crossflash-ch341a
description: Cross-flash an AMD MI25 server GPU with a WX 9100 VBIOS via external CH341A SPI programmer to enable display outputs, fan header, and consumer-board boot
category: infrastructure
---
```

# MI25 → WX 9100 VBIOS Cross-Flash via CH341A

## Goal
Flash a Radeon Pro WX 9100 VBIOS onto an AMD Radeon Instinct MI25 (Vega 10, gfx900, 16GB HBM2) using an external CH341A SPI programmer, converting a passive server card (PCI 1002:6860) into a WX 9100 (PCI 1002:6861) with working miniDP, fan header, and consumer-motherboard boot.

## Inputs
- AMD Radeon Instinct MI25 card, removed from any PC, backplate off (SPI chip exposed)
- CH341A USB SPI programmer with SOIC8 clip and green ZIF adapter board — **no 1.8V adapter** (chip is 3.3V; the 1.8V adapter underpowers it)
- Linux host with `flashrom` ≥ 1.2 (ch341a_spi support), `curl`, `dd`, `file`, `sha1sum`
- Internet access for VBIOS download (no API key required)

## Steps
1. **Download the WX 9100 VBIOS.** Try sources in order until one yields a 262144-byte file: (a) TechPowerUp BIOS page ID 218718 (`https://www.techpowerup.com/vgabios/218718/amd-wx9100-16384-171219`) — note TechPowerUp runs a JS bot check and blocks some IPs, so direct `curl` may fail; (b) the Wayback Machine snapshot of that ROM (`https://web.archive.org/web/20241117031505/https://www.techpowerup.com/vgabios/218718/AMD.WX9100.16384.171219.rom`); (c) Wayback snapshot of the alternate build, TechPowerUp ID 217771 date 180922 (`https://web.archive.org/web/20231221081036/https://www.techpowerup.com/vgabios/217771/AMD.WX9100.16384.180922.rom`); (d) query the Wayback CDX API for any other snapshot of either ROM URL. Save as `WX9100_BIOS.rom`.
2. **Verify the image.** Check size is exactly 262144 bytes (`stat -f%z` on macOS / `stat -c%s` on Linux). Check it is an AMD option ROM containing device 0x6861: run `file WX9100_BIOS.rom` and accept any output matching `PCI ... ROM ... 0x1002:0x6861` (exact wording varies by `file` version); as a fallback grep the raw bytes: `xxd WX9100_BIOS.rom | grep -i 6861` or `strings WX9100_BIOS.rom | grep -i "113-D051"` (WX 9100 VBIOS SKU string). Do not proceed on a mismatch or wrong size.
3. **Pad to 1 MiB.** `dd if=/dev/zero of=pad.bin bs=1k count=768` then `cat WX9100_BIOS.rom pad.bin > WX9100_171219_padded.rom`. Confirm the padded file is exactly 1048576 bytes.
4. **Wire the hardware.** Leave the 1.8V adapter OUT of the CH341A ZIF socket (stock 3.3V only). Insert the green SOIC8 adapter board, pin-1/notch aligned with the ZIF notch, close the lever. Clip onto the M25P80 chip with pin 1 (dot on chip) aligned to pin 1 on the clip (red stripe/triangle); press firmly so all 8 legs are grabbed. Plug the CH341A into USB and confirm detection: `lsusb | grep 1a86` and `dmesg | grep -i ch341`.
5. **Detect the chip (read-only).** Run `flashrom -p ch341a_spi` with no `-c` flag and note the exact chip name flashrom reports (e.g. `M25P80`, `MX25L8006E/MX25L8008`, `W25Q80`, `GD25Q80` — MI25 units vary). Use that reported name as `<CHIP>` in all later commands. If the read is all 0xFF: (a) remove any 1.8V adapter — the #1 cause; (b) press the clip down harder on the pin-2/DO side and wiggle; (c) flip the green ZIF adapter 180° — but change only ONE thing at a time. Diagnostic: card LEDs/coil whine with 0xFF reads means VCC+GND connect but data lines don't; when flashrom runs and coil whine stops, CS/CLK/DI work and only DO remains. Allow ~30 min to find the clip sweet spot.
6. **Back up the original BIOS twice.** `flashrom -p ch341a_spi -c <CHIP> -r mi25_backup1.rom` and again to `mi25_backup2.rom`. Run `sha1sum` on both — the two hashes MUST match each other before proceeding (self-consistency check; the hash will differ per card/OEM revision, so do not compare against any external "expected" hash). If they differ, reseat the clip and re-read until identical. Copy `mi25_backup1.rom` somewhere safe — it is the only path back to stock.
7. **Flash.** `flashrom -p ch341a_spi -c <CHIP> -w WX9100_171219_padded.rom -V`. Confirm the output contains `Verifying flash... VERIFIED.`
8. **Reinstall and boot.** Unplug the CH341A, remove the clip, refit the backplate. Install in a PCIe slot and **connect the 6-pin PCIe power** (forgetting it triggers a piezo alarm — annoying, not damaging). Attach a fan: zip-tie one to the heatsink or wire a 4-pin fan to the card's JST-PH header (enabled by the WX9100 BIOS, runs 100%). The card is passive and will overheat even at idle without airflow. Boot and verify: `lspci -nn | grep Vega` should show `1002:6861` Radeon Pro WX 9100; `rocm-smi` should report the GPU.
9. **Revert (if needed).** `flashrom -p ch341a_spi -c <CHIP> -w mi25_backup1.rom -V` — same clip procedure, writing the backup instead.

## Outputs
- `WX9100_171219_padded.rom` — 1 MiB flashable image
- `mi25_backup1.rom` — verified (double-read, matching sha1) original MI25 BIOS backup
- Card reporting as PCI `1002:6861` Radeon Pro WX 9100 with working miniDP and fan header

## Failure modes
- **1.8V adapter left in** — underpowers the 3.3V SPI chip; reads all 0xFF. Remove it.
- **Flaky clip connection** — the two backup sha1sums differ; reseat clip and re-read until they match.
- **All BIOS download sources dead** — Wayback snapshots can expire; use the CDX API to find new snapshots or fetch the TechPowerUp page in a real browser.
- **Wrong-size or non-0x6861 image** — flashrom would write garbage; the Step 2 gate catches this before any hardware touch.
- **Chip name mismatch** — hardcoding `-c M25P80` fails or misdrives on cards with MX25L/W25Q/GD25Q variants; always use the name from Step 5 detection.
- **Forgetting 6-pin PCIe power on reinstall** — piezo alarm (not damage); plug it in.
- **Overheating** — passive card needs a zip-tied fan even at idle.
- **Power limit 170W vs 150W slot+6-pin headroom** — clocks stutter under sustained load; flatten P-states if it matters.

## Source
Discord thread `1316137596535177246/1527763878040309900` ("MI25 to WX9100", 2026-08-29) and attached `MI25-to-WX9100-FLASH-GUIDE.txt` (reconstructed 2026-07-17). Key quotes: "!! DO NOT use the 1.8V adapter — chip is 3.3V, adapter underpowers it = all 0xFF"; "read twice, sha1sum must match"; "flashrom -p ch341a_spi -c M25P80 -w WX9100_171219_padded.rom -V -> Verifying flash... VERIFIED."