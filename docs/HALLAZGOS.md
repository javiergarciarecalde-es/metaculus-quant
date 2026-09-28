# Hallazgos (bitácora; solo crece)

> Las entradas del 24/09/2026 (sesión 1 y lectura de fuentes) están en `docs/archivo/HALLAZGOS_2026-09-24.md`.
> Las del 25/09/2026 hasta la orden 14 (sesión 2, esquema mixto, historial reescrito, limpieza de reglas) están en `docs/archivo/HALLAZGOS_2026-09-25.md`.

## 25/09/2026 (tarde) — El código a las reglas comunes (orden 14 del mando)
Decisión del usuario del 25/09: adaptarlo ya, antes del lunes 28/09. Resuelve los cuatro choques de
la entrada anterior. **El bot pronostica exactamente igual**: lo demuestra una prueba nueva
(`tests/test_configuracion_igual.py`) que guarda una «foto» de la configuración efectiva sacada
con el código de ANTES (modelos de cada puesto y su respaldo, esfuerzo, intentos, temperatura,
tiempos, pasadas, límites 2-98 % comprobados agregando pronósticos extremos, 1 % por opción,
investigación con Claude, qué torneos se piden en cada modo, cuántas preguntas se ensayan y los
horarios de los flujos) y la compara después de cada cambio. Salió idéntica en todos.
Además se comprobó aparte que los textos que se mandan a los modelos y el del marcador salen
letra por letra iguales (misma huella antes y después).
- **Python 3.12:** `forecasting-tools` 0.3.1 admite de 3.11 a 3.x; instalado todo desde cero con
  3.12 las pruebas pasan. En GitHub también (flujo de pruebas en verde con 3.12).
- **ruff** (el revisor de estilo): misma configuración y tope de versión que los hermanos. El
  formateo va en un commit aparte (e25b134). Las líneas largas dentro de los textos para los
  modelos no se parten (cambiaría lo que leen): llevan la marca `noqa`. Único cambio que se nota
  fuera de GitHub: la fecha «Today is» de los textos se calcula en UTC (en GitHub ya lo era).
  En el flujo de pruebas, ruff es un trabajo aparte: si falla, pytest se ejecuta igual.
- **Parámetros sin valor por defecto:** lector `bot/params.py` (copia de cripto-quant) que para y
  dice qué falta. Pasaron al YAML, con el mismo valor, los números que estaban en el código:
  intentos por modelo, temperaturas del lector, búsquedas a la vez, letras del informe que se pasan
  al director y a Claude (6.000), recortes del registro, espera del marcador (24 h) y tiempos de
  red. Se quedan en el código, a propósito, los hechos (0,1-99,9 % que acepta Metaculus) y los
  recortes de los mensajes en pantalla. Los intentos del director y del lector siguen siendo los de
  la librería (no son un número nuestro). Prueba nueva: cada parámetro del YAML lo lee alguien
  (`tests/test_params_vivos.py`); la puerta no cuenta como ajuste.
- **Tabla de límites** de los documentos en CLAUDE.md y `tests/test_documentacion.py`.
- **Autor de los commits:** el repositorio firmaba como «Claude <noreply@anthropic.com>»; desde
  esta orden firma con la dirección anónima del usuario (comunes §10), solo en este repositorio.
- Ensayo sin envío ni claves: igual que antes (aviso amarillo «Falta METACULUS_TOKEN», código 0;
  la ejecución programada con el envío apagado no hace nada). 82 pruebas en verde.

## 25/09/2026 — Estudio de bots rivales, datos de los otros proyectos y backtest (25 agentes)
Informe completo en `docs/ESTUDIO_BOTS.md` (4 bots con puesto conocido, descripciones de los mejores
cerrados, criba de ~20 bots más, 5 proyectos del usuario en solo lectura, viabilidad del backtest;
un escéptico por cada mejora candidata). Lo esencial:
- Lo básico ya lo tenemos (3 empresas, mediana, 2-98 %, GPT con razonamiento). Mejora más segura:
  **vigilancia** (alarma si hay preguntas abiertas sin pronóstico; primero lo que cierra antes) y
  **registro completo** (informe de investigación entero, estado de la investigación). Ambas 0 $.
- Única mejora de pronóstico medida (débil): curva numérica PCHIP (+2,39 [+0,21, +4,59] en 97 preguntas
  de edisonymy, elegida entre 13 variantes) → proponer solo «en sombra».
