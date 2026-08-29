# Examples

## Example 1 — Happy path, M25P80 chip
```
Input: MI25 card on desk, backplate off. CH341A + SOIC8 clip, no 1.8V adapter.
Fedora laptop with flashrom 1.4.0.

Step 1: curl of techpowerup.com direct ROM fails (bot check).
        curl of the 20241117031505 Wayback snapshot succeeds → WX9100_BIOS.rom
Step 2: stat → 262144 bytes. file → "PCI ISA ROM image (PCI device
        0x1002:0x6861, ...)" — device matches, proceed.
Step 3: dd + cat → WX9100_171219_padded.rom, 1048576 bytes.
Step 5: flashrom -p ch341a_spi → "Found Micron/Numonyx/ST flash chip
        'M25P80' (1024 kB, SPI)" → <CHIP>=M25P80
Step 6: two reads, sha1sums match each other (e.g. both
        ce861229e5d96f5cfc89ae88b56bb11f26f6eeff on the original session's
        card — yours will differ). Backup copied off-host.
Step 7: flashrom -w ... -V → "Verifying flash... VERIFIED."
Step 8: lspci -nn | grep Vega → "Vega [Radeon Pro WX 9100] [1002:6861]"
```

## Example 2 — All 0xFF on detection (1.8V adapter installed)
```
Symptom: flashrom -p ch341a_spi reads all 0xFF; card LEDs lit, coil whine.
Diagnosis per guide: VCC+GND connected, data lines not.
Fix sequence (one change at a time):
  1. Remove 1.8V adapter from ZIF socket, clip direct to CH341A → retry.
  2. Still 0xFF: press clip down on pin-2/DO side, wiggle → retry.
     (Coil whine stops during flashrom = CS/CLK/DI now good.)
  3. Still 0xFF: flip green ZIF adapter 180° → retry.
Result after ~30 min: instant detection of M25P80. Continue at Step 6.
```

## Example 3 — Different SPI chip variant + dead Wayback snapshot
```
Step 1: primary Wayback snapshot returns 404.
        Fallback: query Wayback CDX API for the ROM URL, find a newer
        snapshot, download → 262144 bytes, contains 0x1002:0x6861.
Step 5: flashrom -p ch341a_spi → "Found Macronix flash chip 'MX25L8006E/MX25L8008'
        (1024 kB, SPI)" → <CHIP>="MX25L8006E/MX25L8008" (quote it in shell).
Step 6: flashrom -p ch341a_spi -c "MX25L8006E/MX25L8008" -r mi25_backup1.rom
        (twice; sha1sums match each other — do NOT expect them to equal any
        hash from another card).
Step 7: flashrom -p ch341a_spi -c "MX25L8006E/MX25L8008" \
          -w WX9100_171219_padded.rom -V → VERIFIED.