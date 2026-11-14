# SpeedDos26 for the 1571 (`C1571SpeedDOS26.bin`, `C1571CRSpeedDOS26.bin`)

Drive ROM for the 1571 (external 1571 and C128DCR) with a PIA 6821 at `$5000`: either the
**1571 Switchless Multi-Speeder V3** or the simple **PIA parallel port** in the CPU socket
(schematic shown in the manual; draft, rev. 0.1: not yet built or measured, the timing at 2 MHz
has not been calculated; on the external 1571, registers 0 to 3 of the CIA chip are written as well on
every access to the PIA).
It is the counterpart to SpeedDos26 for the 1541: on the bus the drive behaves like a
1541 with SpeedDos26, and the kernals `C64SpeedDos26`, `C64IISpeedDos26` and `C128SpeedDos26` work
with it unchanged.

- **Two versions**, because the external 1571 and the 1571CR in the C128DCR have different hardware (the
  ROM of the 1571CR hangs in the burst handshake in an external 1571 on the C128, the original ROM too):
  `C1571SpeedDOS26.bin` for the external 1571 (basis Commodore 310654-05, `src/sd26_1571x`) and
  `C1571CRSpeedDOS26.bin` for the C128DCR (basis 318047-01, `src/sd26_1571`). Both source codes were
  generated from the CBM sources with `tools/rekon.py` (starting point byte-identical); the
  SpeedDos26 extension is the same file `src/gemeinsam/sd26_speeddos.s` for both. No
  DolphinDOS and no JiffyDOS code.
- **Files:** 32 KB each, `$8000–$FFFF`. The SpeedDos26 extension (629 bytes) lies inside the ROM itself, in the
  free area of the Commodore ROM from `$ABB0` (external) or `$ADD8` (C128DCR); the ROM checksum
  covers it as well.
  In the Multi-Speeder the file goes into the upper half of an EPROM bank (`$x8000`), with the
  PIA parallel port as a 27C256 into the ROM socket of the 1571.
- **Parallel cable on the PIA** `$5000`: port A to the eight data lines of the user port,
  CA1 from PC2, CA2 to FLAG2 – the same signals as the SpeedDOS cable on the VIA of the 1541. Port A
  of VIA1 is in use in the 1571 (byte ready, side select, clock). Port B of the PIA (RAM banks of the
  Multi-Speeder) remains untouched; only `$5000` and `$5001` are addressed.
- **Double-sided disks** and the 1571 mode (`U0>M1`) come from the Commodore DOS; the
  parallel transfer and the fast loader work in both operating modes.
- **Automatic 2 MHz:** When the drive detects the SpeedDOS kernal on the parallel cable, it switches to
  1571 mode (`sd_par_erkannt`, the same sequence as in the IRQ of the DOS with the C128), unless this is
  locked with `U0>M0` (`lock` bit 7). It thus also runs at 2 MHz on the C64 and in the C64 mode of the C128.

## What has changed from the Commodore DOS

In the Commodore code only the hook points (40 bytes in 18 areas, `make` lists them); everything new is
in `src/gemeinsam/sd26_speeddos.s`:

| Routine | Task |
|---|---|
| `sd_reset` | reset: PIA port A and CA2 to input |
| `sd_atn_byte` | fetch the command byte under ATN and detect the parallel cable (CA1 pulse while CLK is held) |
| `sd_acptr`, `sd_par_empf` | fetch a byte from the computer: parallel or serial |
| `sd_talk_byte`, `sd_par_senden` | send a byte to the computer: parallel or serial |
| `sd_memex`, `sd_lader` | intercept `M-E $0303` of the SpeedDOS kernal and run the built-in fast loader |
| `sd_cmd_t` | command `T:name` – toggle file protection (replaces the command `D`, which has no function) |

Special features of the PIA compared with the VIA of the 1541:

- The CA2 pulse is generated only when port A is **read** (`CRA = $2C`). After a byte has been output,
  the port is therefore read once blindly.
- The CA1 flag is cleared only by reading port A. It is discarded before every reception
  (`sd_ca1_loeschen`, without a CA2 pulse) – otherwise the last pulse of the cable detection would count as a byte.
- Bit 3 of CRA is the flag “parallel mode” (`$04` serial, `$2C` parallel).

The 1571 DOS has the bus routines twice: those of the 1541 (from `$E85B`, 1541 mode at 1 MHz) and its own
(from `$80CE`, 1571 mode at 2 MHz). **Both sets are hooked**; where things continue serially,
bit 5 of `pota1` decides, as in the ROM itself.

**Fast loader:** The SpeedDOS kernal sends a program for the 1541 to `$0300` and starts it with
`M-E $0303`. It calls the 1541 ROM and cannot run in the 1571. If its beginning (`jmp $FB8A`) is at `$0300`,
the drive runs the built-in loader instead: it reads the file block by
block through the controller (buffer 2) and sends a length byte and the data for each block, at the end `0` and
the job status – the same sequence as the 1541 program. If the computer aborts (ATN), the loader ends
without an error message.

Not taken over (compared with SpeedDos26 for the 1541): 40 tracks (in the double-sided format track 36
is already the reverse side), fast formatting and the SpeedDOS sector order when saving.

## Building

    make            # build/sd26_1571.bin, ROM checksum, deviations from the Commodore ROM
    make builds     # ../../Builds/C1571SpeedDOS26.bin and C1571CRSpeedDOS26.bin (32 KB each)
