# Marcador del bot (se actualiza solo cada lunes)

**Actualizado:** 22/10/2026 13:06 UTC. Lo genera `bot/marcador.py`; no se toca a mano.

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
| Pronósticos enviados (cerrados) | 152 |
| Preguntas ya resueltas | 35 |
| Suma de puntuación de pares | 110.3 (en 33 preguntas) |
| Media por pregunta | 3.34 |

## Cada modelo por separado

| Modelo | Tipo:medida | Preguntas | Media |
|---|---|---|---|
| openrouter/anthropic/claude-opus-5.5 | binary:brier | 21 | 0.1668 |
| openrouter/anthropic/claude-opus-5.5 | binary:log | 21 | -0.4975 |
| openrouter/anthropic/claude-opus-5.5 | discrete:dentro_80 | 6 | 0.8333 |
| openrouter/anthropic/claude-opus-5.5 | multiple_choice:log | 1 | -1.1087 |
| openrouter/anthropic/claude-opus-5.5 | numeric:dentro_80 | 5 | 1.0 |
| openrouter/openai/gpt-6-sol | binary:brier | 41 | 0.1446 |
| openrouter/openai/gpt-6-sol | binary:log | 41 | -0.4519 |
| openrouter/openai/gpt-6-sol | discrete:dentro_80 | 12 | 0.9167 |
| openrouter/openai/gpt-6-sol | multiple_choice:log | 2 | -1.2554 |
| openrouter/openai/gpt-6-sol | numeric:dentro_80 | 10 | 1.0 |

## Calibración (preguntas de sí/no)

Si el bot está bien calibrado, «pasó» se parece a «dijimos» en cada tramo.

| Tramo | Preguntas | Dijimos (media) | Pasó de verdad |
|---|---|---|---|
| 0-10 % | 2 | 7.0 % | 0.0 % |
| 10-20 % | 3 | 14.3 % | 0.0 % |
| 20-30 % | 6 | 22.8 % | 16.7 % |
| 30-40 % | 1 | 32.5 % | 100.0 % |
| 40-50 % | 3 | 43.7 % | 33.3 % |
| 50-60 % | 1 | 56.0 % | 100.0 % |
| 60-70 % | 3 | 62.0 % | 66.7 % |
| 70-80 % | 1 | 75.0 % | 100.0 % |
| 80-90 % | 1 | 85.0 % | 100.0 % |

## Las 5 peores preguntas

