# SpeedDos26

Weiterentwicklung von SpeedDOS+ auf Grundlage des kommentierten Quelltexts in `../SpeedDOS+`.
Es besteht aus dem Kernal des C64 (`c64/`), dem Laufwerks-ROM der 1541 (`1541/`), dem
Laufwerks-ROM der 1571 (`1571/`, siehe [c1571-firmware.md](c1571-firmware.md)) und dem Kernal des C128
(`c128/`, siehe [c128-kernal.md](c128-kernal.md)).

## Laufwerks-ROM (`1541/`)

```
cd 1541
make                              # baut und prüft beide Fassungen
make builds                       # legt C1541SpeedDOS26.bin und C1541IISpeedDOS26.bin in ../../Builds ab
make eprom                        # baut ../../Builds/C1541_29F040.BIN: Multi-Speeder-V3-Abbild mit SpeedDos26 in Bank 3 (3@RNROM)
```

Zwei Fassungen aus demselben Quelltext (Ausgangsstand: SpeedDOS+ 2.7 mit 40 Spuren):

| Datei | Größe | Laufwerk | Besonderheit |
|---|---|---|---|
| `C1541SpeedDOS26.bin` | 8 KB, `$E000–$FFFF` | 1541 mit zwei 8-KB-ROMs: nur das obere ROM tauschen | `$C000–$DFFF` bleibt das Commodore-ROM 325302-01; Befehl `&` entfällt |
| `C1541IISpeedDOS26.bin` | 16 KB, `$C000–$FFFF` | 1541-II (ein ROM); auch für den Multi-Speeder vorgesehen (Bank 3) | Befehl `&` erhalten (`-D ZWEI=1`) |

Änderungen gegenüber SpeedDOS+ in beiden Fassungen:

- Einschaltmeldung `73,SPEEDDOS26   1541`.
- Der Code in `$C000–$DFFF` ist der des Commodore-ROMs. Die 40-Spur-Routinen für die BAM, die SpeedDOS+
  dort hatte, sind neu gefasst (`sd26_*`, `src/sd26_40spur.inc`): in der 1541-Fassung liegen sie im Platz
  des entfernten Befehls `&` (`$E7A3`), in der 1541-II-Fassung im freien Bereich ab `$C001`.
- Freie Blöcke: `nfcalc` im unteren ROM zählt nur 35 Spuren. `setbpt` im oberen ROM erkennt den Aufruf
  aus `nfcalc` und legt `sd26_plus36` auf den Stapel, das danach die Spuren 36–40 dazuzählt.
- Formatieren wie bei DolphinDos26: `N:NAME,ID` formatiert 35 Spuren, `N:NAME,ID+` 40 Spuren (SpeedDOS+: immer 40).
  `N:NAME` ohne ID und Validate behalten die Spurzahl der Diskette bei – 40 Spuren, wenn in den BAM-Einträgen
  der Spuren 36–40 (`$C0–$D3`) etwas steht (`sd26_ist40`, `sd26_fmt_ende`). Vorher legten beide immer eine
  40-Spur-BAM an, auch auf 35-Spur-Disketten.
- Beim Reset wird ein PIA 6821 bei `$5000` auf Eingang gestellt (`sd26_pia`, `$FDA3`); RAM dort bleibt unverändert.
- Sektorsuche: der Spurzähler umfasst alle 39 Datenspuren (SpeedDOS+: 36, „DISK FULL“ konnte zu früh kommen).
- Die ROM-Prüfsumme wird beim Einschalten wieder geprüft (`tools/pruefsumme.py` setzt die Ausgleichsbytes).
- Toter Code entfernt (`synclr`/`wrtnum`, `sd_vor_reed`); frei: 38 Byte (1541) bzw. 117 Byte (1541-II).

