# ESTADO (siempre «ahora»)

**Última actualización:** 28/09/2026, 13:05 (hora de Madrid). Sesión local «Metaculus: revisión a
fondo del bot (orden 27)», cerrada.
**Fase:** fase 0, compitiendo. El bot está **encendido** y mira cada 20 minutos la MiniBench y la
temporada de otoño. Desde la mañana del 28/09 **no hay ninguna pregunta abierta** en los dos
torneos (la única pronosticada, la 45707, cerró hacia las 08:00 de Madrid).
**Rama:** todo está en `main` en GitHub. Cada commit se sube solo (gancho `post-commit` = una orden
automática que hace git después de guardar).

## Dónde estamos
| Pieza | Estado |
|---|---|
| Bot en Metaculus | **Kyou-bot**; 9 pronósticos (8 en la zona de pruebas y 1 en la temporada, la 45707) |
| Secretos en GitHub (claves guardadas) | `METACULUS_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` y `OPENROUTER_API_KEY` (la clave de créditos de Metaculus) |
| Interruptor `ENVIO_REAL` | **`true` desde el 27/09 a las 21:04** (decisión del usuario): envía de verdad |
| Normas del torneo | **se cumplen** (auditoría del 28/09, abajo) |
| Tope de gasto de los créditos | puesto y probado; gastado **5,36 $ de 100 $** |
| Tope del plan de Claude (nuevo) | el bot no pasa del **15 %** de tu tope semanal (abajo) |
| Modelos (tu decisión del 28/09) | pronostican GPT-6 Sol, Claude Opus 5.5 y Gemini 3.8 Flash; busca noticias Opus 5.5 (respaldo GPT-6 Sol); lector GPT-6 Sol |
| Investigación con Claude | en las preguntas **pares** sustituye a la búsqueda de pago (opción A); la pausa terminó el 28/09 a las 11:00 |
| Clasificadores en sombra | Gemini 3.8 Flash y Opus 5.5 «extra»; **no deciden nada** |
| Pruebas automáticas | **269 de 269 en verde**, ninguna saltada, y ruff (revisor de estilo) sin quejas |

## Normas del torneo: qué se miró y qué se arregló (orden 27)
Normas oficiales releídas el 28/09 (detalle en `docs/FUENTES.md`) y **regla de cambios** escrita en
`CLAUDE.md`: los cambios que tocan cómo pronostica el bot se deciden solo con preguntas cerradas o
de fuera del torneo, y cada uno va a CHANGELOG con fecha, motivo y con qué datos (lo pedirán para
cobrar).
| Pregunta | Respuesta |
|---|---|
| ¿Algún cambio del 27-28/09 se decidió mirando pronósticos de preguntas abiertas? | **No encontrado.** Todos tienen motivo escrito (gasto, tus preferencias de modelos, diseño decidido antes) |
| ¿El bot puede pronosticar dos veces la misma pregunta? | En la práctica no (comprobado: tras enviar la 45707, las ejecuciones siguientes la saltaron). Había **dos agujeros** y están **cerrados con pruebas**: si Metaculus dejara de decir qué ya pronosticamos, la librería las daba por nuevas; y una pregunta repetida en la lista se enviaba dos veces |
| ¿La vigilancia o la prueba a mano «relanzan» una pregunta? | No: relanzan el bot entero, que solo hace las que faltan. Permitido |
| ¿Se publicaba algo de preguntas abiertas? | El marcador podía subir al repositorio (público) pronósticos de preguntas aún abiertas; **arreglado** (solo tras su hora de cierre). No se había publicado ninguno |

## Tu plan de Claude (lo que gasta el bot) y su tope
| Parte | Medido o previsto por semana | Con qué se compara |
|---|---|---|
| Investigación de las pares | **2,07 $** por pregunta (10 medidas reales del 27/09); ~20-30 $ por semana | tope del bot: 70 $ |
| Clasificador con Opus «extra» | aún sin medir (no ha habido preguntas); previsto 1-9 $ | se apaga el primero, al pasar 56 $ |
| Vigilancia despertando a Claude | nunca ha hecho falta; como mucho 2 veces por semana (≤10 $) | antes podían ser 14 |
| Revisión de los lunes | aún no ha corrido; reserva de 5 $ | incluida en el 15 % |
| **Total previsto** | **~5-9 % de tu tope semanal** en una semana normal | **tope: 15 %** (va bien) |
- 1 % de tu tope semanal ≈ 5 $ equivalentes (medido el 27/09, cota prudente). El marcador de cada
  lunes trae la tabla «Plan de Claude del usuario».
