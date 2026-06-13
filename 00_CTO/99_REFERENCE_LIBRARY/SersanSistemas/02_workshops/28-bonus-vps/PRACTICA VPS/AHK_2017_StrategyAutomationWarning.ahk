#SingleInstance force
#WinActivateForce
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Loop
{
  WinWait Strategy Automation Warning
  sleep 10000 ;Esperamos 10s ya que cuando se produce una desconexion se acumulan las ordenes canceladas del forex y asi no nos machaca a emails
  WinActivate Strategy Automation Warning
  WinGetText texto, Strategy Automation Warning 
  WinGetTitle, title, Strategy Automation Warning
  tit1 := RegExMatch(title, "Strategy Automation Warning") 

  pos3:=RegExMatch(texto, "AN OPEN ORDER EXISTS") ;Para escapar de esta ventana mandamos Alt + c
  pos4:=RegExMatch(texto, "A PARTIALLY FILLED ORDER EXISTS") ;Para escapar de esta ventana mandamos Alt + d
  pos5:=RegExMatch(texto, "was recalculated and a historical position exists") ;Para escapar de esta ventana mandamos Alt + e
  pos6:=RegExMatch(texto, "You have to manually exit") 

  ;---------------------------------------------------------------------------------------------------------------------
  ;CERRAR ORDENES:
  ;Para escapar de esta ventana mandamos Alt + c: "Cancel Order"
  ;---------------------------------------------------------------------------------------------------------------------

  if (pos3 > 0)
  {
      RunWait C:\InicioServidor\MailOrderExists.bat
      Sleep 2000

      count1 := 0
      while (pos3 > 0 and count1 < 100)
      {
	
        WinActivate, Strategy Automation Warning, AN OPEN ORDER EXISTS
        Send {ALTDOWN}c{ALTUP}
        sleep 1000
	
        if count1 > 100
        {
          Runwait C:\InicioServidor\MandarVentanaAtascada.bat
          sleep 1000
	}
	count1 ++
	WinActivate Strategy Automation Warning, AN OPEN ORDER EXISTS
	WinGetText texto, Strategy Automation Warning, AN OPEN ORDER EXISTS
	pos3:=RegExMatch(texto,"AN OPEN ORDER EXISTS")
      }
  }

  ;---------------------------------------------------------------------------------------------------------------------
  ;NO CERRAR POSICIONES ABIERTAS:
  ;Para escapar de esta ventana mandamos Alt + d: "Do not Close position"
  ;---------------------------------------------------------------------------------------------------------------------

  if (pos4 > 0)
  {
      RunWait C:\InicioServidor\MailOrderExists.bat
      Sleep 2000

      count1 := 0
      while (pos4 > 0 and count1 < 100)
      {
        WinActivate, Strategy Automation Warning, A PARTIALLY FILLED ORDER EXISTS
        Send {ALTDOWN}d{ALTUP}
        sleep 1000
	
	if count1 > 100
	{
 	  Runwait C:\InicioServidor\MandarVentanaAtascada.bat
	  sleep 1000
        }
        count1 ++
        WinActivate Strategy Automation Warning, A PARTIALLY FILLED ORDER EXISTS
        WinGetText texto, Strategy Automation Warning, A PARTIALLY FILLED ORDER EXISTS
        pos4:=RegExMatch(texto,"A PARTIALLY FILLED ORDER EXISTS")
      }  
  }

  ;---------------------------------------------------------------------------------------------------------------------
  ;PERMITIR ESTRATEGIA SALIR POSICION:
  ;Para escapar de esta ventana mandamos Alt + e: "Exit this position"
  ;---------------------------------------------------------------------------------------------------------------------

  if (pos5 > 0)
  {
      RunWait C:\InicioServidor\MailOrderExists.bat
      Sleep 2000

      count1 := 0
      while (pos5 > 0 and count1 < 100)
      {
        WinActivate, Strategy Automation Warning, was recalculated and a historical position exists
        Send {ALTDOWN}e{ALTUP}
        sleep 1000
	if count1 > 100
	{
 	  Runwait C:\InicioServidor\MandarVentanaAtascada.bat
	  sleep 1000
        }
        count1 ++
        WinActivate Strategy Automation Warning, was recalculated and a historical position exists
        WinGetText texto, Strategy Automation Warning, was recalculated and a historical position exists
        pos5:=RegExMatch(texto,"was recalculated and a historical position exists")
      }  
  }

  ;---------------------------------------------------------------------------------------------------------------------
  ;SALIR MANUALMENTE:
  ;Nueva respecto a lo anterior, hasta ahora no se trataba nos bloqueaba el script. 
  ;Vamos a activar una estrategia y las órdenes no encajan. TS nos avisa.
  ;Cerramos la ventana PARA EVITAR QUE SI SE QUEDA ARRIBA bloquee la respuesta de otras y mandamos el mail de aviso: algo raro está ocurriendo!
  ;---------------------------------------------------------------------------------------------------------------------

  if (pos6 > 0)
  {
    WinClose Strategy Automation Warning, You have to manually exit
    RunWait C:\InicioServidor\MailManuallyExit.bat
    Sleep, 1000
    WinActivate Strategy Automation Warning, You have to manually exit
    WinGetText texto, Strategy Automation Warning, You have to manually exit
    pos6:=RegExMatch(texto,"You have to manually exit") 
  }
   
}
return