- Revisor/juez/debate/Delphi: sin efecto donde se midió (joy-void: 0 cambios en 72 sesiones, ~2,7 $/pregunta).
- Otros proyectos: ningún dato reutilizable tal cual; solo fuentes públicas (FRED, Yahoo, CBOE, BCE,
  DefiLlama); Binance/Bybit bloquean los servidores de EE. UU. de GitHub. Esperar 2 semanas y contar.
- Backtest con preguntas antiguas: **no** (no podemos leer sus resoluciones; la búsqueda filtra la
  respuesta en el 71-81 % de casos; ~90 $). Sí: comparar gratis combinaciones de los 3 miembros ya
  registrados; hacen falta ~125 preguntas pareadas para ver +3 puntos.

## 25/09/2026 (noche) — Mejoras A, B, C y comparador (decisión del usuario)
- A: el registro guarda la investigación entera (búsqueda y Claude por separado) con su estado
  (ok / vacía / fallo / tiempo; Claude: ok / sin_secreto / sin_cupo / fallo / tiempo /
  saltada_poco_tiempo), criterios, letra pequeña, cierre, fecha dada a los modelos y el razonamiento
  completo de cada modelo. El marcador pasa ese texto largo a `datos/detalle/` (un fichero por pregunta).
- B: preguntas ordenadas por hora de cierre; sin Claude si cierran en menos de 30 min.
- C: enlaces de las condiciones de resolución (hasta 5) en la búsqueda y en Claude; «fecha y volumen al
  citar un mercado»; Claude «verifica primero» 2-3 datos clave; 3 reglas de lectura en los prompts.
- Comparador (`bot/comparador.py`): cambio de puntuación ≈ 100·ln(p_variante/p_enviada) por pregunta
  (sí/no y opciones). Control: la variante «mediana (la actual)» da 0. Decididas de antemano: media,
  sin google, límites 1-99 %. Regla: ≥150 resueltas y ganar en las dos mitades.
- 98 pruebas en verde; ruff limpio.

## 27/09/2026 — Orden 26: clave de créditos, tope de gasto y encendido
- **Clave:** el secreto `OPENROUTER_API_KEY` existe (comprobado solo el nombre). Ensayo sin envío
  lanzado a mano: **verde, «Terminado: 3 pronósticos de ensayo»** (ejecuciones 36338357573 y
  36339352166). Un fallo pasajero de Gemini (503) lo cubrió su respaldo.
- **La clave de Metaculus gasta como «byok»:** en la consulta real `usage` = 0 y lo gastado va en
  `byok_usage`, que cuenta en el límite. Límite **100 $**, sin renovación. Si el código hubiera
  mirado solo `usage`, habría creído que nunca gastaba. Se suma `usage` + `byok_usage`; lo que queda
  se toma de `limit_remaining`.
- **Coste real:** el primer ensayo (3 preguntas) costó **0,91 $** según la clave, es decir **~0,30 $ por
  pregunta**. La librería solo contó 0,55 $ porque no mide la búsqueda `:online`. 100 $ ≈ 330
  preguntas; hasta enero salen ~420 de MiniBench y 300-400 de la temporada.
- **Tope de gasto** (`bot/presupuesto.py`): antes de cada torneo pregunta a la clave cuánto queda.
  La reserva es de 3 $. La MiniBench va primero y solo la para la reserva. La temporada va al ritmo
  de una línea: 25 % desde el primer día y el resto repartido por igual hasta el 06/01. Previsión
  de 0,40 $ por pregunta para contar cuántas caben, y freno de 1,50 $ por pregunta (solo de lo que
  mide la librería). Sin dinero: aviso amarillo, sin rojo. Si OpenRouter contesta 402 a mitad, no
  cuenta como fallo. Con estos números la temporada tendrá pocas preguntas hasta que llegue más
  dinero: la MiniBench (~18 $ por ronda) va por delante de la línea desde la 2.ª ronda.
- **Plan de Claude (investigación con agentes):** entre 2,2 y 2,8 $ equivalentes por pregunta. Una
  tanda de 3 preguntas movió ~9-11 puntos la ventana de 5 horas (medido con la sesión de desarrollo
  también en marcha, así que es una cota alta) y ~1 punto el tope semanal (88 → 89 → 90 %). Una de 3
  investigaciones se pasó de los 300 s.
