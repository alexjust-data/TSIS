Set-Location -LiteralPath 'C:\TSIS_Data'

codex `
  -p tsis `
  -C 'C:\TSIS_Data' `
  --sandbox danger-full-access `
  --ask-for-approval never
