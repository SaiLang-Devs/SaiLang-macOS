; Launcher: starts SaiLang IDLE with the Python already on this computer.
; Built as a silent program (no window of its own).
!include "LogicLib.nsh"
!include "WordFunc.nsh"
!include "findpython.nsh"

Name "SaiLang IDLE ${VERSION}"
OutFile "${OUTDIR}\SaiLang-IDLE.exe"
Icon "${STAGE}\sailang.ico"
RequestExecutionLevel user
SilentInstall silent
ShowInstDetails nevershow

Section
  Call GetArgs
  Call FindPython
  ${If} $PY_DIR == ""
    MessageBox MB_ICONSTOP|MB_OK "SaiLang needs Python 3.9 or newer, but it was not found.$\r$\n$\r$\nInstall it from python.org (tick tcl/tk and IDLE), then start SaiLang again."
    Quit
  ${EndIf}
  ; This launcher sits in the SaiLang folder, next to the src folder.
  Exec "$\"$PYW_EXE$\" -c $\"import sys;sys.path.insert(0,r'$EXEDIR\src');from sailang.idle import main;main(sys.argv[1:])$\" $R0"
SectionEnd