- **Experimento «Claude sí / Claude no»** (decisión del usuario del 27/09; reglas escritas ANTES de ver
  resultados, regla común 3): Claude investiga solo las preguntas de **número par**; las impares son
  el grupo de comparación. Cómo se mide: la puntuación de pares media por pregunta resuelta en cada
  grupo, con los números del marcador. Solo se decide con **≥150 preguntas resueltas en total**. Se
  da por bueno que Claude ayuda si su grupo gana **en las dos mitades** (ordenadas por fecha de
  cierre), la misma regla que el comparador. Hasta enero solo se verían diferencias grandes, de unos
  5-10 puntos.
- **Envío encendido** (27/09, 21:04, con el «sí» del usuario). Prueba a mano en la zona de pruebas:
  **8 pronósticos enviados** («Posted prediction» de Metaculus, cada uno con su comentario privado).
  Fallo encontrado: con el envío encendido, la zona de pruebas **no se limitaba a 3 preguntas** y hacía
  todas, gastando créditos y plan en preguntas de práctica. Se paró a los 14 min y se corrigió (3
  preguntas también con envío, con su prueba). El reparto par/impar funcionó: 5 con Claude y 3 sin.
- Plan de Claude en esa prueba: 1,7-2,1 $ equivalentes por investigación. La ventana de 5 h pasó de
  11 a 30 % con ~6 investigaciones y esta sesión en marcha: **~3 puntos por investigación** (cota
  alta). El tope semanal pasó de 90 a 92 %.
- **Primera ejecución automática en torneo** (19:18 UTC): verde, **1 pronóstico enviado en la
  temporada** (pregunta 45707); la MiniBench no tenía preguntas abiertas. El tope decía «llevamos
  5,36 $ de 25,00 $ permitidos». Coste medio hasta aquí: ~0,35 $ por pregunta (5,36 $ entre ~15).
- **Pausa de Claude hasta el 28/09 a las 11:00** (decisión del usuario): el tope semanal estaba al
  92 %. Para el experimento par/impar, **las preguntas pronosticadas durante la pausa se quitan de
  los dos grupos** (escrito antes de ver resultados).
- **Tres mejoras antes de que abra la temporada** (27/09 noche, decisión del usuario, orden 26):
  (1) **vigilancia que reacciona sola** (`vigilancia.yaml`, a :13 y :43): si el bot se calla más de
  45 min, si su última ejecución falla o si hay preguntas abiertas hace más de 1 h sin pronóstico que
  el tope sí permitiría, lo relanza; tras 2 relanzamientos en 3 h sin arreglo, despierta a Claude
  (40 turnos, 5 $ equivalentes, una vez cada 12 h como mucho, respetando la pausa del plan). Claude
  solo ve líneas de error, no puede subir nada: un paso aparte comprueba que su arreglo no toca lo
  prohibido y lo deja en una rama `vigilancia/…` más un issue. 40 pruebas con fallos simulados.
  (2) **coste por parte** en cada pregunta (`coste_partes`) y resumen semanal del gasto en el
  marcador (clave frente a librería y frente a la línea). La medida por parte suma exactamente el
  total de la librería (probado). (3) **curva PCHIP en sombra** en las numéricas (`sombra_pchip`):
  misma construcción que la librería (mismos puntos y escala), solo cambia rectas por curva suave;
  coincide con la de scipy hasta 1e-12. Ninguna cambia lo que se envía.
- **Sacado de ESTADO el 27/09 (22:45) por su tope de palabras:** la tabla «Lo último que se hizo
  (orden 26)» (clave comprobada por su nombre; prueba sin envío en verde dos veces; 0,91 $ las 3
  primeras preguntas; tope con 31 pruebas; 8 enviados en la zona de pruebas; 1.ª ejecución en torneo
  verde con 1 enviado en la temporada, pregunta 45707; la zona de pruebas con envío hacía todas las
  preguntas y se limitó a 3) y la nota de que la carpeta vieja `stoic-burnell-55dfc1` y las ramas
  `elastic-maxwell`, `lucid-dewdney` y `stoic-burnell` ya estaban fusionadas en `main`.
