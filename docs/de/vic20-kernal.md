# SpeedDos26 für den VIC20/VC20 (`VIC20SpeedDos26PAL.bin`, `VIC20SpeedDos26NTSC.bin`)

Kernal für den VIC-20 (VC20) nach dem Vorbild des C64-Kernals SpeedDos26, 8 KB, `$E000–$FFFF`.
Grundlage ist der Commodore-Kernal 901486-06 (NTSC) bzw. 901486-07 (PAL); das Grundgerüst (ohne
Kassette und RS-232, JiffyDOS-Protokoll, Bedienung) stammt aus dem VIC-20-Kernal DolphinDos26.

| Datei | Fernsehnorm | ersetzt |
|---|---|---|
| `VIC20SpeedDos26PAL.bin` | PAL | Kernal-ROM 901486-07 |
| `VIC20SpeedDos26NTSC.bin` | NTSC | Kernal-ROM 901486-06 |

## Übertragungsarten

Der Kernal wählt bei jedem Zugriff selbst das schnellste Verfahren, das das Gerät beherrscht:

| Gerät | Verfahren | Anzeige beim Laden |
|---|---|---|
| 1541/1571 mit SpeedDos26 oder SpeedDOS+ und Parallelkabel | SpeedDOS-Schnelllader: ein Programm im Laufwerk liest die Spur und sendet die Blöcke parallel | `LOADING SD: $1201-$xxxx` |
| ebenso, bei `VERIFY`, Directory, `LOAD"name",8,2` oder `,8,3` | parallel, byteweise | `LOADING SD:` |
| JiffyDOS-Laufwerk, SD2IEC | JiffyDOS, Schnellladen | `LOADING JD: $1201-$xxxx` |
| ebenso, mit `,8,2` oder Directory | JiffyDOS, byteweise | `LOADING JD:` |
| alle anderen | seriell wie beim Original | `LOADING` |

- Der Schnelllader ist derselbe wie im C64-Kernal: das Laufwerksprogramm (450 Byte) wird mit 15
  `M-W`-Befehlen nach `$0300` der 1541 geschrieben und mit `M-E` bei `$0303` gestartet.
- Speichern läuft byteweise über das Parallelkabel.
- Die JiffyDOS-Routinen stammen aus dem JiffyDOS-Kernal des VIC-20 (PAL und NTSC haben eigene
  Zeitschleifen).

### Parallelkabel am VIC-20

Der Userport des VIC-20 hat die acht Datenleitungen an denselben Pins wie der C64, der Impuls zum
Laufwerk liegt aber an einem anderen Pin:

| Signal | C64 | VIC-20 |
|---|---|---|
| Daten D0–D7 | PB0–PB7, Pins C–L | PB0–PB7 der VIA 1, Pins C–L |
| Laufwerk → Rechner | FLAG2, Pin B | CB1, Pin B |
| Rechner → Laufwerk | PC2, **Pin 8** | CB2, **Pin M** |

Ein C64-Parallelkabel passt deshalb nicht unverändert: die Ader von Pin 8 muss am VIC-20 an Pin M
liegen (Adapter oder eigenes Kabel). Ein Kabel für beide Rechner ist nicht möglich.

Unterschiede zum C64 im Ablauf:

- Der CIA des C64 erzeugt bei jedem Lesen oder Schreiben des Ports einen Impuls an PC2. Die VIA tut
  das nur beim Schreiben; im Parallelbetrieb steht CB2 deshalb auf „Pulsausgang“, und nach jedem
  gelesenen Byte folgt ein Schreibzugriff auf `$9110`.
- Der Merker für den Impuls des Laufwerks (IFR Bit 4) wird nicht beim Abfragen gelöscht, sondern
  durch den Zugriff auf `$9110`.
- Bei der Kabelerkennung (nach jeder Sekundäradresse, bis zu 88 Impulse) schaltet der Kernal CB2
  von Hand über das PCR.
