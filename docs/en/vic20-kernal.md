# SpeedDos26 for the VIC20/VC20 (`VIC20SpeedDos26PAL.bin`, `VIC20SpeedDos26NTSC.bin`)

Kernal for the VIC-20 (VC20) modelled on the C64 kernal SpeedDos26, 8 KB, `$E000–$FFFF`.
It is based on the Commodore kernal 901486-06 (NTSC) and 901486-07 (PAL); the framework (without
cassette and RS-232, JiffyDOS protocol, operation) comes from the VIC-20 kernal DolphinDos26.

| File | TV standard | replaces |
|---|---|---|
| `VIC20SpeedDos26PAL.bin` | PAL | kernal ROM 901486-07 |
| `VIC20SpeedDos26NTSC.bin` | NTSC | kernal ROM 901486-06 |

## Transfer methods

On every access the kernal itself chooses the fastest method the device supports:

| Device | Method | Display when loading |
|---|---|---|
| 1541/1571 with SpeedDos26 or SpeedDOS+ and parallel cable | SpeedDOS fast loader: a program in the drive reads the track and sends the blocks in parallel | `LOADING SD: $1201-$xxxx` |
| the same, with `VERIFY`, directory, `LOAD"name",8,2` or `,8,3` | parallel, byte by byte | `LOADING SD:` |
| JiffyDOS drive, SD2IEC | JiffyDOS, fast loading | `LOADING JD: $1201-$xxxx` |
| the same, with `,8,2` or directory | JiffyDOS, byte by byte | `LOADING JD:` |
| all others | serial as in the original | `LOADING` |

- The fast loader is the same as in the C64 kernal: the drive program (450 bytes) is written to
  `$0300` of the 1541 with 15 `M-W` commands and started with `M-E` at `$0303`.
- Saving runs byte by byte over the parallel cable.
- The JiffyDOS routines come from the JiffyDOS kernal of the VIC-20 (PAL and NTSC have their own
  timing loops).

### Parallel cable on the VIC-20

The user port of the VIC-20 has the eight data lines on the same pins as the C64, but the pulse to
the drive is on a different pin:

| Signal | C64 | VIC-20 |
|---|---|---|
| Data D0–D7 | PB0–PB7, pins C–L | PB0–PB7 of VIA 1, pins C–L |
| Drive → computer | FLAG2, pin B | CB1, pin B |
| Computer → drive | PC2, **pin 8** | CB2, **pin M** |

A C64 parallel cable therefore does not fit unchanged: the wire from pin 8 must go to pin M on the
VIC-20 (adapter or a cable of its own). One cable for both computers is not possible.

Differences from the C64 in the sequence:

- The CIA of the C64 generates a pulse on PC2 with every read or write of the port. The VIA does so
  only on a write; in parallel operation CB2 is therefore set to “pulse output”, and every byte
  read is followed by a write access to `$9110`.
- The flag for the pulse of the drive (IFR bit 4) is not cleared by testing it, but by the access
  to `$9110`.
- During cable detection (after every secondary address, up to 88 pulses) the kernal switches CB2
  by hand through the PCR.
- The data direction of port B and the PCR are saved before parallel operation and restored
  afterwards.

## Operation

- **Power-on screen** with `SPEEDDOS26    VIC-20`, `JIFFYDOS/SD2IEC` and `PAL` or `NTSC`.
- **`@` commands** (in direct mode): `@` message of the drive, `@command`, `@$` and `@$:pattern`
  directory without losing the program, `@8` to `@19` select the default device.
- **Default device:** `LOAD`, `SAVE` and `VERIFY` without a device number use the default device
  (preset 8). `LOAD` without a name loads the first file (`:*`).
- **CTRL+D** changes in direct mode to the next drive that is present (devices 8 to 19) and shows
  its number. During the search the command channel is closed on every drive that is checked.
- **Function keys:** F1 `LIST`, F2 `RUN:`, F3 `RUN`, F4 `VERIFY`, F5 `LOAD`, F6 `SAVE"@:`,
  F7 directory, F8 message of the drive; C= + F1 `OPEN4,4:CMD4:LIST`, C= + F3 `@CD←`,
  C= + F5 change of directory on a directory line, C= + F7 write `LOAD` in front of the name.
- **`>`** works like `@`. **`!`** brings back a program deleted with `NEW` (OLD).
- **Numbers** may begin with `$` (hexadecimal), `%` (binary) or `&` (octal), e.g. `PRINT $FF`
  or `SYS $A000`.
- **`LIST`** shows control characters in strings visibly instead of executing them.
- **Editor:** C= halts the screen output as long as the key is held down; CTRL slows it down as in
  the original. CTRL + DEL deletes the line from the cursor, CTRL + HOME puts the cursor into the
  bottom line, CTRL + = switches to upper case/graphics. RUN/STOP ends quote mode and insert mode.
- **Reset keys:** RUN/STOP held during reset = BASIC warm start, the program is kept.
  Space bar during reset = cold start without starting a cartridge at `$A000`.
- **Removed:** cassette and RS-232 of the kernal. Devices 1 and 2 report `ILLEGAL DEVICE NUMBER`.
  The cassette motor control in the interrupt is removed as well.

Differences from the C64 kernal SpeedDos26: the default device is kept in `sd_defdev` (`$0294`), not
in `fa`. Not taken over are freezing the output (hold C=, press CTRL briefly), the visible control
characters in the directory and the colour bars in the power-on screen.

## Origin and licence (JiffyDOS)

- Kernal: Commodore 901486-06/-07.
- Fast loader and parallel protocol: SpeedDOS+, ported to VIA 1.
- JiffyDOS transfer routines: they are taken instruction-identically from the JiffyDOS kernal of
  the VIC-20. The JiffyDOS drive firmware is not included. JiffyDOS is a product of Mark Fellows /
  Creative Micro Designs and is licensed today through Jim Brain, RETRO Innovations. Please check for
  yourself whether your use calls for an official JiffyDOS licence: <https://www.jiffydos.com>
