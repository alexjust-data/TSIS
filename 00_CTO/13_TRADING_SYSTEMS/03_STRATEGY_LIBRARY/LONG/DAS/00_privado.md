python 'C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\scripts\build_das_frontside_pattern_stats.py' --run-dir 'C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z' --progress-every 25

  Esto irá imprimiendo algo tipo:

  cases_to_analyze=679
  progress cases_analyzed=1/679 records=0 current=SYRA 2024-02-08
  progress cases_analyzed=25/679 records=24 current=...

  Output esperado:

  C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z\frontside_pattern_stats

  Dentro debe crear:

  frontside_pattern_cases.csv
  frontside_pattern_cases.parquet
  DAS_FRONTSIDE_PATTERN_STATS_REPORT_v0_1.md
  BUILD_METADATA.json


 Por codigo, cada que haga un run nuevo hemos de saber:

  cuanto tiempo dura la extension has el high del frontside,
  estadisticas horarios, a que horas son
  a que horas tienen de ser  buenos frontsides o a que horas malos
  - cuanto tienen un primer push, una primer dip con zona de estabilidad tipo banderita y luego rompen al alza este primer psu.
  - de los que rompen al alza que % al alza tienen, tbn por horas, por tiempo,
  - cuando hay fade push, es decir hay un push y una destruccion seguida en el primer dip
  - todos los ejemplos o casa de tikers que tiene un push de 1 vela, dos o tres y se destruyen en las siguientes velas en rojo sin posibilidad de
  nada.
  - cuando casas de breaout primer push y luego patron 1, patron 2, patron 3 ¿cuantos patrones encontramos?
  - Cuantos frontsides terminan en numeros enteros tipo 5$
  - cuantos fronsides terminan cuando hay resistencias anteriores en ese precio y cuanto volumen tenia esa resistencia acumulados. se entiend que
  la resistencia el precio nunca lo habia visitado.
  - cuanto volumen por minuto tiene los frontside que funcionan bien y cuanto volumen los que son fake
  - estadisticas de sector por ganadores y perdedores
  - cuando hace un breaout del primer push con su consolidacion y no solo dle primero, la pregunta sería ¿que tipo de patron se dibuja cuando hay
  breakout? por ejemplo son banderas tipo [Image #1]  o que tipo de patrones son


  • Estas son las preguntas/mediciones que me pediste dejar claras para DAS/frontside, una por una:

  1. ¿Cuánto tiempo dura la extensión hasta el high del frontside?
  2. ¿A qué horas aparecen los frontsides?
  3. ¿A qué horas suelen aparecer los buenos frontsides?
  4. ¿A qué horas suelen aparecer los malos frontsides?
  5. ¿Cuánto dura el primer push?
  6. ¿Qué % tiene el primer push desde la apertura/inicio válido?
  7. ¿Cuál es el máximo del primer push?
  8. ¿Cuál es el máximo % de todo el movimiento/frontside?
  9. ¿Cuánto tarda desde el scanner trigger hasta el primer push?
  10. ¿A qué % desde apertura salta el scanner trigger?
  11. ¿A qué precio salta el scanner trigger?
  12. ¿Con qué volumen acumulado salta el scanner trigger?
  13. ¿Cuándo el scanner llega tarde respecto al movimiento?
  14. ¿Cuándo el scanner debería haber detectado antes el ticker?
  15. ¿Cuándo hay primer push + primer dip + estabilidad tipo banderita?
  16. ¿Cuándo esa banderita rompe al alza?
  17. ¿De los que rompen al alza, qué % adicional suben?
  18. ¿Ese % adicional depende de la hora?
  19. ¿Ese % adicional depende del tiempo de consolidación?
  20. ¿Ese % adicional depende del volumen/minuto?
  21. ¿Cuándo hay fade push?
  22. ¿Cuándo hay push y destrucción inmediata en el primer dip?
  23. ¿Cuántos casos tienen push de 1 vela y luego destrucción?
  24. ¿Cuántos casos tienen push de 2 velas y luego destrucción?
  25. ¿Cuántos casos tienen push de 3 velas y luego destrucción?
  26. ¿Cuántos casos rompen el primer push y luego forman patrón 1, patrón 2, patrón 3?
  27. ¿Qué patrones distintos aparecen después del breakout del primer push?
  28. ¿Los breakouts suelen ser banderas, shelves, una sola vela, VWAP reclaim u otra estructura?
  29. ¿Cuántos frontsides terminan cerca de números enteros tipo $5, $10, etc.?
  30. ¿Cuántos frontsides terminan contra resistencias anteriores?
  31. ¿Qué volumen acumulado existía en esas resistencias anteriores?
  32. ¿Cuánto volumen/minuto tienen los frontsides buenos?
  33. ¿Cuánto volumen/minuto tienen los frontsides fake?
  34. ¿Hay diferencias por sector entre ganadores y perdedores?
  35. ¿Podemos calcular volumen/minuto y patrones frontside desde trades o quotes?
  36. ¿Cuál de trades o quotes tiene premarket y cuál no?
  37. ¿Los tickers necesarios ya están reparados por el proceso quote-guarded?
  38. ¿Siguen existiendo mechas imposibles en los tickers que necesitamos?
  39. ¿Qué casos deben excluirse porque el movimiento viene de dato malo y no de mercado real?
  40. ¿Qué parte debe venir de ohlcv_1m, qué parte de quotes y qué parte de trades?
