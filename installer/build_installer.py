"""Build the Windows programs for SaiLang:

    dist/windows/SaiLang-Setup-v1.0.0.exe   the setup wizard (installs everything)
    dist/windows/SaiLang-IDLE.exe           launcher for SaiLang IDLE
    dist/windows/sai.exe                    launcher for the command line and prompt

Run from the project folder on Linux or Windows, with NSIS (makensis) installed.
    python installer/build_installer.py
"""

import hashlib
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLER = os.path.join(ROOT, "installer")
STAGE = os.path.join(INSTALLER, "stage")
OUT = os.path.join(ROOT, "dist", "windows")
SKIP_NAMES = {"__pycache__", ".pytest_cache"}
SKIP_SUFFIXES = (".pyc", ".sha256", ".zip")
SKIP_FILES = {"sai_example_notes.txt"}


def version():
    text = open(os.path.join(ROOT, "src", "sailang", "__init__.py"), encoding="utf-8").read()
    return re.search(r'__version__\s*=\s*"([^"]+)"', text).group(1)


# ----- icon ---------------------------------------------------------------------
def make_icon(path_ico):
    """Make the SaiLang icon from the SaiLang logo, at 16, 32, 48 and 256 pixels."""
    from PIL import Image
    logo = Image.open(os.path.join(ROOT, "src", "sailang", "assets", "sailang-logo.png")).convert("RGBA")
    base = logo.resize((256, 256), Image.LANCZOS)
    images = [base.resize((s, s), Image.LANCZOS) for s in (16, 32, 48, 256)]
    write_ico(path_ico, images)


def write_ico(path, images):
    """Windows icon file with 32-bit bitmap entries (the format the NSIS compiler reads reliably)."""
    entries, blobs = [], []
    offset = 6 + 16 * len(images)
    for image in images:
        w, h = image.size
        pixels = image.tobytes("raw", "BGRA")
        rows = b"".join(pixels[y * w * 4:(y + 1) * w * 4] for y in range(h - 1, -1, -1))  # bottom-up
        mask_row = ((w + 31) // 32) * 4
        mask = bytes(mask_row * h)
        header = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0, len(rows) + len(mask), 0, 0, 0, 0)
        blob = header + rows + mask
        entries.append(struct.pack("<BBBBHHII", 0 if w >= 256 else w, 0 if h >= 256 else h, 0, 0, 1, 32,
                                   len(blob), offset))
        blobs.append(blob)
        offset += len(blob)
    with open(path, "wb") as handle:
        handle.write(struct.pack("<HHH", 0, 1, len(images)))
        handle.write(b"".join(entries))
        handle.write(b"".join(blobs))


# ----- staging -------------------------------------------------------------------
def copy_tree(source, target):
    for folder, dirs, files in os.walk(source):
        dirs[:] = [d for d in dirs if d not in SKIP_NAMES]
        relative = os.path.relpath(folder, source)
        destination = os.path.join(target, relative) if relative != "." else target
        os.makedirs(destination, exist_ok=True)
        for name in files:
            if name.endswith(SKIP_SUFFIXES) or name in SKIP_FILES:
                continue
            shutil.copy2(os.path.join(folder, name), os.path.join(destination, name))


def stage_files():
    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)
    copy_tree(os.path.join(ROOT, "src"), os.path.join(STAGE, "src"))
    copy_tree(os.path.join(ROOT, "examples"), os.path.join(STAGE, "examples"))
    copy_tree(os.path.join(ROOT, "docs"), os.path.join(STAGE, "docs"))
    for name in ("README.md", "LICENSE", "CHANGELOG.md"):
        shutil.copy2(os.path.join(ROOT, name), os.path.join(STAGE, name))
    make_icon(os.path.join(STAGE, "sailang.ico"))


# ----- compiling ------------------------------------------------------------------
def makensis(script, ver, extra=()):
    args = ["makensis", "-V2", f"-DVERSION={ver}", f"-DSTAGE={STAGE}", f"-DOUTDIR={OUT}",
            f"-DLICENSE={os.path.join(ROOT, 'LICENSE')}", *extra, os.path.join(INSTALLER, script)]
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout[-2000:])
        print(result.stderr[-2000:])
        raise SystemExit(f"NSIS failed on {script}")


def main():
    ver = version()
    os.makedirs(OUT, exist_ok=True)
    stage_files()
    makensis("SaiLang-IDLE.nsi", ver)
    makensis("sai.nsi", ver)
    makensis("SaiLang-Setup.nsi", ver)
    setup = os.path.join(OUT, f"SaiLang-Setup-v{ver}.exe")
    digest = hashlib.sha256(open(setup, "rb").read()).hexdigest()
    with open(setup + ".sha256", "w", encoding="utf-8") as handle:
        handle.write(f"{digest}  {os.path.basename(setup)}\n")
    for name in sorted(os.listdir(OUT)):
        print(f"{name}  {os.path.getsize(os.path.join(OUT, name)) // 1024} KB")
    print(f"SHA-256 of setup: {digest}")


if __name__ == "__main__":
    main()
