# ESTADO (siempre «ahora»)

**Última actualización:** 22/10/2026, 15:10 (hora de Madrid), sesión «Metaculus: revisar el robot
(orden 174)». Antes: 18/10/2026, correo de Metaculus sin créditos extra.
**Fase:** fase 0, compitiendo. El bot está **encendido**; debería mirar cada 20 minutos la MiniBench
y la temporada de otoño, pero **desde el 10/10 GitHub solo lo lanza cada 3-5 horas** (abajo).
Pronostica con los 3 modelos de OpenRouter y la búsqueda de pago (créditos de Metaculus).

## Quién está tocando qué
| Sesión | Qué | Estado |
|---|---|---|
| «Metaculus: revisar el robot (orden 174)» | medir el reloj de GitHub, preguntas perdidas, opciones | hecho y en `main`; espera tu decisión del reloj. Arranque A 12 %, leído L 2 % → relevo al 27 % |

## El reloj de GitHub (orden 174, 22/10)
- **Qué pasa:** desde el 10/10 GitHub lanza el bot **3-8 veces al día de 72** (cada 20 min), en
  tandas cada 3-5 h, el bot y la vigilancia a la vez. No es un fallo nuestro: le pasa a otros
  proyectos de la cuenta. Cambiar los minutos del reloj no sirve (detalle en HALLAZGOS 22/10).
- **Qué cuesta:** una pregunta que abre y cierra entre dos tandas se pierde (0 puntos). Perdidas:
  1 de 64 en la semana al 12/10 (la 45956) y 6 de 43 en la semana al 19/10. Todas por eso.
- **Hecho:** el marcador de los lunes enseña ahora cuántas veces se lanzó el bot cada día y, por
  cada pregunta perdida, cuántas horas estuvo sin lanzarse alrededor de su cierre.
- **Falta tu decisión** (punto 1 de «Decisiones pendientes»).
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
| Créditos de OpenRouter | quedan **~60,89 $ de 100 $** (22/10, 12:28 UTC); ritmo 11-22/10: **1,56 $/día** (OJO: para llegar al 06/01 hacen falta ≤0,76, dejando la reserva de 3 $); el freno de ritmo lo contiene a costa de la temporada (abajo) |
| Créditos extra de Metaculus | **denegados** (correo del 18/10, ronda según la MiniBench del 05/10; sin motivo detallado). Sigue con derecho a premios |
| Pruebas automáticas | **282 de 282 en verde**, ninguna saltada, y ruff (revisor de estilo) sin quejas |

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

## Créditos de OpenRouter hasta el 06/01/2027 (cuenta del 22/10)
| Dato | Valor | Comparado con |
|---|---|---|
| Gastado | 39,11 $ de 100 $ | línea de ritmo a hoy: 43,39 $ (va bien: 4,28 $ por debajo) |
| Coste por pregunta | ~0,23 $ (76 preguntas del 11 al 22/10) | previsto en el tope: 0,40 $ (va bien) |
| Ritmo 11-22/10 | 1,56 $/día | **OJO**: llegar al 06/01 pide ≤0,76 $/día |
| Ritmo 18-22/10 | ~2,7 $/día (ronda de MiniBench del 19/10: 43 preguntas en 2 días) | **OJO** |
- No se acaba antes de tiempo: el **freno de ritmo** retiene preguntas de la temporada para que lo
  gastado no pase de la línea (sube 0,75 $/día). La MiniBench no tiene freno (solo la reserva de 3 $).
- **Lo que significa:** cada ronda de MiniBench (cada 2 semanas) cuesta ~10-14 $, casi toda la
  subida de la línea. Desde ya, el freno dejará **casi todas las preguntas de la temporada sin
  pronóstico** hasta el 06/01 (0 puntos cada una; la puerta de la fase 0 suma la temporada).
- Que GitHub lance más el bot apenas cambia esto: +≤0,1 $/día de MiniBench; la temporada la frena
  la línea igual.

