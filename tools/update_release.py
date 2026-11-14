#!/usr/bin/env python3
"""Refresh this release repository from the sibling development folders.

Run from anywhere:  python3 tools/update_release.py [--manuals-en DIR] [--check]

Copies the ROMs and the manuals (all as PDF in manuals/) and the images of this page
into this repository, writes CHECKSUMS.md5 and CHECKSUMS.sha256, and reports what is
out of date:

- a German development note changed after docs/de and docs/en were derived from it;
- an English manual is missing or older than the German one;
- the checksums printed in a manual differ from the ROMs being published;
- rom/ holds a file that is not on the list below, or one the README does not name;
- README or docs contain a word that must not appear there.

The notes in docs/de are derived by hand from the development notes (build and test
instructions of the development folders are left out), docs/en is their translation.
After updating both, run with --stamp-notes to record the state of the sources.

The script exits with status 1 if anything is out of date, so a release is never
tagged with one language lagging behind. --check only reports and changes nothing.
"""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def find_root(start):
    """Project folder: the first parent with Builds and SpeedDos26 (the repository
    lives in Git/SpeedDOS26; this also works from a worktree below .claude/worktrees)."""
    for d in start.parents:
        if (d / 'Builds').is_dir() and (d / 'SpeedDos26').is_dir():
            return d
    return start.parent


ROOT = find_root(REPO)
# Name in docs/de and docs/en -> German development note it is derived from
NOTES = {
    'speeddos26-notes.md': ('SpeedDos26', 'README.md'),
    'c1571-firmware.md': ('SpeedDos26', '1571/README.md'),
    # no development note for the C128 kernal: derived from the manual chapter and the Makefile
    'c128-kernal.md': ('SpeedDos26', 'c128/Makefile'),
}
# Only these files are published in rom/. Never add an image that holds JiffyDOS drive
# firmware (for example C1541_29F040DEV.bin or the AM27C040 image).
ROMS = ['C64SpeedDos26.bin', 'C64IISpeedDos26.bin',
        'C1541SpeedDOS26.bin', 'C1541IISpeedDOS26.bin',
        'C1571SpeedDOS26.bin', 'C1571CRSpeedDOS26.bin',
        'C128SpeedDos26-DE.bin', 'C128SpeedDos26-EN.bin', 'C1541_29F040.BIN']
# Optional, published when present in Builds (none at the moment)
OPTIONAL_ROMS = []
# Every manual goes to manuals/de and manuals/en as PDF (German from Builds,
# English from --manuals-en); new manuals are added here, never to docs/.
MANUALS = {'SpeedDos26_Handbuch.pdf': 'SpeedDos26_Manual.pdf'}
# ROMs whose MD5 checksums the manuals state
MANUAL_ROMS = ['C64SpeedDos26.bin', 'C64IISpeedDos26.bin', 'C1541SpeedDOS26.bin',
               'C1541IISpeedDOS26.bin', 'C1541_29F040.BIN', 'C1571SpeedDOS26.bin',
               'C1571CRSpeedDOS26.bin',
               'C128SpeedDos26-DE.bin', 'C128SpeedDos26-EN.bin']
