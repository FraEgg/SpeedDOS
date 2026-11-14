# SpeedDos26 for the C128 (`C128SpeedDos26-DE.bin`, `C128SpeedDos26-EN.bin`)

Kernal of the C128 for C128 mode, 16 KB, `$C000–$FFFF`. It replaces the kernal ROM of the C128
(318020-05). It is based on the C128 kernal DolphinDos26 (source code from `../../C128DD26`), with SpeedDOS
instead of DolphinDOS on the parallel cable: SpeedDOS parallel protocol and SpeedDOS fast loader.

| File | Version |
|---|---|
| `C128SpeedDos26-DE.bin` | German keyboard: DIN keyboard driver (`ca65 -D DIN`, `src/din_treiber.s`) |
| `C128SpeedDos26-EN.bin` | US keyboard |

Both versions are built from the same source code. In the C64 mode of the C128, `C64IISpeedDos26.bin` applies.
In the kernal switcher of the C128DCR the C128 kernal belongs at `$xC000` of the bank, `C64IISpeedDos26.bin`
at `$x8000`. In the ready-made images SpeedDos26 is in bank 5 (US keyboard) and bank 6 (German
keyboard); drive and kernal switch together (`5@RNROM`, `6@RNROM`).

## Features

- **Four ways:** burst, SpeedDOS parallel, JiffyDOS, serial. The kernal decides anew every time a
  device is addressed.
- **Burst takes precedence when loading:** If the drive supports the fast serial bus (1571 in
  1571 mode), the C128 loads in burst mode like the original; that is the fastest way there. Display:
  `LOADING BU:`. With `LOAD"NAME",8,2` or `,8,3` burst is skipped and the file is loaded byte by byte
  over the parallel cable.
- **Display:** When loading with the SpeedDOS fast loader, the transfer method, bank and addresses appear,
  e.g. `LOADING SD: $01C01-$06A2A`; with JiffyDOS `JD:`.
- **All memory banks:** Burst and the fast loader load into any bank, so also with `BLOAD` and `BOOT`.
- **FAST mode:** The transfer also works at 2 MHz; the kernal itself briefly switches to 1 MHz for it.
- **Function keys:** as on the C64, F8 shows the message of the drive. F1 to F8 can still be changed
  with `KEY`.
- **Power-on screen:** `SPEEDDOS26+JIFFYDOS+SD2IEC`, below it the note on the Multi-Speeder and
  `PAL SYSTEM` or `NTSC SYSTEM`.
- There is no cassette and no RS-232.
- The kernal works with the 1571 with SpeedDos26 (parallel cable on the PIA) and also with a 1541 with
  SpeedDos26.

Measured times on the C128 with the 1571 are in the manual and in the README in the section “Speed on the 1571”.

## Origin and licence (JiffyDOS)

Like the C128 kernal DolphinDos26 from which it was derived, the kernal contains JiffyDOS transfer routines
that are instruction-identical to a JiffyDOS kernal (JiffyDOS C128 kernal). The JiffyDOS firmware for the
drive is not included. JiffyDOS is a product of Mark Fellows / Creative Micro Designs and is licensed
today through Jim Brain, RETRO Innovations. Please check for yourself whether your use calls for an
official JiffyDOS licence: <https://www.jiffydos.com>

## Building

    make            # build/c128sd26.bin (US version) and build/c128sd26-de.bin (DE version), 16 KB each;
                    # lists the free areas and the deviations from the C128 kernal DolphinDos26
    make builds     # ../../Builds/C128SpeedDos26-EN.bin and C128SpeedDos26-DE.bin
