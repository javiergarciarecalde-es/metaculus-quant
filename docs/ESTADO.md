# ESTADO (siempre «ahora»)

**Última actualización:** 28/09/2026, 11:05 (hora de Madrid). Sesión cerrada. Sesión en la nube «tres mejoras antes
de la temporada (orden 26)» y cambios de modelos del 28/09.
**Fase:** fase 0, compitiendo. El bot está **encendido** y pronostica solo cada 20 minutos en
MiniBench y en la temporada de otoño (abre el lunes 28/09).
**Rama:** todo está en `main` en GitHub. Cada commit se sube solo (gancho `post-commit` = una orden
automática que hace git después de guardar).

## Dónde estamos
| Pieza | Estado |
|---|---|
| Bot en Metaculus | **Kyou-bot** |
| Secretos en GitHub (claves guardadas) | `METACULUS_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` y `OPENROUTER_API_KEY` (la clave de créditos de Metaculus, la puso el usuario el 27/09) |
| Interruptor `ENVIO_REAL` | **`true` desde el 27/09 a las 21:04** (decisión del usuario): envía de verdad |
| Tope de gasto de los créditos | **puesto y probado** (ver abajo) |
| Modelos (tu decisión del 28/09) | pronostican GPT-6 Sol, Claude Opus 5.5 y Gemini 3.8 Flash; busca noticias Opus 5.5 (respaldo GPT-6 Sol). Detalle en CHANGELOG |
| Investigación con Claude | **en pausa hasta hoy 28/09 a las 11:00**; luego, en las preguntas pares, **sustituye a la búsqueda de pago** (opción A, tu decisión del 28/09) |
| Clasificadores en sombra | Gemini 3.8 Flash y Opus 5.5 «extra» (tu plan) dicen si cada pregunta es fácil o difícil; **no deciden nada** |
| Gastado de los 100 $ | **5,36 $** (pruebas del 27/09); ~0,35 $ por pregunta |
| Vigilancia que reacciona sola | **encendida** (27/09, 22:20): dos veces por hora; primera ejecución real en verde, «todo en orden» |
| Pruebas automáticas | **199 de 199 en verde** y ruff (revisor de estilo) sin quejas |

## Qué va solo (sin que tú hagas nada)
| Qué | Cuándo | Dónde |
|---|---|---|
| Pronosticar (MiniBench y temporada, con tope de gasto) | cada 20 min | GitHub |
| Vigilancia: relanza el bot si se calla o falla; si no basta, despierta a Claude | dos veces por hora | GitHub |
| Marcador: puntos, gasto, preguntas perdidas, comparaciones, clasificadores | lunes 08:30 | GitHub |
| **Revisión semanal**: lee el marcador, aplica las reglas escritas y te dice si hay que decidir algo | lunes 09:12, desde el 05/10 | esta conversación de Claude |
| Pausa de Claude, recarga de la clave por Metaculus, curva suave y clasificadores en sombra | solos | bot |
**No va solo:** decidir cambios que tocan los pronósticos (te los propone la revisión), AskNews
(tu cuenta) y, al final, la encuesta y el cobro. Si el reloj de GitHub se parara del todo, se
pararían bot y vigilancia; la revisión del lunes lo detectaría.

## El tope de gasto (qué hace ahora el bot que antes no hacía)
- Antes de cada torneo **pregunta a la clave cuánto queda** (consulta gratuita) y solo empieza las
  preguntas que caben. Si Metaculus sube el límite de la clave, el bot lo ve solo.
- **MiniBench primero** (es la que decide si llega más dinero): solo se para cuando quedan menos de
  3 $ (la «reserva»).
- **Temporada, a ritmo:** puede llevar gastado el 25 % desde el primer día y el resto repartido por
  igual hasta el 06/01. Si la MiniBench ya gastó por encima de esa línea, la temporada espera.
- Se cuentan 0,40 $ por pregunta para decidir cuántas caben (lo medido es ~0,30 $).
- **Sin dinero:** aviso amarillo «Sin dinero…» y nada más; no sale en rojo cada 20 minutos.
- Números en `config/params.yaml` (sección `presupuesto`) y en CHANGELOG.

| Cifra | Valor | Con qué se compara |
|---|---|---|
| Coste real por pregunta | ~0,30 $ | estimación previa 0,34 $: **va bien** |
| Preguntas que pagan 100 $ | ~330 | hasta enero salen ~420 de MiniBench + 300-400 de temporada: **OJO, no llega** |
| Una ronda de MiniBench (~60 preguntas) | ~18 $ | 100 $ dan para ~5 rondas si no llega más dinero |
| Temporada | pocas preguntas hasta que llegue más dinero | desde la 2.ª ronda la MiniBench va por delante de la línea: **OJO** |

## Tu plan de Claude (lo que gasta la investigación con agentes)
| Medida (27/09) | Valor |
|---|---|
| Por pregunta, en dinero equivalente de la API | 2,2-2,8 $ |
| Una tanda de 3 preguntas | ~9-11 % de la ventana de 5 horas y ~1 % del tope semanal (cota alta: esta sesión también gastaba) |
| Previsión con la opción A (pares) | ~10 % de tu tope semanal |
- Si se agota el plan, el bot sigue sin esa investigación, pero **tus otros proyectos se quedan sin
  Claude** hasta que se renueve. Para quitarla del todo: borra el secreto `CLAUDE_CODE_OAUTH_TOKEN`.
