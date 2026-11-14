# SpeedDos26

A further development of SpeedDOS+ based on the commented source code in `../SpeedDOS+`.
It consists of the kernal of the C64 (`c64/`), the drive ROM of the 1541 (`1541/`), the
drive ROM of the 1571 (`1571/`, see [c1571-firmware.md](c1571-firmware.md)) and the kernal of the C128
(`c128/`, see [c128-kernal.md](c128-kernal.md)).

## Drive ROM (`1541/`)

```
cd 1541
make                              # builds and checks both versions
make builds                       # puts C1541SpeedDOS26.bin and C1541IISpeedDOS26.bin into ../../Builds
make eprom                        # builds ../../Builds/C1541_29F040.BIN: Multi-Speeder V3 image with SpeedDos26 in bank 3 (3@RNROM)
```

Two versions from the same source code (starting point: SpeedDOS+ 2.7 with 40 tracks):

| File | Size | Drive | Special feature |
|---|---|---|---|
| `C1541SpeedDOS26.bin` | 8 KB, `$E000–$FFFF` | 1541 with two 8 KB ROMs: replace only the upper ROM | `$C000–$DFFF` remains the Commodore ROM 325302-01; the command `&` is omitted |
| `C1541IISpeedDOS26.bin` | 16 KB, `$C000–$FFFF` | 1541-II (one ROM); also intended for the Multi-Speeder (bank 3) | command `&` kept (`-D ZWEI=1`) |

Changes from SpeedDOS+ in both versions:

- Power-on message `73,SPEEDDOS26   1541`.
- The code in `$C000–$DFFF` is that of the Commodore ROM. The 40-track routines for the BAM, which SpeedDOS+
  had there, have been rewritten (`sd26_*`, `src/sd26_40spur.inc`): in the 1541 version they sit in the space
  of the removed command `&` (`$E7A3`), in the 1541-II version in the free area from `$C001`.
- Blocks free: `nfcalc` in the lower ROM counts only 35 tracks. `setbpt` in the upper ROM detects the call
  from `nfcalc` and puts `sd26_plus36` on the stack, which then adds tracks 36–40.
- Formatting as in DolphinDos26: `N:NAME,ID` formats 35 tracks, `N:NAME,ID+` 40 tracks (SpeedDOS+: always 40).
  `N:NAME` without ID and validate keep the number of tracks of the disk – 40 tracks if the BAM entries
  of tracks 36–40 (`$C0–$D3`) contain anything (`sd26_ist40`, `sd26_fmt_ende`). Before, both always created a
  40-track BAM, even on 35-track disks.
- At reset a PIA 6821 at `$5000` is set to input (`sd26_pia`, `$FDA3`); RAM there remains unchanged.
- Sector search: the track counter covers all 39 data tracks (SpeedDOS+: 36, “DISK FULL” could come too early).
- The ROM checksum is checked again at power-on (`tools/pruefsumme.py` sets the balancing bytes).
- Dead code removed (`synclr`/`wrtnum`, `sd_vor_reed`); free: 38 bytes (1541) and 117 bytes (1541-II).

Checked (both versions passed): power-on message, fast loader, SAVE/VERIFY, command `T`, command `&`,
formatting with 40 tracks (`ID+`, 749 blocks free, also after `I` and after SAVE) and with 35 tracks (664),
`N` without ID and validate with both track counts, ROM test with a falsified byte, behaviour of the PIA at reset.

## C64 kernal (`c64/`)

```
cd c64
make                              # builds build/kernal.bin, lists free areas and deviations
make builds                       # puts C64SpeedDos26.bin and C64IISpeedDos26.bin (C64 II, BASIC + kernal) into ../../Builds
```

Requirements: `ca65`, `ld65`, Python 3.

- `src/` is authoritative and maintained by hand (no generator any more). `SD:` = change of
  SpeedDOS+ from the Commodore kernal 901227-03, `SD26:` = change for SpeedDos26.
