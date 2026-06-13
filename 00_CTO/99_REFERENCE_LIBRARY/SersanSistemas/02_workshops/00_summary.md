
# [practice_03](./02_practice/02_workshops/13-practice-03/transcripts/practica_03.narrative.thematic.md)

## Bases diarias vs Bases intradiarias (1440 minutos)

Comprender por qué los sistemas basados en gráficos diarios pueden ofrecer resultados distorsionados cuando se utilizan precios oficiales de liquidación (*settle*) en lugar de datos reales de negociación.

### Concepto clave

Una vela de 1.440 minutos equivale a un día completo de mercado (24 × 60).
Sin embargo, la construcción de la vela puede realizarse de dos maneras diferentes, lo que afecta directamente a la precisión del análisis y del backtest.

| Tipo de base                   | Fuente del dato                                           | Características                                                        | Riesgo o limitación                                                                              |
| ------------------------------ | --------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Diaria oficial**             | Precio de liquidación (*settle*) calculado por el mercado | No permite modificar la sesión. Refleja el precio oficial de cierre.   | Puede diferir significativamente del precio real negociado. El *settle* se publica a posteriori. |
| **Intradiaria (1440 minutos)** | Precio real de negociación                                | Permite definir la sesión horaria y refleja la acción real del precio. | Requiere mayor capacidad de procesamiento y almacenamiento, pero es más precisa.                 |


### Implicaciones para sistemas automáticos

1. En futuros y ETFs, el uso de datos diarios oficiales puede alterar la detección de señales y el cálculo del rendimiento.
2. Es preferible construir las velas diarias a partir de la base intradiaria (1.440 minutos) para reflejar los precios reales de mercado.
3. Los sistemas intradiarios permiten definir con precisión las sesiones y controlar la hora de cierre.
4. Los gráficos diarios oficiales no permiten modificar la sesión y siempre utilizan el rango completo de la jornada.

### Recomendaciones técnicas

* Configurar en la plataforma:
  **For bar building, use → Session Hours**
  De este modo, la primera barra se genera al inicio de la sesión regular, garantizando coherencia temporal en los cálculos.

* Utilizar la base de 1.440 minutos para construir velas diarias representativas del comportamiento real del activo.

* Extender esta práctica también a los ETFs, ya que sus cierres suelen coincidir con el *settle*, sin reflejar necesariamente la reacción del mercado tras la publicación de resultados empresariales.

### Contexto operativo

Durante la temporada de resultados, las diferencias entre el cierre real y el *settle* pueden ser considerables.
En el caso mencionado, las empresas Apple, Meta y Amazon publicaron resultados el mismo día, generando variaciones de más de 200 puntos tras el cierre oficial del contado.
Estos movimientos, si no se incluyen en la base intradiaria, provocan errores significativos en la interpretación del sistema.