- Pares (Max) frente a impares (búsqueda de pago): reglas escritas antes, en HALLAZGOS del 28/09.

## Lo que queda por hacer
1. **Tú (opcional):** mirar en metaculus.com el perfil de Kyou-bot (Ajustes → My Forecasting Bots).
2. **Hoy 28/09, 11:48 (automático):** comprobación de las primeras preguntas reales con los cambios
   del día: búsqueda con Opus 5.5, opción A (Max en las pares), los dos clasificadores y su coste.
3. **Cada lunes, 09:12, desde el 05/10 (automático):** revisión semanal (rutina de Claude Code).
   La del 05/10 incluye: primera mirada a clasificadores y a Max frente a búsqueda de pago, gasto
   por partes frente a la línea, preguntas perdidas, fiabilidad del reloj de GitHub y **propuesta
   de cambio de modelos** con el gasto medido. Reglas en HALLAZGOS del 28/09.
4. **Al final de la temporada:** la encuesta del bot (obligatoria para cobrar). Te lo recordaré.

## Decisiones pendientes tuyas
1. **AskNews (noticias gratis):** crear tu cuenta en my.asknews.app y mandar el correo (texto
   completo en HALLAZGOS del 28/09). Las claves **no se ponen aún** en GitHub: se decide tras la
   1.ª semana.
2. **Lector** (GPT-4o mini): ¿pasarlo a GPT-6 Sol? Hoy se queda por barato y probado.
3. **Reparto del dinero** entre MiniBench y temporada: con los datos de la 1.ª semana.
4. **Tu correo en el primer commit:** GitHub aún enseña la versión vieja a quien tenga su
   identificador exacto. Para borrarla del todo: soporte de GitHub (opcional).

## Normas del torneo que conviene recordar
- Inscribirse y enviar pronósticos equivale a aceptar las normas.
- La identidad se pide **al cobrar**: pago por Ramp (comprobar que admite España/euros), documento
  de identidad y formulario W-8BEN (fiscal de EE. UU.); los impuestos los pagas tú.
- Para cobrar: enseñar el código o una descripción, aceptar una inspección y rellenar la encuesta.
- Comentarios privados en cada pronóstico: el bot ya los publica.
- Prohibido: pronosticar a mano, retocar el bot mirando preguntas abiertas del torneo, relanzarlo
  porque no guste un resultado.
- **Para apagarlo:** borra la variable `ENVIO_REAL` (o ponla en `false`) en GitHub → Settings →
  Secrets and variables → Actions → Variables.
- Metaculus propone también Market Pulse y Metaculus Cup, pero los créditos son solo para MiniBench y
  FutureEval: el bot no entra en esos dos.

## Cuánto queda sin verificar (de frente)
- En vivo, con preguntas reales: la búsqueda con Opus 5.5 `:online` y su precio; la opción A (Max
  en las pares); los clasificadores; Gemini 3.8 Flash contestando. Lo mira la comprobación de hoy
  a las 11:48; si algo falla, entra un respaldo y el registro lo dice.
- La vigilancia **relanzando** el bot y **despertando a Claude**: solo con fallos simulados.
- Si el reloj de GitHub se para del todo, se paran bot y vigilancia hasta la revisión del lunes.
- El tope de gasto con una ronda entera de MiniBench (solo simulado y en ensayo).

## Para el mando (parte de cierre de la sesión en la nube, 28/09/2026 ~11:05)
- **Hecho (orden 26 y peticiones del usuario del 27-28/09), todo en `main`, 234 pruebas en verde:**
  vigilancia que reacciona sola; coste por parte y resumen semanal del gasto; curva PCHIP en sombra
  (entre las 3 comparaciones decididas de antemano); lista de preguntas perdidas; piezas de GitHub
  sobre Node 24; consulta gratuita de modelos de la clave (solo OpenAI, Anthropic y Google);
  modelos nuevos (Gemini 3.8 Flash; búsqueda con Opus 5.5 y respaldo GPT-6 Sol; OpenAI Sol/Astra;
  Anthropic solo Opus 5.5); opción A (Claude Max sustituye a la búsqueda de pago en las pares);
  dos clasificadores en sombra (Gemini y Opus «xhigh»); arreglo del marcador del 28/09.
- **Rutinas de Claude Code** (disparan en la conversación de la sesión
  `session_013btsc97onUdDY6X7v9VEE3`: **no archivarla**): `trig_01X5xNNWkveFfeTSNe6no1xy`
  (comprobación de hoy 09:48 UTC) y `trig_01Jpv6Pfyp3yo3SxcknZAs4f` (revisión cada lunes 07:12
  UTC). Si esa sesión se cierra, hay que rehacerlas (texto en HALLAZGOS del 28/09).
- **Aviso sin entregar:** desde la nube no se llega al mando «Mando 26/09/2026 (2)»; este apartado
  hace de parte. «Para leer por el usuario»: «Qué va solo» y «Decisiones pendientes tuyas».
- Fallos míos de la sesión, ya arreglados: un commit subido con una prueba en rojo (07:30 UTC) y la
  lista de perdidas que tumbó el marcador (06:45 UTC). Ver HALLAZGOS.
- A las comunes §7 les falta decir qué hacer con un documento propio como `docs/DECISIONES.md`.
