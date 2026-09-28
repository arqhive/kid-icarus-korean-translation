"""Apply the distributed IPS using only Python's standard library."""
import argparse
import hashlib
import json
from pathlib import Path
from ips import apply_patch
from rom_delivery import copy_to_desktop


def main():
    here = Path(__file__).resolve().parent
    manifest = here / 'manifest.json'
    if not manifest.exists():
        manifest = here.parent / 'release' / 'manifest.json'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('output', nargs='?', type=Path)
    args = parser.parse_args()
    info = json.loads(manifest.read_text(encoding='utf-8'))
    old = args.original.read_bytes()
    if hashlib.sha256(old).hexdigest() != info['original']['sha256']:
        raise SystemExit('Original ROM SHA-256 mismatch. Do not apply to an already patched ROM.')
    patch = (manifest.parent / info['patch']['file']).read_bytes()
    if hashlib.sha256(patch).hexdigest() != info['patch']['sha256']:
        raise SystemExit('IPS SHA-256 mismatch.')
    new = apply_patch(old, patch)
    if hashlib.sha256(new).hexdigest() != info['patched']['sha256']:
        raise SystemExit('Patched ROM SHA-256 mismatch.')
    output = (args.output or Path(info['patched']['file'])).resolve()
    if output == args.original.resolve():
        raise SystemExit('Output must be a different file from the original.')
    if output.exists() and output.read_bytes() != new:
        raise SystemExit(f'Refusing to overwrite a different file: {output}')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(new)
    copy_to_desktop(output)
    print(f'Patched and verified: {output}')


if __name__ == '__main__':
    main()
