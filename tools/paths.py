"""Shared paths; generated game data belongs only in work/."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work' / 'build'
FONTS = ROOT / 'fonts'
ASSETS = ROOT / 'tools' / 'assets'
VERSION = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
STEM = f'Palthena_KO_{VERSION}'
FINAL = WORK / 'final'
ORIGINAL_SHA256 = '7a2118c605713898a8befa0dce2835998481bcbdd92850379620450de6209e4b'
ROM = Path(os.environ.get('PALTHENA_JP_ROM', str(ROOT / 'rom' / 'Famicom Mini 24 - Hikari Shinwa - Palthena no Kagami (Japan).gba'))).resolve()
MGBA = Path(os.environ.get('MGBA_LIBRETRO', str(ROOT / 'vendor' / 'mgba_libretro.dll'))).resolve()
sys.path.insert(0, str(ROOT / 'translation'))
