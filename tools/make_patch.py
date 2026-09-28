"""Package an existing successful build as the version in VERSION."""
import hashlib
import json
import shutil
import zipfile
import zlib
from paths import ROOT, ROM, ORIGINAL_SHA256, FINAL, STEM, VERSION
from ips import apply_patch


def fingerprint(path):
    data = path.read_bytes()
    return dict(file=path.name, bytes=len(data), crc32=f'{zlib.crc32(data):08X}',
                **{algo: hashlib.new(algo, data).hexdigest() for algo in ('md5', 'sha1', 'sha256')})


def main():
    source = fingerprint(ROM)
    if source['sha256'] != ORIGINAL_SHA256:
        raise SystemExit('Original ROM SHA-256 mismatch.')
    target = FINAL / (STEM + '.gba')
    patch = FINAL / (STEM + '.ips')
    patched = fingerprint(target)
    meta = json.loads((FINAL / 'build.json').read_text(encoding='utf-8'))
    if patched['sha256'] != meta['patched_sha256']:
        raise SystemExit('Build metadata mismatch; rebuild first.')
    if apply_patch(ROM.read_bytes(), patch.read_bytes()) != target.read_bytes():
        raise SystemExit('IPS round-trip failed.')
    release = ROOT / 'release'
    release.mkdir(exist_ok=True)
    shutil.copyfile(patch, release / patch.name)
    manifest = dict(version=VERSION, original=source, patched=patched, patch=fingerprint(patch))
    (release / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    files = {name: release / name for name in (patch.name, 'manifest.json', 'README_한국어.txt')}
    files.update({'LICENSE': ROOT / 'LICENSE', 'Galmuri-OFL.md': ROOT / 'fonts' / 'Galmuri-OFL.md'})
    files.update({name: ROOT / 'tools' / name for name in ('apply_patch.py', 'ips.py', 'rom_delivery.py')})
    archive = release / (STEM + '_Patch.zip')
    # Fixed timestamps and ordering make repeated packaging deterministic.
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as out:
        for name, path in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 9, 29, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            out.writestr(entry, path.read_bytes())
    print(f'Packaged {VERSION}: {archive}')
    print(f'ROM SHA-256: {patched["sha256"]}')


if __name__ == '__main__':
    main()
