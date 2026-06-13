echo *** This starts TS waiting 30 seconds ***
ping localhost -n 30
start "1" "C:\InicioServidor\TS_LoginPass.exe"
ping localhost -n 10
start "2" "C:\InicioServidor\TS_CLOSEWS_WithoutSaving.exe"
start "3" "C:\InicioServidor\queuedOrder.exe"
start "4" "C:\InicioServidor\queuedOrder2.exe"


ping localhost -n 10
start "5" "C:\InicioServidor\TS_Start_5MinClosed.exe"
start "6" "C:\Inicioservidor\TS_StrategyAutomationWarning.exe"
exit