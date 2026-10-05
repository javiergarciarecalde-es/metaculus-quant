# Revisión semanal del bot — 05/10/2026

## Cómo va
El marcador de hoy (06:51 UTC) salió bien y es el segundo desde que el bot está encendido
(el primero fue el 28/09). Llevamos **8 pronósticos enviados** y, de momento, **0 resueltos**:
Metaculus aún no ha cerrado ninguna pregunta con pronóstico nuestro, así que todavía no hay
ninguna puntuación de pares (el número que de verdad cuenta en el torneo) que mirar. El gasto
de dinero (créditos de las empresas de IA) va por debajo de lo previsto, y el gasto del plan de
Claude del usuario sigue muy lejos de su tope. No hay ninguna pregunta «perdida sin explicar».
No hay ningún problema técnico nuevo que arreglar.

## Cifras de la semana
| Dato | Valor | Comparación |
|---|---|---|
| Pronósticos enviados (cerrados) | 8 | — (aún pocos) |
| Preguntas ya resueltas | 0 | OJO — sin resueltas no se puede juzgar cómo pronostica el bot |
| Puntuación de pares (suma / media) | 0 en 0 preguntas | — (sin datos todavía) |
| Gastado en créditos (últimos 7 días) | 4,79 $ en 26 preguntas | va bien — 20,04 $ por debajo de la línea de ritmo (30,45 $) |
| Gastado en créditos (total) | 10,41 $ de 100 $ | va bien — a este ritmo dura ~18 semanas más |
| Preguntas perdidas sin explicar | 0 | va bien |
| Plan de Claude del usuario (esta semana) | 27,83 $ equivalentes (5,6 puntos) | va bien — muy por debajo del tope semanal (15 puntos ≈ 70 $); el aviso salta al 80 % |
| Clasificador en sombra (Gemini) | 8 preguntas, todas «sin_clasificar», 0 resueltas | — (sin datos para juzgarlo) |
| Clasificador en sombra (Opus) | 7 «difícil», 1 «sin_clasificar», 0 resueltas | — (sin datos para juzgarlo) |
| Pares (Claude Max) frente a impares (búsqueda de pago) | 0 resueltas en los dos grupos | — (sin datos para comparar) |

## Reglas decididas de antemano
- **Comparador y par/impar** (necesita ≥150 preguntas resueltas y ganar en las dos mitades):
  **no se cumple.** Hoy hay 0 resueltas: faltan las 150. Es muy pronto, normal en la primera
  semana real de torneo.
- **Clasificador** (necesita ≥30 resueltas por grupo y una diferencia mayor que el margen del
  95 %, tanto para Gemini como para Opus): **no se cumple.** Hoy hay 0 resueltas en cualquier
  grupo: faltan las 30 por grupo. Tampoco se puede juzgar todavía cuál de los dos clasificadores
  acierta más.

Ninguna regla señala que haya que decidir nada esta semana: no hay suficientes preguntas
resueltas para que el comparador o los clasificadores digan algo fiable.

## Qué necesita del usuario
Nada urgente. Un aviso, no una decisión que pedir ya: en `docs/ESTADO.md` seguía anotado
decidir el **reparto del dinero entre MiniBench y temporada** «con los datos de la 1.ª semana»,
y ya ha pasado una semana desde que se encendió el envío real (27/09). Pero con 0 preguntas
resueltas todavía no hay datos de resultado que mirar (solo de gasto, que ya está en la tabla
de arriba). **Recomendación:** esperar a que haya más preguntas resueltas antes de decidir el
reparto; de momento no cambiar nada. Las demás decisiones pendientes que ya conocía el usuario
(AskNews, el correo del primer commit, si el repositorio sigue público) siguen igual, sin nada
nuevo que añadir esta semana.

## Problemas
Ninguno nuevo. Comprobado en GitHub: no hay ningún issue abierto con título que empiece por
«[vigilancia]», ni ninguna rama `vigilancia/...` sin fusionar (no hay ninguna rama con ese
nombre ahora mismo). Hubo 5 ejecuciones en rojo el 28/09 (al relanzar el bot y al ejecutar las
pruebas, por un corte de pypi.org, el almacén de piezas de Python, que no contestaba a GitHub);
ya están explicadas y arregladas (más reintentos al instalar), y desde entonces —del 28/09 al
05/10— todas las ejecuciones del bot, la vigilancia y el marcador han salido en verde. No faltó
ninguna semana el commit del marcador de los lunes (están el 28/09 y el 05/10, las dos únicas
que han tocado desde que el bot está encendido).
