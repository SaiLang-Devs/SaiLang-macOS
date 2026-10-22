# Learn to Code with SaiLang (book source)

The printable A5 book is built from the content files in `content/`.

    python book/check_examples.py   # runs every example in the book through SaiLang
    python book/build_book.py       # checks the examples, then writes book/build/*.pdf

* `content/part1.py` and `content/part2.py` hold the text, code examples and
  boxes for every page. Each code example lists its expected output (`out`);
  the build stops if SaiLang does not produce it.
* Window examples are started under a display when one is available
  (`xvfb-run -a python book/build_book.py` on Linux).
* Fonts are DejaVu Sans and DejaVu Sans Mono, which are free to use.
* Pages are A5 without bleed. Add bleed and crop marks before sending the file to a printer.