- **Más mejoras gratuitas** (27/09 noche, «adelante» del usuario): lista semanal de preguntas
  perdidas en el marcador (el bot apunta ahora las que deja el tope, línea «dejadas»); piezas de
  GitHub sobre Node 24 (checkout v5, setup-python v6, setup-node v5, upload-artifact v6; Node 20 se
  quitó el 23/09); la curva suave pasa a ser una de las 3 comparaciones decididas de antemano (antes
  de ver resultados) y el comparador la puntúa frente a la enviada (50 · ln del cociente del tramo).
  AskNews: hace falta que el usuario cree su cuenta en my.asknews.app y escriba a rob@asknews.app
  (fuente: plantilla oficial de Metaculus, leída con una búsqueda web el 27/09); ~3.000 consultas al
  mes por bot. El Gmail conectado a la sesión en la nube era otra cuenta: no se usó.
- **Qué modelos deja usar la clave de créditos** (28/09, 05:09 UTC, flujo «Modelos de la clave»,
  consulta gratuita `GET /api/v1/models/user`): **156 de 458** modelos públicos, solo de **OpenAI
  (89), Anthropic (25) y Google (24)**, más alias «~…-latest» de esas tres y 7 enrutadores
  (`openrouter/auto`, `openrouter/free`…, `typesafe/jev-router`). **Ningún modelo chino** (DeepSeek,
  Qwen, Kimi…): confirmado lo que decían las notas de nostreambot. Nuestros modelos, todos
  permitidos. Si se quiere abaratar con los créditos, la vía es un modelo barato de esas tres
  empresas (se propone tras la 1.ª semana, con el gasto por partes).
- **Precios y cambio a Gemini 3.8 Flash** (28/09, consulta gratuita de la clave): Google permitidos
  incluyen `gemini-3.8-flash` (0,75/3,75 $ por millón de tokens de entrada/salida) y `3.5-flash` (el
  que usábamos: 1,5/9 $). Los nuestros: GPT-6 y GPT-5.6 2/10 $, Opus 5.5 4/20 $, Opus 4.8 5/25 $,
  lector gpt-4o-mini 0,15/0,6 $. El usuario decidió pasar a 3.8 Flash (~06:50 UTC): en el marcador,
  las preguntas anteriores llevan 3.5 Flash.
- **Modelos elegidos por el usuario** (28/09 ~07:50 UTC): búsqueda con Opus 5.5 `:online` (antes
  GPT-5.6 Sol), nuevo respaldo de la búsqueda GPT-6 Sol `:online`, respaldo de OpenAI GPT-6 Astra,
  Anthropic sin respaldo. **Sin verificar en vivo:** que `claude-opus-5.5:online` funcione con la
  clave de créditos y cuánto cuesta su búsqueda web; si falla, entra el respaldo y el registro lo
  dice (`base_estado` = «respaldo»). Riesgo anotado: Opus 5.5 busca y también pronostica, así que
  su visión entra dos veces (el texto de la búsqueda le prohíbe dar pronósticos). Los «:batch» (por
  lotes, más baratos) no sirven: preguntas abiertas ~1,5-3 h.
- **Opción A y clasificador en sombra** (decisión del usuario, 28/09 ~08:20 UTC). Reglas escritas
  ANTES de ver resultados (regla común 3):
  - **Experimento par/impar redefinido:** desde esta hora, pares = búsqueda de Claude Max (sin la
    de pago), impares = búsqueda de pago (Opus 5.5 `:online`). Las preguntas anteriores (pares con
    las dos búsquedas, o con Claude en pausa) quedan fuera de esta comparación. Las pares en las
    que Claude falló y entró la de pago cuentan en su grupo (par): es lo que pasa de verdad. Misma
    regla que antes: ≥150 resueltas y ganar en las dos mitades; hasta enero solo se verán
    diferencias grandes. Para pasar a la opción B basta con que Max **no salga peor** (su ventaja
    es el dinero) y que el plan del usuario lo aguante.
  - **Clasificador en sombra:** solo pasa a decidir si las «difíciles» puntúan peor que las
    «fáciles» por más que el margen del 95 %, con ≥30 resueltas en cada grupo. La discrepancia
    entre los 3 modelos se mira con la misma regla. Revisión preliminar: semana del 05/10 (con
    pocas resueltas será solo una primera mirada, no una decisión).
