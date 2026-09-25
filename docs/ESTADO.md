# ESTADO (siempre «ahora»)

**Actualizado:** 25/09/2026 por la noche (sesión 2 en Windows: estudio de bots rivales, marcador,
comparador y mejoras A, B y C; antes, órdenes 12e y 14 del mando).
**Rama:** todo está en `main` en GitHub. Cada commit se sube solo (gancho `post-commit` = una orden
automática que hace git después de guardar).

## Dónde estamos
El bot está **inscrito y a medio encender**. Falta **una sola cosa** para que funcione: la clave de
los créditos de IA, que manda Metaculus por correo. El envío real sigue **apagado**: no ha enviado
nada a Metaculus.

| Pieza | Estado |
|---|---|
| Bot en Metaculus | creado: **Kyou-bot** |
| Formulario de participación y créditos | enviado el 25/09 (se piden 270 $) |
| Repositorio | **público** |
| Secretos en GitHub (claves guardadas) | `METACULUS_TOKEN` y `CLAUDE_CODE_OAUTH_TOKEN` puestos. **Falta `OPENROUTER_API_KEY`** (la clave de créditos, aún no ha llegado) |
| Interruptor `ENVIO_REAL` | no existe todavía → no envía nada |
| Pruebas automáticas (programa que comprueba el bot solo) | **98 de 98 en verde** y ruff (revisor de estilo) sin quejas (25/09, noche) |

## Primera prueba real (25/09, 09:27, sin enviar nada)
| Qué | Resultado |
|---|---|
| Arranque, instalación y Claude Code | bien (Claude Code 2.1.282 instalado en GitHub) |
| Modelos (lista de OpenRouter) | todos existen |
| Pronósticos | **0 de 3**. Sin la clave de créditos, el bot probó los modelos «de Metaculus sin clave» y Metaculus respondió «no tienes cupo para este modelo» (GPT-5 y Claude Sonnet) |
| Investigación con tu Claude Max | parece que funcionó (tardó ~2 min por tanda y no dio error), pero no quedó escrito lo que encontró. Ya lo apunta: se verá en la próxima prueba |
| Color final | **verde, y no debía**: acabó en verde con 0 pronósticos. **Arreglado**: si fallan todas, ahora sale en rojo; si fallan algunas, en amarillo; y avisa si falta la clave de créditos |

Conclusión: el bot **no puede pronosticar hasta que llegue la clave de créditos** (o pongas una clave
tuya). No es un fallo del bot: sin clave no hay modelos que pronostiquen.

## Lo que queda por hacer
1. **Tú: vigilar el correo** (también la carpeta de spam) por la clave de créditos de Metaculus.
   Cuando llegue, ponla como secreto `OPENROUTER_API_KEY` en
   https://github.com/javiergarciarecalde-es/metaculus-quant/settings/secrets/actions/new
   (en «Name», `OPENROUTER_API_KEY`; en el valor pegas la clave). Si la encuentras en spam, Metaculus
   pide que se lo digas.
2. **Después (yo o tú):** repetir la prueba sin envío. Debe acabar en verde con
   «Terminado: 3 pronósticos de ensayo».
3. **Solo si sale bien:** encender el envío real (variable `ENVIO_REAL` = `true`), repetir la prueba
   (ahora envía a la zona de pruebas) y mirar en el perfil de Kyou-bot que aparecen los pronósticos.
   Encenderlo sin la clave no sirve: fallaría cada 20 minutos.
4. **Al final de la temporada:** la encuesta del bot (obligatoria para cobrar). Te lo recordaré.