| Puntuación | Pregunta | Resolución |
|---|---|---|
| -29.3 | [Will UODO publish an announcement specifically about the FELG Dent breach by October 16, 2](https://www.metaculus.com/questions/45914) | no |
| -18.3 | [What will the series score of the 2026 ALCS be after Game 4 (October 16)?](https://www.metaculus.com/questions/45942) | Tied 2-2 |
| -18.1 | [How many European countries will ECDC report with locally-acquired human West Nile virus c](https://www.metaculus.com/questions/45892) | 19.0 |
| -15.4 | [Will the DFB formally and institutionally come out against Infantino's FIFA presidency bef](https://www.metaculus.com/questions/45910) | yes |
| -11.5 | [How many confirmed human West Nile virus cases will RIVM report in the Netherlands for 202](https://www.metaculus.com/questions/45920) | 64.0 |

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
| curva suave (PCHIP) | decidida de antemano | 5 | 1.97 | 12.63 | 1.97 | — | no |
| media | decidida de antemano | 22 | -0.53 | 1.6 | -0.95 | -0.29 | no |
| sin anthropic | exploratoria | 22 | 0.1 | 2.16 | -0.34 | 0.36 | no |
| solo openai | exploratoria | 22 | 0.1 | 2.16 | -0.34 | 0.36 | no |
| límites 1%-99% | exploratoria | 21 | 0.0 | 0.0 | 0.0 | 0.0 | no |
| mediana (la actual) | exploratoria | 22 | 0.0 | 0.0 | 0.0 | 0.0 | no |
| media geométrica de odds | exploratoria | 21 | -0.6 | 1.61 | -1.03 | -0.33 | no |
| sin openai | exploratoria | 22 | -2.5 | 7.17 | -2.47 | -2.51 | no |
| solo anthropic | exploratoria | 22 | -2.5 | 7.17 | -2.47 | -2.51 | no |

## En qué se va el dinero (últimos 7 días)

Dos cifras: lo que dice la **clave** de OpenRouter (la buena: lo que de verdad se ha gastado) y lo que mide la **librería** del bot pregunta a pregunta (no ve la búsqueda de noticias «:online», así que se queda corta). La diferencia es, casi toda, la búsqueda.

| Dato | Valor |
|---|---|
| Preguntas hechas en el periodo | 60 |
| Gastado en total (clave) | 39.11 $ de 100.0 $ |
| Línea de ritmo a esta fecha | 43.39 $ (por debajo: -4.28 $) |
| Gastado en el periodo (clave) | 13.84 $ (~0.231 $ por pregunta) |
| De eso, medido por la librería | 0.0 $ |
| Sin medir por la librería (≈ búsqueda) | 13.84 $ |
| A este ritmo, el dinero llega para | ~4.2 semanas más |

Por parte (lo que mide la librería, media por pregunta):

| Parte | $ por pregunta | $ en el periodo |
|---|---|---|
| busqueda | 0.0 | 0.0 |
| clasificador | 0.0 | 0.0 |
| lector | 0.0 | 0.0 |
| pronostico openrouter/anthropic/claude-opus-5.5 | 0.0 | 0.0 |
| pronostico openrouter/google/gemini-3.8-flash | 0.0 | 0.0 |
| pronostico openrouter/openai/gpt-6-sol | 0.0 | 0.0 |

El cambio de modelos no se hace solo: se propone con estos datos tras la primera semana, en una fecha anunciada.

## Preguntas perdidas (cerradas en los últimos 7 días)

Una pregunta sin pronóstico vale 0 puntos. «Por el tope» = el bot la dejó a propósito para no gastar el dinero antes de tiempo. «Sin explicar» = la vigilancia debió evitarla: si hay alguna, hay que mirar por qué.

| Dato | Valor |
|---|---|
| Preguntas cerradas (con el bot ya encendido) | 81 |
| Con pronóstico nuestro | 59 |
| Perdidas por el tope de gasto (a propósito) | 0 |
| **Perdidas sin explicar** | **22** |

| Cierre (UTC) | Torneo | Pregunta |
|---|---|---|
| 21/10 04:12 | minibench | https://www.metaculus.com/questions/46178 |
| 20/10 18:28 | minibench | https://www.metaculus.com/questions/46172 |
| 20/10 09:30 | minibench | https://www.metaculus.com/questions/46168 |
| 20/10 09:09 | minibench | https://www.metaculus.com/questions/46167 |
| 20/10 09:07 | minibench | https://www.metaculus.com/questions/46166 |
| 20/10 05:15 | minibench | https://www.metaculus.com/questions/46162 |
| 20/10 05:07 | minibench | https://www.metaculus.com/questions/46161 |
| 20/10 04:06 | minibench | https://www.metaculus.com/questions/46160 |
| 19/10 15:33 | minibench | https://www.metaculus.com/questions/46142 |
| 19/10 15:19 | minibench | https://www.metaculus.com/questions/46141 |
| 19/10 15:10 | minibench | https://www.metaculus.com/questions/46140 |
| 19/10 14:46 | minibench | https://www.metaculus.com/questions/46139 |
| 19/10 14:44 | minibench | https://www.metaculus.com/questions/46138 |
| 19/10 14:37 | minibench | https://www.metaculus.com/questions/46137 |
| 19/10 14:15 | minibench | https://www.metaculus.com/questions/46136 |
| 19/10 05:21 | minibench | https://www.metaculus.com/questions/46128 |
| 19/10 04:52 | minibench | https://www.metaculus.com/questions/46127 |
| 22/10 12:00 | 33121 | https://www.metaculus.com/questions/46193 |
| 21/10 15:00 | 33121 | https://www.metaculus.com/questions/46191 |
| 20/10 15:00 | 33121 | https://www.metaculus.com/questions/46069 |
| 19/10 15:00 | 33121 | https://www.metaculus.com/questions/46066 |
| 16/10 09:00 | 33121 | https://www.metaculus.com/questions/46056 |

## Cuántas veces lanzó GitHub el bot

El reloj de GitHub debería lanzar el bot 72 veces al día (cada 20 min) y la vigilancia 48. «A mano» = relanzado por la vigilancia o por una persona. «Hueco» = el mayor tiempo seguido sin lanzar el bot ese día: una pregunta que abre y cierra dentro de un hueco se pierde. Días en UTC.

| Día | Bot: reloj | Bot: a mano | Bot: bien | Mayor hueco (h) | Vigilancia: reloj |
|---|---|---|---|---|---|
| 2026-10-15 | 6 de 72 | 6 | 12 | 4.3 | 6 de 48 |
| 2026-10-16 | 7 de 72 | 1 | 8 | 4.6 | 6 de 48 |
| 2026-10-17 | 8 de 72 | 8 | 16 | 3.5 | 8 de 48 |
| 2026-10-18 | 7 de 72 | 1 | 8 | 5.1 | 7 de 48 |
| 2026-10-19 | 5 de 72 | 4 | 9 | 4.7 | 4 de 48 |
| 2026-10-20 | 6 de 72 | 1 | 7 | 5.0 | 6 de 48 |
| 2026-10-21 | 6 de 72 | 1 | 7 | 5.7 | 6 de 48 |
| 2026-10-22 | 3 de 72 | 1 | 4 | 5.0 | 2 de 48 |

Preguntas perdidas sin explicar y los lanzamientos del bot alrededor de su cierre:

| Cierre (UTC) | Pregunta | Último lanzamiento antes | Primero después | Hueco (h) |
|---|---|---|---|---|
| 21/10 04:12 | https://www.metaculus.com/questions/46178 | 21/10 00:58 | 21/10 05:54 | 4.9 |
| 20/10 18:28 | https://www.metaculus.com/questions/46172 | 20/10 15:12 | 20/10 19:23 | 4.2 |
| 20/10 09:30 | https://www.metaculus.com/questions/46168 | 20/10 05:19 | 20/10 10:11 | 4.9 |
| 20/10 09:09 | https://www.metaculus.com/questions/46167 | 20/10 05:19 | 20/10 10:11 | 4.9 |
| 20/10 09:07 | https://www.metaculus.com/questions/46166 | 20/10 05:19 | 20/10 10:11 | 4.9 |
| 20/10 05:15 | https://www.metaculus.com/questions/46162 | 20/10 00:40 | 20/10 05:19 | 4.7 |
| 20/10 05:07 | https://www.metaculus.com/questions/46161 | 20/10 00:40 | 20/10 05:19 | 4.7 |
| 20/10 04:06 | https://www.metaculus.com/questions/46160 | 20/10 00:40 | 20/10 05:19 | 4.7 |
| 19/10 15:33 | https://www.metaculus.com/questions/46142 | 19/10 10:57 | 19/10 15:37 | 4.7 |
| 19/10 15:19 | https://www.metaculus.com/questions/46141 | 19/10 10:57 | 19/10 15:37 | 4.7 |
| 19/10 15:10 | https://www.metaculus.com/questions/46140 | 19/10 10:57 | 19/10 15:37 | 4.7 |
| 19/10 14:46 | https://www.metaculus.com/questions/46139 | 19/10 10:57 | 19/10 15:37 | 4.7 |
| 19/10 14:44 | https://www.metaculus.com/questions/46138 | 19/10 10:57 | 19/10 15:37 | 4.7 |
| 19/10 14:37 | https://www.metaculus.com/questions/46137 | 19/10 10:57 | 19/10 15:37 | 4.7 |
| 19/10 14:15 | https://www.metaculus.com/questions/46136 | 19/10 10:57 | 19/10 15:37 | 4.7 |
| 19/10 05:21 | https://www.metaculus.com/questions/46128 | 19/10 05:20 | 19/10 07:47 | 2.5 |
| 19/10 04:52 | https://www.metaculus.com/questions/46127 | 19/10 01:45 | 19/10 05:20 | 3.6 |
| 22/10 12:00 | https://www.metaculus.com/questions/46193 | 22/10 07:36 | 22/10 12:27 | 4.9 |
| 21/10 15:00 | https://www.metaculus.com/questions/46191 | 21/10 11:38 | 21/10 16:06 | 4.5 |
| 20/10 15:00 | https://www.metaculus.com/questions/46069 | 20/10 10:11 | 20/10 15:12 | 5.0 |
| 19/10 15:00 | https://www.metaculus.com/questions/46066 | 19/10 10:57 | 19/10 15:37 | 4.7 |
| 16/10 09:00 | https://www.metaculus.com/questions/46056 | 16/10 05:01 | 16/10 09:39 | 4.6 |

## Plan de Claude del usuario (lo que gasta el bot)

El bot no pasa del 15.0 % del tope semanal del plan (70.0 $ equivalentes, ya descontada la reserva para la revisión de los lunes). Pasado el 80 %, se apaga el clasificador con Opus; pasado el tope, también la investigación con Claude (las pares van con la búsqueda de pago). «Puntos» = % del tope semanal, estimado a 5.0 $ por punto (medido el 27/09).

| Parte | Semana del plan que acaba ($) | Semana anterior ($) |
|---|---|---|
| clasificador_opus | 0 | 0 |
| investigacion | 0 | 0 |
| vigilancia | 0 | 0 |
| **Total** | **0** | **0** |
| Puntos del tope semanal (≈ %) | 0.0 | 0.0 |

## Clasificador en sombra: Gemini 3.8 Flash (¿sabe qué preguntas son difíciles?)

Antes de investigar, un modelo dice si cada pregunta es fácil, normal o difícil. **No decide nada todavía**: aquí se mira si acierta. Si acierta, las «difíciles» deberían tener más discrepancia entre los 3 modelos y peor puntuación de pares. Solo pasará a decidir si las difíciles puntúan claramente peor que las fáciles (más que el margen) con al menos 30 resueltas en cada grupo. Hay dos clasificadores a la vez (Gemini y Opus): se comparan con la misma regla.

| Etiqueta | Preguntas | Discrepancia media de los modelos | Resueltas | Puntos de pares (media) | Margen 95 % |
|---|---|---|---|---|---|
| normal | 2 | 0.135 | 0 | — | — |
| dificil | 20 | 0.077 | 2 | 3.84 | 37.63 |
| sin_clasificar | 130 | 0.092 | 31 | 3.31 | 4.78 |

## Clasificador en sombra: Claude Opus 5.5 (xhigh, plan Max) (¿sabe qué preguntas son difíciles?)

Antes de investigar, un modelo dice si cada pregunta es fácil, normal o difícil. **No decide nada todavía**: aquí se mira si acierta. Si acierta, las «difíciles» deberían tener más discrepancia entre los 3 modelos y peor puntuación de pares. Solo pasará a decidir si las difíciles puntúan claramente peor que las fáciles (más que el margen) con al menos 30 resueltas en cada grupo. Hay dos clasificadores a la vez (Gemini y Opus): se comparan con la misma regla.

| Etiqueta | Preguntas | Discrepancia media de los modelos | Resueltas | Puntos de pares (media) | Margen 95 % |
|---|---|---|---|---|---|
| facil | 1 | 0.32 | 1 | 11.32 | — |
| normal | 34 | 0.1 | 18 | 3.55 | 6.79 |
| dificil | 32 | 0.08 | 14 | 2.5 | 7.29 |
| sin_clasificar | 85 | 0.089 | 0 | — | — |
