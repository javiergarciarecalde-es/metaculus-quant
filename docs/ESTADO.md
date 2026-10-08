# ESTADO (siempre «ahora»)

**Última actualización:** 08/10/2026, 10:00 (hora de Madrid). Sesión local «Metaculus: sacar el
robot del plan de Claude (orden 82)».
**Fase:** fase 0, compitiendo. El bot está **encendido** y mira cada 20 minutos la MiniBench y la
temporada de otoño, con los 3 modelos de OpenRouter y la búsqueda de pago (créditos de Metaculus).
**Plan de Claude: 0 desde el 07/10** (23:05 de Madrid, commit `d66176f`): ninguna pieza del bot
usa tu suscripción de Claude.
**Rama:** todo está en `main` en GitHub. Cada commit se sube solo (gancho `post-commit` = una orden
automática que hace git después de guardar).

## Dónde estamos
| Pieza | Estado |
|---|---|
| Bot en Metaculus | **Kyou-bot**; del 05 al 07/10 envió 51 pronósticos (registros de GitHub); 0 resueltos el 05/10 |
| Secretos en GitHub (claves guardadas) | `METACULUS_TOKEN`, `OPENROUTER_API_KEY` (créditos de Metaculus) y `CLAUDE_CODE_OAUTH_TOKEN` (**sin usar** desde el 07/10; no se borra, para poder volver) |
| Interruptor `ENVIO_REAL` | **`true` desde el 27/09 a las 21:04** (decisión del usuario): envía de verdad |
| Modelos (tu decisión del 28/09) | pronostican GPT-6 Sol, Claude Opus 5.5 y Gemini 3.8 Flash (por OpenRouter, créditos); busca noticias Opus 5.5 (respaldo GPT-6 Sol); lector GPT-6 Sol |
| Investigación | **todas las preguntas con la búsqueda de pago** desde el 07/10 (antes las pares, con Claude) |
| Clasificador en sombra | solo Gemini 3.8 Flash (no decide nada); el de Opus, apagado |
| Créditos de OpenRouter | quedan **80,79 $ de 100 $** (07/10, 20:55 UTC) — **OJO: a este ritmo no llegan al 06/01** (abajo) |
| Pruebas automáticas | **276 de 276 en verde**, ninguna saltada, y ruff (revisor de estilo) sin quejas |

## Plan de Claude: 0 desde el 07/10 (orden 82; tu decisión, en DECISIONES)
Comprobado en real: ejecución del bot del 08/10 a las 09:40 de Madrid, en verde; dice «no lo usa
ninguna pieza del bot», no instala Claude Code y no recibe la clave de la suscripción.
| Pieza | Gastaba (semana 28/09-05/10) | Cómo se vuelve a encender |
|---|---|---|
| Investigación con Claude de las preguntas pares | 27,19 $ equivalentes | `investigacion.modo: "claude_max"` |
| Clasificador en sombra con Opus «extra» | 0,64 $ | `clasificador.claude.activo: true` |
| Vigilancia despertando a Claude | 0 (nunca hizo falta) | `vigilancia.claude.activo: true` |
| Revisión semanal de los lunes (rutina en la nube) | 1 vuelta (05/10) | encender la rutina `trig_01P1NPoMLt4LgerQFDWu4MZ8` |
| **Total** | **27,83 $ ≈ 5,6 puntos del tope semanal** | el flujo vuelve a instalar Claude Code solo si alguna de las 3 primeras se enciende |
- La comparación pares/impares queda cortada en el 07/10 (sin conclusión). Corte para comparar
  antes/después: commit `d66176f` (HALLAZGOS, 07-08/10).
- El marcador de los lunes (programa, sin Claude) sigue y su tabla del plan saldrá a 0.

## Créditos de OpenRouter hasta el 06/01/2027 (cuenta del 08/10)
| Supuesto | Gasto por día | Se acabarían | Comparado con el 06/01 |
|---|---|---|---|
| Ritmo medio desde el 28/09 | 1,44 $ | ~02/12 | **OJO**: 5 semanas antes |
| Ese ritmo, con las pares pagando búsqueda (+25 %, sin medir) | 1,80 $ | ~21/11 | **OJO** |
| Ritmo del 05-07/10 (51 preguntas en 2,7 días) | 3,63 $ | ~30/10 | **OJO** |
| Ritmo flojo (5 preguntas al día) | 0,95 $ | ~01/01 | casi |
| Lo que haría falta | ≤0,90 $ | 06/01 | — |
- No se para de golpe: el **freno de ritmo** retiene preguntas de la temporada para estirar el
  dinero hasta el 06/01; la MiniBench va primero y solo la para la reserva de 3 $. Efecto: a partir
  de cierto punto habrá preguntas de la temporada sin pronóstico (0 puntos cada una).