- Datenrichtung von Port B und PCR werden vor dem Parallelbetrieb gesichert und danach
  wiederhergestellt.

## Bedienung

- **Einschaltbild** mit `SPEEDDOS26    VIC-20`, `JIFFYDOS/SD2IEC` und `PAL` bzw. `NTSC`.
- **`@`-Befehle** (im Direktmodus): `@` Meldung des Laufwerks, `@befehl`, `@$` und `@$:muster`
  Directory ohne Verlust des Programms, `@8` bis `@19` Standardgerät wählen.
- **Standardgerät:** `LOAD`, `SAVE` und `VERIFY` ohne Gerätenummer benutzen das Standardgerät
  (Vorgabe 8). `LOAD` ohne Namen lädt die erste Datei (`:*`).
- **CTRL+D** wechselt im Direktmodus zum nächsten vorhandenen Laufwerk (Geräte 8 bis 19) und zeigt
  dessen Nummer an. Bei der Suche wird an jedem geprüften Laufwerk der Befehlskanal geschlossen.
- **Funktionstasten:** F1 `LIST`, F2 `RUN:`, F3 `RUN`, F4 `VERIFY`, F5 `LOAD`, F6 `SAVE"@:`,
  F7 Directory, F8 Meldung des Laufwerks; C= + F1 `OPEN4,4:CMD4:LIST`, C= + F3 `@CD←`,
  C= + F5 Verzeichniswechsel auf einer Directory-Zeile, C= + F7 `LOAD` vor den Namen schreiben.
- **`>`** wirkt wie `@`. **`!`** holt ein mit `NEW` gelöschtes Programm zurück (OLD).
- **Zahlen** dürfen mit `$` (hexadezimal), `%` (binär) oder `&` (oktal) beginnen, z. B. `PRINT $FF`
  oder `SYS $A000`.
- **`LIST`** zeigt Steuerzeichen in Zeichenketten sichtbar an, statt sie auszuführen.
- **Editor:** C= hält die Bildschirmausgabe an, solange die Taste gedrückt ist; CTRL verlangsamt sie
  wie beim Original. CTRL + DEL löscht die Zeile ab dem Cursor, CTRL + HOME setzt den Cursor in die
  unterste Zeile, CTRL + = schaltet auf Großschrift/Grafikzeichen. RUN/STOP beendet den
  Anführungszeichen- und den Einfügemodus.
- **Reset-Tasten:** RUN/STOP beim Reset gedrückt = BASIC-Warmstart, das Programm bleibt erhalten.
  Leertaste beim Reset = Kaltstart ohne Start eines Moduls bei `$A000`.
- **Entfallen:** Kassette und RS-232 des Kernals. Gerät 1 und 2 melden `ILLEGAL DEVICE NUMBER`.
  Die Kassettenmotor-Steuerung im Interrupt ist ebenfalls entfernt.

Abweichungen vom C64-Kernal SpeedDos26: Das Standardgerät steht in `sd_defdev` (`$0294`), nicht in
`fa`. Nicht übernommen sind das Einfrieren der Ausgabe (C= halten, CTRL kurz drücken), die sichtbaren
Steuerzeichen im Directory und die Farbbalken im Einschaltbild.

## Herkunft und Lizenz (JiffyDOS)

- Kernal: Commodore 901486-06/-07.
- Schnelllader und Parallelprotokoll: SpeedDOS+, übertragen auf die VIA 1.
- JiffyDOS-Übertragungsroutinen: Sie stammen befehlsgleich aus dem JiffyDOS-Kernal des VIC-20. Die
  JiffyDOS-Firmware für das Laufwerk ist nicht enthalten. JiffyDOS ist ein Produkt von Mark Fellows /
  Creative Micro Designs und wird heute über Jim Brain, RETRO Innovations, lizenziert. Bitte prüfe
  selbst, ob du wegen der Nutzung eine offizielle JiffyDOS-Lizenz erwerben solltest:
  <https://www.jiffydos.com>
