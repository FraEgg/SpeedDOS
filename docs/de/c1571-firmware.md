# SpeedDos26 für die 1571 (`C1571SpeedDOS26.bin`, `C1571CRSpeedDOS26.bin`)

Laufwerks-ROM für die 1571 (externe 1571 und C128DCR) mit einem PIA 6821 bei `$5000`: entweder der
**1571 Switchless Multi-Speeder V3** oder der einfache **PIA-Parallelport** im CPU-Sockel
(Schaltplan im Handbuch abgebildet; Entwurf, Rev. 0.1: noch nicht aufgebaut und nicht gemessen, das
Zeitverhalten bei 2 MHz ist nicht nachgerechnet; bei der externen 1571 werden bei jedem Zugriff auf den
PIA die Register 0 bis 3 des CIA-Bausteins mitbeschrieben).
Es ist das Gegenstück zu SpeedDos26 für die 1541: Auf der Leitung verhält sich das Laufwerk wie eine
1541 mit SpeedDos26, die Kernals `C64SpeedDos26`, `C64IISpeedDos26` und `C128SpeedDos26` arbeiten
unverändert damit.

- **Zwei Fassungen**, weil die externe 1571 und die 1571CR im C128DCR verschiedene Hardware haben (das
  ROM der 1571CR bleibt in der externen 1571 am C128 beim Burst-Handshake hängen, auch im Original):
  `C1571SpeedDOS26.bin` für die externe 1571 (Basis Commodore 310654-05, `src/sd26_1571x`) und
  `C1571CRSpeedDOS26.bin` für den C128DCR (Basis 318047-01, `src/sd26_1571`). Beide Quelltexte sind
  mit `tools/rekon.py` aus den CBM-Quellen erzeugt (Ausgangsstand byte-identisch); die
  SpeedDos26-Erweiterung ist für beide dieselbe Datei `src/gemeinsam/sd26_speeddos.s`. Kein
  DolphinDOS- und kein JiffyDOS-Code.
- **Dateien:** je 32 KB, `$8000–$FFFF`. Die SpeedDos26-Erweiterung (629 Byte) liegt im ROM selbst, im
  freien Bereich des Commodore-ROMs ab `$ABB0` (extern) bzw. `$ADD8` (C128DCR); die ROM-Prüfsumme
  deckt sie mit ab.
  Im Multi-Speeder kommt die Datei in die obere Hälfte einer EPROM-Bank (`$x8000`), mit dem
  PIA-Parallelport als 27C256 in den ROM-Sockel der 1571.
- **Parallelkabel am PIA** `$5000`: Port A an die acht Datenleitungen des Userports,
  CA1 von PC2, CA2 nach FLAG2 – dieselben Signale wie das SpeedDOS-Kabel am VIA der 1541. Der Port A
  des VIA1 ist in der 1571 belegt (Byte-Ready, Seitenwahl, Takt). Port B des PIA (RAM-Bänke des
  Multi-Speeders) bleibt unberührt; angesprochen werden nur `$5000` und `$5001`.
- **Doppelseitige Disketten** und der 1571-Modus (`U0>M1`) kommen aus dem Commodore-DOS; die
  Parallelübertragung und der Schnelllader arbeiten in beiden Betriebsarten.
- **Automatisch 2 MHz:** Erkennt das Laufwerk den SpeedDOS-Kernal am Parallelkabel, schaltet es in den
  1571-Modus (`sd_par_erkannt`, dieselbe Folge wie im IRQ des DOS beim C128), sofern das nicht mit
  `U0>M0` gesperrt ist (`lock` Bit 7). So läuft es auch am C64 und im C64-Modus des C128 mit 2 MHz.

## Was gegenüber dem Commodore-DOS geändert ist

Im Commodore-Code nur die Einhängepunkte (40 Byte in 18 Bereichen, `make` listet sie), alles Neue liegt
in `src/gemeinsam/sd26_speeddos.s`:

| Routine | Aufgabe |
|---|---|
| `sd_reset` | Reset: PIA Port A und CA2 auf Eingang |
| `sd_atn_byte` | Befehlsbyte unter ATN holen, dabei das Parallelkabel erkennen (CA1-Impuls bei gehaltenem CLK) |
| `sd_acptr`, `sd_par_empf` | Byte vom Rechner holen: parallel oder seriell |
| `sd_talk_byte`, `sd_par_senden` | Byte an den Rechner senden: parallel oder seriell |
| `sd_memex`, `sd_lader` | `M-E $0303` des SpeedDOS-Kernals abfangen und den eingebauten Schnelllader ausführen |
| `sd_cmd_t` | Befehl `T:name` – Dateischutz umschalten (ersetzt den funktionslosen Befehl `D`) |

Besonderheiten des PIA gegenüber dem VIA der 1541:

- Der CA2-Impuls entsteht nur beim **Lesen** von Port A (`CRA = $2C`). Nach dem Ausgeben eines Bytes
  wird der Port deshalb einmal blind gelesen.
- Der CA1-Merker wird nur durch Lesen von Port A gelöscht. Vor jedem Empfang wird er verworfen
  (`sd_ca1_loeschen`, ohne CA2-Impuls) – sonst gälte der letzte Impuls der Kabelerkennung als Byte.
- Bit 3 von CRA ist der Merker „Parallelbetrieb“ (`$04` seriell, `$2C` parallel).

Das 1571-DOS hat die Busroutinen doppelt: die der 1541 (ab `$E85B`, 1541-Modus mit 1 MHz) und eigene
(ab `$80CE`, 1571-Modus mit 2 MHz). **Beide Sätze sind eingehängt**; wo es seriell weitergeht,
entscheidet Bit 5 von `pota1` wie im ROM selbst.

**Schnelllader:** Der SpeedDOS-Kernal schickt ein Programm für die 1541 nach `$0300` und startet es mit
`M-E $0303`. Es ruft das 1541-ROM auf und kann in der 1571 nicht laufen. Steht bei `$0300` sein Anfang
(`jmp $FB8A`), führt das Laufwerk stattdessen den eingebauten Lader aus: Er liest die Datei Block für
Block über den Controller (Puffer 2) und sendet je Block ein Längenbyte und die Daten, am Ende `0` und
den Jobstatus – dieselbe Folge wie das 1541-Programm. Bricht der Rechner ab (ATN), endet der Lader
ohne Fehlermeldung.

Nicht übernommen (gegenüber SpeedDos26 für die 1541): 40 Spuren (im doppelseitigen Format ist Spur 36
schon die Rückseite), das schnelle Formatieren und die SpeedDOS-Sektorfolge beim Speichern.

## Bauen

    make            # build/sd26_1571.bin, ROM-Pruefsumme, Abweichungen zum Commodore-ROM
    make builds     # ../../Builds/C1571SpeedDOS26.bin und C1571CRSpeedDOS26.bin (je 32 KB)