- **Dos clasificadores en sombra** (28/09 ~08:40 UTC, decisión del usuario): Gemini 3.8 Flash
  (créditos) y Claude Opus 5.5 con `--effort xhigh` (plan Max, sin herramientas:
  `--disallowedTools "*"`; opciones comprobadas en la documentación de Claude Code). Regla escrita
  antes de ver resultados: se queda el que separe más la puntuación de «difíciles» y «fáciles»
  con la regla del clasificador; si no hay diferencia clara entre los dos, Gemini (no gasta plan).
  Coste en plan de Opus por pregunta: se apunta en `clasificador_opus.usd_equivalente`.
- **Fallo del marcador del 28/09 (06:45 UTC), arreglado:** la lista de preguntas perdidas llamaba
  sin esperar a una función asíncrona de la librería (`get_questions_matching_filter`) y el
  marcador entero salió en rojo, sin su commit semanal. Mi prueba no lo vio porque simulaba esa
  función. Arreglo: se espera con asyncio; prueba con un cliente simulado asíncrono como el real;
  prueba que avisa si la librería cambia; y cada sección nueva del marcador va aparte: si una
  falla, sale «Esta semana falló» y el resto del marcador (y su commit) sigue.
- **Automatización revisada** (28/09, pregunta del usuario «¿va todo solo?»): bot, vigilancia y
  marcador van solos en GitHub. Faltaba la **revisión**: se programó una rutina de Claude Code
  (cada lunes 09:12 de Madrid, desde el 05/10, en la conversación de esta sesión) que lee el
  marcador, aplica las reglas escritas y propone decisiones al usuario sin cambiar nada por su
  cuenta. El primer marcador (28/09) falló por un fallo mío (arreglado) y daba 51 «perdidas» del
  21-24/09, con el bot apagado (arreglado: `marcador.perdidas_desde_utc`). Queda sin red por
  debajo: si el reloj de GitHub se parase del todo, se pararían bot y vigilancia hasta el lunes.
- **Cierre de la sesión en la nube** (28/09 ~09:05 UTC). Para retomar sin esta conversación:
  - **Correo para AskNews** (lo manda el usuario desde javiergarciarecalde@gmail.com a
    rob@asknews.app, tras crear su cuenta en my.asknews.app). Asunto: «AskNews access request for
    Metaculus Fall 2026 bot tournament – Kyou-bot». Cuerpo: presentación (Javier García Recalde),
    email de la cuenta de AskNews, bot «Kyou-bot», uso de /news (no /deepnews), ~1 búsqueda por
    pregunta (300-400 en la temporada más MiniBench), bot autónomo en GitHub Actions con 3 modelos,
    código abierto en github.com/javiergarciarecalde-es/metaculus-quant, y petición de confirmación
    de activación, límites y renovación. Con las claves: no ponerlas hasta decidirlo con datos.
  - **Rutina de revisión semanal** (si hay que rehacerla): cada lunes 09:12 de Madrid; lee
    docs/MARCADOR.md y datos/marcador.json, comprueba que el marcador salió en verde (si no,
    arreglarlo con pruebas), resume en español llano (pronósticos, puntos, gasto frente a la
    línea, perdidas, clasificadores, Max frente a pago), aplica solo las reglas escritas de
    antemano, revisa la salud (vigilancia, reloj, clave, plan) y propone decisiones al usuario sin
    cambiar pronósticos, modelos ni parámetros por su cuenta; actualiza ESTADO y HALLAZGOS.
- **28/09 ~09:35 UTC, decisiones del usuario:** el **lector** pasa a GPT-6 Sol (con
  `temperatura_lector` null: los modelos que razonan pueden rechazar temperatura 0; la librería le
  pone además 60 s de espera en vez de 40). **AskNews:** cuenta creada y correo enviado por el
  usuario; pendiente de respuesta. Al llegar las claves: no ponerlas sin decidirlo con datos (el
  bot cambiaría al momento de fuente de noticias; pérdida de lectura de las páginas de resolución).

