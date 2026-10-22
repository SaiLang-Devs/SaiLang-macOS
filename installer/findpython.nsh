; Finds an installed Python 3.9+ (per user first, then per machine).
; Sets $PY_DIR (folder), $PYW_EXE (pythonw.exe) and $PY_EXE (python.exe).

Var PY_DIR
Var PYW_EXE
Var PY_EXE

!macro CheckPython ROOT VER
  ${If} $PY_DIR == ""
    ReadRegStr $0 ${ROOT} "Software\Python\PythonCore\${VER}\InstallPath" ""
    ${If} $0 != ""
      ${If} ${FileExists} "$0\pythonw.exe"
        StrCpy $PY_DIR $0
      ${EndIf}
    ${EndIf}
  ${EndIf}
!macroend

Function FindPython
  StrCpy $PY_DIR ""
  !insertmacro CheckPython HKCU 3.14
  !insertmacro CheckPython HKCU 3.13
  !insertmacro CheckPython HKCU 3.12
  !insertmacro CheckPython HKCU 3.11
  !insertmacro CheckPython HKCU 3.10
  !insertmacro CheckPython HKCU 3.9
  !insertmacro CheckPython HKLM 3.14
  !insertmacro CheckPython HKLM 3.13
  !insertmacro CheckPython HKLM 3.12
  !insertmacro CheckPython HKLM 3.11
  !insertmacro CheckPython HKLM 3.10
  !insertmacro CheckPython HKLM 3.9
  StrCpy $PYW_EXE "$PY_DIR\pythonw.exe"
  StrCpy $PY_EXE "$PY_DIR\python.exe"
FunctionEnd

; Puts the command-line arguments (everything after the program's own path) into $R0.
Function GetArgs
  StrCpy $R0 $CMDLINE
  StrCpy $R2 0
  StrCpy $R4 $R0 1
  ${If} $R4 == $\"
    IntOp $R2 $R2 + 1
    ArgsQuoted:
      StrCpy $R4 $R0 1 $R2
      IntOp $R2 $R2 + 1
      ${If} $R4 != $\"
      ${AndIf} $R4 != ""
        Goto ArgsQuoted
      ${EndIf}
  ${Else}
    ArgsPlain:
      StrCpy $R4 $R0 1 $R2
      IntOp $R2 $R2 + 1
      ${If} $R4 != " "
      ${AndIf} $R4 != ""
        Goto ArgsPlain
      ${EndIf}
  ${EndIf}
  StrCpy $R0 $R0 "" $R2
  StrCpy $R4 $R0 1
  ${If} $R4 == " "
    StrCpy $R0 $R0 "" 1
  ${EndIf}
FunctionEnd