- Pasado el 80 % del tope se apaga el clasificador con Opus; pasado el 100 %, las preguntas pares van
  con la búsqueda de pago y la vigilancia ya no despierta a Claude.
- **Apagada** (tu «sí», 12:07) la comprobación que la conversación de la nube se había programado
  cada 4 horas hasta el 05/10: podía gastar más que todo el bot.

## Qué va solo (sin que tú hagas nada)
| Qué | Cuándo | Dónde |
|---|---|---|
| Pronosticar (MiniBench y temporada, con topes de gasto y de plan) | cada 20 min | GitHub |
| Vigilancia: relanza el bot si se calla o falla; si no basta, despierta a Claude | dos veces por hora | GitHub |
| Marcador: puntos, gasto, plan de Claude, preguntas perdidas, clasificadores | lunes 08:30 | GitHub |
| **Revisión semanal** (rutina nueva, memoria limpia cada vez) | lunes 09:12, desde el 05/10 | nube; deja su resumen en `docs/REVISION_SEMANAL.md` |
**No va solo:** decidir cambios que tocan los pronósticos, avisar cuando conteste AskNews y, al
final, la encuesta y el cobro.

## Comprobado hoy en GitHub de verdad
- **La vigilancia relanza el bot:** con el botón de prueba (10:26) y **sola** (10:31), cuando una
  ejecución falló porque pypi.org (el almacén de piezas de Python) no contestaba. Sin despertar a
  Claude. Arreglado que un corte así tumbe el bot: la instalación reintenta con más paciencia.
- Las 269 pruebas pasan también en GitHub (antes una se saltaba siempre).

## Lo que queda por comprobar (sin preguntas no se puede)
| Qué | Cuándo se verá |
|---|---|
| La investigación con Claude tras la pausa, la opción A y los dos clasificadores con preguntas reales; el coste real del clasificador con Opus | con las primeras preguntas de la temporada o de la MiniBench (fechas no publicadas); lo recoge la revisión del 05/10 |
| El tope de gasto con una ronda entera de MiniBench | en la primera ronda con el bot encendido |
| El tope del plan leyendo la cuenta de GitHub | con la primera pregunta que use Claude |
| La vigilancia despertando a Claude | solo con fallos simulados |
| Si el reloj de GitHub se para del todo, se paran bot y vigilancia | lo vería la revisión del lunes |

## Decisiones pendientes tuyas
1. **Archivar la conversación de la nube** «Metaculus: encender el bot con los 100 $ (orden 26)»:
   ya puedes (sus tres rutinas están apagadas y la revisión nueva no depende de ella).
2. **Registros públicos:** decidido el 28/09 (13:05): el repositorio sigue público de momento.
3. **AskNews (noticias gratis):** esperando su respuesta. Cuando lleguen las claves, **no las pongas
   aún** en GitHub (el bot cambiaría de fuente al momento): dímelo y se decide con datos.
4. **Reparto del dinero** entre MiniBench y temporada: con los datos de la 1.ª semana.
5. **Tu correo en el primer commit:** GitHub aún enseña la versión vieja a quien tenga su
   identificador exacto. Para borrarla del todo: soporte de GitHub (opcional).

## Normas del torneo que conviene recordar
- Prohibido: pronosticar a mano, retocar el bot mirando preguntas abiertas del torneo, relanzarlo
  sobre una pregunta porque no guste el resultado. Un solo pronóstico por pregunta.
- Para cobrar: descripción del bot con sus cambios importantes (CHANGELOG), inspección, encuesta
  al final de la temporada (te lo recordaré), pago por Ramp, documento de identidad y W-8BEN.
- **Para apagarlo:** borra la variable `ENVIO_REAL` (o ponla en `false`) en GitHub → Settings →
  Secrets and variables → Actions → Variables.

## Para el mando (orden 27, 28/09/2026)
- Hecho y en `main`: auditoría de normas con dos agujeros cerrados; regla de cambios en CLAUDE.md;
  tope del plan (15 %) con cuenta semanal en GitHub; tope de 2 despertares por semana; rutina
  semanal nueva que escribe en `docs/REVISION_SEMANAL.md` (el mando la recoge los lunes); rutinas
  viejas apagadas; relanzamiento de la vigilancia comprobado en real; instalación resistente a
  cortes de pypi.org.
- Fallos de método encontrados: 23 commits de la sesión en la nube firmados como «Claude»
  (comunes §10); una prueba que se saltaba siempre (comunes §6). A las comunes §7 les falta decir
  qué hacer con un documento propio como `docs/DECISIONES.md`. `docs/MAESTRO.md` aún dice que Claude
  «se añade» a la búsqueda: desde la opción A la sustituye en las pares (lo cambia el usuario).