## 28/09/2026 (tarde) — Orden 27: auditoría de normas del torneo (sesión local)
Normas releídas en la página oficial (docs/FUENTES.md). Lo que se miró y lo que salió:
- **¿Algún cambio desde el 27/09 se decidió viendo pronósticos de preguntas abiertas?** No
  encontrado. Cada cambio tiene su motivo escrito (gasto, preferencia del usuario sobre modelos,
  diseño decidido de antemano, averías) y ninguno cita un pronóstico. La única pregunta del torneo
  pronosticada (45707, del 27/09 19:19 UTC al cierre ~06:00 del 28/09) solo se miró en sus líneas
  de «enviado» (sesión local de la orden 26, buscado en su conversación). La sesión en la nube no se
  puede leer desde aquí: queda como «no encontrado», no como «comprobado».
- **¿Puede la prueba a mano o la vigilancia volver a pronosticar una pregunta?** En la práctica no:
  en modo torneo el bot salta las ya pronosticadas y, tras enviar la 45707, las ejecuciones de
  19:32, 19:51 y 20:18 la vieron abierta y no la tocaron (0 enviados). La zona de pruebas sí repite
  (no puntúa). La vigilancia relanza el bot entero, que solo hace las que faltan: permitido.
- **Dos agujeros encontrados y cerrados, con pruebas** (`bot/normas.py`, `tests/test_normas.py`):
  (1) la librería **falla abierta**: si Metaculus dejara de mandar el historial de nuestros
  pronósticos, daría todas las preguntas por nuevas y el bot las repetiría cada 20 min; ahora esa
  pregunta no se pronostica y la ejecución sale en rojo. (2) Una pregunta que llegara **repetida**
  en la lista se pronosticaba dos veces (la foto de configuración pasó de 12 a 6 envíos con la
  lista duplicada de las pruebas); ahora una vez.
- **Marcador:** subía al repositorio público los pronósticos «de hace más de 24 h» suponiendo que
  la pregunta ya había cerrado; la 45707 siguió abierta ~11 h, así que en la temporada podría no
  bastar. Ahora exige además que su hora de cierre haya pasado. Hasta hoy no se había publicado
  ninguno (marcador del 28/09: 0 cerrados).
- **Riesgos que quedan, para el usuario:** (a) el repositorio es público y los registros de GitHub
  (y los artefactos) muestran investigación y pronósticos mientras la pregunta está abierta: otro
  podría copiarlos. Las normas no lo prohíben; hacerlo privado gastaría minutos de GitHub
  compartidos (el bot y la vigilancia usan ~120 al día). (b) La comprobación programada de las 09:48 UTC (rutina de
  la sesión en la nube) lee el registro de preguntas abiertas: mira estados y costes, que es
  vigilancia, pero con la regla de cambios (CLAUDE.md) no debe mirar pronósticos. (c) La vigilancia
  enseña a Claude líneas de aviso que podrían incluir un trozo de texto de un modelo; sus arreglos
  solo pueden tocar infraestructura, así que no ajusta pronósticos.
- **Otros fallos de método:** 23 commits de la sesión en la nube firmados como «Claude
  <noreply@anthropic.com>» (comunes §10 pide la dirección anónima del usuario; no es su correo
  personal y no se reescribe el historial). La prueba de la curva suave frente a scipy se saltaba
  siempre en GitHub (scipy no estaba instalada): ahora corre y pasa (coincide hasta 1e-12).
- **Regla de cambios** escrita en CLAUDE.md (orden 27, aprobada por el usuario).

## 28/09/2026 (tarde) — Orden 27: lo que gasta el bot del plan de Claude y su tope
- **Medido de verdad** (las 11 investigaciones del 27/09 en la zona de pruebas, registro de GitHub):
  10 salieron bien, entre 1,54 y 2,76 $ equivalentes (media 2,07 $); una se cortó a los 300 s sin
  decir cuánto gastó. El tope semanal se movió 5-6,6 $ por punto (cota baja: otras sesiones
  gastaban a la vez). **Sin medir aún:** el clasificador con Opus «xhigh» (se añadió el 28/09 a las
  08:30 UTC y desde entonces no ha habido preguntas; estimación 0,05-0,3 $ por pregunta), la
  vigilancia despertando a Claude (nunca ha hecho falta; freno 5 $) y la revisión de los lunes (aún
  no ha corrido; reserva de 5 $).
- **Previsión por semana** (20-30 preguntas por semana mientras solo haya 100 $ de créditos; la mitad,
  pares): investigación 20-30 $, clasificador con Opus 1-9 $, vigilancia 0 (máximo 10 $), revisión
  ~5 $: **~5-9 % del tope semanal** en una semana normal; en una semana de ronda de MiniBench con
  muchas preguntas, el tope del 15 % frena primero a Opus y luego a la investigación.