Geprüft (beide Fassungen bestanden): Einschaltmeldung, Schnelllader, SAVE/VERIFY, Befehl `T`, Befehl `&`,
Formatieren mit 40 Spuren (`ID+`, 749 Blöcke frei, auch nach `I` und nach SAVE) und mit 35 Spuren (664),
`N` ohne ID und Validate mit beiden Spurzahlen, ROM-Test mit verfälschtem Byte, Verhalten des PIA beim Reset.

## C64-Kernal (`c64/`)

```
cd c64
make                              # baut build/kernal.bin, listet freie Bereiche und Abweichungen
make builds                       # legt C64SpeedDos26.bin und C64IISpeedDos26.bin (C64 II, BASIC + Kernal) in ../../Builds ab
```

Voraussetzung: `ca65`, `ld65`, Python 3.

- `src/` ist maßgeblich und wird von Hand gepflegt (kein Generator mehr). `SD:` = Änderung von
  SpeedDOS+ gegenüber dem Commodore-Kernal 901227-03, `SD26:` = Änderung für SpeedDos26.
- Freie Bereiche tragen im Quelltext eine Zeile `; FREI: $xxxx-$yyyy (n Bytes)`, heißen `frei_xxxx`
  und sind mit `$AA` gefüllt; `tools/pruefe_frei.py` prüft das bei jedem `make`.

### Entwicklungsschritte

Die Schritte bauen aufeinander auf; die Spalte „frei“ nennt die freien Bytes nach dem jeweiligen Schritt.

| Schritt | Inhalt | frei |
|---|---|---|
| `master` | Ausgangsstand, byte-identisch mit dem SpeedDOS+-Kernal | 0 |
| `ohne-centronics` | Centronics-Druckertreiber (Gerät 5) entfernt | 211 |
| `farben` | Schrift hellgrau (15) auf schwarzem Hintergrund und Rahmen | 211 |
| `ohne-monitor` | Speichermonitor und tote Kassettenreste entfernt; F2 unbelegt, C= beim Reset ohne Funktion | 907 |
| `ohne-ausdruck` | Bildschirmausdruck CTRL-£ entfernt | 1058 |
| `einschaltbild` | farbiges Einschaltbild aus dem DolphinDos26-Kernal (Text `SPEEDDOS26`, PAL/NTSC-Zeile); F2 = Laufwerksstatus | 896 |
| `ohne-vermerk` | versteckter Urhebervermerk samt Ausgaberoutine entfernt (der sichtbare bei `$F14A` bleibt) | 918 |
| `jiffydos` | JiffyDOS-Protokoll eingebaut (Erkennung, Senden, Empfangen, Schnellladen); Anzeige `LOADING SD:` / `LOADING JD:`; `SPEEDDOS26` im Einschaltbild 3 Spalten weiter rechts | 300 |
| `ftasten` | F-Tasten-Routine und Belegung aus dem DolphinDos26-Kernal (12 Tasten); Einschaltbild `SPEEDDOS26+JIFFYDOS+SD2IEC` | 227 |
| `optimierung` | Wartezeit nach ATN wieder 1 ms; Laufwerksprogramm: Fehler beim Folgesektor 0 behoben | 227 |
| `feinschliff` | F-Tasten nur im Direktmodus; SAVE-Busfehler meldet DEVICE NOT PRESENT; Laufwerksprogramm in 15 statt 18 `M-W`; `,8,3` gilt nur für einen Ladevorgang; Kassettenmotor im IRQ und RS-232-Reste entfernt; `make builds` | 265 |

Freie Bereiche im Stand `ohne-ausdruck` (18 Bereiche, `make` listet sie; das Einschaltbild belegt
davon `$EF7C` und den größten Teil von `$F178`):
`$F9AB` 483, `$EF7C` 132, `$FB97` 100, `$F178` 53, `$FC9F` 50 (zwei Einträge), `$F1DE` 48, `$F65F` 47,
`$F55D` 38, `$F0E4` 24, `$F2DB` 19, `$F1B8` 18, `$F226` 13, `$F42B` 13, `$FD9B` 8, `$FEC2` 5, `$ED2A` 4, `$F659` 3.

