# SpeedDos26 für den C128 (`C128SpeedDos26-DE.bin`, `C128SpeedDos26-EN.bin`)

Kernal des C128 für den C128-Modus, 16 KB, `$C000–$FFFF`. Er ersetzt das Kernal-ROM des C128
(318020-05). Grundlage ist der C128-Kernal DolphinDos26 (Quelltext aus `../../C128DD26`), mit SpeedDOS
statt DolphinDOS am Parallelkabel: SpeedDOS-Parallelprotokoll und SpeedDOS-Schnelllader.

| Datei | Fassung |
|---|---|
| `C128SpeedDos26-DE.bin` | deutsche Tastatur: DIN-Tastaturtreiber (`ca65 -D DIN`, `src/din_treiber.s`) |
| `C128SpeedDos26-EN.bin` | US-Tastatur |

Beide Fassungen entstehen aus demselben Quelltext. Im C64-Modus des C128 gilt `C64IISpeedDos26.bin`.
Im Kernal-Umschalter des C128DCR gehört der C128-Kernal nach `$xC000` der Bank, `C64IISpeedDos26.bin`
nach `$x8000`. In den fertigen Abbildern liegt SpeedDos26 in Bank 5 (US-Tastatur) und Bank 6 (deutsche
Tastatur); Laufwerk und Kernal schalten gemeinsam um (`5@RNROM`, `6@RNROM`).

## Eigenschaften

- **Vier Wege:** Burst, SpeedDOS parallel, JiffyDOS, seriell. Der Kernal entscheidet bei jedem
  Ansprechen eines Geräts neu.
- **Burst hat beim Laden Vorrang:** Beherrscht das Laufwerk den schnellen seriellen Bus (1571 im
  1571-Modus), lädt der C128 wie das Original im Burst-Modus; das ist dort der schnellste Weg. Anzeige:
  `LOADING BU:`. Mit `LOAD"NAME",8,2` oder `,8,3` wird Burst ausgelassen und byteweise über das
  Parallelkabel geladen.
- **Anzeige:** Beim Laden mit dem SpeedDOS-Schnelllader erscheinen Übertragungsart, Bank und Adressen,
  z. B. `LOADING SD: $01C01-$06A2A`; bei JiffyDOS `JD:`.
- **Alle Speicherbänke:** Burst und der Schnelllader laden in jede Bank, also auch mit `BLOAD` und `BOOT`.
- **FAST-Modus:** Die Übertragung läuft auch bei 2 MHz; der Kernal schaltet dafür selbst kurz auf 1 MHz.
- **Funktionstasten:** wie am C64, F8 zeigt die Meldung des Laufwerks. F1 bis F8 lassen sich weiter
  mit `KEY` ändern.
- **Einschaltbild:** `SPEEDDOS26+JIFFYDOS+SD2IEC`, darunter der Hinweis auf den Multi-Speeder und
  `PAL SYSTEM` bzw. `NTSC SYSTEM`.
- Kassette und RS-232 gibt es nicht.
- Der Kernal arbeitet mit der 1571 mit SpeedDos26 (Parallelkabel am PIA) und auch mit einer 1541 mit
  SpeedDos26.

Messwerte am C128 mit der 1571 stehen im Handbuch und in der README im Abschnitt „Geschwindigkeit an der 1571“.

## Herkunft und Lizenz (JiffyDOS)

Der Kernal enthält wie der C128-Kernal DolphinDos26, aus dem er entstanden ist, JiffyDOS-Übertragungsroutinen,
die befehlsgleich aus einem JiffyDOS-Kernal stammen (JiffyDOS-C128-Kernal). Die JiffyDOS-Firmware für das
Laufwerk ist nicht enthalten. JiffyDOS ist ein Produkt von Mark Fellows / Creative Micro Designs und wird
heute über Jim Brain, RETRO Innovations, lizenziert. Bitte prüfe selbst, ob du wegen der Nutzung eine
offizielle JiffyDOS-Lizenz erwerben solltest: <https://www.jiffydos.com>

## Bauen

    make            # build/c128sd26.bin (US-Fassung) und build/c128sd26-de.bin (DE-Fassung), je 16 KB;
                    # listet die freien Bereiche und die Abweichungen zum C128-Kernal DolphinDos26
    make builds     # ../../Builds/C128SpeedDos26-EN.bin und C128SpeedDos26-DE.bin
