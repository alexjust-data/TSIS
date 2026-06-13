echo *** Tareas de Mantenimiento y reinicio ***

ping localhost -n 300

echo *** Reiniciamos ***
start "1" "C:\InicioServidor\Restart.exe"
Start "2" "C:\InicioServidor\Desconexion.cmd"