Geblieben sind: Parallelprotokoll, Schnelllader mit Laufwerksprogramm, DOS-Befehle `@`/`>` mit
Directory, `!` (OLD), Zahlen mit `$ % &`, LIST mit sichtbaren Steuerzeichen,
Reset-Tasten RUN/STOP und Leertaste, Rollen anhalten/bremsen, CTRL-DEL und CTRL-HOME.

### Centronics entfernt (`ohne-centronics`)

SpeedDOS+ sprach unter Gerät 5 zuerst einen Centronics-Drucker am Userport an (Strobe an PA2,
Quittung an FLAG2, Merker in `$DD0C`). Das ist entfernt; Gerät 5 ist wieder ein normales Gerät am
seriellen Bus. Der Userport gehört damit allein dem Parallelkabel.

| Bereich | Byte | vorher |
|---|---|---|
| `$ED2A–$ED2D` | 4 | Rest der Abfrage auf LISTEN 5 |
| `$EF7C–$EFFF` | 132 | `sd_cen_listen`, `sd_cen_sa`, `sd_cen_senden`, `sd_strobe` |
| `$F0E4–$F0FB` | 24 | `sd_cen_zeichen` |
| `$F42B–$F437` | 13 | Abwahl des Druckers in `sd_par_aus` |
| `$F55D–$F582` | 38 | `sd_cen_modus` und die nie aufgerufene Prüfsummenroutine, die dem Treiber als Tabelle diente |
| zusammen | **211** | größter Bereich 132 Byte |

Die Parallelroutinen zwischen `$EEBB` und `$EF7B` sind aufgerückt, damit der gewonnene Platz
zusammenhängt. Alle anderen Routinen stehen an ihrer bisherigen Adresse, insbesondere `sd_icrnch`
bei `$F000` (Vektor und F-Tasten-Abfrage prüfen das High-Byte) und das Laufwerksprogramm bei `$F800`.

### Ladezeiten

Gemessen in Taktzyklen (PAL), Programm mit 30 KB (119 Blöcke), Stand `optimierung`:

| Laufwerk | LOAD | LOAD der selbst gespeicherten Kopie | LOAD `,8,2` (byteweise) | SAVE |
|---|---|---|---|---|
| 1541 mit SpeedDOS+-ROM, Parallelkabel | 13,0 s | 8,3 s | 24,9 s | 61,5 s |
| 1541 mit JiffyDOS-ROM | 12,4 s | 9,1 s | 33,5 s | 34,2 s |
| 1541 mit Commodore-ROM (seriell) | 74,4 s | – | 74,7 s | 93,1 s |

Die erste LOAD-Spalte lädt eine Datei in der Standard-Sektorfolge, die zweite die
vom jeweiligen Laufwerk selbst gespeicherte Kopie. Beim SpeedDOS-Laufwerk zeigt der Unterschied
(13,0 s gegenüber 8,3 s) den Gewinn durch die SpeedDOS-Sektorfolge 0, 10, 1, 11 …

### F-Tasten (`ftasten`)

Routine (`sd26_fkey`, `$FEC2`) und Belegung stammen aus dem DolphinDos26-Kernal und ersetzen die
von SpeedDOS+. Text bis zum ersten RETURN erscheint direkt, ab RETURN geht er in den Tastaturpuffer.

| Taste | Text | | Taste | Text |
|---|---|---|---|---|
| F1 | CLR, `LIST` | | F2 | `RUN:` |
| F3 | CLR, `RUN` | | F4 | `VERIFY` |
| F5 | `LOAD` | | F6 | `SAVE"@:` (ohne RETURN) |
| F7 | CLR, `@$` (Directory) | | F8 | `@` (Laufwerksstatus) |
| C=F1 | `OPEN4,4:CMD4:LIST` (ohne RETURN) | | C=F3 | `@CD←` (SD2IEC: Verzeichnis zurück) |
| C=F5 | `@ "CD:` auf einer Directoryzeile (SD2IEC: in Verzeichnis/Image wechseln) | | C=F7 | `LOAD` auf einer Directoryzeile (RETURN selbst drücken) |