## Decisiones pendientes tuyas
1. **Tu correo en el primer commit: quitado** (25/09). Queda un resto: GitHub aún enseña la versión
   vieja a quien tenga su identificador exacto. Para borrarla del todo tendrías que pedírselo al soporte
   de GitHub (https://support.github.com, «remove cached views» / datos sensibles). Es opcional.
2. **Si la clave de créditos no llega** (este otoño son selectivos): (a) esperar; (b) pagar tú una
   clave de OpenRouter con tope de gasto (~0,34 $ por pregunta, ~270 $ hasta enero); (c) no competir
   esta temporada. No se pone ninguna clave de pago sin que lo decidas.
3. **Reloj de GitHub poco fiable** (otro participante vio que solo lanzaba ~22 % de las veces): lo
   miramos tras la primera semana con los datos del registro.
4. **Reloj apagado tras 60 días sin cambios** (norma de GitHub en repositorios públicos): mientras
   haya sesiones que guarden algo al menos una vez al mes, no pasa.
5. **Opcional, noticias gratis (AskNews):** hay que escribirles con tu nombre y LinkedIn; lo harías tú.

## Dinero y cupo
| Concepto | Quién paga | Cuánto (estimado) |
|---|---|---|
| 3 modelos que pronostican + búsqueda normal | créditos de Metaculus (o tú si no dan) | ~0,34 $ por pregunta → ~270 $ hasta enero |
| Investigación con agentes de Opus 5.5 | tu **Claude Max** | 0 € extra, pero **gasta tu cupo semanal** (compartido con tus otros proyectos) |
| Minutos de GitHub | nadie (repositorio público) | 0 € |
- Créditos: ~100 $ al empezar a algunos bots; recargan si la MiniBench va por encima de la media; el
  extra por código abierto (~el doble) llega **después de un periodo de evaluación**, no al principio.
- Para quitar el uso de tu Max en cualquier momento: borra el secreto `CLAUDE_CODE_OAUTH_TOKEN`.

## Normas del torneo que conviene recordar (leídas por Cowork el 25/09)
- No hay botón de aceptar: inscribirse y enviar pronósticos equivale a aceptar las normas.
- La identidad se pide **al cobrar**: pago por Ramp (hay que comprobar que admite España/euros),
  documento de identidad y formulario W-8BEN (fiscal de EE. UU.); los impuestos los pagas tú.
- Para cobrar: enseñar el código o una descripción, aceptar una inspección (demostración y preguntas)
  y rellenar la encuesta. Un solo bot con premio por persona.
- Comentarios obligatorios y privados en cada pronóstico: el bot ya los publica como notas privadas.
- Prohibido: pronosticar a mano, retocar el bot mirando preguntas abiertas del torneo, relanzarlo
  porque no guste un resultado.
- Para **apagarlo**: borra la variable `ENVIO_REAL` (o ponla en `false`).

## Cuánto queda sin verificar (de frente)
- El bot **aún no ha hecho ni un pronóstico real**: falta la clave de créditos.
- Lo que encuentra la investigación con Claude Max y cuánto cupo gasta: se verá en la próxima prueba.
- La búsqueda en internet del modelo (`:online`): necesita la clave de créditos.
- Costes: estimaciones hasta la primera prueba con clave.

## Mejoras del 25/09 por la noche (decididas por ti): hechas
| Pieza | Qué hace | ¿Cambia los pronósticos? |
|---|---|---|
| Estudio de bots rivales | 25 agentes; informe en `docs/ESTUDIO_BOTS.md` (mejoras, datos de tus proyectos, backtest) | — |
| Marcador semanal | cada lunes cruza pronósticos y resultados → `docs/MARCADOR.md` | No |
| Comparador | en el marcador: qué forma de juntar a los 3 modelos habría ido mejor (media, sin Gemini, límites 1-99 %…). Gratis. Solo vale para decidir con ≥150 preguntas resueltas y ganando en las dos mitades | No |
| A. Registro completo | guarda la investigación entera y si funcionó, y el razonamiento de cada modelo | No |
| B. Orden y tiempo | primero las preguntas que cierran antes; sin investigación de Claude si cierra en <30 min | Apenas |
| C. Textos mejores | enlaces de las condiciones «para consultar primero», Claude «verifica primero», 3 reglas de lectura para los modelos | **Sí** (anotado en CHANGELOG) |
- Backtest con preguntas antiguas: **descartado** (no podemos ver sus resoluciones, la búsqueda
  «haría trampa» sin querer y costaría ~90 $). El comparador lo sustituye, gratis.
- Datos de tus otros proyectos: ninguno reutilizable tal cual; se revisa en 2 semanas.
- Plan de Claude: dices que tienes **Max**; la app de escritorio mostraba «Pro» (quizá otra cuenta).

## Limpieza de reglas (25/09, orden 12e del mando): hecha
- `CLAUDE.md` lleva solo lo propio; lo común está en las reglas comunes (se cargan solas). Ninguna
  regla ha cambiado de sentido: tabla de correspondencia en HALLAZGOS (25/09, «Limpieza de reglas»).
- Nuevos: `docs/MAESTRO.md` (qué es el bot y cómo debe ser) y `CHANGELOG.md` (historia de los
  parámetros). Pruebas: 62 de 62 en verde.

## El código a las reglas comunes (25/09, orden 14): hecho
- Decidiste adaptarlo ya. Hecho **sin cambiar qué pronostica el bot**: una prueba compara la
  configuración (modelos, pasadas, límites 2-98 %, tiempos, horarios) con una foto sacada antes de
  tocar nada, y sale idéntica. Detalle en HALLAZGOS (25/09 tarde).
- Ahora: Python 3.12; ruff (revisor de estilo del código) en local y en GitHub; cada número elegido
  está en `config/params.yaml` y, si falta uno, el bot para y dice cuál (antes usaba un valor
  escondido); tabla de límites de tamaño de los documentos en CLAUDE.md con su prueba.
- **Qué puedes comprobar tú:** en GitHub → pestaña «Actions» → flujo «Pruebas», la última ejecución
  en verde con dos trabajos, `pytest` y `ruff`.
- HALLAZGOS: lo del 24/09 ya está archivado en `docs/archivo/` (25/09 noche).

## Para el mando
- A las comunes §7 les falta decir qué hacer con un documento propio de un proyecto como
  `docs/DECISIONES.md` (aquí las decisiones del usuario van ahí, no en ESTADO ni CHANGELOG).
- Orden 14 terminada (25/09): código a las comunes §6 y tabla de límites con su prueba.

## Qué toca en la próxima sesión
- Si ya está la clave: repetir la prueba sin envío, leer el resultado y, si sale bien, preparar el
  encendido del envío real con tu «sí».
- La sesión de la nube debe descargar el repositorio de nuevo antes de trabajar (historial reescrito).
- Tras la primera semana con envío real: ¿el reloj lanza cada 20 min? ¿Cuánto cupo gasta Max?
- Semana del 28/09 (docs/ESTUDIO_BOTS.md §4): alarma por correo si hay preguntas abiertas sin
  pronóstico (probada con fallos simulados) y curva numérica suave «en sombra» (se guarda, no se envía).
