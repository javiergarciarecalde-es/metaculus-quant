# ESTADO (siempre «ahora»)

**Última actualización:** 28/09/2026, 10:20 (hora de Madrid). Sesión en la nube «tres mejoras antes
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

## Las tres mejoras de esta noche (tu decisión de las 21:55; ninguna cambia lo que se envía)
1. **Vigilancia que reacciona sola, sin avisarte.** Un proceso aparte de GitHub (a :13 y :43 de cada
   hora) mira si el bot lleva más de 45 min sin terminar bien, si su última ejecución falló o si hay
   preguntas abiertas hace más de 1 h sin pronóstico que el tope de gasto sí dejaría hacer. Si pasa:
   **relanza el bot**; si 2 relanzamientos en 3 h no bastan, **despierta a Claude** (tu plan, con
   topes; una vez cada 12 h como mucho). Claude no pronostica ni toca los parámetros: como mucho deja
   un arreglo en una rama aparte y un **issue** (una nota en GitHub) para la siguiente sesión.
2. **Medir en qué se va el dinero.** Cada pregunta guarda cuánto costó cada parte (búsqueda de
   noticias, cada modelo, el lector). Cada lunes el marcador resume el gasto frente a la línea de
   ritmo. El cambio de modelos, si lo hay, se te propone con esos datos tras la primera semana.
3. **Curva suave en sombra** para las preguntas numéricas: se calcula y se guarda junto a la enviada;
   no se envía. Se compararán con preguntas resueltas (hacen falta ≥150).

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

## También hecho esta noche (tu «adelante» de las 22:40)
- **Lista semanal de preguntas perdidas** en el marcador: las cerradas sin pronóstico nuestro,
  separando las que el tope dejó a propósito (el bot ahora las apunta) de las «sin explicar».
- **Piezas de GitHub actualizadas** (GitHub quitó la versión vieja, Node 20, el 23/09).
- **La curva suave es ahora una de las 3 comparaciones decididas de antemano** (sustituye a
  «límites 1-99 %») y el marcador ya la puntúa frente a la curva enviada.

## Lo que queda por hacer
1. **Tú:** entra en metaculus.com con tu cuenta y mira el perfil de Kyou-bot (Ajustes → My
   Forecasting Bots): deben verse pronósticos en la zona de pruebas y uno en la temporada (45707).
   Yo no puedo verlo: sin tu cuenta, la web no lo enseña.
2. **Lunes 28/09 y martes:** mirar las primeras ejecuciones del reloj (cada 20 min): que pronostica en
   MiniBench y temporada, y cuánto gasta de verdad (registro `presupuesto_*.jsonl` en los artefactos).
3. **Semana del 05/10:** primera revisión: preguntas llegadas y perdidas, gasto de créditos frente a la
   línea, cupo de Claude, ¿lanza el reloj de GitHub cada 20 min?, primera mirada al clasificador en
   sombra y a búsqueda con Max frente a la de pago (reglas en HALLAZGOS del 28/09).
4. **Al final de la temporada:** la encuesta del bot (obligatoria para cobrar). Te lo recordaré.

## Decisiones pendientes tuyas
1. **Reparto del dinero entre MiniBench y temporada** si no llega más: hoy manda la MiniBench (lo
   pidió el mando) y la temporada se queda con poco. Alternativa: modelos más baratos en la
   temporada. Decidir tras la primera semana, con el gasto real.
2. **Tu correo en el primer commit:** GitHub aún enseña la versión vieja a quien tenga su
   identificador exacto. Para borrarla del todo: soporte de GitHub (opcional).
3. **Reloj de GitHub poco fiable** (otro participante: solo lanzaba ~22 % de las veces): se mira tras
   la primera semana.
4. **Reloj apagado tras 60 días sin cambios** (repositorios públicos): mientras haya sesiones que
   guarden algo al menos una vez al mes, no pasa.
5. **Noticias gratis (AskNews), lo pediste el 27/09:** (1) crea tu cuenta en my.asknews.app (tiene
   que ser tuya: yo no creo cuentas ni acepto condiciones); (2) manda desde tu correo a
   rob@asknews.app el texto preparado (abajo). Dan ~3.000 consultas al mes por bot. Cuando lleguen
   las claves, se ponen como secretos `ASKNEWS_CLIENT_ID` y `ASKNEWS_SECRET`; **no se ponen aún**: el
   bot las usaría al momento en vez de la búsqueda actual. El cambio se decide tras la 1.ª semana,
   con el gasto medido y en fecha anunciada.
   Texto: «Hi Rob, I'm registering my bot for the Metaculus Fall 2026 FutureEval bot tournament and
   MiniBench. AskNews account email: [el de tu cuenta]. Metaculus bot username: Kyou-bot. I plan to
   use /news. Thanks! [tu nombre]»

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
- La vigilancia **relanzando** el bot y **despertando a Claude**: probado solo con fallos simulados
  (40 pruebas). En real solo se ha visto el caso «todo en orden». El permiso de GitHub para relanzar
  está puesto, pero no se ha ejercido en vivo.
- Si el reloj de GitHub deja de lanzar **todo**, también se para la vigilancia (usa el mismo reloj).
  Por eso va dos veces por hora; no hay otra red por debajo.
- Que los pronósticos enviados aparecen en el perfil: Metaculus contestó «Posted prediction» a los 9,
  pero nadie lo ha mirado en la web (lo haces tú).
- Que la pausa de Claude vuelve sola el 28/09 a las 11:00: probado con pruebas simuladas, no en vivo.
- Que el tope se comporta bien con una ronda entera de MiniBench (solo probado con pruebas simuladas
  y con la clave real en ensayo).

## Para el mando
- **Pendiente de entregar** (desde la nube no se llega al mando «Mando 26/09/2026 (2)»): orden 26,
  las tres mejoras hechas y en `main` (vigilancia, gasto por parte, curva en sombra), más la lista de
  preguntas perdidas, las piezas de GitHub al día y la curva suave entre las 3 comparaciones
  decididas de antemano; 199 pruebas en verde. «Para leer por el usuario»: «Las tres mejoras de esta
  noche» y «También hecho esta noche».
- Orden 26: criterio de terminado cumplido el 27/09 (salvo mirar el perfil en la web, que es del
  usuario). Parte de cierre pendiente (cierre B, lo decide el usuario).
- A las comunes §7 les falta decir qué hacer con un documento propio como `docs/DECISIONES.md`.
- Gasto del plan: ver la tabla «Tu plan de Claude». El tope semanal está al 90 %.