- Free areas carry a line `; FREI: $xxxx-$yyyy (n Bytes)` in the source code, are named `frei_xxxx`
  and are filled with `$AA`; `tools/pruefe_frei.py` checks this on every `make`.

### Development steps

The steps build on each other; the column “free” gives the free bytes after each step.

| Step | Contents | free |
|---|---|---|
| `master` | starting point, byte-identical with the SpeedDOS+ kernal | 0 |
| `ohne-centronics` | Centronics printer driver (device 5) removed | 211 |
| `farben` | text light grey (15) on black background and border | 211 |
| `ohne-monitor` | memory monitor and dead cassette remnants removed; F2 unassigned, C= at reset without function | 907 |
| `ohne-ausdruck` | screen hardcopy CTRL-£ removed | 1058 |
| `einschaltbild` | coloured power-on screen from the DolphinDos26 kernal (text `SPEEDDOS26`, PAL/NTSC line); F2 = drive status | 896 |
| `ohne-vermerk` | hidden copyright notice and its output routine removed (the visible one at `$F14A` stays) | 918 |
| `jiffydos` | JiffyDOS protocol built in (detection, sending, receiving, fast loading); display `LOADING SD:` / `LOADING JD:`; `SPEEDDOS26` in the power-on screen 3 columns further right | 300 |
| `ftasten` | function key routine and assignment from the DolphinDos26 kernal (12 keys); power-on screen `SPEEDDOS26+JIFFYDOS+SD2IEC` | 227 |
| `optimierung` | waiting time after ATN 1 ms again; drive program: bug with following sector 0 fixed | 227 |
| `feinschliff` | function keys only in direct mode; SAVE bus error reports DEVICE NOT PRESENT; drive program in 15 instead of 18 `M-W`; `,8,3` applies to one load only; cassette motor in the IRQ and RS-232 remnants removed; `make builds` | 265 |

Free areas at the step `ohne-ausdruck` (18 areas, `make` lists them; the power-on screen occupies
`$EF7C` and most of `$F178` of these):
`$F9AB` 483, `$EF7C` 132, `$FB97` 100, `$F178` 53, `$FC9F` 50 (two entries), `$F1DE` 48, `$F65F` 47,
`$F55D` 38, `$F0E4` 24, `$F2DB` 19, `$F1B8` 18, `$F226` 13, `$F42B` 13, `$FD9B` 8, `$FEC2` 5, `$ED2A` 4, `$F659` 3.

Kept are: parallel protocol, fast loader with drive program, DOS commands `@`/`>` with
directory, `!` (OLD), numbers with `$ % &`, LIST with visible control characters,
reset keys RUN/STOP and space, pausing/slowing the scrolling, CTRL-DEL and CTRL-HOME.

### Centronics removed (`ohne-centronics`)

Under device 5, SpeedDOS+ first addressed a Centronics printer at the user port (strobe at PA2,
acknowledge at FLAG2, flag in `$DD0C`). This has been removed; device 5 is again a normal device on the
serial bus. The user port thus belongs to the parallel cable alone.

| Area | Bytes | before |
|---|---|---|
| `$ED2A–$ED2D` | 4 | rest of the check for LISTEN 5 |
| `$EF7C–$EFFF` | 132 | `sd_cen_listen`, `sd_cen_sa`, `sd_cen_senden`, `sd_strobe` |
| `$F0E4–$F0FB` | 24 | `sd_cen_zeichen` |
| `$F42B–$F437` | 13 | deselecting the printer in `sd_par_aus` |
| `$F55D–$F582` | 38 | `sd_cen_modus` and the never-called checksum routine that served the driver as a table |
| total | **211** | largest area 132 bytes |

The parallel routines between `$EEBB` and `$EF7B` have been moved up so that the space gained is
contiguous. All other routines are at their previous address, in particular `sd_icrnch`
at `$F000` (vector and function key check test the high byte) and the drive program at `$F800`.

