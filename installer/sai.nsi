; Launcher: runs SaiLang from a console window (run a file, check, or the prompt).
!include "LogicLib.nsh"
!include "WordFunc.nsh"
!include "findpython.nsh"

Name "SaiLang ${VERSION}"
OutFile "${OUTDIR}\sai.exe"
Icon "${STAGE}\sailang.ico"
RequestExecutionLevel user
SilentInstall silent
ShowInstDetails nevershow

Section
  Call GetArgs
  Call FindPython
  ${If} $PY_DIR == ""
    MessageBox MB_ICONSTOP|MB_OK "SaiLang needs Python 3.9 or newer, but it was not found.$\r$\n$\r$\nInstall it from python.org (tick tcl/tk and IDLE), then try again."
    Quit
  ${EndIf}
  ExecWait "$\"$PY_EXE$\" -c $\"import sys;sys.path.insert(0,r'$EXEDIR\src');from sailang.cli import main;sys.exit(main(sys.argv[1:]))$\" $R0"
SectionEnd
