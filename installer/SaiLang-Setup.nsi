; SaiLang setup wizard. Installs for the current user, so no administrator rights are needed.
!include "MUI2.nsh"
!include "findpython.nsh"

Name "SaiLang ${VERSION}"
OutFile "${OUTDIR}\SaiLang-Setup-v${VERSION}.exe"
InstallDir "$LOCALAPPDATA\Programs\SaiLang"
InstallDirRegKey HKCU "Software\SaiLang" "InstallDir"
RequestExecutionLevel user
BrandingText "SaiLang ${VERSION} setup"
Icon "${STAGE}\sailang.ico"
UninstallIcon "${STAGE}\sailang.ico"

!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "Welcome to SaiLang ${VERSION}"
!define MUI_WELCOMEPAGE_TEXT "This wizard installs SaiLang, a programming language with English-like commands.$\r$\n$\r$\nYou will get SaiLang IDLE (an editor and runner), a command prompt, examples, and documentation.$\r$\n$\r$\nNo administrator rights are needed. Click Next to continue."
!define MUI_FINISHPAGE_TITLE "SaiLang is installed"
!define MUI_FINISHPAGE_TEXT "Open SaiLang IDLE to start coding. Open the examples folder to try the example programs."
!define MUI_FINISHPAGE_RUN "$INSTDIR\SaiLang-IDLE.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Start SaiLang IDLE"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${LICENSE}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Function .onInit
  Call FindPython
  ${If} $PY_DIR == ""
    MessageBox MB_YESNO|MB_ICONEXCLAMATION "SaiLang needs Python 3.9 or newer, and it was not found on this computer.$\r$\n$\r$\nOpen the Python download page now?$\r$\n$\r$\nWhen you install Python, choose 'Install for me only' and tick 'tcl/tk and IDLE'. Then run this setup again." IDYES open_python IDNO continue_anyway
    open_python:
      ExecShell "open" "https://www.python.org/downloads/"
      Abort
    continue_anyway:
  ${EndIf}
FunctionEnd

Section "SaiLang" SecMain
  SectionIn RO
  SetOutPath "$INSTDIR"
  File /r "${STAGE}\*.*"
  File "${OUTDIR}\SaiLang-IDLE.exe"
  File "${OUTDIR}\sai.exe"

  WriteUninstaller "$INSTDIR\Uninstall.exe"

  CreateDirectory "$SMPROGRAMS\SaiLang"
  CreateShortCut "$SMPROGRAMS\SaiLang\SaiLang IDLE.lnk" "$INSTDIR\SaiLang-IDLE.exe" "" "$INSTDIR\sailang.ico" 0
  CreateShortCut "$SMPROGRAMS\SaiLang\SaiLang Prompt.lnk" "$INSTDIR\sai.exe" "" "$INSTDIR\sailang.ico" 0
  CreateShortCut "$SMPROGRAMS\SaiLang\Examples.lnk" "$INSTDIR\examples"
  CreateShortCut "$SMPROGRAMS\SaiLang\Uninstall SaiLang.lnk" "$INSTDIR\Uninstall.exe"
  CreateShortCut "$DESKTOP\SaiLang IDLE.lnk" "$INSTDIR\SaiLang-IDLE.exe" "" "$INSTDIR\sailang.ico" 0

  ; Double-clicking a .sai file opens it in SaiLang IDLE (current user only).
  WriteRegStr HKCU "Software\Classes\.sai" "" "SaiLang.Program"
  WriteRegStr HKCU "Software\Classes\SaiLang.Program" "" "SaiLang program"
  WriteRegStr HKCU "Software\Classes\SaiLang.Program\DefaultIcon" "" "$INSTDIR\sailang.ico"
  WriteRegStr HKCU "Software\Classes\SaiLang.Program\shell\open\command" "" "$\"$INSTDIR\SaiLang-IDLE.exe$\" $\"%1$\""

  WriteRegStr HKCU "Software\SaiLang" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiLang" "DisplayName" "SaiLang ${VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiLang" "DisplayVersion" "${VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiLang" "Publisher" "SaiLang contributors"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiLang" "DisplayIcon" "$INSTDIR\sailang.ico"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiLang" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiLang" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiLang" "NoRepair" 1
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\SaiLang IDLE.lnk"
  RMDir /r "$SMPROGRAMS\SaiLang"
  DeleteRegKey HKCU "Software\Classes\.sai"
  DeleteRegKey HKCU "Software\Classes\SaiLang.Program"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaiLang"
  DeleteRegKey HKCU "Software\SaiLang"
  RMDir /r "$INSTDIR"
SectionEnd
