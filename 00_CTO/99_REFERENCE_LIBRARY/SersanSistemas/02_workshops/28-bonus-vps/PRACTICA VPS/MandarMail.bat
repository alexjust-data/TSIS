;//usábamos como servidor smtp 1and1 que requiere autenticación de servidor saliente

C:\InicioServidor\mailsend.exe -smtp smtp.1and1.es -port 25 -t xxx@google.com -user xxx@google.com -pass XXXXX -sub "ALERTA SERVIDOR TRADING USA" -M "TradeStation esta cerrado" -f xxx@google.com -auth-login


//si usamos servidor smtp local como servidor smtp

C:\InicioServidor\mailsend.exe -smtp 127.0.0.1 -f xxx@google.com -t xxx@google.com -sub "ALERTA SERVIDOR TRADING" -M "Tradestation esta cerrado en el servidor de TRADING"