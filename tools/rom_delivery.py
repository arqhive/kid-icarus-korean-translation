"""User rule: every ROM build delivers one identical copy to Windows Desktop."""
from pathlib import Path
import hashlib, os, shutil, sys


def copy_to_desktop(rom):
    if sys.platform == 'win32':
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders') as key:
            desktop = Path(os.path.expandvars(winreg.QueryValueEx(key, 'Desktop')[0]))
    else:
        desktop = Path.home() / 'Desktop'
    desktop.mkdir(parents=True, exist_ok=True)
    source = Path(rom).resolve()
    destination = desktop / source.name
    if source != destination.resolve():
        shutil.copy2(source, destination)
    assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(destination.read_bytes()).digest()
    print('Desktop copy:', str(destination), flush=True)
    return destination