# Images of the README, from the manual folder
ASSETS = ['Multi-Speeder_Logo.png', 'sd_01_startbild.png']
# Words that must not appear in README.md, LICENSE.md and docs/
FORBIDDEN = re.compile(r'\b(vice|emulator\w*|emuliert\w*|emulated|x64sc|x128)\b', re.I)
STAMP = REPO / 'tools' / 'derived-from.json'


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def copy(src, dst, check, problems):
    src, dst = pathlib.Path(src), pathlib.Path(dst)
    if not src.exists():
        problems.append('missing source: %s' % src)
        return
    if check:
        if not dst.exists() or sha(src) != sha(dst):
            problems.append('out of date: %s' % dst.relative_to(REPO))
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def main():
    global ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument('--manuals-en', help='folder with the English PDFs (default: Builds)')
    ap.add_argument('--check', action='store_true', help='report only, change nothing')
    ap.add_argument('--stamp-notes', action='store_true',
                    help='record the current German development notes as taken over '
                         '(after updating docs/de and docs/en)')
    ap.add_argument('--root', default=str(ROOT), help='project folder with Builds and SpeedDos26')
    a = ap.parse_args()
    ROOT = pathlib.Path(a.root).resolve()
    BUILDS = ROOT / 'Builds'
    bad = []

    published = list(ROMS)
    for r in ROMS:
        copy(BUILDS / r, REPO / 'rom' / r, a.check, bad)
    for r in OPTIONAL_ROMS:
        if (BUILDS / r).exists():
            published.append(r)
            copy(BUILDS / r, REPO / 'rom' / r, a.check, bad)
        elif (REPO / 'rom' / r).exists():
            bad.append('missing source: %s (but published in rom/)' % (BUILDS / r))
        else:
            print('note: optional ROM not built yet, not published: %s' % r)
    for de, en in MANUALS.items():
        copy(BUILDS / de, REPO / 'manuals' / 'de' / de, a.check, bad)
        src = pathlib.Path(a.manuals_en or BUILDS) / en
        copy(src, REPO / 'manuals' / 'en' / en, a.check, bad)
        if src.exists() and (BUILDS / de).exists() and src.stat().st_mtime < (BUILDS / de).stat().st_mtime:
            bad.append('English manual older than German one: %s' % en)
    for name in ASSETS:
        copy(ROOT / 'SpeedDos26' / 'doc' / 'handbuch' / 'img' / name, REPO / 'assets' / name, a.check, bad)

    # rom/ must hold exactly the published files, and the README must name each one.
    readme = (REPO / 'README.md').read_text(encoding='utf-8') if (REPO / 'README.md').exists() else ''
    if (REPO / 'rom').is_dir():
        for p in sorted((REPO / 'rom').iterdir()):
            if p.name not in published:
                bad.append('not on the list of published ROMs: rom/%s' % p.name)
            elif '(rom/%s)' % p.name not in readme:
                bad.append('README.md does not describe rom/%s' % p.name)

    # The notes are derived by hand; a changed German source makes both languages stale.
    stamps = json.loads(STAMP.read_text()) if STAMP.exists() else {}
    for name, (repo, path) in NOTES.items():
        src = ROOT / repo / path
        if not src.exists():
            bad.append('missing source: %s' % src)
            continue
        now = sha(src)
        if a.stamp_notes:
            stamps[name] = now
        elif stamps.get(name) != now:
            bad.append('notes stale: docs/de/%s and docs/en/%s (German source %s/%s changed)'
                       % (name, name, repo, path))
        for lang in ('de', 'en'):
            if not (REPO / 'docs' / lang / name).exists():
                bad.append('missing note: docs/%s/%s' % (lang, name))
    if a.stamp_notes:
        STAMP.write_text(json.dumps(stamps, indent=2, sort_keys=True) + '\n')

    for md in [REPO / 'README.md', REPO / 'LICENSE.md'] + sorted((REPO / 'docs').rglob('*.md')):
        if md.exists():
            for no, line in enumerate(md.read_text(encoding='utf-8').splitlines(), 1):
                m = FORBIDDEN.search(line)
                if m:
                    bad.append('forbidden word "%s": %s line %d' % (m.group(0), md.relative_to(REPO), no))

    # Every manual must name the checksums of exactly the files published here.
    for lang_dir in ('de', 'en'):
        for pdf in sorted((REPO / 'manuals' / lang_dir).glob('*.pdf')):
            try:
                txt = subprocess.check_output(['pdftotext', str(pdf), '-'], text=True)
            except (OSError, subprocess.CalledProcessError) as e:
                bad.append('cannot read %s: %s' % (pdf.name, e))
                continue
            flat = re.sub(r'\s+', '', txt)
            for f in [REPO / 'rom' / x for x in MANUAL_ROMS]:
                # table cells wrap long checksums in the PDF text, so compare the first 16 digits
                if f.exists() and hashlib.md5(f.read_bytes()).hexdigest()[:16] not in flat:
                    bad.append('%s does not state the MD5 of %s' % (pdf.name, f.name))

    files = sorted(p for d in ('rom', 'manuals') for p in (REPO / d).rglob('*') if p.is_file())
    for algo, out in (('md5', 'CHECKSUMS.md5'), ('sha256', 'CHECKSUMS.sha256')):
        lines = ['%s  %s' % (hashlib.new(algo, f.read_bytes()).hexdigest(), f.relative_to(REPO).as_posix())
                 for f in files]
        text = '\n'.join(lines) + '\n'
        if not a.check:
            (REPO / out).write_text(text)
        elif not (REPO / out).exists() or (REPO / out).read_text() != text:
            bad.append('out of date: %s' % out)

    for x in bad:
        print('PROBLEM:', x)
    print('%d problem(s)' % len(bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
