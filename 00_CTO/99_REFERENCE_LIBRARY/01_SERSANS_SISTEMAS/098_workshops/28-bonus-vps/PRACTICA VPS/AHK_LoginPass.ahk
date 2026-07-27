	
IfWinExist TradeStation Network Logon
{
	WinActivate, TradeStation Network Logon
	Send User
	Sleep 100
	Send {Tab}
	SendInput {Raw}Pass
	Sleep 100	
	Send {Tab}
	Send {ALTDOWN}t{ALTUP}
}
else
{
	Run C:\Program Files (x86)\TradeStation 10.0\Program\ORPlat.exe
	WinWait TradeStation Network Logon
	WinActivate, TradeStation Network Logon
	Send User
	Sleep 100
	Send {Tab}
	SendInput {Raw}Pass
	Sleep 100
	Send {Tab}
	Send {ALTDOWN}t{ALTUP}
}
return