Abweichungen von DolphinDos26: F8 sendet `@` statt `@X`; C=F5 beginnt mit `@`, und ein DOS-Befehl in
Anführungszeichen endet jetzt am schließenden Anführungszeichen (`sd26_anf`); C=F7 schreibt nur
`LOAD`, weil SpeedDOS den Text hinter dem Dateinamen übergeht. Aktiv sind die F-Tasten, solange die
SpeedDOS-Vektoren gesetzt sind (SYS 58451 schaltet DOS-Befehle und F-Tasten ab), und nur bei der
Eingabe im BASIC-Direktmodus, nicht bei `INPUT` in einem laufenden Programm.
CTRL-DEL und CTRL-HOME haben die Codes `$0B`/`$0C` bekommen (vorher `$84`/`$82`, jetzt C=F5/C=F3);
dieselbe Wirkung haben damit CTRL-K und CTRL-L.

### JiffyDOS (`jiffydos`)

Das JiffyDOS-Protokoll ist aus dem DolphinDos26-Kernal (`../C64DD26`) übernommen und an SpeedDOS
angepasst. Reihenfolge bei jeder Übertragung: **SpeedDOS-Parallelkabel → JiffyDOS → seriell.**

| Routine | Adresse | Aufgabe |
|---|---|---|
| `jd_block`, `jd_fl_byte` | `$F9AB` | blockweises Schnellladen (auch VERIFY) |
| `jd_ciout`, `jd_sendbyte`, `jd_nibtab` | `$FA4C` | Byte senden |
| `jd_acptr`, `jd_getbyte`, `jd_sprites_off` | `$FAE6` | Byte empfangen |
| `jd_load_chk`, `jd_fastload`, `jd_print_end` | `$FB5F` | Einstieg ins Schnellladen, Meldungen |
| `jd_detect` | `$FB97` | Erkennung im vorletzten Bit eines Befehlsbytes unter ATN |
| `jd_loadadr` | `$FBBE` | Ladeadresse holen, auf Schnellladen umschalten (TALK mit Sekundäradresse + 1) |
| `sd26_list2` | `$FBEC` | Merker vor jedem LISTEN/TALK löschen |
| `jd_retalk` | `$F226` | UNTALK, TALK, Sekundäradresse |

Einhängepunkte: `list1`/`ciout` rufen `jd_ciout` statt `isour`; die Bitschleife in `isour`
(`$ED62–$ED91`) ist die des JiffyDOS-Kernals; `sd_acptr` verzweigt ohne Parallelbetrieb nach
`jd_acptr`; LOAD holt das High-Byte der Ladeadresse über `jd_loadadr` und geht über
`jd_load_chk`, wenn der SpeedDOS-Schnelllader nicht zum Zug kommt. Die Original-Abfrage
„bei UNLISTEN CLK freigeben“ in `list2` bleibt weg: ein SpeedDOS-Laufwerk im Parallelbetrieb
bliebe sonst hängen (im Test nachgewiesen).

Merker: `r2d2` (`$A3`) Bit 6 = JiffyDOS-Gerät, Bit 7 = EOI beim Senden bzw. Schnellladen aktiv.
Meldungen wie beim SpeedDOS-Schnelllader (` FROM $xxxx`, ` TO $xxxx`). Hinter LOADING/VERIFYING
steht die Übertragungsart (`sd26_modus`, wie im DolphinDos26-Kernal): ` SD:` Parallelkabel,
` JD:` JiffyDOS, bei normaler serieller Übertragung nichts.
Kein Schnellladen bei Sekundäradresse 2, Ladeadressen unter `$0400` und beim Directory.