### Load times

Measured in clock cycles (PAL), program of 30 KB (119 blocks), step `optimierung`:

| Drive | LOAD | LOAD of the copy saved by the drive itself | LOAD `,8,2` (byte by byte) | SAVE |
|---|---|---|---|---|
| 1541 with SpeedDOS+ ROM, parallel cable | 13.0 s | 8.3 s | 24.9 s | 61.5 s |
| 1541 with JiffyDOS ROM | 12.4 s | 9.1 s | 33.5 s | 34.2 s |
| 1541 with Commodore ROM (serial) | 74.4 s | – | 74.7 s | 93.1 s |

The first LOAD column loads a file in the standard sector order, the second the
copy saved by the respective drive itself. With the SpeedDOS drive the difference
(13.0 s versus 8.3 s) shows the gain from the SpeedDOS sector order 0, 10, 1, 11 …

### Function keys (`ftasten`)

Routine (`sd26_fkey`, `$FEC2`) and assignment come from the DolphinDos26 kernal and replace those
of SpeedDOS+. Text up to the first RETURN appears directly, from RETURN on it goes into the keyboard buffer.

| Key | Text | | Key | Text |
|---|---|---|---|---|
| F1 | CLR, `LIST` | | F2 | `RUN:` |
| F3 | CLR, `RUN` | | F4 | `VERIFY` |
| F5 | `LOAD` | | F6 | `SAVE"@:` (without RETURN) |
| F7 | CLR, `@$` (directory) | | F8 | `@` (drive status) |
| C=F1 | `OPEN4,4:CMD4:LIST` (without RETURN) | | C=F3 | `@CD←` (SD2IEC: one directory back) |
| C=F5 | `@ "CD:` on a directory line (SD2IEC: change into directory/image) | | C=F7 | `LOAD` on a directory line (press RETURN yourself) |

Deviations from DolphinDos26: F8 sends `@` instead of `@X`; C=F5 starts with `@`, and a DOS command in
quotation marks now ends at the closing quotation mark (`sd26_anf`); C=F7 writes only
`LOAD`, because SpeedDOS skips the text after the file name. The function keys are active as long as the
SpeedDOS vectors are set (SYS 58451 switches off DOS commands and function keys), and only during
input in BASIC direct mode, not with `INPUT` in a running program.
CTRL-DEL and CTRL-HOME have been given the codes `$0B`/`$0C` (before `$84`/`$82`, now C=F5/C=F3);
CTRL-K and CTRL-L therefore have the same effect.

### JiffyDOS (`jiffydos`)

The JiffyDOS protocol has been taken over from the DolphinDos26 kernal (`../C64DD26`) and adapted to
SpeedDOS. Order for every transfer: **SpeedDOS parallel cable → JiffyDOS → serial.**

| Routine | Address | Task |
|---|---|---|
| `jd_block`, `jd_fl_byte` | `$F9AB` | block-wise fast loading (also VERIFY) |
| `jd_ciout`, `jd_sendbyte`, `jd_nibtab` | `$FA4C` | send a byte |
| `jd_acptr`, `jd_getbyte`, `jd_sprites_off` | `$FAE6` | receive a byte |
| `jd_load_chk`, `jd_fastload`, `jd_print_end` | `$FB5F` | entry into fast loading, messages |
| `jd_detect` | `$FB97` | detection in the second-to-last bit of a command byte under ATN |
| `jd_loadadr` | `$FBBE` | fetch the load address, switch to fast loading (TALK with secondary address + 1) |
| `sd26_list2` | `$FBEC` | clear the flags before every LISTEN/TALK |
| `jd_retalk` | `$F226` | UNTALK, TALK, secondary address |