- Aún no hay ninguna pregunta hecha con todo por la búsqueda de pago: el coste nuevo se verá en el
  marcador del lunes 12/10.

## Qué va solo (sin que tú hagas nada)
| Qué | Cuándo | Dónde |
|---|---|---|
| Pronosticar (MiniBench y temporada, con tope de gasto) | cada 20 min | GitHub |
| Vigilancia: relanza el bot si se calla, falla o se olvida preguntas (sin Claude) | dos veces por hora | GitHub |
| Marcador: puntos, gasto, preguntas perdidas, clasificador | lunes 08:30 | GitHub |
**Ya no va solo:** la revisión semanal de los lunes (apagada el 07/10; `docs/REVISION_SEMANAL.md` se
queda en la del 05/10). **Nunca va solo:** decidir cambios que tocan los pronósticos, avisar cuando
conteste AskNews y, al final, la encuesta y el cobro.

## Lo que queda por comprobar
| Qué | Cuándo se verá |
|---|---|
| Coste por pregunta con todas por la búsqueda de pago | marcador del 12/10 |
| La vigilancia con un fallo real ya sin Claude (relanza; solo probado con pruebas automáticas) | cuando haya un fallo |
| Si el reloj de GitHub se para del todo, se paran bot y vigilancia | marcador de los lunes (ya no hay revisión) |

## Decisiones pendientes tuyas
1. **Créditos que no llegan al 06/01** (nuevo): opciones, sin prisa hasta ver el marcador del
   12/10: (a) no hacer nada: el freno deja preguntas de la temporada sin hacer hacia el final;
   (b) pedir más créditos a Metaculus (se pidieron 270 $ y dieron 100 $); (c) abaratar el bot
   (cambiar modelos: se decide con datos, en fecha anunciada). Ninguna cuesta dinero tuyo.
2. **AskNews (noticias gratis):** esperando su respuesta. Cuando lleguen las claves, **no las pongas
   aún** en GitHub (el bot cambiaría de fuente al momento): dímelo y se decide con datos.
3. **Reparto del dinero** entre MiniBench y temporada: con preguntas resueltas.
4. **Archivar la conversación de la nube** «Metaculus: encender el bot con los 100 $ (orden 26)»:
   ya puedes.
5. **Tu correo en el primer commit:** GitHub aún enseña la versión vieja a quien tenga su
   identificador exacto. Para borrarla del todo: soporte de GitHub (opcional).

## Normas del torneo que conviene recordar
- Prohibido: pronosticar a mano, retocar el bot mirando preguntas abiertas del torneo, relanzarlo
  sobre una pregunta porque no guste el resultado. Un solo pronóstico por pregunta (auditoría del
  28/09 en HALLAZGOS; regla de cambios en CLAUDE.md).
- Para cobrar: descripción del bot con sus cambios importantes (CHANGELOG), inspección, encuesta
  al final de la temporada, pago por Ramp, documento de identidad y W-8BEN. **Si se gana algo, no
  se cobra hasta que conteste Fremap** (reglas comunes §13).
- **Para apagarlo:** borra la variable `ENVIO_REAL` (o ponla en `false`) en GitHub → Settings →
  Secrets and variables → Actions → Variables.

## Para el mando (orden 82, 08/10/2026)
- Hecho y en `main`: las 4 piezas que gastaban el plan, apagadas por parámetro o rutina (tabla de
  arriba); comprobado en una ejecución real en verde; CHANGELOG, DECISIONES, HALLAZGOS al día.
- `docs/MAESTRO.md` aún describe la investigación con Claude: lo cambia el usuario si quiere.
- Fallo de método (08/10): se vieron en pantalla las cifras de una pregunta abierta al leer un
  registro; no se usaron. Trampa añadida en CLAUDE.md.
