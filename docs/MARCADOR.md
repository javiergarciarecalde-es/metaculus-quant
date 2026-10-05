# Marcador del bot (se actualiza solo cada lunes)

**Actualizado:** 05/10/2026 06:51 UTC. Lo genera `bot/marcador.py`; no se toca a mano.

Qué es cada cosa:
- **Puntuación de pares** (spot peer): la que da Metaculus y cuenta en el torneo. Positiva = mejor
  que la media de los demás bots en esa pregunta; negativa = peor.
- **Log** (por modelo): logaritmo de la probabilidad que el modelo dio a lo que pasó. 0 es
  perfecto; cuanto más negativo, peor. Sirve para comparar a los 3 modelos entre sí.
- **Brier**: error al cuadrado en preguntas de sí/no. 0 es perfecto; 0,25 es decir siempre 50 %.
- Con pocas preguntas resueltas todo esto es **ruido**: no sacar conclusiones con menos de ~50.

## Resumen

| Dato | Valor |
|---|---|
| Pronósticos enviados (cerrados) | 8 |
| Preguntas ya resueltas | 0 |
| Suma de puntuación de pares | 0 (en 0 preguntas) |
| Media por pregunta | — |

## Cada modelo por separado

| Modelo | Tipo:medida | Preguntas | Media |
|---|---|---|---|

## Calibración (preguntas de sí/no)

Si el bot está bien calibrado, «pasó» se parece a «dijimos» en cada tramo.

| Tramo | Preguntas | Dijimos (media) | Pasó de verdad |
|---|---|---|---|

## Las 5 peores preguntas

| Puntuación | Pregunta | Resolución |
|---|---|---|

## ¿Qué forma de juntar a los 3 modelos habría ido mejor?

Se recalcula, sin preguntar de nuevo a nadie, qué habríamos enviado con otra forma de
juntar los pronósticos de los 3 modelos. «Cambio medio» = puntos de pares por pregunta
que habríamos ganado (+) o perdido (-) frente a lo que enviamos. «Margen 95 %»: si el
cambio medio es menor que el margen, la diferencia puede ser suerte. Solo las «decididas
de antemano» sirven para decidir, y solo si **cumplen la regla**: al menos
150 preguntas resueltas, ganar de media y ganar en las dos
mitades (preguntas antiguas y recientes). Numéricas: solo la curva suave, frente a la
curva enviada (cuenta la mitad, como en Metaculus).

| Variante | Tipo | Preguntas | Cambio medio | Margen 95 % | Mitad antigua | Mitad reciente | ¿Cumple la regla? |
|---|---|---|---|---|---|---|---|
| — | — | 0 | — | — | — | — | — |

## En qué se va el dinero (últimos 7 días)

Dos cifras: lo que dice la **clave** de OpenRouter (la buena: lo que de verdad se ha gastado) y lo que mide la **librería** del bot pregunta a pregunta (no ve la búsqueda de noticias «:online», así que se queda corta). La diferencia es, casi toda, la búsqueda.

| Dato | Valor |
|---|---|
| Preguntas hechas en el periodo | 26 |
| Gastado en total (clave) | 10.41 $ de 100.0 $ |
| Línea de ritmo a esta fecha | 30.45 $ (por debajo: -20.04 $) |
| Gastado en el periodo (clave) | 4.79 $ (~0.184 $ por pregunta) |
| De eso, medido por la librería | 4.92 $ |
| Sin medir por la librería (≈ búsqueda) | 0.0 $ |
| A este ritmo, el dinero llega para | ~18.1 semanas más |

Por parte (lo que mide la librería, media por pregunta):

| Parte | $ por pregunta | $ en el periodo |
|---|---|---|
| busqueda | 0.0 | 0.0 |
| clasificador | 0.0 | 0.0 |
| lector | 0.0014 | 0.036 |
| pronostico openrouter/anthropic/claude-opus-5.5 | 0.0 | 0.0 |
| pronostico openrouter/google/gemini-3.8-flash | 0.0 | 0.0 |
| pronostico openrouter/openai/gpt-6-sol | 0.0 | 0.0 |

El cambio de modelos no se hace solo: se propone con estos datos tras la primera semana, en una fecha anunciada.

## Preguntas perdidas (cerradas en los últimos 7 días)

Una pregunta sin pronóstico vale 0 puntos. «Por el tope» = el bot la dejó a propósito para no gastar el dinero antes de tiempo. «Sin explicar» = la vigilancia debió evitarla: si hay alguna, hay que mirar por qué.

| Dato | Valor |
|---|---|
| Preguntas cerradas (con el bot ya encendido) | 18 |
| Con pronóstico nuestro | 18 |
| Perdidas por el tope de gasto (a propósito) | 0 |
| **Perdidas sin explicar** | **0** |

## Plan de Claude del usuario (lo que gasta el bot)

El bot no pasa del 15.0 % del tope semanal del plan (70.0 $ equivalentes, ya descontada la reserva para la revisión de los lunes). Pasado el 80 %, se apaga el clasificador con Opus; pasado el tope, también la investigación con Claude (las pares van con la búsqueda de pago). «Puntos» = % del tope semanal, estimado a 5.0 $ por punto (medido el 27/09).

| Parte | Semana del plan que acaba ($) | Semana anterior ($) |
|---|---|---|
| clasificador_opus | 0.64 | 0 |
| investigacion | 27.19 | 0 |
| vigilancia | 0 | 0 |
| **Total** | **27.83** | **0** |
| Puntos del tope semanal (≈ %) | 5.6 | 0.0 |

## Clasificador en sombra: Gemini 3.8 Flash (¿sabe qué preguntas son difíciles?)

Antes de investigar, un modelo dice si cada pregunta es fácil, normal o difícil. **No decide nada todavía**: aquí se mira si acierta. Si acierta, las «difíciles» deberían tener más discrepancia entre los 3 modelos y peor puntuación de pares. Solo pasará a decidir si las difíciles puntúan claramente peor que las fáciles (más que el margen) con al menos 30 resueltas en cada grupo. Hay dos clasificadores a la vez (Gemini y Opus): se comparan con la misma regla.

| Etiqueta | Preguntas | Discrepancia media de los modelos | Resueltas | Puntos de pares (media) | Margen 95 % |
|---|---|---|---|---|---|
| sin_clasificar | 8 | 0.181 | 0 | — | — |

## Clasificador en sombra: Claude Opus 5.5 (xhigh, plan Max) (¿sabe qué preguntas son difíciles?)

Antes de investigar, un modelo dice si cada pregunta es fácil, normal o difícil. **No decide nada todavía**: aquí se mira si acierta. Si acierta, las «difíciles» deberían tener más discrepancia entre los 3 modelos y peor puntuación de pares. Solo pasará a decidir si las difíciles puntúan claramente peor que las fáciles (más que el margen) con al menos 30 resueltas en cada grupo. Hay dos clasificadores a la vez (Gemini y Opus): se comparan con la misma regla.

| Etiqueta | Preguntas | Discrepancia media de los modelos | Resueltas | Puntos de pares (media) | Margen 95 % |
|---|---|---|---|---|---|
| dificil | 7 | 0.09 | 0 | — | — |
| sin_clasificar | 1 | 0.819 | 0 | — | — |
