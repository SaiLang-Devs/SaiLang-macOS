# Building SaiLang for macOS on GitHub

This project includes a GitHub Actions workflow that builds a standalone
macOS program with no Python install needed for the people who use it.

## Steps

1. Create a new repository on github.com (for example `SaiLang`).
2. Upload the contents of this folder. Keep the `.github` folder; it is hidden
   in some file managers, so make sure it is included.
3. Open the repository's **Actions** tab, choose **build-macos**, then
   **Run workflow**.
4. When the run finishes, open it and download the artifact **SaiLang-macos**.
   It contains `SaiLang-v1.0.0-macos-arm64.tar.gz` and its SHA-256 file.

## Notes

- The build runs on an Apple Silicon (M1/M2/M3/M4) Mac runner. It targets Macs
  with Apple Silicon. Intel Macs need a separate build on a `macos-13` runner.
- The program is not code-signed or notarised. On a Mac, people may need to
  allow it in System Settings > Privacy & Security, or run
  `xattr -d com.apple.quarantine sai` after unpacking.
- The smoke test runs during the build. If it fails, the build fails.
