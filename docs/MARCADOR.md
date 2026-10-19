# Marcador del bot (se actualiza solo cada lunes)

**Actualizado:** 19/10/2026 13:45 UTC. Lo genera `bot/marcador.py`; no se toca a mano.

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
| Pronósticos enviados (cerrados) | 105 |
| Preguntas ya resueltas | 22 |
| Suma de puntuación de pares | 36.78 (en 20 preguntas) |
| Media por pregunta | 1.84 |

## Cada modelo por separado

| Modelo | Tipo:medida | Preguntas | Media |
|---|---|---|---|
| openrouter/anthropic/claude-opus-5.5 | binary:brier | 11 | 0.2232 |
| openrouter/anthropic/claude-opus-5.5 | binary:log | 11 | -0.6202 |
| openrouter/anthropic/claude-opus-5.5 | discrete:dentro_80 | 4 | 1.0 |
| openrouter/anthropic/claude-opus-5.5 | multiple_choice:log | 1 | -1.1087 |
| openrouter/anthropic/claude-opus-5.5 | numeric:dentro_80 | 4 | 1.0 |
| openrouter/openai/gpt-6-sol | binary:brier | 21 | 0.1923 |
| openrouter/openai/gpt-6-sol | binary:log | 21 | -0.5501 |
| openrouter/openai/gpt-6-sol | discrete:dentro_80 | 8 | 1.0 |
| openrouter/openai/gpt-6-sol | multiple_choice:log | 2 | -1.2554 |
| openrouter/openai/gpt-6-sol | numeric:dentro_80 | 8 | 1.0 |

## Calibración (preguntas de sí/no)

Si el bot está bien calibrado, «pasó» se parece a «dijimos» en cada tramo.

| Tramo | Preguntas | Dijimos (media) | Pasó de verdad |
|---|---|---|---|
| 0-10 % | 2 | 7.0 % | 0.0 % |
| 10-20 % | 1 | 11.0 % | 0.0 % |
| 20-30 % | 2 | 24.0 % | 50.0 % |
| 30-40 % | 1 | 32.5 % | 100.0 % |
| 40-50 % | 1 | 40.0 % | 100.0 % |
| 60-70 % | 3 | 62.0 % | 66.7 % |
| 80-90 % | 1 | 85.0 % | 100.0 % |

## Las 5 peores preguntas

| Puntuación | Pregunta | Resolución |
|---|---|---|
| -29.3 | [Will UODO publish an announcement specifically about the FELG Dent breach by October 16, 2](https://www.metaculus.com/questions/45914) | no |
| -18.3 | [What will the series score of the 2026 ALCS be after Game 4 (October 16)?](https://www.metaculus.com/questions/45942) | Tied 2-2 |
| -15.4 | [Will the DFB formally and institutionally come out against Infantino's FIFA presidency bef](https://www.metaculus.com/questions/45910) | yes |
| -11.5 | [How many confirmed human West Nile virus cases will RIVM report in the Netherlands for 202](https://www.metaculus.com/questions/45920) | 64.0 |
| -10.3 | [What will Rosstat report as Russia's average retail price of AI-95 gasoline in the weekly ](https://www.metaculus.com/questions/45913) | 80.92 |

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
| media | decidida de antemano | 12 | -0.4 | 2.61 | 1.68 | -1.44 | no |
| curva suave (PCHIP) | decidida de antemano | 4 | -3.23 | 9.61 | -3.23 | — | no |
| sin anthropic | exploratoria | 12 | 0.53 | 3.81 | -0.12 | 0.86 | no |
| solo openai | exploratoria | 12 | 0.53 | 3.81 | -0.12 | 0.86 | no |
| límites 1%-99% | exploratoria | 11 | 0.0 | 0.0 | 0.0 | 0.0 | no |
| mediana (la actual) | exploratoria | 12 | 0.0 | 0.0 | 0.0 | 0.0 | no |
| media geométrica de odds | exploratoria | 11 | -0.78 | 2.71 | 1.3 | -1.97 | no |
| sin openai | exploratoria | 12 | -3.05 | 11.86 | 5.94 | -7.54 | no |
| solo anthropic | exploratoria | 12 | -3.05 | 11.86 | 5.94 | -7.54 | no |

## En qué se va el dinero (últimos 7 días)

Dos cifras: lo que dice la **clave** de OpenRouter (la buena: lo que de verdad se ha gastado) y lo que mide la **librería** del bot pregunta a pregunta (no ve la búsqueda de noticias «:online», así que se queda corta). La diferencia es, casi toda, la búsqueda.

| Dato | Valor |
|---|---|
| Preguntas hechas en el periodo | 38 |
| Gastado en total (clave) | 31.07 $ de 100.0 $ |
| Línea de ritmo a esta fecha | 41.09 $ (por debajo: -10.02 $) |
| Gastado en el periodo (clave) | 8.69 $ (~0.229 $ por pregunta) |
| De eso, medido por la librería | 0.0 $ |
| Sin medir por la librería (≈ búsqueda) | 8.69 $ |
| A este ritmo, el dinero llega para | ~7.6 semanas más |

Por parte (lo que mide la librería, media por pregunta):

| Parte | $ por pregunta | $ en el periodo |
|---|---|---|
| busqueda | 0.0 | 0.0 |
| busqueda respaldo | 0.0 | 0.0 |
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
| Preguntas cerradas (con el bot ya encendido) | 43 |
| Con pronóstico nuestro | 37 |
| Perdidas por el tope de gasto (a propósito) | 0 |
| **Perdidas sin explicar** | **6** |

| Cierre (UTC) | Torneo | Pregunta |
|---|---|---|
| 19/10 05:21 | minibench | https://www.metaculus.com/questions/46128 |
| 19/10 04:52 | minibench | https://www.metaculus.com/questions/46127 |
| 16/10 09:00 | 33121 | https://www.metaculus.com/questions/46056 |
| 12/10 16:00 | 33121 | https://www.metaculus.com/questions/46005 |
| 13/10 21:00 | 33121 | https://www.metaculus.com/questions/45964 |
| 13/10 00:00 | 33121 | https://www.metaculus.com/questions/45960 |

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
| dificil | 10 | 0.094 | 2 | 3.84 | 37.63 |
| sin_clasificar | 95 | 0.099 | 18 | 1.62 | 6.33 |

## Clasificador en sombra: Claude Opus 5.5 (xhigh, plan Max) (¿sabe qué preguntas son difíciles?)

Antes de investigar, un modelo dice si cada pregunta es fácil, normal o difícil. **No decide nada todavía**: aquí se mira si acierta. Si acierta, las «difíciles» deberían tener más discrepancia entre los 3 modelos y peor puntuación de pares. Solo pasará a decidir si las difíciles puntúan claramente peor que las fáciles (más que el margen) con al menos 30 resueltas en cada grupo. Hay dos clasificadores a la vez (Gemini y Opus): se comparan con la misma regla.

| Etiqueta | Preguntas | Discrepancia media de los modelos | Resueltas | Puntos de pares (media) | Margen 95 % |
|---|---|---|---|---|---|
| facil | 1 | 0.32 | 1 | 11.32 | — |
| normal | 34 | 0.1 | 12 | 3.9 | 8.36 |
| dificil | 32 | 0.08 | 7 | -3.05 | 10.57 |
| sin_clasificar | 38 | 0.107 | 0 | — | — |
