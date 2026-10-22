# Publishing SaiLang

This guide is for the person who maintains SaiLang. It covers putting the
source code on GitHub, giving Windows users a download, and releasing responsibly.

Nothing in this document has been done for you. The steps assume you have
your own GitHub account. The release ZIP and checksum are created by
`tools/build_zip.py`.

## A. Publish the source code on GitHub

### A1. Create the repository

1. Sign in at https://github.com and click **New** (or the **+** menu > **New repository**).
2. Name it `SaiLang`. Choose **Public** so people can download it.
3. Do **not** tick "Add a README" or "Add a .gitignore". The project already has them.
4. Click **Create repository**.

### A2. Upload the source files

Easiest method, no command-line tools needed:

1. On the new empty repository page, click **uploading an existing file**.
2. Drag in the *contents* of the `SaiLang-v1.0.0` folder (the folder itself
   is not needed; the files and subfolders are). Do **not** upload the ZIP.
3. Type a commit message such as "SaiLang 1.0.0" and click **Commit changes**.

Method with Git (if you have it installed):

```
cd SaiLang-v1.0.0
git init
git add .
git commit -m "SaiLang 1.0.0"
git branch -M main
git remote add origin https://github.com/YOUR-NAME/SaiLang.git
git push -u origin main
```

### A3. Check the README, licence, and release notes

* `README.md` is shown on the repository front page.
* `LICENSE` is the MIT licence. Keep it, or choose another open-source licence
  and replace the file.
* `CHANGELOG.md` holds the release notes.

### A4. Publish version v1.0.0 as a GitHub Release

1. On the repository page, click **Releases** > **Draft a new release**.
2. Click **Choose a tag**, type `v1.0.0`, and choose **Create new tag on publish**.
3. Title: `SaiLang v1.0.0`.
4. Description: paste the 1.0.0 section from `CHANGELOG.md`.
5. Drag `SaiLang-v1.0.0.zip` and `SaiLang-v1.0.0.zip.sha256` into the
   attachment box.
6. Click **Publish release**.

### A5. Update the repository for later versions

1. Change the code and tests. Run `python -m unittest discover -s tests`.
2. Update `CHANGELOG.md` and the version number in `src/sailang/__init__.py`
   and `pyproject.toml`.
3. Commit and push (or upload the changed files on GitHub).
4. Run `python tools/build_zip.py`, then create a new release with a new tag
   such as `v1.0.1`.

## B. Distribute SaiLang to Windows users

### B1. What the ZIP is (a portable package)

`SaiLang-v1.0.0.zip` is a **portable** package. Users extract it and run
`sai.bat`. It does not install anything system-wide and does not need
administrator rights. Users must have Python 3.9+ installed, and the launcher
explains how to get it if not.

A real **installer** (a Setup.exe that adds Start menu entries and an
uninstaller) is not included in 1.0.0. If you want one, build it with a
tool such as Inno Setup or NSIS. Inno Setup can run without administrator
rights when configured for per-user install.

### B2. Creating the download

```
python tools/build_zip.py
```

This writes `dist/SaiLang-v1.0.0.zip` and `dist/SaiLang-v1.0.0.zip.sha256`.
Upload both to the GitHub Release.

### B3. Checksums

The `.sha256` file lets users confirm the download was not changed. On Windows:

```
certutil -hashfile SaiLang-v1.0.0.zip SHA256
```

Compare the output with the text in the `.sha256` file.

### B4. Standalone executables (not included)

SaiLang 1.0.0 does **not** build a standalone `.exe`. Tools such as PyInstaller
can bundle the Python engine into an `.exe`, which would let users run SaiLang
without installing Python. This has not been tested for this release, so do not
advertise it until you have tested it on Windows 10 and 11.

### B5. Code signing (optional)

Windows shows a warning for unsigned programs. A code-signing certificate
removes or reduces that warning. Certificates cost money and must come from a
trusted authority. Signing is only needed for an `.exe` or installer, not for
the `.bat` launchers or the ZIP.

## C. Publish responsibly

### C1. Licence

SaiLang uses the MIT licence, which lets anyone use, change, and share the
software, provided the copyright notice stays in place. Keep `LICENSE` in the
repository and in every release.

### C2. Dependencies and licences

| Dependency | Needed for | Licence |
|------------|------------|---------|
| Python 3.9+ | Running the engine | PSF License |
| Tkinter (part of Python) | Windows, images, games | PSF License / Tcl-Tk licence |

SaiLang has no third-party Python packages. Check the licence of anything you
add later.

### C3. Honest claims

Describe SaiLang 1.0.0 as an interpreted language that runs `.sai` files
through a Python engine. Do not describe it as a native or compiled language
until a compiler exists and has been tested. The same applies to any claim of
native `.exe` output or a bytecode compiler.

### C4. Version numbers

Use semantic versioning: `MAJOR.MINOR.PATCH`.

* PATCH: bug fixes that do not change how programs behave.
* MINOR: new features that keep existing programs working.
* MAJOR: changes that break existing programs.

### C5. Release testing

Before every release:

1. Run `python -m unittest discover -s tests -v` on Windows 10 and Windows 11.
2. Extract the ZIP into a new folder and run `sai.bat examples\hello.sai`.
3. Open the desktop, image, and game examples and check each one works.
4. Check the ZIP contains the files listed in the README.

### C6. Bug reports and security issues

* Bugs: open an issue on GitHub with the SaiLang version, Windows version,
  the program that fails, and the full error message.
* Security problems: use GitHub's **Report a vulnerability** option (Security
  tab). Do not post security details in a public issue. See `SECURITY.md`.