- **La comprobación encadenada de la nube** (cada 4 h hasta el 05/10, despertando una conversación
  muy larga) podía gastar más que todo el bot junto: apagada con el «sí» del usuario (12:07).
- **Tope puesto** (`bot/plan_claude.py`): 15 % del tope semanal = 70 $ equivalentes por semana del
  plan (5 $ por punto, menos 5 $ de reserva para la revisión). Al 80 % (56 $) se apaga el
  clasificador con Opus; al 100 %, la investigación con Claude y los despertares de la vigilancia.
  La vigilancia, además, como mucho 2 despertares por semana. Cada uso apunta su coste en un
  artefacto `plan-claude-<id>` (orden de la lista de artefactos de GitHub: de más nuevo a más viejo,
  visto en la respuesta real del 28/09). Si la cuenta no se puede leer, solo se apaga Opus.
- **Regla escrita antes de ver resultados (experimento par/impar):** las preguntas pares que se
  queden sin Claude por el tope (`claude_estado` = «tope_plan») se quitan de la comparación, igual
  que las de la pausa; las impares no se tocan.
- **Calibrar el «5 $ por punto»:** con la tarjeta de uso de la aplicación (el % semanal) y la tabla
  «Plan de Claude» del marcador de los lunes. Si sale otra cifra, se cambia en `config/params.yaml`
  con su entrada en CHANGELOG.

## 28/09/2026 (tarde) — Orden 27: lo que quedaba sin verificar y la revisión semanal
- **Relanzamiento de la vigilancia, comprobado en GitHub de verdad** (sin preguntas abiertas, así
  que sin pronosticar nada): (1) con el botón de prueba nuevo (vigilancia 36409654631 → bot
  36409737166, lanzado por «github-actions[bot]», que es como la vigilancia reconoce los suyos);
  (2) **sola**, a las 10:31 UTC (vigilancia 36410150135 → bot 36410250191), porque la ejecución
  anterior había fallado. Ninguna despertó a Claude (hacen falta 2 relanzamientos en 3 h sin arreglo).
- **Fallo encontrado por el camino:** esas dos ejecuciones relanzadas salieron en rojo al instalar
  las piezas: pypi.org no contestaba a las máquinas de GitHub (5 esperas de 15 s agotadas en
  `python-dateutil`) y pip acabó diciendo «ResolutionImpossible». No era el código (las pruebas de
  un minuto antes instalaron lo mismo). Arreglo: la instalación de bot, vigilancia y marcador
  reintenta 10 veces con 60 s de espera y, si aun así falla, otra vez al minuto (prueba en
  `tests/test_flujos.py`). Una ejecución a mano a las 10:37 (0 preguntas abiertas, 0 enviados)
  salió en verde, así que la vigilancia no llegó a despertar a Claude por un corte ya pasado.
- **Sin poder verificar todavía** (no hay preguntas en ningún torneo desde las ~06:00 UTC): la
  vuelta de la investigación tras la pausa, la opción A, los clasificadores y el tope de gasto con
  una ronda de MiniBench. La página de la MiniBench da 403 desde aquí (fecha de la próxima ronda
  desconocida).
- **Revisión semanal rehecha** (sí del usuario, 12:07): rutina nueva `trig_01P1NPoMLt4LgerQFDWu4MZ8`
  («metaculus-quant: revisión semanal (lunes, escribe en el repo)»), lunes 09:12 de Madrid, Sonnet 5
  (más barato para el plan; la tarea es leer el marcador y aplicar reglas ya escritas), memoria
  limpia en cada vuelta, sin conectores (se le quitaron Gmail, Drive y Calendar, que se añadían
  solos), firma los commits con la dirección anónima del usuario, no arregla ni cambia nada y
  sobrescribe `docs/REVISION_SEMANAL.md`. Apagadas (no borradas) las tres rutinas que vivían en la
  conversación de la nube: `trig_01Jpv6Pfyp3yo3SxcknZAs4f` (revisión vieja),
  `trig_01X5xNNWkveFfeTSNe6no1xy` (ya había corrido) y `trig_01392sLyrpnQiigTnsHXj3Qx` (la
  encadenada cada 4 h). Esa conversación ya se puede archivar.
