# Marcador del bot (se actualiza solo cada lunes)

**Actualizado:** 28/09/2026 08:45 UTC. Lo genera `bot/marcador.py`; no se toca a mano.

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
| Pronósticos enviados (cerrados) | 0 |
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
| Preguntas hechas en el periodo | 15 |
| Gastado en total (clave) | 5.36 $ de 100.0 $ |
| Línea de ritmo a esta fecha | 25.0 $ (por debajo: -19.64 $) |
| Gastado en el periodo (clave) | 4.45 $ (~0.297 $ por pregunta) |
| De eso, medido por la librería | 2.95 $ |
| Sin medir por la librería (≈ búsqueda) | 1.5 $ |
| A este ritmo, el dinero llega para | ~20.6 semanas más |

El cambio de modelos no se hace solo: se propone con estos datos tras la primera semana, en una fecha anunciada.

## Preguntas perdidas (cerradas en los últimos 7 días)

Una pregunta sin pronóstico vale 0 puntos. «Por el tope» = el bot la dejó a propósito para no gastar el dinero antes de tiempo. «Sin explicar» = la vigilancia debió evitarla: si hay alguna, hay que mirar por qué.

| Dato | Valor |
|---|---|
| Preguntas cerradas | 52 |
| Con pronóstico nuestro | 1 |
| Perdidas por el tope de gasto (a propósito) | 0 |
| **Perdidas sin explicar** | **51** |

| Cierre (UTC) | Torneo | Pregunta |
|---|---|---|
| 24/09 02:49 | minibench | https://www.metaculus.com/questions/45796 |
| 24/09 00:10 | minibench | https://www.metaculus.com/questions/45795 |
| 23/09 14:36 | minibench | https://www.metaculus.com/questions/45794 |
| 23/09 05:51 | minibench | https://www.metaculus.com/questions/45793 |
| 23/09 02:22 | minibench | https://www.metaculus.com/questions/45792 |
| 22/09 20:32 | minibench | https://www.metaculus.com/questions/45791 |
| 22/09 18:30 | minibench | https://www.metaculus.com/questions/45790 |
| 22/09 17:10 | minibench | https://www.metaculus.com/questions/45789 |
| 22/09 16:36 | minibench | https://www.metaculus.com/questions/45788 |
| 22/09 13:19 | minibench | https://www.metaculus.com/questions/45787 |
| 22/09 12:44 | minibench | https://www.metaculus.com/questions/45786 |
| 22/09 10:02 | minibench | https://www.metaculus.com/questions/45785 |
| 22/09 08:29 | minibench | https://www.metaculus.com/questions/45784 |
| 22/09 07:41 | minibench | https://www.metaculus.com/questions/45783 |
| 22/09 04:45 | minibench | https://www.metaculus.com/questions/45782 |
| 22/09 03:09 | minibench | https://www.metaculus.com/questions/45781 |
| 22/09 00:30 | minibench | https://www.metaculus.com/questions/45780 |
| 22/09 00:29 | minibench | https://www.metaculus.com/questions/45779 |
| 21/09 23:44 | minibench | https://www.metaculus.com/questions/45778 |
| 21/09 23:08 | minibench | https://www.metaculus.com/questions/45777 |
| 21/09 22:38 | minibench | https://www.metaculus.com/questions/45776 |
| 21/09 22:15 | minibench | https://www.metaculus.com/questions/45775 |
| 21/09 22:03 | minibench | https://www.metaculus.com/questions/45774 |
| 21/09 22:01 | minibench | https://www.metaculus.com/questions/45773 |
| 21/09 21:38 | minibench | https://www.metaculus.com/questions/45772 |
| 21/09 21:21 | minibench | https://www.metaculus.com/questions/45771 |
| 21/09 21:07 | minibench | https://www.metaculus.com/questions/45770 |
| 21/09 21:01 | minibench | https://www.metaculus.com/questions/45769 |
| 21/09 20:53 | minibench | https://www.metaculus.com/questions/45768 |
| 21/09 19:54 | minibench | https://www.metaculus.com/questions/45767 |

## Clasificador en sombra: Gemini 3.8 Flash (¿sabe qué preguntas son difíciles?)

Antes de investigar, un modelo dice si cada pregunta es fácil, normal o difícil. **No decide nada todavía**: aquí se mira si acierta. Si acierta, las «difíciles» deberían tener más discrepancia entre los 3 modelos y peor puntuación de pares. Solo pasará a decidir si las difíciles puntúan claramente peor que las fáciles (más que el margen) con al menos 30 resueltas en cada grupo. Hay dos clasificadores a la vez (Gemini y Opus): se comparan con la misma regla.

| Etiqueta | Preguntas | Discrepancia media de los modelos | Resueltas | Puntos de pares (media) | Margen 95 % |
|---|---|---|---|---|---|
| — | 0 | — | 0 | — | — |

## Clasificador en sombra: Claude Opus 5.5 (xhigh, plan Max) (¿sabe qué preguntas son difíciles?)

Antes de investigar, un modelo dice si cada pregunta es fácil, normal o difícil. **No decide nada todavía**: aquí se mira si acierta. Si acierta, las «difíciles» deberían tener más discrepancia entre los 3 modelos y peor puntuación de pares. Solo pasará a decidir si las difíciles puntúan claramente peor que las fáciles (más que el margen) con al menos 30 resueltas en cada grupo. Hay dos clasificadores a la vez (Gemini y Opus): se comparan con la misma regla.

| Etiqueta | Preguntas | Discrepancia media de los modelos | Resueltas | Puntos de pares (media) | Margen 95 % |
|---|---|---|---|---|---|
| — | 0 | — | 0 | — | — |
