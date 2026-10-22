"""Build the SaiLang website into dist/SaiLang-Website/ and package it as a ZIP.

Usage (from the project folder):
    python tools/build_website.py [path/to/SaiLang-v1.0.0.zip]

The SaiLang download ZIP is copied into the site's downloads folder, and its
size and SHA-256 are written into the download page. Search pages are indexed
into search-index.js so search works when the files are opened directly.
"""

import hashlib
import html
import json
import os
import re
import shutil
import sys
import zipfile
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "website", "src")
DIST = os.path.join(ROOT, "dist")
SITE_NAME = "SaiLang-Website"
SKIP_FROM_SEARCH = {"search.html"}


def read_version():
    with open(os.path.join(ROOT, "src", "sailang", "__init__.py"), encoding="utf-8") as handle:
        match = re.search(r'__version__\s*=\s*"([^"]+)"', handle.read())
    if not match:
        raise SystemExit("Could not find __version__ in src/sailang/__init__.py")
    return match.group(1)


class PageText(HTMLParser):
    """Collects the page title and the visible text inside <main>."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.parts = []
        self._in_title = False
        self._main_depth = 0
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        elif tag == "main":
            self._main_depth += 1
        elif tag in ("script", "style", "noscript"):
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "main" and self._main_depth:
            self._main_depth -= 1
        elif tag in ("script", "style", "noscript") and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif self._main_depth and not self._skip_depth:
            self.parts.append(data)


def visible_text(page_html):
    parser = PageText()
    parser.feed(page_html)
    text = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    return parser.title.strip(), text


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fill(template, values):
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def main(argv):
    version = read_version()
    zip_source = argv[1] if len(argv) > 1 else os.path.join(DIST, f"SaiLang-v{version}.zip")
    if not os.path.isfile(zip_source):
        raise SystemExit(f"SaiLang ZIP not found: {zip_source}. Run tools/build_zip.py first.")
    zip_name = os.path.basename(zip_source)
    sha = sha256_of(zip_source)
    size_kb = f"{os.path.getsize(zip_source) / 1024:.0f}"
    setup_source = os.path.join(DIST, "windows", f"SaiLang-Setup-v{version}.exe")
    if not os.path.isfile(setup_source):
        raise SystemExit(f"Windows setup not found: {setup_source}. Run installer/build_installer.py first.")
    setup_name = os.path.basename(setup_source)
    setup_sha = sha256_of(setup_source)
    setup_kb = f"{os.path.getsize(setup_source) / 1024:.0f}"

    out = os.path.join(DIST, SITE_NAME)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "downloads"))
    os.makedirs(os.path.join(out, "assets"))

    header = open(os.path.join(SRC, "_header.html"), encoding="utf-8").read()
    footer = open(os.path.join(SRC, "_footer.html"), encoding="utf-8").read()
    values = {"VERSION": version, "ZIP_NAME": zip_name, "SHA256": sha, "SIZE_KB": size_kb,
              "SETUP_NAME": setup_name, "SETUP_SHA256": setup_sha, "SETUP_SIZE_KB": setup_kb}

    pages = {}
    for name in sorted(os.listdir(SRC)):
        if not name.endswith(".html") or name.startswith("_"):
            continue
        content = open(os.path.join(SRC, name), encoding="utf-8").read()
        content = content.replace("<!--HEADER-->", header).replace("<!--FOOTER-->", footer)
        content = fill(content, values)
        with open(os.path.join(out, name), "w", encoding="utf-8") as handle:
            handle.write(content)
        pages[name] = content

    for name in os.listdir(os.path.join(SRC, "assets")):
        shutil.copy2(os.path.join(SRC, "assets", name), os.path.join(out, "assets", name))

    shutil.copy2(zip_source, os.path.join(out, "downloads", zip_name))
    shutil.copy2(setup_source, os.path.join(out, "downloads", setup_name))
    with open(os.path.join(out, "downloads", setup_name + ".sha256"), "w", encoding="utf-8") as handle:
        handle.write(f"{setup_sha}  {setup_name}\n")
    with open(os.path.join(out, "downloads", zip_name + ".sha256"), "w", encoding="utf-8") as handle:
        handle.write(f"{sha}  {zip_name}\n")

    index = []
    for name, content in pages.items():
        if name in SKIP_FROM_SEARCH:
            continue
        title, text = visible_text(content)
        index.append({"url": name, "title": title or name, "text": text})
    payload = json.dumps(index, ensure_ascii=False).replace("</", "<\\/")
    with open(os.path.join(out, "search-index.js"), "w", encoding="utf-8") as handle:
        handle.write("window.SAI_INDEX = " + payload + ";\n")

    site_zip = os.path.join(DIST, f"{SITE_NAME}-v{version}.zip")
    with zipfile.ZipFile(site_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        for folder, _dirs, files in os.walk(out):
            for name in files:
                full = os.path.join(folder, name)
                # Files go at the top of the ZIP, so index.html is at the root of the site.
                archive.write(full, os.path.relpath(full, out))

    print(f"Built {len(pages)} pages into {out}")
    print(f"Search index: {len(index)} pages")
    print(f"Website ZIP: {site_zip} ({os.path.getsize(site_zip) // 1024} KB)")
    return site_zip


if __name__ == "__main__":
    main(sys.argv)
