"""Build all stages from the original Japanese ROM, without legacy artifacts."""
import hashlib
import os
import subprocess
import sys
from paths import ROOT, WORK, ROM, ORIGINAL_SHA256, FINAL, STEM


def main():
    if sys.flags.optimize:
        raise SystemExit('Assertions must stay enabled: do not use python -O.')
    if not ROM.is_file():
        raise SystemExit(f'Original ROM missing: {ROM}\nUse rom/ or set PALTHENA_JP_ROM.')
    if hashlib.sha256(ROM.read_bytes()).hexdigest() != ORIGINAL_SHA256:
        raise SystemExit('Original ROM SHA-256 mismatch. Use the supported unmodified Japanese ROM.')
    WORK.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    for name in ('analyze_rom.py', 'build_logo_v2.py', 'build_text_patch.py',
                 'audit_kana.py', 'build_text_v3.py'):
        print(f'Building: {name}', flush=True)
        subprocess.run([sys.executable, str(ROOT / 'tools' / name)], cwd=ROOT, env=env, check=True)
    print(f'Built: {FINAL / (STEM + ".gba")}', flush=True)


if __name__ == '__main__':
    main()