**Herkunft und Lizenz:** JiffyDOS ist ein Produkt von Mark Fellows / Creative Micro Designs und wird
heute über Jim Brain, RETRO Innovations, lizenziert. Die JiffyDOS-Übertragungsroutinen dieses Kernals
sind befehlsgleich aus einem JiffyDOS-Kernal übernommen (über den C64-Kernal DolphinDos26); die
JiffyDOS-Firmware für das Laufwerk ist nicht enthalten. Bitte prüfe selbst, ob du wegen der Nutzung
eine offizielle JiffyDOS-Lizenz erwerben solltest: <https://www.jiffydos.com>

**Getestet mit S-JiffyDOS 1541:** Der Kernal ist auch mit S-JiffyDOS 1541 (SJD41) getestet. S-JiffyDOS 1541 von Jochen Adler ist eine Erweiterung des JiffyDOS-ROMs für die 1541. Zum Computer hin benutzt es die Übertragungsroutinen von JiffyDOS; der Kernal spricht es deshalb wie ein JiffyDOS-Laufwerk an (Anzeige `LOADING JD:`). Im Laufwerk beschleunigt es zusätzlich Laden, Speichern, Löschen und Validate und bringt 40 Spuren, Dateischutz und einen erweiterten Status mit. Weitere Informationen: [S-JIFFYDOS 1541 (funet.fi / zimmers.net)](https://bio.nic.funet.fi/pub/cbm/c64/diskutil/misc/s-jiffydos1541.html), [Commodore News: SJD41 (2013)](https://www.commodore-news.com/news/item/2755/en/mobile), [RetroTechCollection: JiffyDOS Kernal Upgrade](https://wiki.retrotechcollection.com/JiffyDOS_Kernal_Upgrade).

### Platzrechnung vor dem Einbau

Maßstab ist das JiffyDOS-Protokoll, wie es in `../C64DD26` neben dem Parallelkabel eingebaut ist
(Erkennung, Empfangen, Senden, Schnellladen):

| Routine (C64DD26) | Byte | Aufgabe |
|---|---|---|
| `jd_detect`, `jd_list2` | 39 + 9 | Erkennung nach LISTEN/TALK, Merker |
| `jd_acptr` … `jd_sprites_off` | 123 | Byte empfangen |
| `jd_ciout`, `jd_sendbyte`, `jd_nibtab` | 154 | Byte senden |
| `jd_loadadr`, `jd_loadadr2` | 32 + 19 | Ladeadresse, Schnellladen anstoßen |
| `jd_load_chk`, `jd_fastload`, `jd_block` | 43 + 161 | blockweises Schnellladen |
| `jd_retalk`, `jd_print_end` | 13 + 8 | Hilfsroutinen |
| zusammen | **601** | davon nur für LOAD (ohne Senden): 447 |

**Ergebnis:** Mit dem Entfernen von Centronics allein (211 Byte) passte JiffyDOS nicht; nach dem
Entfernen von Monitor, Bildschirmausdruck und Kassettenresten (918 Byte frei) passte es. Der Einbau
hat 585 Byte belegt; mit der Anzeige der Übertragungsart sind noch 300 Byte frei (größter Bereich 48 Byte).

Die Zahlen für JiffyDOS stammen aus dem fertigen C64DD26-Kernal; der Einbau hier braucht eigene
Anschlussstellen an die SpeedDOS-Routinen und kann einige Byte abweichen. Zu beachten: die
Zeitschleifen von `jd_sendbyte` und die Tabelle `jd_nibtab` dürfen keine Seitengrenze kreuzen, und
`$F9AB–$FA1B` wird vom Schnelllader mit in die 1541 übertragen (dort ohne Bedeutung).

Noch nicht geholt, aber ohne Funktionsverlust möglich: Kassettenmotor im IRQ (`$EA61–$EA7A`, ca. 23),
einzelne Füllbytes.