## Qué va solo (sin que tú hagas nada)
| Qué | Cuándo | Dónde |
|---|---|---|
| Pronosticar (MiniBench y temporada, con tope de gasto) | cada 20 min (de hecho, cada 3-5 h desde el 10/10) | GitHub |
| Vigilancia: relanza el bot si se calla, falla o se olvida preguntas (sin Claude) | dos veces por hora (de hecho, a la vez que el bot) | GitHub |
| Marcador: puntos, gasto, preguntas perdidas, lanzamientos por día, clasificador | lunes 08:30 (el 19/10 salió a las 15:45) | GitHub |
**Ya no va solo:** la revisión semanal de los lunes (apagada el 07/10; `docs/REVISION_SEMANAL.md` se
queda en la del 05/10). **Nunca va solo:** decidir cambios que tocan los pronósticos, avisar cuando
conteste AskNews y, al final, la encuesta y el cobro.

## Lo que queda por comprobar
| Qué | Cuándo se verá |
|---|---|
| Tabla nueva de lanzamientos por día en GitHub (probada contra GitHub desde local; el marcador lanzado a mano el 22/10 la saca allí) | **tú:** en el marcador del lunes 26/10, «Cuántas veces lanzó GitHub el bot» y «Preguntas perdidas» |
| La vigilancia con un fallo real ya sin Claude (relanza; solo probado con pruebas automáticas) | cuando haya un fallo |
| Si el reloj de GitHub se para del todo, se paran bot y vigilancia | marcador de los lunes |

## Decisiones pendientes tuyas
1. **El reloj de GitHub** (recomendación primero):
   - **(C) Recomendada: un servicio de reloj gratuito en internet** que cada 20 min le pida a GitHub
     lanzar el bot. Va de día y de noche (las perdidas cierran de madrugada). 0 €, 0 minutos de
     GitHub (repositorio público), no gasta más créditos que ahora. Pide que **tú** crees la cuenta en
     ese servicio y un permiso (token) de GitHub limitado a lanzar este bot; te guío paso a paso.
     Riesgo: si alguien robara ese permiso solo podría lanzar el bot más veces (no cambia nada).
   - (B) El Programador de tareas de Windows de tu ordenador lo lanza cada 20 min. 0 €, nada que
     crear, pero solo con el ordenador encendido (de noche seguiría perdiendo). Necesita tu «sí».
   - (A) Dejarlo así: ~6 preguntas perdidas por semana (unos 10 de cada 70).
   - Descartada: un truco dentro de GitHub que se relanza solo; choca con sus condiciones de uso y
     podría afectar a toda tu cuenta (todos los proyectos).
2. **Créditos hasta el 06/01:** Metaculus **no da más** (correo del 18/10). Con la MiniBench costando
   ~10-14 $ cada dos semanas, el freno dejará sin hacer casi toda la temporada desde ya (tabla de
   arriba). Opciones: (a) no hacer nada; (c) abaratar el bot (cambiar modelos: se decide con datos
   de preguntas cerradas, en fecha anunciada); (d) repartir el dinero entre MiniBench y temporada
   (punto 4). Ninguna cuesta dinero tuyo.
3. **AskNews (noticias gratis):** esperando su respuesta. Cuando lleguen las claves, **no las pongas
   aún** en GitHub (el bot cambiaría de fuente al momento): dímelo y se decide con datos.
4. **Reparto del dinero** entre MiniBench y temporada: con preguntas resueltas.
5. **Archivar la conversación de la nube** «Metaculus: encender el bot con los 100 $ (orden 26)»:
   ya puedes.
6. **Tu correo en el primer commit:** GitHub aún enseña la versión vieja a quien tenga su
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

## Para el mando (orden 174, 22/10/2026)
- Hecho y en `main`: medición del reloj de GitHub (HALLAZGOS 22/10), causa de la 45956 y de las 6
  del 19/10 (huecos de 3,6-9,9 h sin lanzar), tabla nueva en el marcador, FUENTES y trampas.
- No aplicado: el arreglo del reloj (sale de GitHub: decide el usuario, decisión 1) ni nada que
  toque el gasto. Visto de paso: la librería ya no mide el coste por pieza (marcador: 0,0 $).
