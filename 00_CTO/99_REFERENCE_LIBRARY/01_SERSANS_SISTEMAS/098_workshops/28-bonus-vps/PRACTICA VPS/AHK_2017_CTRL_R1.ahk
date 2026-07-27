#SingleInstance force
#WinActivateForce
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Loop
{
  IfWinExist TradeStation 9.5
  {
    WinActivate
    if(A_Hour=4)
    {
      if (A_Min>29)
      {
        Send {Ctrl Down}r{Ctrl Up}
        Sleep 60000
      }
    }
    Sleep 10000
  }
}
return