Hook points: `list1`/`ciout` call `jd_ciout` instead of `isour`; the bit loop in `isour`
(`$ED62–$ED91`) is that of the JiffyDOS kernal; without parallel mode `sd_acptr` branches to
`jd_acptr`; LOAD fetches the high byte of the load address via `jd_loadadr` and goes through
`jd_load_chk` when the SpeedDOS fast loader does not come into play. The original check
“release CLK on UNLISTEN” in `list2` is left out: a SpeedDOS drive in parallel mode
would otherwise hang (proven in testing).

Flags: `r2d2` (`$A3`) bit 6 = JiffyDOS device, bit 7 = EOI when sending or fast loading active.
Messages as with the SpeedDOS fast loader (` FROM $xxxx`, ` TO $xxxx`). After LOADING/VERIFYING
comes the transfer method (`sd26_modus`, as in the DolphinDos26 kernal): ` SD:` parallel cable,
` JD:` JiffyDOS, nothing for normal serial transfer.
No fast loading with secondary address 2, load addresses below `$0400` and for the directory.

**Origin and licence:** JiffyDOS is a product of Mark Fellows / Creative Micro Designs and is licensed
today through Jim Brain, RETRO Innovations. The JiffyDOS transfer routines of this kernal are
instruction-identical to those of a JiffyDOS kernal (taken over via the C64 kernal DolphinDos26); the
JiffyDOS firmware for the drive is not included. Please check for yourself whether your use calls for
an official JiffyDOS licence: <https://www.jiffydos.com>

**Tested with S-JiffyDOS 1541:** The kernal has also been tested with S-JiffyDOS 1541 (SJD41). S-JiffyDOS 1541 by Jochen Adler is an extension of the JiffyDOS ROM for the 1541. Towards the computer it uses the transfer routines of JiffyDOS; the kernal therefore addresses it like a JiffyDOS drive (display `LOADING JD:`). Inside the drive it additionally speeds up loading, saving, scratching and validating and adds 40 tracks, file protection and an extended status. Further information: [S-JIFFYDOS 1541 (funet.fi / zimmers.net)](https://bio.nic.funet.fi/pub/cbm/c64/diskutil/misc/s-jiffydos1541.html), [Commodore News: SJD41 (2013)](https://www.commodore-news.com/news/item/2755/en/mobile), [RetroTechCollection: JiffyDOS Kernal Upgrade](https://wiki.retrotechcollection.com/JiffyDOS_Kernal_Upgrade).

### Space calculation before the integration

The yardstick is the JiffyDOS protocol as it is built into `../C64DD26` next to the parallel cable
(detection, receiving, sending, fast loading):

| Routine (C64DD26) | Bytes | Task |
|---|---|---|
| `jd_detect`, `jd_list2` | 39 + 9 | detection after LISTEN/TALK, flags |
| `jd_acptr` … `jd_sprites_off` | 123 | receive a byte |
| `jd_ciout`, `jd_sendbyte`, `jd_nibtab` | 154 | send a byte |
| `jd_loadadr`, `jd_loadadr2` | 32 + 19 | load address, trigger fast loading |
| `jd_load_chk`, `jd_fastload`, `jd_block` | 43 + 161 | block-wise fast loading |
| `jd_retalk`, `jd_print_end` | 13 + 8 | helper routines |
| total | **601** | of which for LOAD only (without sending): 447 |

**Result:** Removing Centronics alone (211 bytes) was not enough for JiffyDOS; after
removing the monitor, the screen hardcopy and the cassette remnants (918 bytes free) it fitted. The integration
took 585 bytes; with the display of the transfer method 300 bytes are still free (largest area 48 bytes).

The figures for JiffyDOS come from the finished C64DD26 kernal; the integration here needs its own
connection points to the SpeedDOS routines and may differ by a few bytes. Note: the
timing loops of `jd_sendbyte` and the table `jd_nibtab` must not cross a page boundary, and
`$F9AB–$FA1B` is transferred into the 1541 along with the fast loader (without meaning there).

Not yet reclaimed, but possible without loss of function: cassette motor in the IRQ (`$EA61–$EA7A`, approx. 23),
individual fill bytes.
