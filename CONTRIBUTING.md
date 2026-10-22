# Contributing to SaiLang

1. Fork the repository and create a branch.
2. Run the tests before and after your change:
   `python -m unittest discover -s tests -v`
3. Add a test for every new language feature or bug fix.
4. Keep the language specification in `docs/LANGUAGE_SPEC.md` up to date. A
   change to syntax or scope rules is a language change and needs a note in
   `CHANGELOG.md`.
5. Open a pull request that explains what changed and why.
